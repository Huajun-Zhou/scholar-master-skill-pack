"""PDF 解析（PyMuPDF）。

输出：每页文本 + 整篇拼接文本，附极简结构信息。
不修改原始 PDF。
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import fitz  # PyMuPDF

from .utils import file_sha1, now_iso, stable_id


def parse_pdf(pdf_path: Path) -> dict[str, Any]:
    """解析单个 PDF。"""
    doc = fitz.open(pdf_path)
    pages: list[dict[str, Any]] = []
    try:
        for i, page in enumerate(doc):
            text = page.get_text("text") or ""
            pages.append({
                "page": i + 1,
                "text": text,
                "char_count": len(text),
            })
        raw_meta = dict(doc.metadata or {})
        n_pages = len(doc)
    finally:
        doc.close()

    sha1 = file_sha1(pdf_path)
    source_id = stable_id("SRC", sha1)

    nonempty = sum(1 for p in pages if p["char_count"] >= 50)
    text_pages_ratio = (nonempty / n_pages) if n_pages else 0.0

    return {
        "source_id": source_id,
        "source_file": pdf_path.name,
        "sha1": sha1,
        "size_bytes": pdf_path.stat().st_size,
        "n_pages": n_pages,
        "text_pages_ratio": round(text_pages_ratio, 3),
        "raw_metadata": raw_meta,
        "pages": pages,
        "parser": {"engine": "pymupdf", "version": fitz.__version__},
        "extracted_at": now_iso(),
    }


def write_pdf_text(parsed: dict[str, Any], out_dir: Path) -> Path:
    """写入 data/processed/pdf_text/{source_id}.json。"""
    import json
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{parsed['source_id']}.json"
    with path.open("w", encoding="utf-8") as f:
        json.dump(parsed, f, ensure_ascii=False, indent=2)
    return path


def parse_quality(parsed: dict[str, Any], min_ratio: float = 0.7) -> str:
    """根据 text_pages_ratio 判定 ok / partial / needs_ocr_or_manual_review。"""
    r = parsed["text_pages_ratio"]
    if r >= min_ratio:
        return "ok"
    if r >= 0.3:
        return "partial"
    return "needs_ocr_or_manual_review"


def write_paper_sections(parsed: dict[str, Any], meta: dict[str, Any],
                         sections: list[dict[str, Any]],
                         out_dir: Path) -> Path:
    """写入 data/processed/paper_sections/{source_id}.json。"""
    import json
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / f"{parsed['source_id']}.json"
    payload = {
        "source_id": parsed["source_id"],
        "source_file": parsed["source_file"],
        "n_pages": parsed["n_pages"],
        "metadata": meta,
        "sections": sections,
        "section_count": len(sections),
        "raw_metadata": parsed.get("raw_metadata") or {},
    }
    with path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    return path


def discover_pdfs(raw_dir: Path) -> list[Path]:
    """列出 data/raw/papers/*.pdf，按文件名稳定排序。"""
    return sorted(p for p in raw_dir.glob("*.pdf") if p.is_file())
