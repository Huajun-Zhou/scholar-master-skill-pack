"""Design Research 工作流 — 9-agent 研究设计。

task_decomposer → scholar_mentor → method_mapper → thinking_model_agent
→ research_designer → evidence_auditor → risk_reviewer
→ revision_planner → final_writer
"""

from __future__ import annotations

from autogen_agentchat.teams import GraphFlow
from autogen_ext.models.openai import OpenAIChatCompletionClient

from ..agents import (
    build_evidence_auditor,
    build_final_writer,
    build_method_mapper,
    build_research_designer,
    build_revision_planner,
    build_risk_reviewer,
    build_scholar_mentor,
    build_task_decomposer,
    build_thinking_model_agent,
)
from ..graph_builders import linear_chain
from ..termination import make_termination


def build_design_research_flow(
    model_client: OpenAIChatCompletionClient | None = None,
) -> GraphFlow:
    """构建设计研究工作流 — 9-agent 完整科研设计管线。

    Agents:
        1. task_decomposer       — 拆解研究请求
        2. scholar_mentor        — 提取方法论指导
        3. method_mapper         — 匹配可迁移方法
        4. thinking_model_agent  — 应用思维模型
        5. research_designer     — 生成研究方案
        6. evidence_auditor      — A/B/C 证据审计
        7. risk_reviewer         — 审稿人风险模拟
        8. revision_planner      — 生成修改方案
        9. final_writer          — 输出最终报告
    """
    agents = [
        build_task_decomposer(model_client),
        build_scholar_mentor(model_client),
        build_method_mapper(model_client),
        build_thinking_model_agent(model_client),
        build_research_designer(model_client),
        build_evidence_auditor(model_client),
        build_risk_reviewer(model_client),
        build_revision_planner(model_client),
        build_final_writer(model_client),
    ]

    builder = linear_chain(agents)
    graph = builder.build()

    return GraphFlow(
        participants=builder.get_participants(),
        graph=graph,
        name="design_research",
        description="Design Research — 9-agent pipeline for publication-ready research design",
        termination_condition=make_termination(max_messages=120),
        max_turns=120,
    )
