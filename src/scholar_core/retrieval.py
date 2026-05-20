"""知识检索层 — 纯数据操作，不依赖 LLM。

从 wiki/、method_cards/、thinking_models/、data/registry/ 中检索相关内容。
使用关键词匹配 + frontmatter 加权排序。
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from .config import get_retrieval_config, project_root
from .types import EvidenceItem, MethodCard, ThinkingModel, WikiChunk


# ---- Wiki 检索 ----

def search_scholar_wiki(query: str, top_k: int | None = None) -> list[WikiChunk]:
    """全文检索 wiki/ 下所有 .md 文件。"""
    cfg = get_retrieval_config()
    if top_k is None:
        top_k = cfg.get("wiki_top_k", 8)

    root = project_root()
    wiki_dir = root / "wiki"
    if not wiki_dir.is_dir():
        return []

    all_pages: list[WikiChunk] = []

    for md_path in sorted(wiki_dir.rglob("*.md")):
        try:
            page = _read_md_page(md_path)
        except Exception:
            continue
        fm = page.get("frontmatter", {}) or {}
        body = page.get("body", "")

        chunk = WikiChunk(
            page_id=fm.get("page_id", md_path.stem),
            title=fm.get("title", md_path.stem),
            content=body,
            evidence_level=fm.get("evidence_level", "B"),
            source_papers=fm.get("source_papers", []) or [],
            path=str(md_path.relative_to(root)),
        )
        all_pages.append(chunk)

    ranked = _rank_by_query(all_pages, query, cfg)
    return ranked[:top_k]


# ---- Method Card 检索 ----

def retrieve_method_cards(query: str, top_k: int | None = None) -> list[MethodCard]:
    """从 method_cards/cards/*.md 检索方法卡片。"""
    cfg = get_retrieval_config()
    if top_k is None:
        top_k = cfg.get("method_card_top_k", 5)

    root = project_root()
    cards_dir = root / "method_cards" / "cards"
    if not cards_dir.is_dir():
        return []

    cards: list[MethodCard] = []
    for md_path in sorted(cards_dir.glob("*.md")):
        try:
            page = _read_md_page(md_path)
        except Exception:
            continue
        fm = page.get("frontmatter", {}) or {}
        body = page.get("body", "")

        card = MethodCard(
            name=fm.get("title", md_path.stem),
            definition=_extract_section(body, "方法定义") or _extract_section(body, "1. 方法定义"),
            source_papers=fm.get("source_papers", []) or [],
            applicable_problems=_extract_list_section(body, "适用问题类型"),
            core_mechanism=_extract_section(body, "核心机制") or _extract_section(body, "4. 核心机制"),
            typical_flow=_extract_list_section(body, "典型流程"),
            input_conditions=_extract_list_section(body, "输入条件"),
            output_results=_extract_list_section(body, "输出结果"),
            advantages=_extract_list_section(body, "优势"),
            limitations=_extract_list_section(body, "局限"),
            transfer_conditions=_extract_section(body, "可迁移方案") or _extract_section(body, "10. 可迁移方案"),
            unsuitable_scenarios=_extract_list_section(body, "不适用场景"),
            path=str(md_path.relative_to(root)),
        )
        cards.append(card)

    # 用 title + definition 文本做检索
    scored: list[tuple[float, MethodCard]] = []
    query_lower = query.lower()
    for card in cards:
        search_text = f"{card.name}\n{card.definition}\n{' '.join(card.applicable_problems)}".lower()
        score = _text_match_score(query_lower, search_text)
        if score > 0:
            scored.append((score, card))
    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored[:top_k]]


# ---- Thinking Model 检索 ----

def retrieve_thinking_models(query: str, top_k: int | None = None) -> list[ThinkingModel]:
    """从 thinking_models/models/*.md 检索思维模型。"""
    cfg = get_retrieval_config()
    if top_k is None:
        top_k = cfg.get("thinking_model_top_k", 5)

    root = project_root()
    models_dir = root / "thinking_models" / "models"
    if not models_dir.is_dir():
        return []

    models: list[ThinkingModel] = []
    for md_path in sorted(models_dir.glob("*.md")):
        try:
            page = _read_md_page(md_path)
        except Exception:
            continue
        fm = page.get("frontmatter", {}) or {}
        body = page.get("body", "")

        model = ThinkingModel(
            name=fm.get("title", md_path.stem),
            description=_extract_section(body, "模型描述") or _extract_section(body, "2. 模型描述"),
            reasoning_chain=_extract_section(body, "典型推理链") or _extract_section(body, "4. 典型推理链"),
            applicable_scenarios=_extract_list_section(body, "适用场景"),
            unsuitable_scenarios=_extract_list_section(body, "不适用场景"),
            source_papers=fm.get("source_papers", []) or [],
            path=str(md_path.relative_to(root)),
        )
        models.append(model)

    scored: list[tuple[float, ThinkingModel]] = []
    query_lower = query.lower()
    for model in models:
        search_text = f"{model.name}\n{model.description}".lower()
        score = _text_match_score(query_lower, search_text)
        if score > 0:
            scored.append((score, model))
    scored.sort(key=lambda x: -x[0])
    return [m for _, m in scored[:top_k]]


# ---- Evidence 查询 ----

def retrieve_evidence(paper_ids: list[str] | None = None,
                      evidence_level: str | None = None) -> list[EvidenceItem]:
    """从 data/registry/ 和 wiki/claims/ 查询 evidence。

    如果 paper_ids 为 None，返回全部 evidence。
    """
    root = project_root()
    items: list[EvidenceItem] = []

    # 1. 从 paper_registry.jsonl 加载论文证据
    registry_path = root / "data" / "registry" / "paper_registry.jsonl"
    if registry_path.is_file():
        papers = _read_jsonl(registry_path)
        for p in papers:
            pid = p.get("paper_id", "")
            if paper_ids and pid not in paper_ids:
                continue
            title = p.get("title", "")[:100]
            items.append(EvidenceItem(
                claim=f"[Paper] {title}",
                evidence_level="A",
                source_id=pid,
                confidence=1.0,
                limitation="",
            ))

    # 2. 从 claims JSONL 加载（如果存在）
    claims_dir = root / "wiki" / "claims"
    if claims_dir.is_dir():
        for claim_file in sorted(claims_dir.glob("*.jsonl")):
            try:
                claims = _read_jsonl(claim_file)
            except Exception:
                continue
            for c in claims:
                cid = c.get("paper_id", claim_file.stem)
                if paper_ids and cid not in paper_ids:
                    continue
                level = c.get("evidence_level", "B")
                if evidence_level and level != evidence_level:
                    continue
                items.append(EvidenceItem(
                    claim=c.get("claim", "")[:200],
                    evidence_level=level,
                    source_id=c.get("claim_id", cid),
                    confidence=float(c.get("certainty", "0.5")),
                    limitation=c.get("limitation", ""),
                ))

    # 3. 优先级排序：A > B > C > Insufficient
    level_order = {"A": 0, "B": 1, "C": 2, "Insufficient": 3}
    items.sort(key=lambda e: level_order.get(e.evidence_level, 4))
    return items


def list_all_papers() -> list[dict[str, Any]]:
    """列出所有已注册论文。"""
    root = project_root()
    registry_path = root / "data" / "registry" / "paper_registry.jsonl"
    if not registry_path.is_file():
        return []
    return _read_jsonl(registry_path)


def list_all_method_card_names() -> list[str]:
    """列出所有方法卡片名称。"""
    root = project_root()
    cards_dir = root / "method_cards" / "cards"
    if not cards_dir.is_dir():
        return []
    names = []
    for md_path in sorted(cards_dir.glob("*.md")):
        try:
            page = _read_md_page(md_path)
            fm = page.get("frontmatter", {}) or {}
            names.append(fm.get("title", md_path.stem))
        except Exception:
            pass
    return names


def list_all_thinking_model_names() -> list[str]:
    """列出所有思维模型名称。"""
    root = project_root()
    models_dir = root / "thinking_models" / "models"
    if not models_dir.is_dir():
        return []
    names = []
    for md_path in sorted(models_dir.glob("*.md")):
        try:
            page = _read_md_page(md_path)
            fm = page.get("frontmatter", {}) or {}
            names.append(fm.get("title", md_path.stem))
        except Exception:
            pass
    return names


# ---- 内部辅助 ----

def _read_md_page(path: Path) -> dict[str, Any]:
    """读取 Markdown 文件，返回 {frontmatter, body}。"""
    import yaml
    raw = path.read_text(encoding="utf-8")
    frontmatter: dict[str, Any] = {}
    body = raw

    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
            except Exception:
                pass
            body = parts[2].lstrip("\n")

    return {"frontmatter": frontmatter, "body": body, "path": str(path)}


def _extract_section(body: str, section_name: str) -> str:
    """从 Markdown body 中提取指定章节的内容。"""
    # 匹配 "## N. Section Name" 或 "## Section Name" 或 "### Section Name"
    escaped = re.escape(section_name)
    pattern = re.compile(
        rf"^#{{2,3}}\s+(?:\d+\.\s*)?{escaped}\s*\n+(.*?)(?=\n+#{{2,3}}\s|\Z)",
        re.DOTALL | re.MULTILINE | re.IGNORECASE,
    )
    m = pattern.search(body)
    if not m:
        return ""
    return m.group(1).strip()


def _extract_list_section(body: str, section_name: str) -> list[str]:
    """从 Markdown body 中提取指定章节的列表项。"""
    text = _extract_section(body, section_name)
    if not text:
        return []
    items: list[str] = []
    for line in text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("- "):
            item = stripped[2:].strip()
            # 去掉粗体标记
            item = re.sub(r"\*\*(.+?)\*\*", r"\1", item)
            if len(item) >= 3:
                items.append(item)
    return items[:20]


def _rank_by_query(chunks: list[WikiChunk], query: str, cfg: dict[str, Any]) -> list[WikiChunk]:
    """按查询相关度排序。"""
    ranking_cfg = cfg.get("ranking", {})
    title_weight = float(ranking_cfg.get("title_match_weight", 3.0))
    fk_weight = float(ranking_cfg.get("frontmatter_keyword_weight", 2.0))
    body_weight = float(ranking_cfg.get("body_match_weight", 1.0))
    prefer_abc = ranking_cfg.get("prefer_A_over_B_over_C", True)

    query_lower = query.lower()
    query_terms = _tokenize(query_lower)

    scored: list[tuple[float, WikiChunk]] = []
    for chunk in chunks:
        score = 0.0

        # 标题匹配
        title_lower = chunk.title.lower()
        if query_lower in title_lower:
            score += title_weight * 5.0
        else:
            score += title_weight * sum(1.0 for t in query_terms if t in title_lower)

        # 正文匹配
        body_lower = chunk.content.lower()
        if query_lower in body_lower:
            score += body_weight * 2.0
        score += body_weight * sum(0.2 for t in query_terms if t in body_lower) / max(len(query_terms), 1)

        # 证据等级加权
        if prefer_abc:
            level_boost = {"A": 2.0, "B": 1.0, "C": 0.0}.get(chunk.evidence_level, 0.0)
            score += level_boost

        if score > 0:
            scored.append((score, chunk))

    scored.sort(key=lambda x: -x[0])
    return [c for _, c in scored]


def _text_match_score(query_lower: str, text_lower: str) -> float:
    """简单文本匹配评分。"""
    if query_lower in text_lower:
        return 5.0
    terms = _tokenize(query_lower)
    if not terms:
        return 0.0
    hits = sum(1.0 for t in terms if t in text_lower)
    return hits / len(terms)


def _tokenize(text: str) -> list[str]:
    """简易分词（中英文混用）。

    中文使用 bigram + 完整短语两级分词，英文按字母数字分词。
    """
    tokens: list[str] = []
    # 提取英文单词
    eng_tokens = re.findall(r"[a-zA-Z0-9]+", text)
    tokens.extend(eng_tokens)
    # 提取中文字符序列并生成 bigram
    cn_sequences = re.findall(r"[一-鿿]+", text)
    for seq in cn_sequences:
        if len(seq) <= 2:
            tokens.append(seq)
        else:
            # bigram 切分（如 "自适应阈值" → "自适", "适应", "应阈", "阈值"）
            for i in range(len(seq) - 1):
                tokens.append(seq[i:i + 2])
            # 保留完整序列用于精确匹配
            tokens.append(seq)
    # 去重但保留顺序信息
    seen: set[str] = set()
    out: list[str] = []
    for t in tokens:
        if t and t not in seen:
            out.append(t)
            seen.add(t)
    return out


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    """读取 JSONL 文件。"""
    records: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records
