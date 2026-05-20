"""Phase 3: Wiki 综合构建。

从所有 Paper Cards 中归纳研究主线、概念体系、方法族、数据集、实验范式，
生成 Scholar Wiki 的核心页面。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .registry import list_papers
from .utils import ensure_dir, now_iso, project_paths
from .wiki_ops import read_page, write_page


def load_all_paper_cards(root: Path) -> list[dict[str, Any]]:
    """加载 wiki/papers/ 下所有 Paper Card 的 frontmatter 和内容摘要。"""
    paths = project_paths(root)
    papers_dir = paths["wiki"] / "papers"
    cards: list[dict[str, Any]] = []
    for card_path in sorted(papers_dir.glob("*.md")):
        try:
            page = read_page(card_path)
        except Exception:
            continue
        fm = page.get("frontmatter", {})
        body = page.get("body", "")
        # 提取关键段落
        title = fm.get("title", card_path.stem)
        year = fm.get("paper_year") or _extract_year(body, title)
        pid = (fm.get("source_papers") or [""])[0]

        cards.append({
            "file": card_path.name,
            "path": str(card_path),
            "paper_id": pid,
            "title": title,
            "year": year,
            "authors": fm.get("authors", []),
            "venue": fm.get("venue", ""),
            "frontmatter": fm,
            "body": body,
            "char_count": len(body),
        })
    # 按年份排序
    cards.sort(key=lambda c: (c["year"] or 9999, c["title"]))
    return cards


def _extract_year(body: str, title: str) -> int | None:
    import re
    for line in body.split("\n")[:20]:
        m = re.search(r"\byear:\s*(\d{4})", line, re.IGNORECASE)
        if m:
            return int(m.group(1))
    return None


def collect_all_methods(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """从所有 Paper Card 中收集方法名称和关联信息。"""
    import re
    methods: dict[str, dict[str, Any]] = {}
    for c in cards:
        body = c["body"]
        # 提取方法框架中的方法名
        method_section = _extract_section(body, "方法框架")
        for line in method_section.split("\n"):
            m = re.match(r"-\s*(?:模型|算法|方法)[：:]\s*(.+)", line.strip())
            if m:
                name = m.group(1).strip()[:80]
                if name and len(name) >= 3:
                    if name not in methods:
                        methods[name] = {"name": name, "papers": [], "paper_ids": []}
                    methods[name]["papers"].append(c["title"])
                    methods[name]["paper_ids"].append(c["paper_id"])
    return sorted(methods.values(), key=lambda x: -len(x["papers"]))


def collect_all_datasets(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """从所有 Paper Card 中收集数据集名称。"""
    import re
    datasets: dict[str, dict[str, Any]] = {}
    for c in cards:
        body = c["body"]
        ds_section = _extract_section(body, "方法框架") + "\n" + _extract_section(body, "实验设计")
        for match in re.finditer(r"(?:数据集|dataset)[：:]\s*(.+)", ds_section, re.IGNORECASE):
            for ds in re.split(r"[,;，；、]", match.group(1)):
                ds = ds.strip()[:60]
                if ds and len(ds) >= 2:
                    if ds not in datasets:
                        datasets[ds] = {"name": ds, "papers": [], "paper_ids": []}
                    datasets[ds]["papers"].append(c["title"])
                    datasets[ds]["paper_ids"].append(c["paper_id"])
    return sorted(datasets.values(), key=lambda x: -len(x["papers"]))


def collect_all_concepts(cards: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """从 Paper Cards 的 frontmatter keywords/abstract 和核心思想节提取关键概念。"""
    import re
    concepts: dict[str, dict[str, Any]] = {}
    for c in cards:
        body = c["body"]
        core = _extract_section(body, "核心思想")
        abstract = _extract_section(body, "一句话贡献")
        text = core + "\n" + abstract
        # 提取技术术语（中英文，2-6 词）
        for match in re.finditer(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,5})", text):
            term = match.group(1).strip()
            if len(term) >= 8 and len(term) <= 60:
                if term not in concepts:
                    concepts[term] = {"name": term, "papers": [], "paper_ids": []}
                concepts[term]["papers"].append(c["title"])
                concepts[term]["paper_ids"].append(c["paper_id"])
    return sorted(concepts.values(), key=lambda x: -len(x["papers"]))


def _extract_section(body: str, section_name: str) -> str:
    """从 Markdown body 中提取指定章节的文本。"""
    import re
    pattern = re.compile(
        r"##\s+\d+\.\s*" + re.escape(section_name) + r"\s*\n(.*?)(?=\n##\s+\d+\.)",
        re.DOTALL,
    )
    m = pattern.search(body)
    return m.group(1) if m else ""


def assemble_wiki_context(root: Path) -> dict[str, Any]:
    """装配 Wiki 构建所需的完整上下文摘要。

    返回一个适合传递给 LLM 的综合摘要，包含：
    - 论文总览表
    - 研究时间线
    - 方法清单
    - 数据集清单
    - 概念清单
    """
    cards = load_all_paper_cards(root)
    methods = collect_all_methods(cards)
    datasets = collect_all_datasets(cards)
    concepts = collect_all_concepts(cards)

    # 生成论文摘要表
    paper_table: list[str] = []
    for i, c in enumerate(cards, 1):
        year_str = str(c["year"]) if c["year"] else "?"
        title = c["title"][:80]
        paper_table.append(f"| {i} | {year_str} | {title} | {c['paper_id']} | {c.get('venue', '?')[:30]} |")

    summary = {
        "n_papers": len(cards),
        "year_range": f"{cards[0]['year']}–{cards[-1]['year']}" if cards else "N/A",
        "paper_table": "\n".join(paper_table),
        "cards": cards,
        "top_methods": methods[:30],
        "top_datasets": datasets[:30],
        "top_concepts": concepts[:30],
        "all_methods": methods,
        "all_datasets": datasets,
        "all_concepts": concepts,
    }
    return summary


def write_source_registry_page(root: Path) -> Path:
    """生成 wiki/source_registry.md — 纯机械操作。"""
    paths = project_paths(root)
    cards = load_all_paper_cards(root)
    papers = list_papers(paths["registry"] / "paper_registry.jsonl")

    lines = [
        "# Source Registry",
        "",
        f"更新: {now_iso()}",
        "",
        f"## 总览",
        f"- 论文总数: {len(cards)}",
        "",
        "## 论文清单",
        "",
        "| # | paper_id | title | year | authors | venue | pages |",
        "|---:|---|---|---:|---|---|---:|",
    ]
    for i, p in enumerate(papers, 1):
        title = (p.get("title", "") or "")[:60].replace("|", "\\|")
        authors = ", ".join((p.get("authors") or [])[:3])
        lines.append(
            f"| {i} | {p.get('paper_id', '')} | {title} | "
            f"{p.get('year', '') or '?'} | {authors} | "
            f"{p.get('venue', '')[:30]} | {p.get('n_pages', '?')} |"
        )
    lines.append("")

    path = paths["wiki"] / "source_registry.md"
    write_page(path, {
        "page_id": "source-registry",
        "page_type": "meta",
        "title": "Source Registry",
        "status": "reviewed",
        "evidence_level": "A",
        "updated_at": now_iso(),
    }, "\n".join(lines))
    return path


def write_wiki_hub_page(root: Path, page_name: str,
                        frontmatter: dict[str, Any],
                        content: str) -> Path:
    """通用 Wiki 页面写入。"""
    paths = project_paths(root)
    path = paths["wiki"] / f"{page_name}.md"
    fm = {
        "page_id": f"wiki-{page_name}",
        "page_type": "synthesis",
        "updated_at": now_iso(),
        "status": "draft",
        "evidence_level": "B",
        **frontmatter,
    }
    write_page(path, fm, content)
    return path


def generate_research_timeline_content(cards: list[dict[str, Any]]) -> str:
    """生成 research_timeline.md 的内容。"""
    by_year: dict[int, list[dict[str, Any]]] = {}
    for c in cards:
        y = c["year"] or 0
        by_year.setdefault(y, []).append(c)

    lines = [
        "# Research Timeline",
        "",
        f"基于 {len(cards)} 篇公开论文的时间线分析。",
        "",
    ]
    for year in sorted(by_year.keys()):
        lines.append(f"## {year}")
        lines.append("")
        for c in by_year[year]:
            authors_short = ", ".join((c.get("authors") or [])[:3])
            venue_short = (c.get("venue") or "")[:50]
            lines.append(f"- **{c['title'][:100]}**")
            lines.append(f"  - paper_id: `{c['paper_id']}`")
            lines.append(f"  - 作者: {authors_short}")
            if venue_short:
                lines.append(f"  - 出处: {venue_short}")
        lines.append("")
    return "\n".join(lines)
