#!/usr/bin/env python3
"""测试 AutoGen Tools — 验证每个 tool 可被 AssistantAgent 调用。"""

import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from autogen_app.tools import (
    ask_scholar_tool,
    audit_evidence_tool,
    critique_paper_tool,
    design_research_tool,
    get_evidence_tool,
    get_method_cards_tool,
    get_thinking_models_tool,
    list_papers_tool,
    search_wiki_tool,
    write_report_tool,
)


async def test_search_wiki():
    result = await search_wiki_tool("去噪 自适应")
    assert "Scholar Wiki" in result, "Missing header"
    assert len(result) > 100, "Result too short"
    print(f"  search_wiki_tool: {len(result)} chars ✓")


async def test_get_method_cards():
    result = await get_method_cards_tool("鲁棒 优化")
    assert "方法卡片" in result, "Missing header"
    assert "Method Card" in result, "Missing card content"
    print(f"  get_method_cards_tool: {len(result)} chars ✓")


async def test_get_thinking_models():
    result = await get_thinking_models_tool("鲁棒 物理")
    assert "思维模型" in result, "Missing header"
    print(f"  get_thinking_models_tool: {len(result)} chars ✓")


async def test_get_evidence():
    result = await get_evidence_tool("")
    assert "Evidence Registry" in result, "Missing header"
    print(f"  get_evidence_tool: {len(result)} chars ✓")


async def test_list_papers():
    result = await list_papers_tool()
    assert "论文清单" in result, "Missing header"
    assert "PAPER_" in result, "Missing paper IDs"
    print(f"  list_papers_tool: {len(result)} chars ✓")


async def test_ask_scholar():
    result = await ask_scholar_tool("如何提出高质量研究问题？")
    assert "基于 Scholar Skill" in result, "Missing template"
    assert "证据" in result, "Missing evidence section"
    print(f"  ask_scholar_tool: {len(result)} chars ✓")


async def test_design_research():
    result = await design_research_tool("图像去噪自适应阈值", target_journal="TIP")
    assert "Research Design Report" in result, "Missing template"
    assert "方法迁移映射" in result or "方法" in result, "Missing method section"
    print(f"  design_research_tool: {len(result)} chars ✓")


async def test_audit_evidence():
    result = await audit_evidence_tool(
        "我们提出了一个全新的方法，在理论上优于所有现有方法。"
        "陈志远教授明确提出了多智能体自动写论文框架。"
    )
    assert "Evidence Audit" in result, "Missing template"
    print(f"  audit_evidence_tool: {len(result)} chars ✓")


async def test_critique_paper():
    sample = Path(__file__).resolve().parent.parent / "reports" / "baseline" / "sample_paper_for_critique.md"
    if sample.is_file():
        result = await critique_paper_tool(str(sample), target_journal="TIP")
        assert "Paper Critique" in result, "Missing template"
        print(f"  critique_paper_tool: {len(result)} chars ✓")
    else:
        print(f"  critique_paper_tool: SKIP (sample paper not found)")


async def test_write_report():
    out = Path(__file__).resolve().parent.parent / "reports" / "autogen_runs" / "test_tool_output.md"
    result = await write_report_tool(str(out), "# Test Report\n\nHello from AutoGen tool test.")
    assert "报告已写入" in result, "Missing confirmation"
    assert out.is_file(), "File not written"
    print(f"  write_report_tool: {result} ✓")


async def main():
    print()
    print("AutoGen Tools — Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("search_wiki_tool", test_search_wiki),
        ("get_method_cards_tool", test_get_method_cards),
        ("get_thinking_models_tool", test_get_thinking_models),
        ("get_evidence_tool", test_get_evidence),
        ("list_papers_tool", test_list_papers),
        ("ask_scholar_tool", test_ask_scholar),
        ("design_research_tool", test_design_research),
        ("audit_evidence_tool", test_audit_evidence),
        ("critique_paper_tool", test_critique_paper),
        ("write_report_tool", test_write_report),
    ]

    passed = 0
    failed = 0
    for name, test_fn in tests:
        try:
            await test_fn()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {name} — {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print()
    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 60)
    return failed == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
