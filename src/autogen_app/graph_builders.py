"""DiGraph 构建工具 — 辅助构建 GraphFlow DAG。"""

from __future__ import annotations

from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.teams import DiGraphBuilder


def linear_chain(agents: list[AssistantAgent],
                 entry: str | None = None) -> DiGraphBuilder:
    """构建线性链 DAG: a0 → a1 → a2 → ... → an。

    参数:
        agents: 按顺序排列的 agent 列表
        entry: 入口 agent 名称（默认第一个）
    """
    builder = DiGraphBuilder()
    for agent in agents:
        builder.add_node(agent)

    for i in range(len(agents) - 1):
        builder.add_edge(agents[i].name, agents[i + 1].name)

    entry_name = entry or agents[0].name
    builder.set_entry_point(entry_name)

    return builder


def named_chain(
    builder: DiGraphBuilder,
    names: list[str],
    entry: str | None = None,
) -> DiGraphBuilder:
    """按名称串联 agent。

    参数:
        builder: 已有 DiGraphBuilder（agents 已 add_node）
        names: agent 名称列表，按顺序串联
        entry: 入口 agent 名称（默认第一个）
    """
    for i in range(len(names) - 1):
        builder.add_edge(names[i], names[i + 1])
    builder.set_entry_point(entry or names[0])
    return builder
