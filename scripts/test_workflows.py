#!/usr/bin/env python3
"""测试 AutoGen Workflows — 验证所有 GraphFlow 工作流可正确构建。"""

import os
import sys
from pathlib import Path

if "OPENAI_API_KEY" not in os.environ:
    os.environ["OPENAI_API_KEY"] = "sk-test-dummy-key-for-workflow-verification"

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))


def test_imports():
    """验证所有工作流模块可导入。"""
    from autogen_app.workflows import (
        build_ask_scholar_flow,
        build_critique_paper_flow,
        build_design_research_flow,
    )
    assert build_ask_scholar_flow is not None
    assert build_design_research_flow is not None
    assert build_critique_paper_flow is not None
    print("  Workflow imports: 3/3 ✓")


def test_ask_scholar_flow():
    """验证 ask_scholar 工作流可构建。"""
    from autogen_app.workflows import build_ask_scholar_flow

    flow = build_ask_scholar_flow()
    assert flow.name == "ask_scholar"
    assert len(flow._participants) == 4
    names = [p.name for p in flow._participants]
    assert names == ["task_decomposer", "scholar_mentor", "evidence_auditor", "final_writer"], \
        f"Unexpected agent order: {names}"

    # 验证每个 agent 有正确的 system message
    for p in flow._participants:
        msgs = getattr(p, "_system_messages", [])
        assert msgs, f"{p.name}: missing system messages"

    print(f"  ask_scholar_flow:")
    print(f"    participants: {names}")
    print(f"    termination: {flow._termination_condition}")
    print(f"  ✓")


def test_design_research_flow():
    """验证 design_research 工作流可构建。"""
    from autogen_app.workflows import build_design_research_flow

    flow = build_design_research_flow()
    assert flow.name == "design_research"
    assert len(flow._participants) == 9
    names = [p.name for p in flow._participants]
    expected = [
        "task_decomposer", "scholar_mentor", "method_mapper",
        "thinking_model_agent", "research_designer", "evidence_auditor",
        "risk_reviewer", "revision_planner", "final_writer",
    ]
    assert names == expected, f"Unexpected: {names}"

    # 验证每个 agent 有 tools
    for p in flow._participants:
        tools = getattr(p, "_tools", [])
        msgs = getattr(p, "_system_messages", [])
        assert msgs, f"{p.name}: missing system messages"
        # task_decomposer 可以无工具
        if p.name != "task_decomposer":
            assert tools, f"{p.name}: should have tools"

    print(f"  design_research_flow: {len(flow._participants)} agents ✓")


def test_critique_paper_flow():
    """验证 critique_paper 工作流可构建。"""
    from autogen_app.workflows import build_critique_paper_flow

    flow = build_critique_paper_flow()
    assert flow.name == "critique_paper"
    assert len(flow._participants) == 6
    names = [p.name for p in flow._participants]
    expected = [
        "task_decomposer", "scholar_mentor", "risk_reviewer",
        "evidence_auditor", "revision_planner", "final_writer",
    ]
    assert names == expected, f"Unexpected: {names}"

    print(f"  critique_paper_flow: {len(flow._participants)} agents ✓")


def test_graph_structure():
    """验证 DiGraph 结构正确。"""
    from autogen_app.workflows import build_design_research_flow

    flow = build_design_research_flow()
    graph = flow._graph

    # 验证节点数 (dict: {name: DiGraphNode})
    nodes = graph.nodes
    assert len(nodes) == 9, f"Expected 9 nodes, got {len(nodes)}"

    # 验证节点名称
    expected_names = [
        "task_decomposer", "scholar_mentor", "method_mapper",
        "thinking_model_agent", "research_designer", "evidence_auditor",
        "risk_reviewer", "revision_planner", "final_writer",
    ]
    assert sorted(nodes.keys()) == sorted(expected_names), f"Unexpected: {sorted(nodes.keys())}"

    # 验证边链结构 (每个节点指向下一个)
    for i in range(len(expected_names) - 1):
        cur = nodes[expected_names[i]]
        nxt = expected_names[i + 1]
        assert cur.edges, f"{expected_names[i]} has no edges"
        assert cur.edges[0].target == nxt, \
            f"{expected_names[i]} → {cur.edges[0].target}, expected → {nxt}"

    # 最后一个节点无边
    assert nodes["final_writer"].edges == []

    # 验证入口点
    entry = graph.default_start_node
    assert entry == "task_decomposer", f"Expected task_decomposer, got {entry}"

    # 验证无环
    assert not graph.has_cycles_with_exit(), "Graph has cycles"

    print(f"  Graph: {len(nodes)} nodes, entry={entry}, no cycles ✓")


def test_cli_module():
    """验证 CLI 模块可导入且命令已定义。"""
    from autogen_app.cli import ask, design, critique, main
    import inspect

    assert inspect.iscoroutinefunction(ask)
    assert inspect.iscoroutinefunction(design)
    assert inspect.iscoroutinefunction(critique)
    assert callable(main)
    print("  CLI: ask/design/critique/main all defined ✓")


def test_message_filters():
    """验证消息过滤模块。"""
    from autogen_app.message_filters import (
        get_message_content,
        get_message_source,
        is_text_message,
    )

    # 简单模拟消息对象
    class MockMsg:
        def __init__(self, content, source="test", msg_type="TextMessage"):
            self.content = content
            self.source = source
            self.type = msg_type

    msg = MockMsg("Hello world", source="scholar_mentor")
    assert get_message_content(msg) == "Hello world"
    assert get_message_source(msg) == "scholar_mentor"
    assert is_text_message(msg) is True
    print("  message_filters: all helpers work ✓")


def test_termination():
    """验证终止条件。"""
    from autogen_app.termination import make_termination, FINISH_MARKER

    term = make_termination()
    assert term is not None
    assert FINISH_MARKER == "FINAL_REPORT"
    print(f"  termination: marker='{FINISH_MARKER}' ✓")


def test_output_parser():
    """验证输出解析器。"""
    import tempfile
    from autogen_app.output_parser import (
        extract_agent_outputs,
        extract_final_report,
        save_run_artifacts,
    )

    class MockMsg:
        def __init__(self, content, source="test", msg_type="TextMessage"):
            self.content = content
            self.source = source
            self.type = msg_type

    msgs = [
        MockMsg("Step 1 complete", source="task_decomposer"),
        MockMsg("Methodology analysis...", source="scholar_mentor"),
        MockMsg("Final design FINAL_REPORT", source="final_writer"),
    ]

    final = extract_final_report(msgs)
    assert "FINAL_REPORT" in final

    outputs = extract_agent_outputs(msgs)
    assert "task_decomposer" in outputs
    assert "scholar_mentor" in outputs
    assert "final_writer" in outputs

    with tempfile.TemporaryDirectory() as tmp:
        run_dir = Path(tmp) / "test_run"
        saved = save_run_artifacts(run_dir, outputs, {"test": True})
        assert len(saved) == 4  # 3 agent outputs + metadata.json
        assert (run_dir / "metadata.json").is_file()

    print(f"  output_parser: {len(saved)} artifacts saved ✓")


def main():
    print()
    print("AutoGen Workflows — Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("Workflow imports", test_imports),
        ("Ask Scholar flow", test_ask_scholar_flow),
        ("Design Research flow", test_design_research_flow),
        ("Critique Paper flow", test_critique_paper_flow),
        ("Graph structure", test_graph_structure),
        ("CLI module", test_cli_module),
        ("Message filters", test_message_filters),
        ("Termination", test_termination),
        ("Output parser", test_output_parser),
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
