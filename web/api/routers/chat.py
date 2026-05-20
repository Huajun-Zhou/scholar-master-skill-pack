"""Chat SSE streaming endpoint.

For MVP, this endpoint assembles context and streams it back as
structured SSE events without an actual LLM call. The structure is
designed so an LLM integration can be swapped in later.
"""

from __future__ import annotations

import asyncio
import json
import time
import uuid
from pathlib import Path
from typing import Any, AsyncGenerator

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from services.context_assembler import assemble_context, classify_question
from services.content_loader import load_all_papers
from services.llm_client import stream_answer
from services.evidence_checker import check_hallucination

router = APIRouter(prefix="/api", tags=["chat"])

# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class ChatRequest(BaseModel):
    question: str = Field(..., min_length=1, description="User's research question")
    session_id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="Optional session identifier",
    )


# ---------------------------------------------------------------------------
# SSE event helpers
# ---------------------------------------------------------------------------


def _sse_data(event: str, data: dict[str, Any]) -> str:
    """Format a single SSE event with ``event`` and ``data`` fields."""
    return json.dumps({"event": event, **data}, ensure_ascii=False)


def _sse_event(event: str, data: dict[str, Any]) -> dict[str, str]:
    """Return the dict format expected by ``EventSourceResponse``."""
    return {"event": event, "data": json.dumps(data, ensure_ascii=False)}


# ---------------------------------------------------------------------------
# Streaming chat
# ---------------------------------------------------------------------------


@router.post("/chat")
async def chat_stream(request: Request, body: ChatRequest):
    """SSE streaming chat endpoint.

    Streams events:
        1. ``context-assembly``  — assembled context sections
        2. ``answer``            — answer text (multiple chunks)
        3. ``evidence-section``  — structured A/B/C evidence
        4. ``done``              — final event with metadata

    For MVP this returns the assembled context + a constructed prompt
    (no actual LLM call). The architecture supports plugging in an LLM
    by replacing the ``generate_answer`` coroutine.
    """
    root: Path = request.state.project_root
    question = body.question.strip()
    session_id = body.session_id or str(uuid.uuid4())

    if not question:
        raise HTTPException(status_code=400, detail="Question is required")

    async def event_generator() -> AsyncGenerator[dict[str, str], None]:
        # --- Phase 1: assemble context ---
        yield _sse_event("status", {"phase": "context-assembly", "message": "正在检索 Scholar Wiki..."})

        try:
            context = assemble_context(root, question)
        except Exception as exc:
            yield _sse_event(
                "error",
                {"message": f"Failed to assemble context: {exc}"},
            )
            return

        qtype = context["question_type"]
        n_sections = len(context["context_sections"])
        n_evidence = len(context["evidence_sources"])

        yield _sse_event(
            "context-assembly",
            {
                "question": question,
                "question_type": qtype,
                "sections_count": n_sections,
                "evidence_count": n_evidence,
                "scholar_briefing_loaded": bool(context["scholar_briefing"]),
            },
        )

        # --- Phase 2: generate answer via DeepSeek LLM ---
        yield _sse_event("status", {"phase": "answer", "message": "正在通过 DeepSeek 生成回答..."})

        assembled_text = context["assembled_text"]
        full_answer = ""

        try:
            async for token in stream_answer(question, assembled_text, qtype):
                full_answer += token
                yield _sse_event("answer", {"chunk": token, "session_id": session_id})
        except Exception as exc:
            yield _sse_event(
                "error",
                {"message": f"LLM 调用失败: {exc}"},
            )
            preview = (
                f"\n\n---\n*[LLM 调用失败，以下为上下文预览]*\n\n"
                f"## 回答预览\n\n{assembled_text[:2000]}...\n"
            )
            yield _sse_event("answer", {"chunk": preview, "session_id": session_id})

        # --- Phase 3: answer self-check (evidence verification) ---
        yield _sse_event(
            "status",
            {"phase": "evidence-check", "message": "正在验证引用的证据..."},
        )

        hallucination_warning = check_hallucination(full_answer, root)
        if hallucination_warning:
            yield _sse_event("answer", {
                "chunk": hallucination_warning,
                "session_id": session_id,
            })
            yield _sse_event(
                "warning",
                {
                    "type": "hallucination_check",
                    "message": "部分 evidence_id 未在知识库中找到，可能为 LLM 幻觉。",
                },
            )

        # --- Phase 4: evidence section ---
        yield _sse_event(
            "status",
            {"phase": "evidence-section", "message": "正在整理证据..."},
        )

        evidence_section = _build_evidence_section(context, root)
        yield _sse_event("evidence-section", evidence_section)

        # --- Phase 5: done ---
        yield _sse_event(
            "done",
            {
                "session_id": session_id,
                "question_type": qtype,
                "sections_used": n_sections,
                "evidence_ids_found": n_evidence,
                "timestamp": time.time(),
            },
        )

    return EventSourceResponse(event_generator())


# ===================================================================
# MVP answer construction
# ===================================================================


def _build_answer_preview(
    question: str, qtype: str, context: dict[str, Any]
) -> list[str]:
    """Build the answer text chunks for MVP mode.

    Returns a list of text chunks (simulating streaming tokens).
    """
    parts: list[str] = []

    # Intro header
    parts.append(f"## 回答预览\n\n")
    parts.append(f"**问题类型**: {qtype}\n\n")

    if qtype == "factual":
        parts.append("以下是根据 Scholar Wiki 检索到的事实信息：\n\n")
    elif qtype == "method":
        parts.append("以下是与该方法问题相关的方法卡片内容：\n\n")
    elif qtype == "transfer":
        parts.append("以下是用于方法迁移的基础上下文（请注意：迁移推断属于 C 类证据）：\n\n")
    elif qtype == "review":
        parts.append("以下是用于论文审查的参考上下文：\n\n")

    # Assembled context (condensed)
    sections = context.get("context_sections", [])
    for sec in sections[:5]:  # top 5 sections
        title = sec.get("title", "")
        content = sec.get("content", "")
        # take first 300 chars as preview
        preview = content[:300].strip()
        if len(content) > 300:
            preview += "..."
        parts.append(f"### {title}\n\n{preview}\n\n")

    # Note about MVP mode
    parts.append(
        "\n---\n\n"
        "*[MVP 模式] 以上内容是基于本地知识库检索到的上下文预览。"
        "接入 LLM 后此处将显示完整的自然语言回答。*\n\n"
    )

    # Full assembled text for transparency
    parts.append(
        "\n<details><summary>点击查看完整上下文</summary>\n\n"
    )
    parts.append(f"```markdown\n{context['assembled_text'][:2000]}\n```\n\n")
    parts.append("</details>\n")

    return parts


def _build_evidence_section(
    context: dict[str, Any], root: Path
) -> dict[str, Any]:
    """Build the structured A/B/C evidence section.

    Returns:
        {
            "a_direct": [...],
            "b_synthetic": [...],
            "c_transfer": [...],
            "total": int,
        }
    """
    evidence_ids = context.get("evidence_sources", [])
    papers = load_all_papers(root)

    a_evidence: list[dict[str, str]] = []
    b_evidence: list[dict[str, str]] = []
    c_evidence: list[dict[str, str]] = []

    # For each evidence ID, assign a category based on heuristic
    for evid in evidence_ids:
        entry = {"evidence_id": evid}

        # Try to find the source paper
        paper_match = None
        for p in papers:
            if evid.startswith(f"EVID-{p['paper_id']}"):
                paper_match = p
                break

        if paper_match:
            entry["paper_id"] = paper_match["paper_id"]
            entry["paper_title"] = paper_match["title"]

        # Simple heuristic: if evidence_id appears in multiple papers, it's B
        paper_count = sum(1 for p in papers if evid.startswith(f"EVID-{p['paper_id']}"))
        if paper_count >= 2:
            entry["level"] = "B"
            b_evidence.append(entry)
        elif "TRANSFER" in evid.upper() or "C" in evid.split("-")[-1][:1]:
            entry["level"] = "C"
            c_evidence.append(entry)
        else:
            entry["level"] = "A"
            a_evidence.append(entry)

    return {
        "a_direct": a_evidence,
        "b_synthetic": b_evidence,
        "c_transfer": c_evidence,
        "total": len(a_evidence) + len(b_evidence) + len(c_evidence),
    }
