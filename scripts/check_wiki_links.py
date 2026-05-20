#!/usr/bin/env python3
"""检查 Wiki Markdown 链接完整性。

被 .claude/settings.json 的 PostToolUse hook 调用。Phase 0 静默 exit 0。

Phase 3 起检查：
- 所有 Markdown 链接指向真实存在的文件 / 锚点
- frontmatter.related_pages 可达
- 无孤立核心页面
- 无重复 slug
"""
from __future__ import annotations

import sys


def main() -> int:
    return 0


if __name__ == "__main__":
    sys.exit(main())
