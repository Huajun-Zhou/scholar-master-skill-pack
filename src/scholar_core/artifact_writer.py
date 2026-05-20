"""产物写入 — 将报告/回答写入文件系统。"""

from __future__ import annotations

import json
from pathlib import Path


def write_artifact(path: str, content: str) -> Path:
    """写入产物文件（Markdown 或 JSON），自动创建父目录。"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return p


def write_json_artifact(path: str, data: dict) -> Path:
    """写入 JSON 产物。"""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return p
