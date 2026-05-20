#!/usr/bin/env python3
"""按 config/quality_gates.yaml 运行 QG1-QG9 并生成汇总报告。

用法：
    python scripts/run_quality_gates.py --phase 1
    python scripts/run_quality_gates.py --all

Phase 1 起逐 phase 启用对应 QG。
"""
from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", type=int, help="只跑指定 Phase 的 QG")
    parser.add_argument("--all", action="store_true", help="跑所有 QG")
    args = parser.parse_args(argv)
    print(f"[run_quality_gates] phase={args.phase} all={args.all}")
    print("[run_quality_gates] Phase 1+ will implement actual checks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
