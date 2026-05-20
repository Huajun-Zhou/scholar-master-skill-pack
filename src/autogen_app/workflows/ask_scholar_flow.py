"""Ask Scholar 工作流 — 4-agent 问答。

task_decomposer → scholar_mentor → evidence_auditor → final_writer
"""

from __future__ import annotations

from autogen_agentchat.teams import GraphFlow
from autogen_ext.models.openai import OpenAIChatCompletionClient

from ..agents import (
    build_evidence_auditor,
    build_final_writer,
    build_scholar_mentor,
    build_task_decomposer,
)
from ..graph_builders import linear_chain
from ..termination import make_termination


def build_ask_scholar_flow(
    model_client: OpenAIChatCompletionClient | None = None,
) -> GraphFlow:
    """构建 Ask Scholar 工作流。

    Agents:
        task_decomposer (0 tools) → scholar_mentor (2 tools)
        → evidence_auditor (2 tools) → final_writer (1 tool)
    """
    agents = [
        build_task_decomposer(model_client),
        build_scholar_mentor(model_client),
        build_evidence_auditor(model_client),
        build_final_writer(model_client),
    ]

    builder = linear_chain(agents)
    graph = builder.build()

    return GraphFlow(
        participants=builder.get_participants(),
        graph=graph,
        name="ask_scholar",
        description="Ask Scholar — 4-agent Q&A with A/B/C evidence grading",
        termination_condition=make_termination(),
    )
