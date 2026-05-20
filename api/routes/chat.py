"""POST /api/chat — SSE 流式问答，使用 DeepSeek LLM 生成真正的学术回答。"""

from __future__ import annotations

import json
import os
import uuid
from pathlib import Path

from fastapi import APIRouter
from openai import OpenAI
from starlette.responses import StreamingResponse

router = APIRouter()

DEEPSEEK_BASE_URL = "https://api.deepseek.com"
DEEPSEEK_MODEL = "deepseek-chat"

# 项目根
_ROOT = Path(__file__).resolve().parent.parent.parent


def _make_client(api_key: str) -> OpenAI:
    """用用户的 API key 创建 DeepSeek 客户端。"""
    return OpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)


@router.post("/chat")
async def chat(req: dict):
    """SSE 流式问答接口 — DeepSeek LLM 驱动。

    Request:  {"question": "...", "api_key": "sk-...", "session_id": "..." (optional)}
    用户的 api_key 不会被存储，仅用于当次请求。
    """
    question = req.get("question", "").strip()
    if not question:
        return StreamingResponse(_empty_stream("问题不能为空"), media_type="text/event-stream")

    api_key = req.get("api_key", "").strip()
    if not api_key:
        return StreamingResponse(
            _empty_stream("请先设置 DeepSeek API Key（在侧边栏点击齿轮图标）"),
            media_type="text/event-stream",
        )

    session_id = req.get("session_id", str(uuid.uuid4())[:8])

    async def generate():
        # Phase 1: 上下文检索
        yield _sse("phase", {"phase": "context-assembly"})

        # 加载学者速览
        briefing = _load_briefing()
        # 构建 Wiki 上下文
        wiki_context = _build_context(question)

        yield _sse("phase", {
            "phase": "context-found",
            "sections_count": 8,
            "sections": {"context_chars": len(wiki_context)},
        })

        # Phase 2: LLM 生成
        yield _sse("phase", {"phase": "answer"})

        system_prompt = f"""你是基于一位通信安全学者（陈志远教授，北京邮电大学网络空间安全学院）15篇公开论文构建的科研助手。你不是该学者本人，而是基于其公开成果的AI研究助手。

## 学者的研究画像
{briefing}

## 回答规则
1. **先给出核心回答**：基于知识库中的证据直接回答问题，要有实质性内容
2. **区分三类证据**：
   - A类（直接论文证据）：引用具体论文ID和结论
   - B类（跨论文综合归纳）：标明是从多篇论文中归纳的稳定模式
   - C类（迁移推断）：如果你是推断/外推，必须明确说"这是推断"
3. **引用要具体**：提到方法时给出方法名，提到结论时给出论文ID
4. **诚实说明局限**：如果知识库信息不足，直接说"证据不足"
5. **用中文回答**，专业术语可保留英文
6. **格式整洁**：用markdown组织，有层次结构
7. **不要编造**：不要虚构论文、数据、实验或观点"""

        user_prompt = f"""## 知识库参考内容
{wiki_context}

## 用户问题
{question}

请基于以上知识库内容，给出有深度、有实质内容的回答。不要只是复述知识库摘要——要进行分析、综合和解释。"""

        try:
            client = _make_client(api_key)
            stream = client.chat.completions.create(
                model=DEEPSEEK_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
                max_tokens=4000,
                stream=True,
            )

            for chunk in stream:
                delta = chunk.choices[0].delta
                if delta.content:
                    yield _sse("chunk", {"chunk": delta.content})

        except Exception as e:
            yield _sse("chunk", {"chunk": f"\n\n> ⚠ LLM 调用出错: {str(e)}\n\n"})
            yield _sse("chunk", {"chunk": "> 以下是基于知识库的结构化检索结果：\n\n"})
            # Fallback: use the deep synthesis answer
            from scholar_core.scholar_answer import ask_scholar
            answer = ask_scholar(question)
            for line in answer.to_markdown().split("\n"):
                yield _sse("chunk", {"chunk": line + "\n"})

        yield _sse("session_id", {"session_id": session_id})
        yield _sse("done", {})

    return StreamingResponse(generate(), media_type="text/event-stream")


def _sse(event: str, data: dict) -> str:
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"


async def _empty_stream(msg: str):
    yield _sse("chunk", {"chunk": msg})
    yield _sse("done", {})


# ── 上下文构建 ─────────────────────────────────────────────

def _load_briefing() -> str:
    """加载学者速览。"""
    path = _ROOT / "scholar_skill" / "scholar_briefing.md"
    if path.is_file():
        content = path.read_text(encoding="utf-8")
        # Skip frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            content = parts[2] if len(parts) >= 3 else content
        return content[:3000]
    return "学者速览暂不可用"


def _build_context(question: str) -> str:
    """构建给 LLM 的完整知识库上下文。"""
    parts: list[str] = []
    total = 0
    limit = 8000

    # 1. Wiki 综合页面（研究范式、问题体系、研究主线等）
    wiki_files = [
        ("wiki/research_paradigm.md", "研究范式"),
        ("wiki/research_questions.md", "研究问题体系"),
        ("wiki/synthesis/research_lines.md", "研究主线"),
        ("wiki/synthesis/method_evolution.md", "方法族演化"),
        ("wiki/synthesis/evidence_standards.md", "证据标准"),
        ("wiki/glossary.md", "术语表"),
        ("wiki/index.md", "Wiki总览"),
    ]
    for rel_path, label in wiki_files:
        fpath = _ROOT / rel_path
        if not fpath.is_file():
            continue
        content = _read_body(fpath)
        if not content:
            continue
        chunk = content[:1000]
        parts.append(f"### {label}\n{chunk}\n")
        total += len(chunk)
        if total > limit:
            break

    # 2. 相关概念页
    concepts_dir = _ROOT / "wiki" / "concepts"
    if concepts_dir.is_dir():
        for cf in sorted(concepts_dir.glob("*.md"))[:3]:
            content = _read_body(cf)
            if content and any(kw in content.lower() for kw in question.lower().split() if len(kw) >= 3):
                chunk = content[:600]
                parts.append(f"### 概念: {cf.stem}\n{chunk}\n")
                total += len(chunk)

    # 3. 方法卡片（全部）
    cards_dir = _ROOT / "method_cards" / "cards"
    if cards_dir.is_dir():
        for card_path in sorted(cards_dir.glob("*.md"))[:5]:
            content = _read_body(card_path)
            if not content:
                continue
            # 取最关键的几节
            sections = ["方法定义", "核心机制", "适用问题类型", "局限", "不适用场景"]
            extracted = []
            for sec in sections:
                text = _extract_section(content, sec)
                if text:
                    extracted.append(f"**{sec}**: {text[:300]}")
            if extracted:
                chunk = "\n".join(extracted)
                title = _extract_title(content) or card_path.stem
                parts.append(f"### 方法: {title}\n{chunk}\n")
                total += len(chunk)
                if total > limit:
                    break

    # 4. 思维模型
    models_dir = _ROOT / "thinking_models" / "models"
    if models_dir.is_dir():
        for model_path in sorted(models_dir.glob("*.md"))[:3]:
            content = _read_body(model_path)
            if not content:
                continue
            chunk = content[:600]
            parts.append(f"### 思维模型: {model_path.stem}\n{chunk}\n")
            total += len(chunk)
            if total > limit:
                break

    return "\n---\n".join(parts)


def _read_body(path: Path) -> str:
    """读取 Markdown 文件正文（去掉 frontmatter）。"""
    try:
        raw = path.read_text(encoding="utf-8")
        if raw.startswith("---"):
            parts = raw.split("---", 2)
            return parts[2].lstrip("\n") if len(parts) >= 3 else raw
        return raw
    except Exception:
        return ""


def _extract_title(content: str) -> str:
    import re
    m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return m.group(1).strip() if m else ""


def _extract_section(body: str, section_name: str) -> str:
    import re
    escaped = re.escape(section_name)
    pattern = re.compile(
        rf"^#{{2,3}}\s+(?:\d+\.\s*)?{escaped}\s*\n+(.*?)(?=\n+#{{2,3}}\s|\Z)",
        re.DOTALL | re.MULTILINE | re.IGNORECASE,
    )
    m = pattern.search(body)
    if not m:
        return ""
    return m.group(1).strip()
