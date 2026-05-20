"""Evidence Gate — 证据门禁规则引擎。

在 evidence_auditor agent 执行后检查输出是否通过质量门禁。
不通过时返回修订指令，供工作流 runner 路由回退重试。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


def _find_project_root() -> Path:
    cur = Path(__file__).resolve().parent
    for p in [cur, *cur.parents]:
        if (p / "pyproject.toml").is_file() and (p / "CLAUDE.md").is_file():
            return p
    return cur.parent.parent


def load_gate_rules() -> dict[str, Any]:
    """加载证据门禁规则。"""
    import yaml
    root = _find_project_root()
    path = root / "config" / "evidence_gate.yaml"
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return (yaml.safe_load(f) or {}).get("evidence_gate", {})


@dataclass
class GateResult:
    """门禁检查结果。"""
    passed: bool = True
    unsupported_claims: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    required_actions: list[str] = field(default_factory=list)
    summary: str = ""


def check_gate(audit_text: str) -> GateResult:
    """检查 evidence_auditor 输出是否通过门禁。

    从 audit_evidence_tool 返回的 Markdown 文本中提取关键信息，
    按规则检查是否符合 A/B/C 证据标准。

    参数:
        audit_text: evidence_auditor agent 的完整输出文本

    返回:
        GateResult: 通过/不通过 + 具体问题和修复建议
    """
    rules = load_gate_rules()
    max_unsupported = int(rules.get("max_unsupported_major_claims", 0))
    max_c_core = int(rules.get("max_c_level_core_claims", 2))
    require_ab_method = rules.get("require_a_or_b_for_method_claims", True)

    result = GateResult()

    # 1. 解析 audit 输出
    # 查找 "Gate 结果: 未通过" 或 "Gate Result: FAIL"
    audit_lower = audit_text.lower()

    has_gate_fail = (
        "gate 结果: 未通过" in audit_lower
        or "gate 结果: **未通过**" in audit_lower
        or "gate result: fail" in audit_lower
    )

    # 2. 提取无证据主张
    unsupported_keywords = [
        ("Insufficient", "Insufficient"),
        ("证据不足", "Insufficient"),
        ("unsupported", "Insufficient"),
    ]

    for line in audit_text.split("\n"):
        line_stripped = line.strip()

        # 跳过表头和分隔行
        if not line_stripped or line_stripped.startswith("|") and "---" in line_stripped:
            continue
        if "| Claim |" in line_stripped or "| ---" in line_stripped:
            continue

        # 解析表格行: | claim | level | support | risk | action |
        if line_stripped.startswith("|") and line_stripped.endswith("|"):
            cols = [c.strip() for c in line_stripped.split("|")[1:-1]]
            if len(cols) >= 5:
                claim, level, support, risk, action = cols[0], cols[1], cols[2], cols[3], cols[4]

                # 检查无证据项
                if level in ("Insufficient",):
                    result.unsupported_claims.append(claim[:100])
                    if action in ("remove",):
                        result.required_actions.append(
                            f"移除或重写无证据主张: {claim[:60]}..."
                        )

                # 检查 C 级核心主张
                if level == "C" and action == "downgrade":
                    result.warnings.append(f"C 级主张需降级: {claim[:60]}...")

    # 3. 检查方法论主张
    if require_ab_method:
        for line in audit_text.split("\n"):
            if "方法" in line and "C" in line and "|" in line:
                result.warnings.append("方法论主张为 C 级 — 需要 A 或 B 级证据支持")
                result.required_actions.append("方法主张需升级到 A/B 级或显式标注为 C 迁移推断")

    # 4. 应用规则
    if has_gate_fail or len(result.unsupported_claims) > max_unsupported:
        result.passed = False
        if result.unsupported_claims:
            result.required_actions.insert(
                0, f"修复 {len(result.unsupported_claims)} 个无证据主张后重新审计"
            )

    # 5. 生成摘要
    if result.passed:
        result.summary = "通过 — 所有核心主张有充分证据支持"
    else:
        reasons = []
        if result.unsupported_claims:
            reasons.append(f"{len(result.unsupported_claims)} 个无证据主张")
        if result.warnings:
            reasons.append(f"{len(result.warnings)} 个警告")
        result.summary = f"未通过 — {', '.join(reasons)}"

    return result


def format_gate_feedback(gate: GateResult) -> str:
    """将门禁结果格式化为可反馈给 agent 的修正指令。"""
    lines = [
        "",
        "---",
        "## [EVIDENCE GATE RESULT]",
        "",
        f"**Gate 状态**: {'通过 ✓' if gate.passed else '未通过 ✗'}",
        f"**摘要**: {gate.summary}",
    ]

    if gate.unsupported_claims:
        lines.append("")
        lines.append("### 无证据主张（必须修复）")
        for c in gate.unsupported_claims:
            lines.append(f"- [Insufficient] {c}")

    if gate.warnings:
        lines.append("")
        lines.append("### 警告")
        for w in gate.warnings:
            lines.append(f"- {w}")

    if gate.required_actions:
        lines.append("")
        lines.append("### 需要执行的操作")
        for i, action in enumerate(gate.required_actions, 1):
            lines.append(f"{i}. {action}")

    lines.append("")
    return "\n".join(lines)


class GateFailedError(Exception):
    """门禁失败异常 — 触发工作流重试。"""

    def __init__(self, gate: GateResult):
        self.gate = gate
        super().__init__(gate.summary)
