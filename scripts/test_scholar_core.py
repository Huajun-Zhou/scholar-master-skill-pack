#!/usr/bin/env python3
"""测试 Scholar Core 全部模块。"""

import sys
from pathlib import Path

# 确保 src 在路径中
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from scholar_core.retrieval import (
    list_all_method_card_names,
    list_all_papers,
    list_all_thinking_model_names,
    retrieve_evidence,
    retrieve_method_cards,
    retrieve_thinking_models,
    search_scholar_wiki,
)
from scholar_core.scholar_answer import ask_scholar
from scholar_core.research_design import design_research
from scholar_core.paper_review import critique_paper
from scholar_core.evidence_audit import audit_evidence
from scholar_core.artifact_writer import write_artifact
from scholar_core.run_logger import generate_run_id, log_run


def test_retrieval():
    print("=" * 60)
    print("TEST: Retrieval")
    print("=" * 60)

    # Wiki
    results = search_scholar_wiki("去噪 自适应 阈值")
    assert len(results) > 0, "Wiki search returned no results"
    print(f"  Wiki search: {len(results)} results ✓")

    # Method Cards
    cards = retrieve_method_cards("鲁棒 优化")
    assert len(cards) > 0, "Method cards returned no results"
    print(f"  Method cards: {len(cards)} results ✓")

    # Thinking Models
    models = retrieve_thinking_models("鲁棒 物理")
    assert len(models) > 0, "Thinking models returned no results"
    print(f"  Thinking models: {len(models)} results ✓")

    # Evidence
    evidence = retrieve_evidence()
    assert len(evidence) > 0, "Evidence returned no results"
    print(f"  Evidence: {len(evidence)} items ✓")

    # List all
    papers = list_all_papers()
    assert len(papers) == 23, f"Expected 23 papers, got {len(papers)}"
    print(f"  Papers: {len(papers)} ✓")

    card_names = list_all_method_card_names()
    assert len(card_names) == 7, f"Expected 7 method cards, got {len(card_names)}"
    print(f"  Method card names: {len(card_names)} ✓")

    model_names = list_all_thinking_model_names()
    assert len(model_names) == 6, f"Expected 6 thinking models, got {len(model_names)}"
    print(f"  Thinking model names: {len(model_names)} ✓")

    print()


def test_scholar_answer():
    print("=" * 60)
    print("TEST: Scholar Answer")
    print("=" * 60)

    answer = ask_scholar("如何基于陈志远教授的方法论提出高质量研究问题？")
    assert answer.question, "Missing question"
    assert answer.direct_answer, "Missing answer"
    assert len(answer.sources_used) > 0, "Missing sources"

    md = answer.to_markdown()
    assert "基于 Scholar Skill 的科研回答" in md, "Missing template header"
    assert answer.question in md, "Missing question in markdown"

    print(f"  Question: {answer.question[:50]}...")
    print(f"  Answer length: {len(answer.direct_answer)} chars")
    print(f"  Evidence items: {len(answer.evidence_items)}")
    print(f"  Sources used: {len(answer.sources_used)}")
    print(f"  Limitations: {len(answer.limitations)}")
    print(f"  Markdown length: {len(md)} chars")
    print("  ✓")
    print()


def test_research_design():
    print("=" * 60)
    print("TEST: Research Design")
    print("=" * 60)

    design = design_research("图像去噪中的自适应阈值策略", target_journal="TIP")
    assert design.topic, "Missing topic"
    assert len(design.method_mappings) > 0, "Missing method mappings"
    assert len(design.research_questions) > 0, "Missing research questions"

    md = design.to_markdown()
    assert "Research Design Report" in md, "Missing template header"
    assert design.topic in md, "Missing topic in markdown"

    print(f"  Topic: {design.topic}")
    print(f"  Journal: {design.target_journal}")
    print(f"  Method mappings: {len(design.method_mappings)}")
    print(f"  Research questions: {len(design.research_questions)}")
    print(f"  Pipeline steps: {len(design.method_pipeline)}")
    print(f"  Risks: {len(design.risks)}")
    print(f"  Markdown length: {len(md)} chars")
    print("  ✓")
    print()


def test_evidence_audit():
    print("=" * 60)
    print("TEST: Evidence Audit")
    print("=" * 60)

    # 测试一段有问题的文本
    text = """我们提出了一个全新的图像去噪方法，使用自适应阈值策略。
    该方法在理论上优于所有现有方法。实验证明，我们的方法在各种噪声条件下都达到了SOTA性能。
    陈志远教授明确提出了这个多智能体自动写论文的框架。"""

    audit = audit_evidence(text, strict=True)
    assert len(audit.claims) > 0, "No claims extracted"

    md = audit.to_markdown()
    assert "Evidence Audit" in md, "Missing template header"

    print(f"  Claims extracted: {len(audit.claims)}")
    print(f"  Pass gate: {audit.pass_gate}")
    print(f"  Unsupported major: {len(audit.unsupported_major_claims)}")
    print(f"  Warnings: {len(audit.warnings)}")
    print(f"  Summary: {audit.summary}")
    for c in audit.claims:
        print(f"    - [{c.evidence_level}] {c.claim[:60]}... (action={c.action})")
    print("  ✓")
    print()


def test_paper_review():
    print("=" * 60)
    print("TEST: Paper Review")
    print("=" * 60)

    # 使用 Phase 0 创建的示例论文
    sample_paper = Path(__file__).resolve().parent.parent / "reports" / "baseline" / "sample_paper_for_critique.md"
    if sample_paper.is_file():
        review = critique_paper(str(sample_paper), target_journal="TIP")
        assert review.overall_verdict, "Missing verdict"
        md = review.to_markdown()
        assert "Paper Critique Report" in md, "Missing template header"

        print(f"  Paper: {review.paper_title}")
        print(f"  Verdict: {review.overall_verdict[:80]}...")
        print(f"  Must fix: {len(review.must_fix)}")
        print(f"  Should fix: {len(review.should_fix)}")
        print(f"  Major risks: {len(review.major_risks)}")
        print(f"  Recommendation: {review.recommendation[:80]}...")
        print(f"  Markdown length: {len(md)} chars")
    else:
        print("  Sample paper not found, skipping")

    print("  ✓")
    print()


def test_run_logger():
    print("=" * 60)
    print("TEST: Run Logger")
    print("=" * 60)

    run_id = generate_run_id("test")
    run_dir = Path(__file__).resolve().parent.parent / "reports" / "autogen_runs"
    log_run(run_dir, run_id, {"test": True, "workflow": "test_scholar_core"})

    assert (run_dir / run_id / "metadata.json").is_file(), "Metadata not written"
    print(f"  Run ID: {run_id}")
    print(f"  Run dir: {run_dir / run_id}")
    print("  ✓")
    print()


def main():
    print()
    print("Schola Core — Full Test Suite")
    print("=" * 60)
    print()

    tests = [
        ("Retrieval", test_retrieval),
        ("Scholar Answer", test_scholar_answer),
        ("Research Design", test_research_design),
        ("Evidence Audit", test_evidence_audit),
        ("Paper Review", test_paper_review),
        ("Run Logger", test_run_logger),
    ]

    passed = 0
    failed = 0

    for name, test_fn in tests:
        try:
            test_fn()
            passed += 1
        except Exception as e:
            print(f"  FAIL: {name} — {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
