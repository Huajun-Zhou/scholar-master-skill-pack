"""学者问答 — 基于 Scholar Wiki 的深度知识合成引擎。

从 Wiki 中提取结构化内容，组合为有实质性分析的回答。
支持可选的 LLM 集成——当有 LLM client 时使用 LLM 合成，
否则使用基于知识库提取的深度模板合成。
"""

from __future__ import annotations

import re
from typing import Any

from .retrieval import (
    retrieve_evidence,
    retrieve_method_cards,
    retrieve_thinking_models,
    search_scholar_wiki,
)
from .types import EvidenceItem, MethodCard, ScholarAnswer, ThinkingModel, WikiChunk


def ask_scholar(question: str, *, model_client: Any = None) -> ScholarAnswer:
    """基于 Scholar Wiki 回答问题，区分 A/B/C 证据。

    当 model_client 可用时使用 LLM 合成回答；
    否则使用基于知识库的结构化深度提取。
    """
    wiki_pages = search_scholar_wiki(question, top_k=8)
    method_cards = retrieve_method_cards(question, top_k=5)
    thinking_models = retrieve_thinking_models(question, top_k=3)
    evidence_items = retrieve_evidence(evidence_level="A")[:5]

    if model_client is not None:
        return _llm_answer(question, wiki_pages, method_cards, thinking_models,
                           evidence_items, model_client)
    return _deep_synthesis_answer(question, wiki_pages, method_cards,
                                  thinking_models, evidence_items)


# ── 深度合成模式（无 LLM 时使用）───────────────────────────────────

def _deep_synthesis_answer(
    question: str,
    wiki_pages: list[WikiChunk],
    method_cards: list[MethodCard],
    thinking_models: list[ThinkingModel],
    evidence_items: list[EvidenceItem],
) -> ScholarAnswer:
    """从知识库中深度提取并结构化合成回答。"""

    direct_answer = _compose_synthesis(question, wiki_pages, method_cards, thinking_models)
    insights = _compose_insights_deep(wiki_pages, method_cards, thinking_models)
    suggestions = _compose_transfer_deep(method_cards, thinking_models, question)
    limitations = _identify_limitations(question, method_cards)

    sources = [p.path for p in wiki_pages[:5]]
    sources.extend(c.path for c in method_cards[:3])
    sources.extend(m.path for m in thinking_models[:2])

    return ScholarAnswer(
        question=question,
        direct_answer=direct_answer,
        evidence_items=evidence_items,
        methodological_insight=insights,
        transferable_suggestions=suggestions,
        limitations=limitations,
        sources_used=sources,
    )


def _compose_synthesis(
    question: str,
    wiki_pages: list[WikiChunk],
    method_cards: list[MethodCard],
    thinking_models: list[ThinkingModel],
) -> str:
    """从知识库中提取关键信息合成有深度的回答。"""
    question_lower = question.lower()
    parts: list[str] = []

    # ── 1. 研究范式层面 ──
    paradigm_pages = [p for p in wiki_pages
                      if 'paradigm' in p.path or 'research_questions' in p.path]
    if paradigm_pages:
        parts.append("## 研究框架定位\n")
        for pp in paradigm_pages[:2]:
            extracted = _extract_relevant_section(pp.content, question_lower)
            if extracted:
                parts.append(extracted)

    # ── 2. 论文证据 ──
    paper_pages = [p for p in wiki_pages if 'papers/' in p.path]
    if paper_pages:
        parts.append("## 直接论文证据\n")
        parts.append("| 论文 | 核心贡献 |")
        parts.append("|------|---------|")
        for pp in paper_pages[:5]:
            title = _extract_title(pp.content)
            one_liner = _extract_section_field(pp.content, "一句话贡献")
            parts.append(f"| {title[:60]} | {one_liner[:100]} |")
        parts.append("")

    # ── 3. 综合知识（非论文页面） ──
    synthesis_pages = [p for p in wiki_pages
                       if 'papers/' not in p.path
                       and 'paradigm' not in p.path
                       and 'source_registry' not in p.path]
    if synthesis_pages:
        parts.append("## 知识库综合分析\n")
        for sp in synthesis_pages[:3]:
            content_summary = _summarize_page(sp)
            if content_summary:
                parts.append(content_summary)

    # ── 4. 方法卡片 ──
    if method_cards:
        parts.append("## 相关方法\n")
        for card in method_cards[:3]:
            parts.append(f"### {card.name}")
            if card.definition:
                parts.append(f"**定义**: {card.definition[:200]}")
            if card.core_mechanism:
                parts.append(f"**核心机制**: {card.core_mechanism[:300]}")
            if card.applicable_problems:
                parts.append(f"**适用场景**: {', '.join(card.applicable_problems[:3])}")
            parts.append("")

    # ── 5. 思维模型 ──
    if thinking_models:
        parts.append("## 思维模型指引\n")
        for model in thinking_models[:2]:
            parts.append(f"**{model.name}**: {model.description[:200]}")
            if model.reasoning_chain:
                parts.append(f"  推理链: {model.reasoning_chain[:250]}")

    if not parts:
        return (f"关于「{question}」，当前知识库中暂无足够匹配的内容。"
                f"已检索 {len(wiki_pages)} 个 Wiki 页面、{len(method_cards)} 个方法卡片。"
                f"建议尝试更具体的问题表述或补充相关论文。")

    return "\n".join(parts)


def _compose_insights_deep(
    wiki_pages: list[WikiChunk],
    method_cards: list[MethodCard],
    thinking_models: list[ThinkingModel],
) -> str:
    """深度方法论洞察。"""
    lines: list[str] = []

    # 识别跨方法的共同模式
    if len(method_cards) >= 2:
        lines.append("### 跨方法模式识别\n")
        all_mechanisms = [c.core_mechanism[:100] for c in method_cards[:3] if c.core_mechanism]
        if all_mechanisms:
            lines.append("从多个方法中可观察到以下共同模式：")
            for i, mech in enumerate(all_mechanisms, 1):
                lines.append(f"{i}. {mech}")
            lines.append("")

    if thinking_models:
        lines.append("### 思维模型应用分析\n")
        for model in thinking_models[:2]:
            lines.append(f"**{model.name}**")
            if model.reasoning_chain:
                lines.append(f"- 推理链: {model.reasoning_chain[:200]}")
            if model.applicable_scenarios:
                lines.append(f"- 适用: {', '.join(model.applicable_scenarios[:2])}")
            if model.unsuitable_scenarios:
                lines.append(f"- 不适用: {', '.join(model.unsuitable_scenarios[:2])}")
            lines.append("")

    if method_cards:
        lines.append("### 方法机制概要\n")
        for card in method_cards[:2]:
            lines.append(f"- **{card.name}**: {card.core_mechanism[:200]}")

    return "\n".join(lines) if lines else "（请提出更具体的问题以获取方法论洞察）"


def _compose_transfer_deep(
    method_cards: list[MethodCard],
    thinking_models: list[ThinkingModel],
    question: str,
) -> str:
    """生成有实质内容的 C 类迁移建议。"""
    lines = [
        "**以下为 C 类迁移推断**——基于陈志远教授公开成果的方法论迁移，并非其原文结论。\n"
    ]

    for card in method_cards[:3]:
        lines.append(f"### {card.name} 的迁移可能性\n")
        if card.transfer_conditions:
            lines.append(f"**迁移条件**: {card.transfer_conditions[:250]}")
        if card.unsuitable_scenarios:
            lines.append(f"**⚠ 不适用场景**: {', '.join(card.unsuitable_scenarios[:3])}")
        if card.limitations:
            lines.append(f"**已知局限**: {', '.join(card.limitations[:3])}")
        lines.append("")

    for model in thinking_models[:2]:
        if model.applicable_scenarios:
            lines.append(f"**{model.name}** 可指导「{question[:50]}」的研究设计")
            lines.append(f"  适用场景: {', '.join(model.applicable_scenarios[:2])}")
            lines.append("")

    return "\n".join(lines)


def _identify_limitations(question: str, method_cards: list[MethodCard]) -> list[str]:
    """识别回答局限性。"""
    limitations = [
        "以上回答基于 Scholar Wiki 中已有的知识资产，并非陈志远教授本人观点",
        "知识库覆盖 2025-2026 年发表的 15 篇论文，可能存在未覆盖的研究方向",
    ]
    for card in method_cards[:2]:
        if card.limitations:
            limitations.append(f"「{card.name}」已知局限: {card.limitations[0][:150]}")
    limitations.append("如需更精确的回答，建议提供具体的研究领域和问题背景")
    return limitations


# ── LLM 模式 ─────────────────────────────────────────────────

def _llm_answer(
    question: str,
    wiki_pages: list[WikiChunk],
    method_cards: list[MethodCard],
    thinking_models: list[ThinkingModel],
    evidence_items: list[EvidenceItem],
    model_client: Any,
) -> ScholarAnswer:
    """使用 LLM 生成回答。"""
    context = _build_llm_context(question, wiki_pages, method_cards, thinking_models)
    prompt = f"""你是一个基于学者论文知识库的科研助手。请基于以下知识库内容回答用户问题。

## 知识库内容
{context}

## 用户问题
{question}

## 回答要求
1. 先给出直接回答（基于知识库中的证据）
2. 区分 A 类（直接论文证据）、B 类（跨论文综合归纳）、C 类（迁移推断）
3. 引用具体的论文 ID 和方法名
4. 诚实说明局限性
5. 使用中文回答，专业术语保留英文

## 回答格式
### 直接回答
[基于知识库的综合回答]

### 证据支撑
| 证据 | 等级 | 来源 |

### 方法论洞察
[跨论文的方法论分析]

### 可迁移建议（C类推断）
[方法的可迁移性分析]

### 局限说明
[知识库覆盖范围的局限]"""

    try:
        response = model_client.complete(prompt)
        direct_answer = response if isinstance(response, str) else str(response)
    except Exception:
        direct_answer = _compose_synthesis(question, wiki_pages, method_cards, thinking_models)

    return _deep_synthesis_answer(question, wiki_pages, method_cards,
                                  thinking_models, evidence_items)


def _build_llm_context(
    question: str,
    wiki_pages: list[WikiChunk],
    method_cards: list[MethodCard],
    thinking_models: list[ThinkingModel],
) -> str:
    """构建给 LLM 的上下文。"""
    parts: list[str] = []
    total_chars = 0
    max_chars = 6000

    for page in wiki_pages[:5]:
        snippet = page.content[:800]
        parts.append(f"### [{page.title}]\n{snippet}\n")
        total_chars += len(snippet)
        if total_chars > max_chars:
            break

    for card in method_cards[:3]:
        card_text = card.to_markdown()[:600]
        parts.append(card_text)
        total_chars += len(card_text)
        if total_chars > max_chars:
            break

    for model in thinking_models[:2]:
        model_text = model.to_markdown()[:400]
        parts.append(model_text)

    return "\n---\n".join(parts)


# ── 内容提取辅助函数 ──────────────────────────────────────────

def _extract_title(content: str) -> str:
    m = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    return m.group(1).strip() if m else ""


def _extract_section_field(content: str, field_name: str) -> str:
    """从 Markdown 中提取指定小节的内容。"""
    pattern = rf"##\s+\d+\.\s+{re.escape(field_name)}\s*\n(.*?)(?=\n##\s+\d+\.|\n##\s+[A-Z]|\Z)"
    m = re.search(pattern, content, re.DOTALL)
    if not m:
        # Try without numbering
        pattern2 = rf"##\s+{re.escape(field_name)}\s*\n(.*?)(?=\n##\s|\Z)"
        m = re.search(pattern2, content, re.DOTALL)
    return m.group(1).strip()[:300] if m else ""


def _extract_relevant_section(content: str, query: str) -> str:
    """从页面内容中提取与查询最相关的小节。"""
    sections = re.split(r"\n##\s+", content)
    best_section = ""
    best_score = 0
    query_terms = set(query.split())

    for sec in sections:
        score = sum(1 for t in query_terms if t in sec)
        if score > best_score:
            best_score = score
            best_section = sec

    if best_section and best_score > 0:
        lines = best_section.strip().split("\n")
        return "\n".join(lines[:15])
    return ""


def _summarize_page(page: WikiChunk) -> str:
    """生成页面的结构化摘要。"""
    content = page.content
    lines: list[str] = []
    lines.append(f"### {page.title}\n")

    # 提取表格
    tables = re.findall(r"\|.*\|.*\n\|[-| ]+\n(?:\|.*\|.*\n)+", content)
    if tables:
        for t in tables[:1]:
            lines.append(t)

    # 提取第一段有意义的段落
    paragraphs = [p.strip() for p in content.split("\n\n") if len(p.strip()) > 80]
    if paragraphs:
        cleaned = paragraphs[0].replace("#", "").strip()
        lines.append(cleaned[:400])

    return "\n".join(lines)
