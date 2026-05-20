"""学者委员会辩论引擎。

4 角色 × 3 轮辩论 × 严格工具隔离 × Round 2 并行执行

这是整个 AutoGen 升级中最核心的多智能体价值体现：
- 每个 agent 只能访问其角色限定的工具（信息不对称 → 真实分工）
- Round 2 两个 agent 并行执行（Evidence Inspector + Skeptic Reviewer 同时攻击）
- Methodologist 收到两份独立挑战后修订方案
- Synthesizer 整合完整辩论记录
"""

from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..output_parser import extract_agent_outputs, save_run_artifacts
from .agents import (
    build_evidence_inspector,
    build_methodologist,
    build_skeptic_reviewer,
    build_synthesizer,
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _generate_run_id() -> str:
    ts = _now_iso().replace(":", "").replace("-", "")[:15]
    return f"committee-{ts}"


async def _run_agent(agent, task: str, label: str = "") -> str:
    """运行单个 agent，返回其输出内容。"""
    print(f"  [{label or agent.name}] 执行中...")
    result = await agent.run(task=task)
    parts: list[str] = []
    for msg in result.messages:
        source = getattr(msg, "source", "")
        if source == agent.name:
            content = str(getattr(msg, "content", ""))
            if content:
                parts.append(content)
    output = "\n\n".join(parts)
    print(f"  [{label or agent.name}] 完成 ({len(output)} chars)")
    return output


async def run_committee(
    topic: str,
    target_journal: str = "",
    output_dir: str = "reports/autogen_runs",
    *,
    model_client=None,
) -> dict[str, Any]:
    """执行学者委员会辩论。

    返回:
        {run_id, proposal, audit, attack, revision, final_report, run_dir}
    """
    run_id = _generate_run_id()
    root = _find_project_root()
    run_dir = root / output_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n{'='*60}")
    print(f"  学者委员会 — 研究方案辩论")
    print(f"  run_id: {run_id}")
    print(f"  主题: {topic[:80]}")
    print(f"{'='*60}\n")

    # 保存输入
    (run_dir / "topic.txt").write_text(f"{topic}\n目标期刊: {target_journal}", encoding="utf-8")
    all_outputs: dict[str, str] = {}

    # ═══════════════════════════════════════════════════════════
    # Round 1: Methodologist 提出方案
    # ═══════════════════════════════════════════════════════════
    print("━" * 40)
    print("Round 1: Methodologist 提出研究方案")
    print("━" * 40)

    methodologist = build_methodologist(model_client)
    proposal_task = f"""请基于陈志远教授的方法论，为以下研究主题设计一个具体的研究方案。

研究主题: {topic}
目标期刊: {target_journal or '领域主流期刊'}

要求:
1. 使用 search_wiki_tool 查找相关研究范式和问题定义模式
2. 使用 get_method_cards_tool 查找可迁移的方法
3. 使用 get_thinking_models_tool 查找适用的思维模型
4. 输出完整的研究方案（问题框架→方法论→实验设计→预期贡献）
5. 每个主张标注你认为的证据等级（A/B/C）
6. 结束时标注 PROPOSAL_COMPLETE
"""
    proposal = await _run_agent(methodologist, proposal_task, "Methodologist")
    all_outputs["methodologist_proposal"] = proposal
    (run_dir / "01_proposal.md").write_text(proposal, encoding="utf-8")

    # ═══════════════════════════════════════════════════════════
    # Round 2: 并行执行 — Evidence Inspector + Skeptic Reviewer
    # ═══════════════════════════════════════════════════════════
    print("\n" + "━" * 40)
    print("Round 2: 并行挑战 — Evidence Inspector + Skeptic Reviewer")
    print("━" * 40)

    inspector = build_evidence_inspector(model_client)
    skeptic = build_skeptic_reviewer(model_client)

    audit_task = f"""请对以下研究方案进行严格的证据审计。

{proposal[:8000]}

逐条审计每个事实性主张，区分 A/B/C/Insufficient。
特别注意：Methodologist 可能错误标注了证据等级，你需要纠正。
标注 AUDIT_COMPLETE。
"""

    attack_task = f"""请以极度怀疑的审稿人身份，攻击以下研究方案。

{proposal[:8000]}

研究主题: {topic}
目标期刊: {target_journal or '顶级期刊'}

请从新颖性、方法论、实验设计、贡献夸大、发表可行性等维度进行全面攻击。
标注 ATTACK_COMPLETE。
"""

    # 并行执行！
    audit, attack = await asyncio.gather(
        _run_agent(inspector, audit_task, "Evidence Inspector"),
        _run_agent(skeptic, attack_task, "Skeptic Reviewer"),
    )

    all_outputs["evidence_inspector_audit"] = audit
    all_outputs["skeptic_reviewer_attack"] = attack
    (run_dir / "02a_evidence_audit.md").write_text(audit, encoding="utf-8")
    (run_dir / "02b_skeptic_attack.md").write_text(attack, encoding="utf-8")
    # model_client will be closed at the end of run_committee

    # ═══════════════════════════════════════════════════════════
    # Round 3: Methodologist 回应挑战并修订
    # ═══════════════════════════════════════════════════════════
    print("\n" + "━" * 40)
    print("Round 3: Methodologist 回应挑战并修订方案")
    print("━" * 40)

    methodologist2 = build_methodologist(model_client)
    revision_task = f"""你的研究方案收到了两份独立评估。请认真回应并修订你的方案。

## 你的原始方案
{proposal[:3000]}

## 证据检察官的审计报告
{audit[:4000]}

## 怀疑论审稿人的攻击报告
{attack[:4000]}

请逐条回应：
1. 证据审计中发现的错误标注 —— 你是否同意？如何修正？
2. 审稿人的每个攻击 —— 你是否接受？如何改进方案？
3. 修订后的最终方案（完整输出，不是增量补丁）
4. 哪些攻击你不同意？为什么？（这是你的"辩护权"）

标注 REVISION_COMPLETE。
"""
    revision = await _run_agent(methodologist2, revision_task, "Methodologist (revised)")
    all_outputs["methodologist_revision"] = revision
    (run_dir / "03_revision.md").write_text(revision, encoding="utf-8")

    # ═══════════════════════════════════════════════════════════
    # Round 4: Synthesizer 整合最终报告
    # ═══════════════════════════════════════════════════════════
    print("\n" + "━" * 40)
    print("Round 4: Synthesizer 整合最终报告")
    print("━" * 40)

    synthesizer = build_synthesizer(model_client)
    final_path = str(run_dir / "final_report.md")
    synthesize_task = f"""请整合以下学者委员会的全部辩论记录，生成最终报告。

## 原始方案 (Methodologist)
{proposal[:3000]}

## 证据审计 (Evidence Inspector)
{audit[:3000]}

## 审稿攻击 (Skeptic Reviewer)
{attack[:3000]}

## 修订方案 (Methodologist 回应)
{revision[:4000]}

研究主题: {topic}

使用 write_report_tool 将最终报告写入: {final_path}
必须包含 FINAL_REPORT 标记。
"""
    final_output = await _run_agent(synthesizer, synthesize_task, "Synthesizer")
    all_outputs["synthesizer_final"] = final_output
    (run_dir / "04_final_output.md").write_text(final_output, encoding="utf-8")

    # ═══════════════════════════════════════════════════════════
    # 保存元数据
    # ═══════════════════════════════════════════════════════════
    metadata = {
        "run_id": run_id,
        "topic": topic,
        "target_journal": target_journal,
        "architecture": "Scholar Committee — 4 roles × 3 debate rounds",
        "created_at": _now_iso(),
        "outputs": {
            k: len(v) for k, v in all_outputs.items()
        },
    }
    (run_dir / "metadata.json").write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2))

    # 生成摘要
    summary = _generate_summary(all_outputs)
    (run_dir / "summary.md").write_text(summary, encoding="utf-8")

    print(f"\n{'='*60}")
    print(f"  学者委员会辩论完成")
    print(f"  run_id: {run_id}")
    print(f"  Proposal: {len(proposal)} chars")
    print(f"  Audit: {len(audit)} chars")
    print(f"  Attack: {len(attack)} chars")
    print(f"  Revision: {len(revision)} chars")
    print(f"  输出: {run_dir}")
    print(f"{'='*60}\n")

    return {
        "run_id": run_id,
        "proposal": proposal,
        "audit": audit,
        "attack": attack,
        "revision": revision,
        "final_report": final_output,
        "run_dir": run_dir,
    }


def _generate_summary(outputs: dict[str, str]) -> str:
    """生成委员会辩论摘要。"""
    proposal_chars = len(outputs.get("methodologist_proposal", ""))
    audit_chars = len(outputs.get("evidence_inspector_audit", ""))
    attack_chars = len(outputs.get("skeptic_reviewer_attack", ""))
    revision_chars = len(outputs.get("methodologist_revision", ""))

    # 简单提取关键指标
    audit_text = outputs.get("evidence_inspector_audit", "")
    attack_text = outputs.get("skeptic_reviewer_attack", "")
    revision_text = outputs.get("methodologist_revision", "")

    audit_insufficient = audit_text.count("Insufficient") + audit_text.count("证据不足")
    attack_fatal = attack_text.count("致命")
    revision_accepted = revision_text.count("接受") + revision_text.count("同意")

    return f"""# 学者委员会辩论摘要

## 规模
- 原始方案: {proposal_chars:,} chars
- 证据审计: {audit_chars:,} chars
- 审稿攻击: {attack_chars:,} chars
- 修订方案: {revision_chars:,} chars
- 总产出: {sum(len(v) for v in outputs.values()):,} chars

## 关键指标
- 证据不足标记: {audit_insufficient} 处
- 致命攻击: {attack_fatal} 处
- 修订中接受的批评: {revision_accepted} 处
"""


def _find_project_root() -> Path:
    cur = Path(__file__).resolve().parent
    for p in [cur, *cur.parents]:
        if (p / "pyproject.toml").is_file() and (p / "CLAUDE.md").is_file():
            return p
    return cur.parent.parent
