"""Context assembler v2 — 结构化知识检索，真正释放 Scholar Wiki 炼化价值。

v1 (旧): 关键词匹配 → 加载全部 wiki 页面 → 拼成 prompt → 丢给 LLM
v2 (新):
  1. 语义匹配 → 精准检索最相关的 Method Card / Thinking Model / Paper
  2. 结构化提取 → 不是 dump 整篇 markdown，而是提取最相关的章节
  3. 思维模型注入 → 匹配推理链，引导 LLM 的思考框架
  4. 证据验证 → 交叉检查 evidence_id 是否存在
  5. 上下文优化 → 按优先级排序，控制 token 总量
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "src"))
from scholar_skill_pack.wiki_ops import read_page

from services.content_loader import (
    load_all_methods,
    load_all_papers,
    load_all_thinking_models,
    load_method,
    load_thinking_model,
    load_wiki_page,
)

# ---------------------------------------------------------------------------
# Question-type classification (enhanced)
# ---------------------------------------------------------------------------

FACTUAL_KEYWORDS = [
    "是什么", "什么是", "有哪些", "介绍", "概述", "总结", "梳理",
    "what", "which", "list", "describe", "explain", "define",
    "论文", "paper", "发表", "contribution", "贡献",
]

METHOD_KEYWORDS = [
    "如何", "怎么", "怎样做", "设计", "实现", "构建",
    "how to", "how do", "approach", "framework", "architecture",
    "算法", "mechanism", "机制", "原理", "为什么", "为何",
    "loss", "objective", "optimization", "训练", "train",
    "核心思想", "思路", "洞察", "insight", "关键",
]

TRANSFER_KEYWORDS = [
    "迁移", "transfer", "apply", "应用", "扩展到", "extend", "adapt",
    "如果", "假设", "could", "可以用于", "能不能用",
    "搬到", "借鉴", "套用",
]

REVIEW_KEYWORDS = [
    "审稿", "review", "critique", "审查", "评价", "不足之处",
    "weakness", "limitation", "局限", "改进", "improve",
    "打分", "score", "rate", "评估", "evaluate",
]


def classify_question(question: str) -> str:
    q_lower = question.lower()
    scores = {"factual": 0, "method": 0, "transfer": 0, "review": 0}

    for kw in FACTUAL_KEYWORDS:
        if kw in q_lower:
            scores["factual"] += 1
    for kw in METHOD_KEYWORDS:
        if kw in q_lower:
            scores["method"] += 1
    for kw in TRANSFER_KEYWORDS:
        if kw in q_lower:
            scores["transfer"] += 1.5  # higher weight per keyword
    for kw in REVIEW_KEYWORDS:
        if kw in q_lower:
            scores["review"] += 1.5

    # Transfer wins ties (it's the most valuable type)
    if scores["transfer"] >= 2:
        return "transfer"
    if scores["review"] >= 2:
        return "review"
    if scores["method"] >= scores["factual"] and scores["method"] >= 1:
        return "method"

    return "factual"


# ---------------------------------------------------------------------------
# Smart keyword matching — find relevant content by topic
# ---------------------------------------------------------------------------

def _question_keywords(question: str) -> list[str]:
    """Extract meaningful keywords from a question."""
    # Remove common stop words
    stop = {"的", "了", "是", "在", "我", "有", "和", "就", "不", "人", "都", "一",
            "一个", "上", "也", "很", "到", "说", "要", "去", "你", "会", "着",
            "没有", "看", "好", "自己", "这", "他", "她", "它", "们", "那", "些",
            "the", "a", "an", "is", "in", "of", "to", "for", "with", "and", "or",
            "how", "what", "why", "when", "where", "can", "do", "does", "about",
            "陈志远教授", "学者", "该学者", "请问", "请", "可以", "能否"}
    words = re.findall(r"[一-鿿]+|[a-zA-Z]+", question)
    return [w for w in words if w.lower() not in stop and len(w) >= 2]


def _match_score(text: str, keywords: list[str]) -> int:
    """Count how many keywords appear in the text."""
    text_lower = text.lower()
    return sum(1 for kw in keywords if kw.lower() in text_lower)


# ---------------------------------------------------------------------------
# Main context assembly — the "deep refinement" engine
# ---------------------------------------------------------------------------

MAX_CONTEXT_CHARS = 8000  # Keep total context manageable for the LLM


def assemble_context(root: Path, question: str) -> dict[str, Any]:
    """Assemble RELEVANT (not all) context using structured knowledge.

    Strategy:
    1. Scholar Briefing (always) — the condensed scholar profile
    2. Best-matching Method Cards (top 2-3) — with most relevant sections only
    3. Best-matching Thinking Model (top 1) — reasoning chain + description
    4. Most relevant Paper Cards (top 3) — titles, contributions, methods only
    5. Relevant wiki synthesis pages (top 2) — evidence_standards, problem_framing, etc.
    """
    qtype = classify_question(question)
    keywords = _question_keywords(question)

    sections: list[dict[str, str]] = []
    total_chars = 0

    # --- 1. Scholar Briefing (always, truncated if needed) ---
    briefing = _load_scholar_briefing(root)
    briefing_trimmed = _trim(briefing, 1500)
    sections.append({"title": "Scholar Briefing", "content": briefing_trimmed})
    total_chars += len(briefing_trimmed)

    # --- 2. Best-matching Method Cards (top 2-3, key sections only) ---
    methods = load_all_methods(root)
    scored_methods = []
    for m in methods:
        full = load_method(root, m["method_id"])
        if full:
            score = _match_score(full["body"][:500] + m["title"], keywords)
            scored_methods.append((score, full))
    scored_methods.sort(key=lambda x: -x[0])

    method_count = 0
    for score, method in scored_methods:
        if score == 0 and method_count > 0:
            break  # Stop when we hit irrelevant methods
        if total_chars >= MAX_CONTEXT_CHARS:
            break

        # Extract only the MOST relevant sections:
        # - Section 1 (方法定义) always
        # - Section 4 (核心机制) always — this is the "why it works"
        # - Section 3 (适用问题类型) for transfer questions
        # - Section 10 (可迁移方案) for transfer questions
        # - Section 12 (不适用场景) for review questions
        body = method["body"]
        extracted = _extract_section(body, "方法定义", 400)
        extracted += "\n\n" + _extract_section(body, "核心机制", 600)

        if qtype in ("transfer", "method"):
            extracted += "\n\n" + _extract_section(body, "适用问题类型", 300)
        if qtype == "transfer":
            extracted += "\n\n" + _extract_section(body, "可迁移方案", 400)
        if qtype == "review":
            extracted += "\n\n" + _extract_section(body, "局限", 300)
            extracted += "\n\n" + _extract_section(body, "不适用场景", 200)

        extracted = _trim(extracted, 1500)
        sections.append({
            "title": f"Method: {method['title']} (relevance: {score})",
            "content": extracted,
        })
        total_chars += len(extracted)
        method_count += 1
        if method_count >= 3:
            break

    # --- 3. Best-matching Thinking Model (top 1) ---
    models = load_all_thinking_models(root)
    scored_models = []
    for m in models:
        full = load_thinking_model(root, m["model_id"])
        if full:
            score = _match_score(full["body"][:500] + m["title"], keywords)
            scored_models.append((score, full))
    scored_models.sort(key=lambda x: -x[0])

    if scored_models and scored_models[0][0] > 0 and total_chars < MAX_CONTEXT_CHARS:
        _, model = scored_models[0]
        body = model["body"]
        # Extract: name + description + reasoning chain + applicable scenarios
        extracted = _extract_section(body, "思维模型名称", 100)
        extracted += "\n\n" + _extract_section(body, "模型描述", 300)
        extracted += "\n\n" + _extract_section(body, "典型推理链", 500)
        extracted += "\n\n" + _extract_section(body, "适用场景", 200)
        extracted = _trim(extracted, 1000)
        sections.append({
            "title": f"Thinking Model: {model['title']} (matched)",
            "content": extracted,
        })
        total_chars += len(extracted)

    # --- 4. Most relevant Papers (top 3) ---
    papers = load_all_papers(root)
    scored_papers = []
    for p in papers:
        score = _match_score(p["title"] + " " + p.get("venue", ""), keywords)
        scored_papers.append((score, p))
    scored_papers.sort(key=lambda x: -x[0])

    paper_lines = []
    for score, p in scored_papers:
        if score == 0:
            break
        paper_lines.append(
            f"- **{p['title'][:80]}** ({p.get('year', '?')}) — `{p['paper_id']}`"
            f"  | {p.get('venue', '')[:40]}"
        )
        if len(paper_lines) >= 3:
            break

    if paper_lines:
        paper_text = "\n".join(paper_lines)
        sections.append({"title": "Relevant Papers", "content": paper_text})
        total_chars += len(paper_text)

    # --- 5. Relevant wiki synthesis pages (top 1-2) ---
    wiki_pages = {
        "research_paradigm": "研究范式",
        "glossary": "术语表",
        "open_questions": "开放问题",
        "limitations": "局限性",
        "synthesis/evidence_standards": "证据标准",
        "synthesis/problem_framing_patterns": "问题定义模式",
        "synthesis/method_evolution": "方法演化",
    }

    wiki_scores = []
    for rel_path, name in wiki_pages.items():
        wiki_path = root / "wiki" / f"{rel_path}.md"
        if wiki_path.is_file():
            try:
                wp = load_wiki_page(str(wiki_path))
                score = _match_score(wp["body"][:500] + name, keywords)
                wiki_scores.append((score, name, wp))
            except Exception:
                continue
    wiki_scores.sort(key=lambda x: -x[0])

    wiki_count = 0
    for score, name, wp in wiki_scores:
        if score == 0 and wiki_count > 0:
            break
        if total_chars >= MAX_CONTEXT_CHARS:
            break
        content = _trim(wp["body"], 800)
        sections.append({"title": f"Wiki: {name}", "content": content})
        total_chars += len(content)
        wiki_count += 1
        if wiki_count >= 2:
            break

    # --- 6. Research Paradigm (for transfer/review questions) ---
    if qtype in ("transfer", "review") and total_chars < MAX_CONTEXT_CHARS - 1000:
        paradigm_path = root / "wiki" / "research_paradigm.md"
        if paradigm_path.is_file():
            try:
                wp = load_wiki_page(str(paradigm_path))
                paradigm_text = wp["body"]
                # Extract key sections only
                extracted = _extract_section(paradigm_text, "范式总览", 300)
                extracted += "\n\n" + _extract_section(paradigm_text, "方法设计范式", 400)
                extracted += "\n\n" + _extract_section(paradigm_text, "可迁移研究框架", 400)
                extracted = _trim(extracted, 800)
                sections.append({"title": "Research Paradigm", "content": extracted})
                total_chars += len(extracted)
            except Exception:
                pass

    # --- 7. Numerical facts (precision injection) ---
    if total_chars < MAX_CONTEXT_CHARS - 400:
        nums_text = _extract_numerical_facts(root, keywords, max_facts=4)
        if nums_text:
            sections.append({"title": "Numerical Facts (cite these exact numbers)", "content": nums_text})
            total_chars += len(nums_text)

    # --- 8. Cross-method comparison (related methods in same family) ---
    if method_count > 0 and total_chars < MAX_CONTEXT_CHARS - 400:
        cross_text = _build_cross_method_context(scored_methods)
        if cross_text:
            sections.append({"title": "Method Comparison (how this relates to other methods)", "content": cross_text})
            total_chars += len(cross_text)

    # --- 9. Relevant Claims (direct quotes from papers) ---
    if total_chars < MAX_CONTEXT_CHARS - 500:
        claims_text = _load_relevant_claims(root, keywords, max_claims=5)
        if claims_text:
            sections.append({"title": "Verified Claims (direct paper quotes)", "content": claims_text})
            total_chars += len(claims_text)

    # --- Build assembled text ---
    assembled_lines = [
        f"# Context for: {question}",
        f"## Question Type: {qtype}",
        f"## Keywords: {', '.join(keywords[:10])}",
        "",
    ]
    for sec in sections:
        assembled_lines.append(f"## {sec['title']}")
        assembled_lines.append(sec["content"])
        assembled_lines.append("")

    # --- Verify evidence IDs ---
    all_eids = _extract_evidence_ids_from_text("\n".join(assembled_lines))
    valid_eids = _verify_evidence_ids(root, all_eids)

    return {
        "question": question,
        "question_type": qtype,
        "keywords": keywords[:10],
        "scholar_briefing": briefing_trimmed,
        "context_sections": sections,
        "assembled_text": "\n".join(assembled_lines),
        "evidence_sources": valid_eids,
        "total_chars": total_chars,
    }


# ===================================================================
# Helpers
# ===================================================================

def _load_scholar_briefing(root: Path) -> str:
    fp = root / "scholar_skill" / "scholar_briefing.md"
    if fp.is_file():
        try:
            return read_page(fp).get("body", "")
        except Exception:
            pass
    return "(Scholar briefing not found)"


def _extract_section(body: str, section_name: str, max_chars: int = 500) -> str:
    """Extract a named section from markdown body."""
    # Find "## N. section_name" or "### section_name"
    patterns = [
        rf"##\s+\d+\.\s*{re.escape(section_name)}\s*\n+(.*?)(?=\n+##\s+\d+\.|\n+##\s+[A-Z]|\Z)",
        rf"###\s+{re.escape(section_name)}\s*\n+(.*?)(?=\n+###\s+|\n+##\s|\Z)",
        rf"##\s+{re.escape(section_name)}\s*\n+(.*?)(?=\n+##\s|\Z)",
    ]
    for pattern in patterns:
        m = re.search(pattern, body, re.DOTALL | re.IGNORECASE)
        if m:
            text = m.group(1).strip()
            return text[:max_chars] + ("..." if len(text) > max_chars else "")
    return ""


def _trim(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "..."


def _extract_evidence_ids_from_text(text: str) -> list[str]:
    return re.findall(r"EVID-[\w]+-[\w]+-[\w]+", text)


def _load_relevant_claims(root: Path, keywords: list[str], max_claims: int = 5) -> str:
    """Load the most relevant claims from wiki/claims/ that match the question keywords.

    Each claim contains: claim_text, evidence_ids, page, section, confidence.
    We return them as structured text so the LLM can quote the actual paper claims.
    """
    claims_dir = root / "wiki" / "claims"
    if not claims_dir.is_dir():
        return ""

    all_claims: list[dict[str, Any]] = []
    for claims_file in claims_dir.glob("*.jsonl"):
        try:
            for line in claims_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                claim = json.loads(line)
                all_claims.append(claim)
        except Exception:
            continue

    if not all_claims:
        return ""

    # Score claims by keyword match
    import json as _json
    scored = []
    for c in all_claims:
        text = c.get("claim_text", "") + " " + c.get("section", "")
        score = _match_score(text, keywords)
        if score > 0:
            scored.append((score, c))
    scored.sort(key=lambda x: -x[0])

    if not scored:
        return ""

    lines = ["以下是从论文中提取的可验证 claims（引用时请使用原文表述和 evidence_id）：", ""]
    count = 0
    for score, c in scored:
        if count >= max_claims:
            break
        confidence_mark = {"high": "✓✓", "medium": "✓", "low": "?"}.get(
            c.get("confidence", ""), "?"
        )
        lines.append(
            f"- [{confidence_mark}] {c.get('claim_text', '')}\n"
            f"  — {c.get('paper_id', '')}, page {c.get('page', '?')}, "
            f"section: {c.get('section', '?')}"
            f"  evidence: {', '.join(c.get('evidence_ids', [])[:2])}"
        )
        count += 1

    return "\n".join(lines)


def _extract_numerical_facts(root: Path, keywords: list[str], max_facts: int = 4) -> str:
    """Extract numerical facts (PSNR values, parameter settings, dataset sizes)
    from Paper Cards that match the question keywords.

    These numbers let the LLM make precise citations instead of vague claims.
    """
    import json as _json

    papers_dir = root / "wiki" / "papers"
    if not papers_dir.is_dir():
        return ""

    # Numerical patterns to look for
    num_patterns = [
        (r"(\d+\.?\d*)\s*dB", "dB"),
        (r"PSNR[:\s]*(\d+\.?\d*)", "PSNR"),
        (r"SSIM[:\s]*(\d+\.?\d*)", "SSIM"),
        (r"(\d+\.?\d*)\s*dB.*PSNR", "PSNR+dB"),
        (r"×(\d+)", "scale"),
        (r"(\d+)\s*×\s*(\d+)", "kernel_size"),
        (r"c\s*=\s*(\d+\.?\d*)\s*σ", "threshold"),
        (r"ρ\s*=\s*(\d+\.?\d*)", "ADMM_rho"),
        (r"(\d+)\s*次迭代", "iterations"),
        (r"(\d+)\s*iterations", "iterations"),
    ]

    facts: list[tuple[int, str]] = []
    for card_path in sorted(papers_dir.glob("*.md")):
        try:
            page = read_page(card_path)
        except Exception:
            continue
        body = page.get("body", "")
        title = page.get("frontmatter", {}).get("title", card_path.stem)

        # Only include if keywords match
        if not any(kw.lower() in body.lower() for kw in keywords):
            continue

        # Extract the "实验设计" and "关键结论" sections
        exp_section = _extract_section(body, "实验设计", 1500)
        result_section = _extract_section(body, "关键结论", 1000)
        combined = exp_section + "\n" + result_section

        for pattern, fact_type in num_patterns:
            for match in re.finditer(pattern, combined, re.IGNORECASE):
                num_text = match.group(0).strip()
                if len(num_text) >= 3:
                    score = _match_score(body[:500], keywords)
                    # Prefer matches from the "实验设计" or "关键结论" sections
                    context_start = max(0, match.start() - 60)
                    context_end = min(len(combined), match.end() + 60)
                    ctx = combined[context_start:context_end].replace("\n", " ").strip()
                    facts.append((score, f"- [{fact_type}] {ctx} — from *{title[:50]}*"))

    # Deduplicate and sort by relevance
    seen: set[str] = set()
    unique_facts = []
    for score, fact in sorted(facts, key=lambda x: -x[0]):
        # Use first 30 chars as dedup key
        key = fact[:40]
        if key not in seen:
            seen.add(key)
            unique_facts.append(fact)
        if len(unique_facts) >= max_facts:
            break

    if not unique_facts:
        return ""

    return (
        "以下是论文中可引用的精确数值（引用时请直接使用这些数字，不要自己编造）：\n\n"
        + "\n".join(unique_facts)
    )


def _build_cross_method_context(
    scored_methods: list[tuple[int, dict[str, Any]]],
) -> str:
    """Build a brief comparison context showing how the top-matched method
    relates to other methods in the scholar's toolkit.

    This allows the LLM to naturally make statements like:
    "While Method A does X well, Method B takes a different approach..."
    """
    if len(scored_methods) < 2:
        return ""

    # Take top 1-2 methods and compare with the rest
    top_methods = scored_methods[:2]
    other_methods = scored_methods[2:5]

    if not other_methods:
        return ""

    lines = ["以下是该学者工具包中与当前讨论相关的其他方法，供你进行对比分析：", ""]

    for score, method in top_methods:
        title = method.get("title", "")
        source_papers = method.get("frontmatter", {}).get("source_papers", [])
        lines.append(f"**主方法：{title}** (papers: {', '.join(source_papers[:3])})")
        # Extract just the 1-sentence definition
        def_section = _extract_section(method.get("body", ""), "方法定义", 200)
        if def_section:
            lines.append(f"  定义：{def_section[:150]}...")
        lines.append("")

    lines.append("**可对比的其他方法**（该方法论体系中的相关模块）：")
    lines.append("")

    for score, method in other_methods[:3]:
        title = method.get("title", "")
        source_papers = method.get("frontmatter", {}).get("source_papers", [])
        def_section = _extract_section(method.get("body", ""), "方法定义", 120)
        core = _extract_section(method.get("body", ""), "核心机制", 120)

        lines.append(f"- **{title}** (papers: {len(source_papers)})")
        if def_section:
            lines.append(f"  {def_section[:100]}...")
        if core:
            # Extract the first "why it works" sentence
            why_match = re.search(r"为什么有效[：:](.+?)(?=\n|$)", core)
            if why_match:
                lines.append(f"  为什么有效：{why_match.group(1).strip()[:100]}...")
        lines.append("")

    lines.append(
        "**对比指导**：请在你的回答中自然地比较这些方法——"
        "指出它们在什么情况下各自适用，什么情况下一个优于另一个。"
        "这种跨方法对比能展现该学者方法论体系的完整性和互补性。"
    )

    return "\n".join(lines)


def _verify_evidence_ids(root: Path, eids: list[str]) -> list[str]:
    """Cross-check evidence IDs against the evidence registry."""
    valid = []
    claims_dir = root / "wiki" / "claims"
    if not claims_dir.is_dir():
        return list(set(eids))  # Can't verify, return all

    # Build a quick index of known evidence IDs from claims files
    known_eids: set[str] = set()
    for claims_file in claims_dir.glob("*.jsonl"):
        try:
            for line in claims_file.read_text(encoding="utf-8").splitlines():
                if '"evidence_id"' in line or '"evidence_ids"' in line:
                    found = re.findall(r"EVID-[\w]+-[\w]+-[\w]+", line)
                    known_eids.update(found)
        except Exception:
            continue

    for eid in set(eids):
        if eid in known_eids:
            valid.append(eid)
        else:
            # Mark as unverified but still include — the LLM should note uncertainty
            valid.append(f"{eid} [unverified]")

    return valid
