"""Evidence hallucination checker.

After the LLM generates an answer, this module scans all evidence IDs
cited in the answer and verifies them against the claims registry.
Any IDs not found are marked as potential hallucinations.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

EVID_PATTERN = re.compile(r"EVID-[\w]+-[\w]+-[\w]+")


def build_evidence_index(root: Path) -> set[str]:
    """Build an in-memory index of all known evidence IDs from claims files."""
    claims_dir = root / "wiki" / "claims"
    if not claims_dir.is_dir():
        return set()

    known: set[str] = set()

    # 1. Scan claims JSONL files
    for claims_file in claims_dir.glob("*.jsonl"):
        try:
            for line in claims_file.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line:
                    continue
                try:
                    claim = json.loads(line)
                    for eid in claim.get("evidence_ids", []):
                        known.add(eid)
                except json.JSONDecodeError:
                    continue
        except Exception:
            continue

    # 2. Also scan Paper Card markdown files (evidence IDs in text)
    papers_dir = root / "wiki" / "papers"
    if papers_dir.is_dir():
        for paper_file in papers_dir.glob("*.md"):
            try:
                body = paper_file.read_text(encoding="utf-8")
                found = EVID_PATTERN.findall(body)
                known.update(found)
            except Exception:
                continue

    return known


def check_hallucination(answer_text: str, root: Path) -> str:
    """Scan answer for evidence IDs and verify against the registry.

    Returns a warning string if any IDs are not found in the claims registry.
    Returns empty string if all IDs are valid (or if no IDs found).
    """
    cited_ids = set(EVID_PATTERN.findall(answer_text))
    if not cited_ids:
        return ""

    known = build_evidence_index(root)

    valid = cited_ids & known
    invalid = cited_ids - known

    if not invalid:
        # All good — optionally mention that all citations verified
        return (
            f"\n\n---\n\n"
            f"*[证据自检通过] 回答中引用的 {len(valid)} 个 evidence_id "
            f"均在知识库注册表中找到。*"
        )

    # Some invalid IDs found
    warning = (
        f"\n\n---\n\n"
        f"## 证据自查报告\n\n"
        f"| 状态 | 数量 |\n"
        f"|---|---|\n"
        f"| 已验证 ✓ | {len(valid)} |\n"
        f"| 未找到 ⚠ | {len(invalid)} |\n\n"
    )
    if valid:
        warning += "**已验证的 evidence_id**（在知识库中确认存在）：\n"
        for eid in sorted(valid)[:5]:
            warning += f"- `{eid}` ✓\n"
        if len(valid) > 5:
            warning += f"- ... 还有 {len(valid) - 5} 个\n"
        warning += "\n"

    if invalid:
        warning += "**未找到的 evidence_id**（可能为 LLM 幻觉，请谨慎对待）：\n"
        for eid in sorted(invalid)[:5]:
            warning += f"- `{eid}` ⚠\n"
        if len(invalid) > 5:
            warning += f"- ... 还有 {len(invalid) - 5} 个\n"
        warning += (
            "\n*这些 evidence_id 格式上像引用但在知识库中不存在。"
            "LLM 可能在生成文本时编造了它们。建议忽略这部分引用或手动核实原文。*"
        )

    return warning
