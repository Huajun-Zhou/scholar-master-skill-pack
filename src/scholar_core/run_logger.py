"""运行日志 — 记录每次 Scholar Core 调用。"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def generate_run_id(prefix: str = "run") -> str:
    """生成运行 ID。"""
    ts = now_iso().replace(":", "").replace("-", "")[:15]
    return f"{prefix}-{ts}"


def log_run(run_dir: Path, run_id: str, metadata: dict[str, Any]) -> Path:
    """写入 metadata.json 到运行目录。"""
    run_dir = Path(run_dir) / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    meta = {
        "run_id": run_id,
        "created_at": now_iso(),
        **metadata,
    }

    meta_path = run_dir / "metadata.json"
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    return run_dir


def write_run_artifact(run_dir: Path, filename: str, content: str) -> Path:
    """在运行目录中写入一个产物文件。"""
    run_dir = Path(run_dir)
    run_dir.mkdir(parents=True, exist_ok=True)
    path = run_dir / filename
    path.write_text(content, encoding="utf-8")
    return path
