"""Phase 10: 增量维护引擎。

支持新增论文时的增量更新流程，避免全量重建。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .ingest import ingest_all
from .registry import list_papers, list_sources
from .utils import ensure_dir, now_iso, project_paths


def detect_new_papers(root: Path) -> list[str]:
    """对比 data/raw/papers/ 与 source_registry，返回新增 PDF 文件名列表。"""
    paths = project_paths(root)
    pdfs = set(p.name for p in (paths["raw_papers"].glob("*.pdf")))
    registry = paths["registry"] / "source_registry.jsonl"

    known = set()
    if registry.is_file():
        with registry.open("r", encoding="utf-8") as f:
            for line in f:
                try:
                    rec = json.loads(line)
                    known.add(rec.get("source_file", ""))
                except Exception:
                    pass
    new = sorted(pdfs - known)
    return new


def incremental_ingest(root: Path) -> dict[str, Any]:
    """检测新增 PDF 并仅解析新论文。

    返回 {"new_papers": [...], "run_id": str, "warnings": [...]}
    """
    new = detect_new_papers(root)
    if not new:
        return {"new_papers": [], "run_id": "", "message": "无新增论文"}

    print(f"检测到 {len(new)} 篇新论文: {new}")
    summary = ingest_all(root, force=False)
    return {
        "new_papers": new,
        "run_id": summary.get("run_id", ""),
        "n_parsed": summary.get("n_total", 0),
        "results": summary.get("results", []),
        "qg1": summary.get("qg1", {}),
    }


def stage_new_paper_updates(root: Path, new_paper_ids: list[str]) -> Path:
    """为新论文生成 staged wiki updates。"""
    paths = project_paths(root)
    run_id = f"inc-{now_iso().replace(':', '').replace('-', '')[:15]}"
    staging_dir = ensure_dir(paths["wiki"] / "logs" / "staging" / run_id)

    (staging_dir / "new_papers.json").write_text(
        json.dumps(new_paper_ids, ensure_ascii=False, indent=2), encoding="utf-8")

    merge_plan = [
        f"# Incremental Merge Plan — {run_id}",
        f"",
        f"## 新增论文",
    ]
    for pid in new_paper_ids:
        merge_plan.append(f"- `{pid}`")
    merge_plan.extend([
        "",
        "## 待更新页面",
        "- [ ] wiki/research_timeline.md — 新增年份条目",
        "- [ ] wiki/research_questions.md — 如涉及新问题类型",
        "- [ ] wiki/source_registry.md — 添加新论文",
        "- [ ] wiki/glossary.md — 如引入新术语",
        "- [ ] wiki/synthesis/research_lines.md — 如影响研究主线",
        "- [ ] wiki/synthesis/method_evolution.md — 如引入新方法或方法变化",
        "- [ ] method_cards/ — 如新论文强化或补充现有方法",
        "",
        "## 检查项",
        "- [ ] QG1: 新论文解析质量",
        "- [ ] QG2: Paper Card evidence 覆盖",
        "- [ ] QG3: Wiki frontmatter/link 完整",
        "- [ ] 新论文是否推翻旧结论 (→ wiki/contradictions.md)",
    ])
    (staging_dir / "merge_plan.md").write_text("\n".join(merge_plan), encoding="utf-8")
    return staging_dir


def write_change_log(root: Path, run_id: str,
                     changes: dict[str, Any]) -> Path:
    """写入 wiki/logs/{date}-{run_id}.md 变更日志。"""
    paths = project_paths(root)
    log_dir = ensure_dir(paths["wiki"] / "logs")
    date_str = now_iso()[:10]
    log_path = log_dir / f"{date_str}-{run_id}.md"

    lines = [
        f"# Wiki Update Log — {run_id}",
        f"",
        f"- 日期: {now_iso()}",
        f"",
        "## 新增论文",
    ]
    for p in changes.get("new_papers", []):
        lines.append(f"- {p}")

    lines.append("")
    lines.append("## 新增页面")
    for p in changes.get("new_pages", []) or ["（无）"]:
        lines.append(f"- {p}")

    lines.append("")
    lines.append("## 修改页面")
    for p in changes.get("modified_pages", []) or ["（无）"]:
        lines.append(f"- {p}")

    lines.append("")
    lines.append("## 合并概念")
    for p in changes.get("merged_concepts", []) or ["（无）"]:
        lines.append(f"- {p}")

    lines.append("")
    lines.append("## 新增方法卡片")
    for p in changes.get("new_method_cards", []) or ["（无）"]:
        lines.append(f"- {p}")

    lines.append("")
    lines.append("## 证据不足项")
    for p in changes.get("weak_evidence", []) or ["（无）"]:
        lines.append(f"- {p}")

    lines.append("")
    lines.append("## 需要人工复核")
    for p in changes.get("needs_review", []) or ["（无）"]:
        lines.append(f"- {p}")

    lines.append("")
    with log_path.open("w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    return log_path
