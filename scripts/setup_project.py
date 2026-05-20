#!/usr/bin/env python3
"""项目骨架检查 / raw PDF 保护。

被 .claude/settings.json 的 PreToolUse hook 调用：
    python scripts/setup_project.py --protect-raw-pdfs

Phase 0 占位：当前实现仅打印保护策略提示，始终 exit 0，
不阻塞工具调用。Phase 1 接入实际的工具调用上下文识别后再启用阻断。
"""
from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--protect-raw-pdfs", action="store_true",
                        help="保护 data/raw/papers/*.pdf 不被修改/删除")
    parser.add_argument("--check-skeleton", action="store_true",
                        help="检查项目骨架完整性")
    args = parser.parse_args(argv)

    # Phase 0：仅打印；Phase 1 起接入实际拦截。
    if args.protect_raw_pdfs:
        pass  # silent — 避免污染 hook 输出
    if args.check_skeleton:
        print("[setup_project] skeleton check is a Phase 1 task.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
