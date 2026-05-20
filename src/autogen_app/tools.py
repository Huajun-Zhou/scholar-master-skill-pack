"""AutoGen Tools — 将 Scholar Core API 包装为 AutoGen 可调用的 async tool 函数。

每个 tool 返回字符串 (Markdown)，供 AutoGen agent 消费。
"""

from __future__ import annotations

from pathlib import Path

from scholar_core.artifact_writer import write_artifact as _core_write_artifact
from scholar_core.evidence_audit import audit_evidence as _core_audit
from scholar_core.paper_review import critique_paper as _core_critique
from scholar_core.research_design import design_research as _core_design
from scholar_core.retrieval import (
    list_all_papers,
    retrieve_evidence,
    retrieve_method_cards,
    retrieve_thinking_models,
    search_scholar_wiki,
)
from scholar_core.scholar_answer import ask_scholar as _core_ask


# ---- Wiki / 检索类 ----

async def search_wiki_tool(query: str, top_k: int = 8) -> str:
    """检索 Scholar Wiki。

    参数:
        query: 搜索关键词或问题
        top_k: 返回结果数 (默认 8)

    返回:
        Markdown 格式的检索结果
    """
    results = search_scholar_wiki(query, top_k=top_k)
    if not results:
        return f"未找到与「{query}」相关的 Wiki 页面。"

    lines = [f"## Scholar Wiki 检索: {query}", "", f"共 {len(results)} 个相关页面:", ""]
    for i, chunk in enumerate(results, 1):
        lines.append(f"### {i}. {chunk.title}")
        lines.append(f"- 路径: `{chunk.path}`")
        lines.append(f"- 证据等级: {chunk.evidence_level}")
        if chunk.source_papers:
            lines.append(f"- 来源论文: {', '.join(chunk.source_papers[:5])}")
        lines.append(f"- 摘要: {chunk.content[:300]}...")
        lines.append("")
    return "\n".join(lines)


async def get_method_cards_tool(query: str, top_k: int = 5) -> str:
    """检索方法卡片。

    参数:
        query: 搜索关键词
        top_k: 返回结果数 (默认 5)

    返回:
        Markdown 格式的方法卡片列表
    """
    cards = retrieve_method_cards(query, top_k=top_k)
    if not cards:
        return f"未找到与「{query}」相关的方法卡片。"

    lines = [f"## 方法卡片检索: {query}", "", f"共 {len(cards)} 个方法:", ""]
    for card in cards:
        lines.append(card.to_markdown())
        lines.append("\n---\n")
    return "\n".join(lines)


async def get_thinking_models_tool(query: str, top_k: int = 5) -> str:
    """检索思维模型。

    参数:
        query: 搜索关键词
        top_k: 返回结果数 (默认 5)

    返回:
        Markdown 格式的思维模型列表
    """
    models = retrieve_thinking_models(query, top_k=top_k)
    if not models:
        return f"未找到与「{query}」相关的思维模型。"

    lines = [f"## 思维模型检索: {query}", "", f"共 {len(models)} 个模型:", ""]
    for model in models:
        lines.append(model.to_markdown())
        lines.append("\n---\n")
    return "\n".join(lines)


async def get_evidence_tool(paper_ids: str = "") -> str:
    """查询证据注册表。

    参数:
        paper_ids: 逗号分隔的 paper_id 列表（留空=全部）

    返回:
        Markdown 格式的证据列表
    """
    ids = [p.strip() for p in paper_ids.split(",") if p.strip()] if paper_ids else None
    evidence = retrieve_evidence(paper_ids=ids)

    if not evidence:
        return "未找到相关证据。"

    lines = [f"## Evidence Registry", "", f"共 {len(evidence)} 条证据:", ""]
    lines.append("| Claim | Level | Source | Confidence |")
    lines.append("|---|---:|---:|")
    for ev in evidence[:30]:
        lines.append(
            f"| {ev.claim[:60]} | {ev.evidence_level} | "
            f"{ev.source_id} | {ev.confidence:.2f} |"
        )
    if len(evidence) > 30:
        lines.append(f"| ... | | | |")
        lines.append(f"| *(共 {len(evidence)} 条，仅显示前 30)* | | | |")
    return "\n".join(lines)


async def list_papers_tool() -> str:
    """列出所有已注册论文。

    返回:
        Markdown 格式的论文清单
    """
    papers = list_all_papers()
    if not papers:
        return "论文注册表为空。"

    lines = [f"## 论文清单", "", f"共 {len(papers)} 篇:", ""]
    lines.append("| # | paper_id | title | year |")
    lines.append("|---:|---|---:|")
    for i, p in enumerate(papers, 1):
        title = (p.get("title", "") or "")[:80].replace("|", "\\|")
        year = p.get("year", "?")
        lines.append(f"| {i} | {p.get('paper_id', '')} | {title} | {year} |")
    return "\n".join(lines)


# ---- 组合类 ----

async def ask_scholar_tool(question: str) -> str:
    """向 Scholar Skill 提问。

    返回区分 A/B/C 三类证据的结构化回答。

    参数:
        question: 科研问题

    返回:
        Markdown 格式的 A/B/C 证据回答
    """
    answer = _core_ask(question)
    return answer.to_markdown()


async def design_research_tool(topic: str, target_journal: str = "") -> str:
    """基于目标学者方法论生成研究设计方案。

    参数:
        topic: 研究主题
        target_journal: 目标投稿期刊（可选）

    返回:
        Markdown 格式的完整研究方案
    """
    design = _core_design(topic, target_journal=target_journal)
    return design.to_markdown()


async def critique_paper_tool(paper_path: str, target_journal: str = "") -> str:
    """按目标学者研究范式审查论文草稿。

    审查维度: 问题定义、方法设计、证据链、贡献清晰度、投稿风险

    参数:
        paper_path: 论文草稿文件路径
        target_journal: 目标投稿期刊（可选）

    返回:
        Markdown 格式的审查报告
    """
    review = _core_critique(paper_path, target_journal=target_journal)
    return review.to_markdown()


async def audit_evidence_tool(text: str) -> str:
    """对文本执行 A/B/C/Insufficient 证据审计。

    参数:
        text: 待审计的文本

    返回:
        Markdown 格式的证据审计报告，含 gate 结果
    """
    audit = _core_audit(text, strict=True)
    return audit.to_markdown()


async def write_report_tool(path: str, content: str) -> str:
    """将报告写入文件系统。

    参数:
        path: 输出文件路径（相对于项目根或绝对路径）
        content: 报告内容 (Markdown)

    返回:
        确认消息
    """
    p = _core_write_artifact(path, content)
    return f"报告已写入: {p}"
