"""AutoGen Agent 工厂 — 9 个科研 agent。

每个 agent 有独立的 system_message、tools 和职责。
使用 AssistantAgent，遵循 global_policy + agent-specific prompt。
"""

from __future__ import annotations

from autogen_agentchat.agents import AssistantAgent
from autogen_ext.models.openai import OpenAIChatCompletionClient

from . import tools as at
from .prompts import make_system_message


def _client(model_client: OpenAIChatCompletionClient | None = None) -> OpenAIChatCompletionClient:
    """获取或创建默认 model_client。"""
    if model_client is not None:
        return model_client
    from .model_clients import build_model_client
    return build_model_client()


# ---- 9 Agent Factory Functions ----

def build_task_decomposer(
    model_client: OpenAIChatCompletionClient | None = None,
) -> AssistantAgent:
    """任务拆解 agent — 把用户请求拆成子任务，不执行。"""
    return AssistantAgent(
        name="task_decomposer",
        model_client=_client(model_client),
        system_message=make_system_message("task_decomposer_agent"),
        description="Decompose research requests into subtasks. Does not execute.",
    )


def build_scholar_mentor(
    model_client: OpenAIChatCompletionClient | None = None,
) -> AssistantAgent:
    """博导方法论 agent — 从 Scholar Wiki 提取方法论指导。"""
    return AssistantAgent(
        name="scholar_mentor",
        model_client=_client(model_client),
        tools=[at.search_wiki_tool, at.ask_scholar_tool],
        system_message=make_system_message("scholar_mentor_agent"),
        description="Extract methodological guidance from Scholar Wiki. "
                    "Uses search_wiki_tool and ask_scholar_tool.",
    )


def build_method_mapper(
    model_client: OpenAIChatCompletionClient | None = None,
) -> AssistantAgent:
    """方法映射 agent — 匹配可迁移方法卡片。"""
    return AssistantAgent(
        name="method_mapper",
        model_client=_client(model_client),
        tools=[at.get_method_cards_tool, at.search_wiki_tool],
        system_message=make_system_message("method_mapper_agent"),
        description="Map research topics to relevant Method Cards. "
                    "Uses get_method_cards_tool.",
    )


def build_thinking_model_agent(
    model_client: OpenAIChatCompletionClient | None = None,
) -> AssistantAgent:
    """思维模型 agent — 应用可迁移科研思维模型。"""
    return AssistantAgent(
        name="thinking_model_agent",
        model_client=_client(model_client),
        tools=[at.get_thinking_models_tool, at.search_wiki_tool],
        system_message=make_system_message("thinking_model_agent"),
        description="Apply transferable Thinking Models to research problems. "
                    "Uses get_thinking_models_tool.",
    )


def build_research_designer(
    model_client: OpenAIChatCompletionClient | None = None,
) -> AssistantAgent:
    """研究设计 agent — 生成发表级研究方案。"""
    return AssistantAgent(
        name="research_designer",
        model_client=_client(model_client),
        tools=[at.design_research_tool, at.ask_scholar_tool],
        system_message=make_system_message("research_designer_agent"),
        description="Design publication-ready research projects. "
                    "Uses design_research_tool and ask_scholar_tool.",
    )


def build_evidence_auditor(
    model_client: OpenAIChatCompletionClient | None = None,
) -> AssistantAgent:
    """证据审计 agent — 严格审查 A/B/C 证据等级。"""
    return AssistantAgent(
        name="evidence_auditor",
        model_client=_client(model_client),
        tools=[at.audit_evidence_tool, at.search_wiki_tool],
        system_message=make_system_message("evidence_auditor_agent"),
        description="Strict evidence auditor. Classifies claims as A/B/C/Insufficient. "
                    "Blocks unsupported major claims.",
    )


def build_risk_reviewer(
    model_client: OpenAIChatCompletionClient | None = None,
) -> AssistantAgent:
    """风险审稿 agent — 模拟审稿人挑问题。"""
    return AssistantAgent(
        name="risk_reviewer",
        model_client=_client(model_client),
        tools=[at.critique_paper_tool, at.ask_scholar_tool, at.search_wiki_tool],
        system_message=make_system_message("risk_reviewer_agent"),
        description="Strict academic reviewer simulating TPAMI/IJCV/ICLR standards. "
                    "Uses critique_paper_tool.",
    )


def build_revision_planner(
    model_client: OpenAIChatCompletionClient | None = None,
) -> AssistantAgent:
    """修改规划 agent — 整合审查意见，分类为 Must/Should/Optional。"""
    return AssistantAgent(
        name="revision_planner",
        model_client=_client(model_client),
        tools=[at.ask_scholar_tool, at.search_wiki_tool],
        system_message=make_system_message("revision_planner_agent"),
        description="Convert auditor/reviewer feedback into actionable revision plans. "
                    "Classifies fixes as Must/Should/Optional.",
    )


def build_final_writer(
    model_client: OpenAIChatCompletionClient | None = None,
) -> AssistantAgent:
    """最终报告 agent — 合成所有上游输出为最终报告。"""
    return AssistantAgent(
        name="final_writer",
        model_client=_client(model_client),
        tools=[at.write_report_tool],
        system_message=make_system_message("final_writer_agent"),
        description="Synthesize all upstream outputs into final Markdown report. "
                    "Uses write_report_tool. Must end with FINAL_REPORT.",
    )


# ---- 便捷方法：按名称构建 ----

AGENT_BUILDERS = {
    "task_decomposer": build_task_decomposer,
    "scholar_mentor": build_scholar_mentor,
    "method_mapper": build_method_mapper,
    "thinking_model_agent": build_thinking_model_agent,
    "research_designer": build_research_designer,
    "evidence_auditor": build_evidence_auditor,
    "risk_reviewer": build_risk_reviewer,
    "revision_planner": build_revision_planner,
    "final_writer": build_final_writer,
}


def build_agent(name: str, model_client: OpenAIChatCompletionClient | None = None) -> AssistantAgent:
    """按名称构建单个 agent。"""
    builder = AGENT_BUILDERS.get(name)
    if builder is None:
        raise ValueError(f"Unknown agent: {name}. Available: {list(AGENT_BUILDERS.keys())}")
    return builder(model_client=model_client)


def build_all_agents(model_client: OpenAIChatCompletionClient | None = None) -> dict[str, AssistantAgent]:
    """构建全部 9 个 agent。"""
    client = _client(model_client)
    return {name: build(client) for name, build in AGENT_BUILDERS.items()}
