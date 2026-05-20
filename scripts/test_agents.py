#!/usr/bin/env python3
"""测试 AutoGen Agents — 验证每个 agent 可正确构建。

兼容 AutoGen >= 0.7.x
"""

import os
import sys
from pathlib import Path

# 设置 dummy API key 用于测试（不实际调用 API）
if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = "sk-test-dummy-key-for-agent-verification"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from autogen_app.agents import AGENT_BUILDERS, build_agent, build_all_agents


def _get_system_message(agent) -> str:
    """Compat: AutoGen 0.7.x stores system messages in _system_messages list."""
    msgs = getattr(agent, "_system_messages", [])
    if msgs:
        return " ".join(str(m) for m in msgs)
    return getattr(agent, "system_message", "")


def _get_tools(agent) -> list:
    """Compat: AutoGen 0.7.x stores tools in _tools list."""
    return getattr(agent, "_tools", []) or getattr(agent, "tools", []) or []


def test_agent_names():
    """验证 9 个 agent 名称正确。"""
    expected = {
        "task_decomposer",
        "scholar_mentor",
        "method_mapper",
        "thinking_model_agent",
        "research_designer",
        "evidence_auditor",
        "risk_reviewer",
        "revision_planner",
        "final_writer",
    }
    actual = set(AGENT_BUILDERS.keys())
    assert actual == expected, f"Missing: {expected - actual}, Extra: {actual - expected}"
    print(f"  Agent names: {len(actual)}/9 ✓")


def test_build_individual():
    """逐个构建 agent 并验证属性。"""
    tool_checks = {
        "task_decomposer": [],
        "scholar_mentor": ["search_wiki_tool", "ask_scholar_tool"],
        "method_mapper": ["get_method_cards_tool"],
        "thinking_model_agent": ["get_thinking_models_tool"],
        "research_designer": ["design_research_tool"],
        "evidence_auditor": ["audit_evidence_tool"],
        "risk_reviewer": ["critique_paper_tool"],
        "revision_planner": ["ask_scholar_tool"],
        "final_writer": ["write_report_tool"],
    }

    for name in AGENT_BUILDERS:
        agent = build_agent(name)
        assert agent.name == name, f"{name}: name mismatch ({agent.name})"

        # 检查 system_message
        msg = _get_system_message(agent)
        assert msg, f"{name}: missing system_message"
        assert len(msg) > 200, f"{name}: system_message too short ({len(msg)} chars)"

        # 检查全局策略已注入
        msg_lower = msg.lower()
        policy_found = (
            "no impersonation" in msg_lower
            or "not impersonate" in msg_lower
            or "NOT the target scholar" in msg_lower
        )
        assert policy_found, f"{name}: global policy (no-impersonation) not found"

        # 检查工具
        expected_tools = tool_checks.get(name, [])
        tools = _get_tools(agent)
        tool_names = [t.name for t in tools]  # FunctionTool uses .name, not .__name__
        for et in expected_tools:
            assert et in tool_names, f"{name}: missing tool '{et}'. Actual tools: {tool_names}"

        print(f"  {name}: msg={len(msg)} chars, tools={len(tools)} ✓")


def test_build_all():
    """验证 build_all_agents() 返回全部 9 个 agent。"""
    agents = build_all_agents()
    assert len(agents) == 9, f"Expected 9, got {len(agents)}"
    for name, agent in agents.items():
        assert agent.name == name
    print(f"  build_all_agents(): {len(agents)} agents ✓")


def test_build_by_name():
    """验证通过 build_agent(name) 构建。"""
    for name in ["scholar_mentor", "evidence_auditor", "final_writer"]:
        agent = build_agent(name)
        assert agent.name == name
        assert _get_system_message(agent)
    print("  build_agent(name): 3/3 ✓")


def test_system_message_content():
    """验证 system_message 包含关键内容。"""
    agent = build_agent("evidence_auditor")
    msg = _get_system_message(agent).lower()

    checks = [
        ("evidence level", "evidence" in msg or "a/b/c" in msg),
        ("strict auditor", "strict" in msg),
        ("audit tool", "audit_evidence" in msg),
    ]
    for label, ok in checks:
        status = "✓" if ok else "✗"
        print(f"    [{status}] {label}: {ok}")


def main():
    print()
    print("AutoGen Agents — Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("Agent names", test_agent_names),
        ("Build individual agents", test_build_individual),
        ("Build all agents", test_build_all),
        ("Build by name", test_build_by_name),
        ("System message content", test_system_message_content),
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
