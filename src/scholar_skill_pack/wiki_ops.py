"""Wiki 读写、frontmatter 解析、staging 与合并。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from .utils import now_iso


def read_page(path: Path) -> dict[str, Any]:
    """读取 Wiki 页面：返回 {frontmatter, body, raw}。"""
    if not path.is_file():
        raise FileNotFoundError(f"Wiki page not found: {path}")

    raw = path.read_text(encoding="utf-8")
    frontmatter: dict[str, Any] = {}
    body = raw

    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            try:
                frontmatter = yaml.safe_load(parts[1]) or {}
            except yaml.YAMLError:
                frontmatter = {"_parse_error": "YAML frontmatter 解析失败"}
            body = parts[2].lstrip("\n")
    return {"frontmatter": frontmatter, "body": body, "path": str(path)}


def write_page(path: Path, frontmatter: dict[str, Any], body: str) -> None:
    """写 Wiki 页面（原子写：先写 tmp 再 rename）。"""
    path.parent.mkdir(parents=True, exist_ok=True)

    fm_yaml = yaml.dump(frontmatter, allow_unicode=True, sort_keys=False).strip()
    content = f"---\n{fm_yaml}\n---\n\n{body.strip()}\n"

    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def list_pages(wiki_dir: Path, subdir: str = "papers") -> list[Path]:
    """列出 wiki/{subdir}/ 下所有 .md 文件。"""
    d = wiki_dir / subdir
    if not d.is_dir():
        return []
    return sorted(d.glob("*.md"))


def stage_update(staging_dir: Path, run_id: str,
                 changes: list[dict[str, Any]]) -> Path:
    """生成 staging 目录与 review_summary。

    changes 每项: {"action": "new"|"edit", "path": str, "frontmatter": {...}, "body": str}
    """
    run_dir = staging_dir / run_id
    proposed_new = run_dir / "proposed_new_pages"
    proposed_edit = run_dir / "proposed_edits"
    proposed_new.mkdir(parents=True, exist_ok=True)
    proposed_edit.mkdir(parents=True, exist_ok=True)

    new_count = 0
    edit_count = 0

    for ch in changes:
        action = ch.get("action", "new")
        target = proposed_new if action == "new" else proposed_edit
        rel = Path(ch["path"])
        out = target / rel.name
        write_page(out, ch.get("frontmatter", {}), ch.get("body", ""))

        if action == "new":
            new_count += 1
        else:
            edit_count += 1

    # 生成 review_summary
    summary_lines = [
        f"# Staging Review — {run_id}",
        f"",
        f"- 新增页面: {new_count}",
        f"- 修改页面: {edit_count}",
        f"- 生成时间: {now_iso()}",
        f"",
        f"## 新增",
    ]
    for ch in changes:
        if ch.get("action") == "new":
            summary_lines.append(f"- {ch['path']}")
    summary_lines.append("")
    summary_lines.append("## 修改")
    for ch in changes:
        if ch.get("action") == "edit":
            summary_lines.append(f"- {ch['path']}")
    summary_lines.append("")

    (run_dir / "review_summary.md").write_text("\n".join(summary_lines), encoding="utf-8")
    return run_dir
