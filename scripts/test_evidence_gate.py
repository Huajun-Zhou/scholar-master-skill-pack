#!/usr/bin/env python3
"""测试 Evidence Gate — 验证门禁检查逻辑正确。"""

import os
import sys
from pathlib import Path

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = "sk-test"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from autogen_app.evidence_gate import (
    GateResult,
    check_gate,
    format_gate_feedback,
    load_gate_rules,
)


def test_load_rules():
    """验证门禁规则可加载。"""
    rules = load_gate_rules()
    assert "max_unsupported_major_claims" in rules
    assert "max_c_level_core_claims" in rules
    assert rules["max_unsupported_major_claims"] == 0
    assert rules["require_a_or_b_for_method_claims"] is True
    print(f"  rules loaded: {rules}")
    print("  ✓")


def test_gate_pass_on_clean_output():
    """验证干净输出通过门禁。"""
    clean_audit = """# Evidence Audit

## 总结

通过 — 所有 3 个 claims 有 A 或 B 级证据支持

## Gate 结果: 通过

## 无证据核心主张

（无）

## Claims

| Claim | Evidence Level | Support | Risk | Action |
|---|---|---|---|---|
| 该方法使用自适应阈值策略 | A | PAPER_8111E254 | 低 | keep |
| 多篇论文验证了该策略有效性 | B | 3 papers | 低-中 | keep |
| 可迁移到新领域 | C | 迁移推断 | 中 | keep |
"""
    gate = check_gate(clean_audit)
    assert gate.passed, f"Expected pass, got: {gate.summary}"
    assert len(gate.unsupported_claims) == 0
    print(f"  {gate.summary} ✓")


def test_gate_fail_on_unsupported():
    """验证无证据输出被门禁阻止。"""
    bad_audit = """# Evidence Audit

## 总结

未通过 — 1 个无证据核心主张

## Gate 结果: **未通过**

## 无证据核心主张

- 我们提出的方法在理论上优于所有现有方法

## Claims

| Claim | Evidence Level | Support | Risk | Action |
|---|---|---|---|---|
| 我们提出的方法在理论上优于所有现有方法 | Insufficient | 无来源 | 高 | remove |
| 一些相关背景 | B | 2 papers | 低 | keep |
| 可迁移到新领域 | C | 推断 | 中 | keep |
"""
    gate = check_gate(bad_audit)
    assert not gate.passed, f"Expected fail, got: {gate.summary}"
    assert len(gate.unsupported_claims) >= 1
    assert len(gate.required_actions) >= 1
    print(f"  {gate.summary}")
    print(f"  unsupported: {len(gate.unsupported_claims)} claims")
    print(f"  required_actions: {len(gate.required_actions)}")
    print("  ✓")


def test_gate_on_mixed_output():
    """验证混合质量输出的门禁行为。"""
    mixed_audit = """# Evidence Audit

## 总结

未通过 — 1 个无证据核心主张 — 2 个警告

## Gate 结果: **未通过**

## 无证据核心主张

- 陈志远教授明确提出了多智能体自动写论文框架

## 警告

- 2 个核心主张为 C 级迁移推断

## Claims

| Claim | Evidence Level | Support | Risk | Action |
|---|---|---|---|---|
| 陈志远教授明确提出了多智能体框架 | Insufficient | 无来源 | 高 | remove |
| 自适应阈值策略有效 | A | PAPER_8111E254 | 低 | keep |
| 该策略可迁移 | C | 推断 | 中 | downgrade |
"""
    gate = check_gate(mixed_audit)
    assert not gate.passed
    assert "多智能体" in gate.unsupported_claims[0] or "自动写论文" in gate.unsupported_claims[0]
    print(f"  {gate.summary}")
    print(f"  unsupported claims: {gate.unsupported_claims}")
    print("  ✓")


def test_format_feedback():
    """验证门禁反馈格式化。"""
    gate = GateResult(
        passed=False,
        unsupported_claims=["主张A无证据", "主张B编造了citation"],
        warnings=["核心主张C级过多"],
        required_actions=["移除无证据主张A", "为主张B添加证据来源"],
        summary="未通过 — 2 个无证据主张",
    )
    feedback = format_gate_feedback(gate)
    assert "EVIDENCE GATE" in feedback
    assert "未通过" in feedback
    assert "主张A" in feedback
    print(f"  feedback length: {len(feedback)} chars")
    print(f"  contains all sections: ✓")


def test_gate_module_imports():
    """验证 evidence_gate 模块完整可导入。"""
    from autogen_app.evidence_gate import GateFailedError, format_gate_feedback
    # Test GateFailedError
    gate = GateResult(passed=False, unsupported_claims=["test"],
                      summary="未通过 — 测试")
    err = GateFailedError(gate)
    assert "未通过" in str(err)
    print("  GateFailedError: works ✓")
    print("  all symbols importable: ✓")


def main():
    print()
    print("Evidence Gate — Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("Load gate rules", test_load_rules),
        ("Gate pass on clean output", test_gate_pass_on_clean_output),
        ("Gate fail on unsupported claims", test_gate_fail_on_unsupported),
        ("Gate on mixed quality output", test_gate_on_mixed_output),
        ("Format gate feedback", test_format_feedback),
        ("Module imports", test_gate_module_imports),
    ]

    passed = 0
    failed = 0
    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"\n  FAIL: {name} — {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print()
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 60)
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
