"""配置加载 — 读取 scholar / evidence / retrieval 配置。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def _find_project_root() -> Path:
    """向上查找项目根（存在 pyproject.toml + CLAUDE.md）。"""
    cur = Path(__file__).resolve().parent
    for p in [cur, *cur.parents]:
        if (p / "pyproject.toml").is_file() and (p / "CLAUDE.md").is_file():
            return p
    # fallback: 从 scholar_core 上溯到项目根
    return cur.parent.parent


def load_yaml(name: str) -> dict[str, Any]:
    """读取 config/{name}。"""
    root = _find_project_root()
    path = root / "config" / name
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def get_retrieval_config() -> dict[str, Any]:
    return load_yaml("retrieval.yaml").get("retrieval", {})


def get_evidence_config() -> dict[str, Any]:
    return load_yaml("evidence.yaml").get("evidence_policy", {})


def project_root() -> Path:
    return _find_project_root()
