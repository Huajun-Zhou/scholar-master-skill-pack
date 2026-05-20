"""终止条件 — GraphFlow 工作流用。"""

from autogen_agentchat.conditions import TextMentionTermination, MaxMessageTermination

FINISH_MARKER = "FINAL_REPORT"


def make_termination(marker: str = FINISH_MARKER, max_messages: int = 80):
    """创建组合终止条件: 文本标记 或 消息数超限。"""
    return TextMentionTermination(marker) | MaxMessageTermination(max_messages)
