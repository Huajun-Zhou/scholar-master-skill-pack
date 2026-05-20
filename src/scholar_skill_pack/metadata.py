"""论文元信息识别（标题 / 作者 / 年份 / 摘要 / 关键词 / 章节）。

策略：
1. 优先用 PDF 元数据（doc.metadata.title / author / subject）；
2. 元数据缺失或可疑时用首页文本启发式补全；
3. 章节检测用模式匹配（编号 / 已知节名 / 大写）。

仅针对学术论文常见结构；目标 80%+ 召回，不追求 100%。
"""
from __future__ import annotations

import re
from typing import Any

# ---- 已知节名（英文，含 IEEE 罗马数字） ----
KNOWN_SECTIONS = [
    "abstract", "introduction", "related work", "background",
    "preliminaries", "method", "methods", "methodology",
    "approach", "proposed method", "model", "framework",
    "experiment", "experiments", "experimental results", "evaluation",
    "results", "discussion", "ablation", "ablation study",
    "limitation", "limitations", "conclusion", "conclusions",
    "acknowledgment", "acknowledgments", "acknowledgement", "acknowledgements",
    "references", "supplementary material", "appendix",
]
# 把 "1." / "1" / "I." / "II." 等编号前缀匹配出来
_NUM_PATTERN = re.compile(
    r"^\s*(?:(\d+(?:\.\d+){0,2})|([IVXLCM]{1,5}))[\.\)\s]+(.{1,80})$"
)
_YEAR_RE = re.compile(r"\b(19[7-9]\d|20[0-4]\d)\b")
_DOI_RE = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.IGNORECASE)


def extract_metadata(parsed: dict[str, Any]) -> dict[str, Any]:
    """从已解析页面中识别论文级元信息。"""
    raw = parsed.get("raw_metadata") or {}
    pages = parsed.get("pages") or []
    first_page_text = pages[0]["text"] if pages else ""
    full_text = "\n".join(p["text"] for p in pages)

    title = (raw.get("title") or "").strip()
    if not title or len(title) < 6:
        title = _heuristic_title(first_page_text) or ""

    authors_raw = (raw.get("author") or "").strip()
    authors = _split_authors(authors_raw) if authors_raw else _heuristic_authors(first_page_text)

    year = _heuristic_year(raw.get("creationDate"), raw.get("subject"), first_page_text)
    doi = _heuristic_doi(raw.get("subject"), full_text[:6000])
    venue = _heuristic_venue(raw.get("subject"), first_page_text)
    abstract = _heuristic_abstract(first_page_text)
    keywords = _heuristic_keywords(first_page_text + "\n" + (pages[1]["text"] if len(pages) > 1 else ""))

    return {
        "title": title or "Untitled",
        "authors": authors,
        "year": year,
        "venue": venue,
        "doi": doi,
        "abstract": abstract,
        "keywords": keywords,
        "title_source": "pdf_meta" if (raw.get("title") or "").strip() else "heuristic",
        "needs_review": (not title) or (year is None) or (len(authors) == 0),
    }


def detect_sections(pages: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """检测章节切分，返回 [{name, level, start_page, start_offset, ...}]。"""
    items: list[tuple[int, int, str, int]] = []  # (page, line_idx, name, level)
    for p in pages:
        text = p["text"] or ""
        for li, raw_line in enumerate(text.split("\n")):
            line = raw_line.strip()
            if not line or len(line) > 90:
                continue
            hit = _match_heading(line)
            if hit:
                name, level = hit
                items.append((p["page"], li, name, level))

    # 去除噪声：节名出现 ≥ 3 次的疑似页眉/页脚，丢弃
    from collections import Counter
    counter = Counter(item[2].lower() for item in items)
    items = [it for it in items if counter[it[2].lower()] <= 2 or it[2].lower() in {"references"}]

    sections: list[dict[str, Any]] = []
    for i, (page, li, name, level) in enumerate(items):
        sections.append({
            "name": name,
            "level": level,
            "start_page": page,
            "start_line": li,
            "end_page": items[i + 1][0] if i + 1 < len(items) else None,
            "end_line": items[i + 1][1] if i + 1 < len(items) else None,
        })
    return sections


def _match_heading(line: str) -> tuple[str, int] | None:
    """返回 (heading_name, level) 或 None。"""
    low = line.lower()
    # 已知节名独占一行
    if low in KNOWN_SECTIONS:
        return line, 1
    # 编号 + 标题: "1. Introduction" / "II. Related Work"
    m = _NUM_PATTERN.match(line)
    if m:
        num_arabic, num_roman, rest = m.group(1), m.group(2), m.group(3).strip()
        if not rest or len(rest) < 3:
            return None
        # 仅当 rest 像标题时（首字母大写 / 全大写 / 在已知节名内）
        if rest.lower() in KNOWN_SECTIONS or rest.isupper() or _is_titlecase(rest):
            level = 1
            if num_arabic and "." in num_arabic:
                level = num_arabic.count(".") + 1
            return rest, level
    # 全大写短行（IEEE 风格）
    if line.isupper() and 4 <= len(line) <= 60:
        return line.title(), 1
    return None


def _is_titlecase(s: str) -> bool:
    words = s.split()
    if not words:
        return False
    capped = sum(1 for w in words if w[:1].isupper())
    return capped / len(words) >= 0.5


# ---- 启发式 ----

def _heuristic_title(page1: str) -> str | None:
    """首页前若干非空行中找最像标题的一行（长度合适、非全大写署名）。"""
    lines = [l.strip() for l in page1.split("\n") if l.strip()]
    candidates: list[tuple[int, str]] = []
    for i, line in enumerate(lines[:40]):
        if 15 <= len(line) <= 200 and not _looks_like_doi_line(line):
            # 排除明显的页眉
            if re.search(r"\b(vol|no|pp|doi|http|www|page)\b", line, re.IGNORECASE):
                continue
            candidates.append((i, line))
        if len(candidates) >= 5:
            break
    if not candidates:
        return None
    # 选最长的前 3 行中合并
    top = sorted(candidates, key=lambda x: -len(x[1]))[:3]
    top_sorted = sorted(top, key=lambda x: x[0])
    return " ".join(l for _, l in top_sorted)[:300]


def _looks_like_doi_line(line: str) -> bool:
    return bool(_DOI_RE.search(line)) or "doi" in line.lower()


def _split_authors(s: str) -> list[str]:
    parts = re.split(r"\s*(?:,|;|\band\b|&)\s*", s, flags=re.IGNORECASE)
    return [p.strip() for p in parts if p.strip()]


def _heuristic_authors(page1: str) -> list[str]:
    """首页前 30 行中找疑似作者行（含逗号且无 'Abstract' 等关键词）。"""
    lines = [l.strip() for l in page1.split("\n") if l.strip()]
    for line in lines[:30]:
        low = line.lower()
        if "abstract" in low or "doi" in low or "@" in line and "abstract" not in low:
            continue
        # 启发式：包含逗号 + 大写名字风格
        if "," in line and re.search(r"\b[A-Z][a-z]+\b.*\b[A-Z][a-z]+\b", line):
            return _split_authors(line)
    return []


def _heuristic_year(creation_date: str | None, subject: str | None,
                    first_page: str) -> int | None:
    if creation_date:
        m = re.search(r"D:(\d{4})", creation_date)
        if m:
            y = int(m.group(1))
            if 1970 <= y <= 2100:
                return y
    for src in (subject or "", first_page[:1500]):
        m = _YEAR_RE.search(src)
        if m:
            return int(m.group(1))
    return None


def _heuristic_doi(subject: str | None, head: str) -> str:
    for src in (subject or "", head):
        m = _DOI_RE.search(src)
        if m:
            return m.group(0)
    return ""


def _heuristic_venue(subject: str | None, page1: str) -> str:
    if subject:
        # 形如 "Light: Science & Applications, doi:..."
        v = subject.split(",")[0].strip()
        if 3 <= len(v) <= 80 and "doi" not in v.lower():
            return v
    # 首页第一行常含 venue
    first_line = next((l for l in page1.split("\n") if l.strip()), "")
    if re.search(r"\b(IEEE|ACM|Light|Optica|Nature|Science|ICCV|CVPR|NeurIPS|ICML|ICLR|AAAI|ECCV|BMVC|TPAMI|TIP|TGRS)\b",
                 first_line):
        return first_line.strip()[:120]
    return ""


def _heuristic_abstract(page1: str) -> str:
    """从 'Abstract' 起到下一节标题之间的段落。"""
    m = re.search(r"\babstract\b\s*[:\-]?\s*", page1, re.IGNORECASE)
    if not m:
        return ""
    tail = page1[m.end():]
    # 截到 "Introduction" / "1." / "Keywords" 等
    end_m = re.search(
        r"\n\s*(?:1[\.\s]+introduction|introduction\b|keywords?\b|index\s+terms\b|i\.\s+introduction)",
        tail, re.IGNORECASE,
    )
    snippet = tail[: end_m.start()] if end_m else tail[:1500]
    return re.sub(r"\s+", " ", snippet).strip()[:1500]


def _heuristic_keywords(text: str) -> list[str]:
    m = re.search(r"\b(keywords?|index\s+terms)\b\s*[:\-—]\s*(.+?)(?:\n\n|\n[A-Z][a-z]+ ?\n|$)",
                  text, re.IGNORECASE | re.DOTALL)
    if not m:
        return []
    raw = m.group(2)
    parts = re.split(r"[,;，；·•]", raw)
    return [re.sub(r"\s+", " ", p).strip() for p in parts if p.strip()][:20]
