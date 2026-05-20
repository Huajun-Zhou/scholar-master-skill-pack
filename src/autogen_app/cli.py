"""CLI 入口 — scholar-ask / scholar-design / scholar-critique。

用法:
    scholar-ask "如何提出高质量研究问题？"
    scholar-design "图像去噪自适应阈值" --target-journal TIP
    scholar-critique drafts/my_paper.md --target-journal TPAMI
"""

from __future__ import annotations

import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .model_clients import build_model_client
from .output_parser import extract_agent_outputs, save_run_artifacts
from .workflows.ask_scholar_flow import build_ask_scholar_flow
from .workflows.critique_paper_flow import build_critique_paper_flow
from .workflows.design_research_flow import build_design_research_flow


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _generate_run_id(workflow: str) -> str:
    ts = _now_iso().replace(":", "").replace("-", "")[:15]
    return f"{workflow}-{ts}"


def _find_project_root() -> Path:
    cur = Path(__file__).resolve().parent
    for p in [cur, *cur.parents]:
        if (p / "pyproject.toml").is_file() and (p / "CLAUDE.md").is_file():
            return p
    return cur.parent.parent


async def _run_workflow(flow, task: str, run_id: str, output_dir: str,
                        workflow_name: str, *, enable_gate: bool = True,
                        **meta) -> int:
    """通用工作流执行器 — 顺序执行每个 agent，支持证据门禁和自动重试。

    参数:
        run_id: 如果为空字符串，自动生成
        output_dir: 如果以 / 开头，视为绝对路径；否则相对于项目根
    """
    root = _find_project_root()
    if not run_id:
        run_id = _generate_run_id(workflow_name)
    # output_dir 支持绝对路径和相对路径
    out_path = Path(output_dir)
    if not out_path.is_absolute():
        out_path = root / output_dir
    run_dir = out_path / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # 保存输入
    (run_dir / "input.md").write_text(f"# {workflow_name} Input\n\n{task}", encoding="utf-8")

    # 加载门禁配置
    from .evidence_gate import check_gate, load_gate_rules
    gate_rules = load_gate_rules()
    max_retries = gate_rules.get("max_retries", 2) if enable_gate else 0

    # 获取所有 participant agents（按顺序）
    agents = list(flow._participants)
    print(f"[{workflow_name}] 启动...")
    print(f"  run_id: {run_id}")
    print(f"  agents: {[a.name for a in agents]}")
    if enable_gate:
        print(f"  evidence gate: enabled (max_retries={max_retries})")

    all_messages: list[Any] = []
    agent_outputs: dict[str, str] = {}
    gate_history: list[dict[str, Any]] = []
    final_passed = True

    for attempt in range(max_retries + 1):
        if attempt > 0:
            print(f"\n  [GATE] 第 {attempt}/{max_retries} 次重试...")

        agent_outputs = {}

        # 第一个 agent 接收完整 task
        current_input = task

        for i, agent in enumerate(agents):
            agent_name = agent.name
            print(f"  [{i+1}/{len(agents)}] {agent_name} 执行中...")

            try:
                result = await agent.run(task=current_input)
                messages = result.messages

                # 提取该 agent 的输出
                agent_content_parts: list[str] = []
                for msg in messages:
                    source = getattr(msg, "source", "")
                    if source == agent_name:
                        content = str(getattr(msg, "content", ""))
                        if content:
                            agent_content_parts.append(content)
                    all_messages.append(msg)

                agent_output = "\n\n".join(agent_content_parts)
                agent_outputs[agent_name] = agent_output

                # 保存到文件
                (run_dir / f"{agent_name}.md").write_text(agent_output, encoding="utf-8")

                # 只有 final_writer 输出 FINAL_REPORT 才算完成
                if agent_name == "final_writer" and "FINAL_REPORT" in agent_output:
                    print(f"    → 最终报告已生成")

                # 将当前 agent 的输出传递给下一个 agent
                if agent_output:
                    current_input = (
                        f"上一阶段 ({agent_name}) 的输出如下。请根据你的角色和工具，继续完成你的部分：\n\n"
                        f"---\n{agent_output[:5000]}\n---\n\n"
                        f"原始任务: {task[:1000]}"
                    )
                else:
                    current_input = f"请根据你的角色和工具执行任务。\n原始任务: {task[:1000]}"

            except Exception as e:
                print(f"    → 错误: {e}")
                (run_dir / f"{agent_name}.md").write_text(
                    f"执行失败: {e}", encoding="utf-8")
                agent_outputs[agent_name] = f"ERROR: {e}"

        # Gate 检查
        if enable_gate and "evidence_auditor" in agent_outputs:
            auditor_output = agent_outputs["evidence_auditor"]
            if auditor_output and "ERROR" not in auditor_output:
                gate = check_gate(auditor_output)
                gate_history.append({
                    "attempt": attempt,
                    "passed": gate.passed,
                    "unsupported": gate.unsupported_claims,
                    "warnings": gate.warnings,
                })

                if gate.passed:
                    print(f"  [GATE] 通过 ✓ — {gate.summary}")
                    final_passed = True
                    break
                else:
                    print(f"  [GATE] 未通过 ✗ — {gate.summary}")
                    final_passed = False
                    if attempt < max_retries:
                        feedback = _format_gate_task_feedback(gate)
                        task = f"{task}\n\n{feedback}"
            else:
                break  # 没有 evidence_auditor 或出错，跳过 gate
        else:
            break  # 没有 gate 或没有 auditor

    # 保存元数据
    import json
    saved: list[Path] = []
    for f in sorted(run_dir.iterdir()):
        if f.is_file():
            saved.append(f)

    (run_dir / "metadata.json").write_text(json.dumps({
        "run_id": run_id,
        "workflow": workflow_name,
        "task": task[:200],
        "created_at": _now_iso(),
        "n_messages": len(all_messages),
        "agents_responded": list(agent_outputs.keys()),
        "gate_enabled": enable_gate,
        "gate_passed": final_passed,
        "gate_history": gate_history,
        **meta,
    }, ensure_ascii=False, indent=2))

    if gate_history:
        (run_dir / "gate_history.json").write_text(
            json.dumps(gate_history, ensure_ascii=False, indent=2))

    has_final = any("FINAL_REPORT" in agent_outputs.get(a, "") for a in agent_outputs)

    print(f"\n[{workflow_name}] 执行完成:")
    print(f"  文件数: {len(saved)}")
    print(f"  Agent 响应: {list(agent_outputs.keys())}")
    print(f"  FINAL_REPORT: {'✓' if has_final else '✗'}")
    if enable_gate:
        print(f"  Evidence Gate: {'✓ 通过' if final_passed else '✗ 未通过'}")

    return 0


def _format_gate_task_feedback(gate) -> str:
    """将门禁结果格式化为 agent 修正指令。"""
    lines = [
        "",
        "---",
        "## [EVIDENCE GATE FEEDBACK — 上一轮未通过，请修正]",
        "",
        f"**问题**: {gate.summary}",
    ]
    if gate.unsupported_claims:
        lines.append("")
        lines.append("### 必须修复的无证据主张")
        for c in gate.unsupported_claims:
            lines.append(f"- 移除或添加证据支撑: {c[:100]}")
    if gate.warnings:
        lines.append("")
        lines.append("### 需要关注的警告")
        for w in gate.warnings:
            lines.append(f"- {w}")
    if gate.required_actions:
        lines.append("")
        lines.append("### 必须执行的操作")
        for i, action in enumerate(gate.required_actions, 1):
            lines.append(f"{i}. {action}")
    lines.append("")
    lines.append("请根据以上反馈修正后重新生成。所有输出必须保持 A/B/C 证据标记。")
    lines.append("")
    return "\n".join(lines)


# ---- CLI 命令 ----

async def ask(question: str, *, output_dir: str = "reports/autogen_runs",
              run_id: str = "", model: str | None = None,
              temperature: float | None = None) -> int:
    """运行 ask_scholar 工作流。"""
    client = build_model_client(model=model, temperature=temperature)
    flow = build_ask_scholar_flow(model_client=client)

    task = f"""
请回答以下科研问题，严格区分 A/B/C 三类证据:

{question}

要求:
1. 使用 search_wiki_tool 和 ask_scholar_tool 获取知识
2. 所有重要结论必须标注 A/B/C 证据等级
3. 不确定的内容写"证据不足"
4. 最后使用 write_report_tool 将完整报告写入 {output_dir}/{run_id}/final_report.md
5. 报告末尾必须包含 FINAL_REPORT
"""
    code = await _run_workflow(flow, task, run_id, output_dir, "ask_scholar",
                               question=question, model=model)
    await client.close()
    return code


async def design(topic: str, *, target_journal: str = "",
                 output_dir: str = "reports/autogen_runs",
                 run_id: str = "", model: str | None = None,
                 temperature: float | None = None) -> int:
    """运行 design_research 工作流。"""
    client = build_model_client(model=model, temperature=temperature)
    flow = build_design_research_flow(model_client=client)

    task = f"""
请基于陈志远教授的方法论，为以下研究主题设计一个完整的发表级研究方案。

研究主题: {topic}
目标期刊: {target_journal or '领域主流期刊'}

流程要求:
1. task_decomposer: 拆解研究请求
2. scholar_mentor: 使用 search_wiki_tool 和 ask_scholar_tool 提取相关方法论
3. method_mapper: 使用 get_method_cards_tool 匹配可迁移方法
4. thinking_model_agent: 使用 get_thinking_models_tool 应用思维模型
5. research_designer: 使用 design_research_tool 生成研究方案
6. evidence_auditor: 使用 audit_evidence_tool 审计所有 claims 的证据等级
7. risk_reviewer: 使用 critique_paper_tool 模拟审稿人风险
8. revision_planner: 分类修改建议为 Must/Should/Optional
9. final_writer: 使用 write_report_tool 将最终报告写入 {output_dir}/{run_id}/final_report.md

所有输出必须保留 A/B/C 证据标记。报告末尾必须包含 FINAL_REPORT。
"""
    code = await _run_workflow(flow, task, run_id, output_dir, "design_research",
                               topic=topic, target_journal=target_journal, model=model)
    await client.close()
    return code


async def critique(paper_path: str, *, target_journal: str = "",
                   output_dir: str = "reports/autogen_runs",
                   run_id: str = "", model: str | None = None,
                   temperature: float | None = None) -> int:
    """运行 critique_paper 工作流。"""
    client = build_model_client(model=model, temperature=temperature)
    flow = build_critique_paper_flow(model_client=client)

    task = f"""
请按陈志远教授公开成果中体现的证据标准与研究范式，审查以下论文草稿。

论文路径: {paper_path}
目标期刊: {target_journal or '领域主流期刊'}

审查维度:
1. 问题定义质量 — 是否存在可挑战的隐含假设 gap
2. 方法设计 — 是否有理论分析/数学推导支撑
3. 证据链完整性 — 是否包含4层消融（必要性→替代方案→参数敏感性→极限测试）
4. 贡献清晰度 — 是否有"首次"定位和完整的问题-理论-方法-实验闭环
5. 局限性诚实度 — 是否讨论了方法的边界和失效条件

流程:
1. task_decomposer: 拆解审查请求
2. scholar_mentor: 使用 search_wiki_tool 获取审查标准
3. risk_reviewer: 使用 critique_paper_tool 执行多维度审查
4. evidence_auditor: 使用 audit_evidence_tool 审计论文的 claims
5. revision_planner: 分类为 Must Fix / Should Fix / Optional
6. final_writer: 使用 write_report_tool 将审查报告写入 {output_dir}/{run_id}/final_report.md

所有批评建议必须附方法论来源。分类使用 Must Fix / Should Fix / Optional / Evidence Insufficient。
报告末尾必须包含 FINAL_REPORT。
"""
    code = await _run_workflow(flow, task, run_id, output_dir, "critique_paper",
                               paper_path=paper_path, target_journal=target_journal, model=model)
    await client.close()
    return code


async def run_committee_cli(topic: str, *, target_journal: str = "",
                           output_dir: str = "reports/autogen_runs",
                           model: str | None = None,
                           temperature: float | None = None) -> int:
    """Run scholar committee debate."""
    from .model_clients import build_model_client
    from .committee.debate import run_committee

    client = build_model_client(model=model, temperature=temperature)
    try:
        result = await run_committee(
            topic=topic,
            target_journal=target_journal,
            output_dir=output_dir,
            model_client=client,
        )
        print(f"Report: {result['run_dir']}/final_report.md")
        return 0
    finally:
        await client.close()


# ---- CLI entry point ----

def main():
    """CLI 主入口 — 由 pyproject.toml [project.scripts] 调用。"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Academic Master Skill Pack — AutoGen Workflow CLI",
        prog="scholar",
    )
    subparsers = parser.add_subparsers(dest="command", help="工作流命令")

    # scholar-ask
    ask_parser = subparsers.add_parser("ask", help="向 Scholar Skill 提问")
    ask_parser.add_argument("question", help="科研问题")
    ask_parser.add_argument("--output-dir", default="reports/autogen_runs")
    ask_parser.add_argument("--run-id", default="")
    ask_parser.add_argument("--model", default=None)
    ask_parser.add_argument("--temperature", type=float, default=None)

    # scholar-design
    design_parser = subparsers.add_parser("design", help="生成研究设计方案")
    design_parser.add_argument("topic", help="研究主题")
    design_parser.add_argument("--target-journal", default="")
    design_parser.add_argument("--output-dir", default="reports/autogen_runs")
    design_parser.add_argument("--run-id", default="")
    design_parser.add_argument("--model", default=None)
    design_parser.add_argument("--temperature", type=float, default=None)

    # scholar-critique
    critique_parser = subparsers.add_parser("critique", help="审查论文")
    critique_parser.add_argument("paper_path", help="论文草稿路径")
    critique_parser.add_argument("--target-journal", default="")
    critique_parser.add_argument("--output-dir", default="reports/autogen_runs")
    critique_parser.add_argument("--run-id", default="")
    critique_parser.add_argument("--model", default=None)
    critique_parser.add_argument("--temperature", type=float, default=None)

    # scholar-committee (学者委员会)
    cmt_parser = subparsers.add_parser("committee", help="学者委员会辩论 (4角色x3轮)")
    cmt_parser.add_argument("topic", help="研究主题")
    cmt_parser.add_argument("--target-journal", default="")
    cmt_parser.add_argument("--output-dir", default="reports/autogen_runs")
    cmt_parser.add_argument("--model", default=None)
    cmt_parser.add_argument("--temperature", type=float, default=None)

    args = parser.parse_args()

    if args.command == "ask":
        code = asyncio.run(ask(
            args.question,
            output_dir=args.output_dir,
            run_id=args.run_id,
            model=args.model,
            temperature=args.temperature,
        ))
    elif args.command == "design":
        code = asyncio.run(design(
            args.topic,
            target_journal=args.target_journal,
            output_dir=args.output_dir,
            run_id=args.run_id,
            model=args.model,
            temperature=args.temperature,
        ))
    elif args.command == "critique":
        code = asyncio.run(critique(
            args.paper_path,
            target_journal=args.target_journal,
            output_dir=args.output_dir,
            run_id=args.run_id,
            model=args.model,
            temperature=args.temperature,
        ))
    elif args.command == "committee":
        code = asyncio.run(run_committee_cli(
            args.topic,
            target_journal=args.target_journal,
            output_dir=args.output_dir,
            model=args.model,
            temperature=args.temperature,
        ))
    else:
        parser.print_help()
        code = 1

    sys.exit(code)


if __name__ == "__main__":
    main()
