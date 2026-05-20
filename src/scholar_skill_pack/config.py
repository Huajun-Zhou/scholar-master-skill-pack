"""配置加载（scholar / pipeline / quality_gates / prompts）。"""
from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

CONFIG_FILES = ["scholar.yaml", "pipeline.yaml", "quality_gates.yaml", "prompts.yaml"]


def load_config(root: Path, name: str) -> dict[str, Any]:
    """读取 config/{name} 并返回字典。"""
    path = root / "config" / name
    if not path.is_file():
        raise FileNotFoundError(f"Config not found: {path}")
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_all(root: Path) -> dict[str, dict[str, Any]]:
    """读取全部配置，按文件名（去 .yaml）作 key。"""
    return {name.removesuffix(".yaml"): load_config(root, name) for name in CONFIG_FILES}
