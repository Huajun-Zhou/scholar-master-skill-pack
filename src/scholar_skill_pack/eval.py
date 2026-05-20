"""评估体系运行入口。

实现：Phase 9。Phase 0 占位。
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def run_eval(root: Path, suite: str = "all") -> dict[str, Any]:
    """suite ∈ {golden, hallucination, transfer, all}。Phase 9 实现。"""
    raise NotImplementedError("Phase 9 will implement run_eval().")
