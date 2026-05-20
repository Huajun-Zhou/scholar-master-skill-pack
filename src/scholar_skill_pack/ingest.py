"""Phase 1 ingest 编排：PDF → pdf_text → sections → chunks → registries → 报告。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .chunker import chunk_paper, write_chunks
from .config import load_config
from .metadata import detect_sections, extract_metadata
from .pdf_parser import (
    discover_pdfs,
    parse_pdf,
    parse_quality,
    write_paper_sections,
    write_pdf_text,
)
from .registry import append_extraction_run, upsert_paper, upsert_source
from .utils import ensure_dir, now_iso, project_paths, slugify, stable_id


def _make_paper_id(meta: dict[str, Any], source_id: str) -> str:
    """paper_id 基于 (title, first_author, year)；缺失时回退到 source_id。"""
    title = (meta.get("title") or "").strip().lower()
    first = (meta.get("authors") or [""])[0].strip().lower()
    year = meta.get("year")
    if title and (first or year):
        return stable_id("PAPER", f"{title}|{first}|{year}")
    return source_id.replace("SRC_", "PAPER_")


def ingest_all(root: Path, force: bool = False) -> dict[str, Any]:
    """执行整套 Phase 1 ingest，返回汇总结果。"""
    paths = project_paths(root)
    pipeline = load_config(root, "pipeline.yaml").get("pipeline", {})
    quality = load_config(root, "quality_gates.yaml").get("quality_gates", {}).get("QG1", {})
    chunker_cfg = pipeline.get("chunker", {})
    parser_cfg = pipeline.get("pdf_parser", {})

    chunk_size = int(chunker_cfg.get("chunk_size", 2000))
    overlap = int(chunker_cfg.get("chunk_overlap", 200))
    min_ratio = float(parser_cfg.get("min_text_ratio", 0.7))

    pdfs = discover_pdfs(paths["raw_papers"])
    if not pdfs:
        return {"papers": [], "n_total": 0, "warnings": ["no pdfs in data/raw/papers/"]}

    ensure_dir(paths["pdf_text"])
    ensure_dir(paths["paper_sections"])
    ensure_dir(paths["chunks"])
    ensure_dir(paths["registry"])
    ensure_dir(paths["reports"] / "ingestion_reports")

    source_registry = paths["registry"] / "source_registry.jsonl"
    paper_registry = paths["registry"] / "paper_registry.jsonl"
    extraction_runs = paths["registry"] / "extraction_runs.jsonl"

    # 已处理 source_id 索引
    seen_sha1: dict[str, str] = {}  # sha1 → source_id（用于查重）
    if source_registry.is_file():
        with source_registry.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    if rec.get("sha1"):
                        seen_sha1[rec["sha1"]] = rec["source_id"]
                except Exception:
                    pass

    results: list[dict[str, Any]] = []
    warnings: list[str] = []
    duplicates: list[tuple[str, str]] = []  # (file, dup_of_file)

    for i, pdf in enumerate(pdfs, 1):
        rec: dict[str, Any] = {"file": pdf.name}
        try:
            parsed = parse_pdf(pdf)
        except Exception as e:
            rec["status"] = "parse_failed"
            rec["error"] = repr(e)
            results.append(rec)
            warnings.append(f"{pdf.name}: parse failed — {e!r}")
            continue

        sha1 = parsed["sha1"]
        source_id = parsed["source_id"]
        if sha1 in seen_sha1 and seen_sha1[sha1] != source_id:
            # 不可能（source_id 由 sha1 派生），但保留防御。
            duplicates.append((pdf.name, seen_sha1[sha1]))
        elif _is_duplicate_content(seen_sha1, sha1, source_id, pdf.name, paths):
            # 同 sha1 已被另一个文件占用 → 重复
            pass
        seen_sha1[sha1] = source_id

        # 写 pdf_text（除非已存在且非 force）
        pdf_text_path = paths["pdf_text"] / f"{source_id}.json"
        if force or not pdf_text_path.is_file():
            write_pdf_text(parsed, paths["pdf_text"])

        meta = extract_metadata(parsed)
        sections = detect_sections(parsed["pages"])
        write_paper_sections(parsed, meta, sections, paths["paper_sections"])

        paper_id = _make_paper_id(meta, source_id)

        chunks = chunk_paper(parsed, paper_id, sections,
                             chunk_size=chunk_size, overlap=overlap)
        write_chunks(chunks, paths["chunks"], source_id)

        quality_label = parse_quality(parsed, min_ratio=min_ratio)

        upsert_source(source_registry, {
            "source_id": source_id,
            "source_file": pdf.name,
            "sha1": sha1,
            "size_bytes": parsed["size_bytes"],
            "n_pages": parsed["n_pages"],
            "text_pages_ratio": parsed["text_pages_ratio"],
            "parse_quality": quality_label,
            "section_count": len(sections),
            "n_chunks": len(chunks),
            "ingested_at": now_iso(),
            "parser": parsed["parser"],
        })

        upsert_paper(paper_registry, {
            "paper_id": paper_id,
            "source_id": source_id,
            "source_file": pdf.name,
            "title": meta.get("title", ""),
            "title_source": meta.get("title_source"),
            "authors": meta.get("authors", []),
            "year": meta.get("year"),
            "venue": meta.get("venue", ""),
            "doi": meta.get("doi", ""),
            "abstract": meta.get("abstract", "")[:1500],
            "keywords": meta.get("keywords", []),
            "n_pages": parsed["n_pages"],
            "needs_review": meta.get("needs_review", False) or quality_label != "ok",
            "registered_at": now_iso(),
        })

        rec.update({
            "status": "ok",
            "source_id": source_id,
            "paper_id": paper_id,
            "title": meta.get("title", ""),
            "year": meta.get("year"),
            "n_pages": parsed["n_pages"],
            "n_sections": len(sections),
            "n_chunks": len(chunks),
            "text_pages_ratio": parsed["text_pages_ratio"],
            "parse_quality": quality_label,
            "needs_review": meta.get("needs_review", False) or quality_label != "ok",
        })
        results.append(rec)

    # 重复内容检测：以 paper_id 聚合同一篇内容
    pid_to_files: dict[str, list[str]] = {}
    for r in results:
        if r.get("status") == "ok" and r.get("paper_id"):
            pid_to_files.setdefault(r["paper_id"], []).append(r["file"])
    duplicate_papers = {pid: files for pid, files in pid_to_files.items() if len(files) > 1}

    run_id = f"ingest-{now_iso().replace(':', '').replace('-', '')[:15]}"
    append_extraction_run(extraction_runs, {
        "run_id": run_id,
        "phase": 1,
        "started_at": now_iso(),
        "n_pdfs": len(pdfs),
        "n_ok": sum(1 for r in results if r.get("status") == "ok"),
        "duplicate_papers": duplicate_papers,
    })

    return {
        "run_id": run_id,
        "n_total": len(pdfs),
        "results": results,
        "warnings": warnings,
        "duplicate_papers": duplicate_papers,
        "qg1": _qg1_summary(results, quality, min_ratio),
    }


def _is_duplicate_content(seen_sha1, sha1, source_id, fname, paths) -> bool:
    return False  # 占位：当前 sha1 → source_id 一一映射，无需额外判断


def _qg1_summary(results: list[dict[str, Any]], qg1: dict[str, Any],
                 min_ratio: float) -> dict[str, Any]:
    """QG1 质量门禁汇总。"""
    ok_results = [r for r in results if r.get("status") == "ok"]
    n = len(ok_results)
    has_title = sum(1 for r in ok_results if r.get("title"))
    has_source_id = sum(1 for r in ok_results if r.get("source_id"))
    above_ratio = sum(1 for r in ok_results if r.get("text_pages_ratio", 0) >= min_ratio)
    needs_review = sum(1 for r in ok_results if r.get("needs_review"))

    passed = (
        has_title == n
        and has_source_id == n
        and above_ratio == n
    )
    return {
        "n_papers": n,
        "has_title_candidate": f"{has_title}/{n}",
        "has_source_id": f"{has_source_id}/{n}",
        "text_ratio_above_min": f"{above_ratio}/{n}",
        "min_text_ratio": min_ratio,
        "needs_review": needs_review,
        "passed": passed,
    }


def write_parse_report(root: Path, summary: dict[str, Any]) -> Path:
    """生成 reports/ingestion_reports/parse_report.md。"""
    report_dir = ensure_dir(project_paths(root)["reports"] / "ingestion_reports")
    report_path = report_dir / "parse_report.md"

    qg = summary.get("qg1", {})
    results = summary.get("results", [])
    dup = summary.get("duplicate_papers", {}) or {}

    lines: list[str] = []
    lines.append("# Phase 1 Parse Report")
    lines.append("")
    lines.append(f"- run_id: {summary.get('run_id')}")
    lines.append(f"- generated_at: {now_iso()}")
    lines.append(f"- 总论文数: {summary.get('n_total')}")
    lines.append("")
    lines.append("## QG1 质量门禁")
    lines.append("")
    lines.append("| 指标 | 值 |")
    lines.append("|---|---|")
    for k, v in qg.items():
        lines.append(f"| {k} | {v} |")
    lines.append("")
    lines.append(f"**结果: {'通过 ✓' if qg.get('passed') else '未通过 ✗'}**")
    lines.append("")
    if dup:
        lines.append("## 重复内容（同一 paper_id 多文件）")
        lines.append("")
        for pid, files in dup.items():
            lines.append(f"- `{pid}` ← {', '.join(files)}")
        lines.append("")
    lines.append("## 论文清单")
    lines.append("")
    lines.append("| # | file | title | year | pages | sections | chunks | ratio | quality | review |")
    lines.append("|---:|---|---|---:|---:|---:|---:|---:|---|:---:|")
    for i, r in enumerate(sorted(results, key=lambda x: x["file"]), 1):
        if r.get("status") != "ok":
            lines.append(f"| {i} | {r['file']} | **{r.get('status')}**: {r.get('error', '')} ||||||| |")
            continue
        title = (r.get("title") or "")[:80].replace("|", "\\|")
        lines.append(
            f"| {i} | {r['file']} | {title} | {r.get('year') or ''} | "
            f"{r.get('n_pages')} | {r.get('n_sections')} | {r.get('n_chunks')} | "
            f"{r.get('text_pages_ratio')} | {r.get('parse_quality')} | "
            f"{'✗' if r.get('needs_review') else '✓'} |"
        )
    lines.append("")
    lines.append("## 警告")
    lines.append("")
    for w in summary.get("warnings", []) or ["（无）"]:
        lines.append(f"- {w}")
    lines.append("")

    with report_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return report_path
