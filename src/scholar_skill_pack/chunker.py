"""Chunking：把论文文本切成可索引片段。

策略：
1. 优先按检测到的 section 切分；
2. 单个 section 超过 chunk_size 字符的，按段落继续切分；
3. 检测不到 section 的回退到按页切分；
4. 相邻 chunks 之间保留 overlap 字符。

每个 chunk 含：chunk_id / source_id / paper_id / page_start / page_end /
section / text / char_count。
"""
from __future__ import annotations

from typing import Any

from .utils import stable_id


def chunk_paper(parsed: dict[str, Any], paper_id: str,
                sections: list[dict[str, Any]],
                chunk_size: int = 2000, overlap: int = 200) -> list[dict[str, Any]]:
    """切分单篇论文。"""
    pages = parsed["pages"]
    source_id = parsed["source_id"]

    if sections and len(sections) >= 2:
        section_texts = _slice_by_sections(pages, sections)
    else:
        section_texts = [
            {"name": f"page-{p['page']}", "level": 0,
             "page_start": p["page"], "page_end": p["page"], "text": p["text"]}
            for p in pages if p["text"].strip()
        ]

    chunks: list[dict[str, Any]] = []
    counter = 0
    for sec in section_texts:
        for piece in _split_long(sec["text"], chunk_size, overlap):
            text = piece.strip()
            if not text:
                continue
            chunk_id = f"{paper_id}-C{counter:03d}"
            chunks.append({
                "chunk_id": chunk_id,
                "source_id": source_id,
                "paper_id": paper_id,
                "section": sec["name"],
                "page_start": sec["page_start"],
                "page_end": sec["page_end"],
                "text": text,
                "char_count": len(text),
            })
            counter += 1
    return chunks


def _slice_by_sections(pages: list[dict[str, Any]],
                       sections: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """根据 section 锚点把页面文本切成段落块。"""
    # 用 (page, line_idx) 二元组定位
    page_idx = {p["page"]: i for i, p in enumerate(pages)}
    out: list[dict[str, Any]] = []
    for s in sections:
        sp, sl = s["start_page"], s["start_line"]
        ep, el = s["end_page"], s["end_line"]
        if ep is None:
            ep, el = pages[-1]["page"], None
        text = _extract_range(pages, page_idx, sp, sl, ep, el)
        out.append({
            "name": s["name"],
            "level": s["level"],
            "page_start": sp,
            "page_end": ep,
            "text": text,
        })
    return out


def _extract_range(pages, page_idx, sp, sl, ep, el) -> str:
    parts: list[str] = []
    for i in range(page_idx[sp], page_idx[ep] + 1):
        page = pages[i]
        lines = page["text"].split("\n")
        if i == page_idx[sp] and i == page_idx[ep]:
            sub = lines[sl + 1: (el if el is not None else len(lines))]
        elif i == page_idx[sp]:
            sub = lines[sl + 1:]
        elif i == page_idx[ep]:
            sub = lines[: (el if el is not None else len(lines))]
        else:
            sub = lines
        parts.append("\n".join(sub))
    return "\n".join(parts).strip()


def _split_long(text: str, chunk_size: int, overlap: int) -> list[str]:
    if len(text) <= chunk_size:
        return [text]
    # 优先按双换行切，保留段落边界
    paragraphs = [p for p in text.split("\n\n") if p.strip()]
    if not paragraphs:
        return _hard_split(text, chunk_size, overlap)

    out: list[str] = []
    cur = ""
    for p in paragraphs:
        if len(cur) + len(p) + 2 <= chunk_size:
            cur = (cur + "\n\n" + p) if cur else p
        else:
            if cur:
                out.append(cur)
            if len(p) > chunk_size:
                out.extend(_hard_split(p, chunk_size, overlap))
                cur = ""
            else:
                # 用上一段尾部做 overlap
                tail = out[-1][-overlap:] if out else ""
                cur = (tail + "\n\n" + p) if tail else p
    if cur:
        out.append(cur)
    return out


def _hard_split(text: str, chunk_size: int, overlap: int) -> list[str]:
    out: list[str] = []
    i = 0
    while i < len(text):
        out.append(text[i: i + chunk_size])
        i += max(chunk_size - overlap, 1)
    return out


def write_chunks(chunks: list[dict[str, Any]], out_dir, source_id: str):
    """写入 jsonl。"""
    import json
    from pathlib import Path
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{source_id}.jsonl"
    with path.open("w", encoding="utf-8") as f:
        for c in chunks:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    return path
