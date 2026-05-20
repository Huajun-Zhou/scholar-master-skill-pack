#!/usr/bin/env python3
"""按 schemas/{name}.schema.json 校验 JSON 对象 / 文件。

用法：
    python scripts/validate_json.py paper_card path/to/file.json
    python scripts/validate_json.py method_card path/to/dir/

Phase 0 占位 → Phase 1 实现：调用 scholar_skill_pack.schema_validate.validate。
"""
from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("schema_name",
                        choices=["paper_card", "evidence", "method_card",
                                 "thinking_model", "wiki_page", "qa_eval"])
    parser.add_argument("path", nargs="?", help="JSON 文件或目录")
    args = parser.parse_args(argv)

    print(f"[validate_json] schema={args.schema_name} target={args.path or '<stdin>'}")
    print("[validate_json] Phase 1 will implement actual validation.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
