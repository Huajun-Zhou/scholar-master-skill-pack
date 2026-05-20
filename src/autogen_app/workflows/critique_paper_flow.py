"""Critique Paper 工作流 — 7-agent 论文审查。

task_decomposer → scholar_mentor → risk_reviewer
→ evidence_auditor → revision_planner → final_writer
"""

from __future__ import annotations

from autogen_agentchat.teams import GraphFlow
from autogen_ext.models.openai import OpenAIChatCompletionClient

from ..agents import (
    build_evidence_auditor,
    build_final_writer,
    build_revision_planner,
    build_risk_reviewer,
    build_scholar_mentor,
    build_task_decomposer,
)
from ..graph_builders import linear_chain
from ..termination import make_termination


def build_critique_paper_flow(
    model_client: OpenAIChatCompletionClient | None = None,
) -> GraphFlow:
    """构建论文审查工作流 — 7-agent 论文审查管线。

    Agents:
        1. task_decomposer    — 拆解审查请求
        2. scholar_mentor     — 提供审查的方法论标准
        3. risk_reviewer      — 多维度审稿人风险分析
        4. evidence_auditor   — A/B/C 证据链审计
        5. revision_planner   — Must/Should/Optional 分类修改方案
        6. final_writer       — 输出审查报告
    """
    agents = [
        build_task_decomposer(model_client),
        build_scholar_mentor(model_client),
        build_risk_reviewer(model_client),
        build_evidence_auditor(model_client),
        build_revision_planner(model_client),
        build_final_writer(model_client),
    ]

    builder = linear_chain(agents)
    graph = builder.build()

    return GraphFlow(
        participants=builder.get_participants(),
        graph=graph,
        name="critique_paper",
        description="Critique Paper — 7-agent review pipeline using scholar's evidence standards",
        termination_condition=make_termination(max_messages=100),
        max_turns=100,
    )
