"""Wiki lint 汇总：调用 check_* 脚本，输出统一报告。

实现：Phase 3。Phase 0 占位。
"""
from __future__ import annotations

from pathlib import Path
from typing import Any


def run_lint(root: Path) -> dict[str, Any]:
    """运行所有 lint 检查，返回 {checks: [...], summary: {...}}。"""
    raise NotImplementedError("Phase 3 will implement run_lint().")
