#!/usr/bin/env python3
"""检查 Wiki / Paper Cards 的 evidence 覆盖率。

被 .claude/settings.json 的 PostToolUse hook 调用。Phase 0 静默 exit 0。

Phase 1 / Phase 3 起检查：
- A 类结论是否都有 evidence_id
- B 类综合是否 ≥ 2 个 paper_id
- C 类迁移是否标记
- 报告写入 reports/quality_reports/
"""
from __future__ import annotations

import sys


def main() -> int:
    # 静默 exit，避免污染 hook 输出。
    return 0


if __name__ == "__main__":
    sys.exit(main())
