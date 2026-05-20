"""消息过滤 — 解析和过滤 agent 消息。"""

from __future__ import annotations

from typing import Any


def is_tool_call(msg: Any) -> bool:
    """判断消息是否为工具调用。"""
    msg_type = getattr(msg, "type", "")
    return msg_type in ("ToolCallRequestEvent", "ToolCallExecutionEvent")


def is_text_message(msg: Any) -> bool:
    """判断消息是否为文本输出。"""
    msg_type = getattr(msg, "type", "")
    return msg_type in ("TextMessage", "AssistantMessage", "ThoughtEvent")


def get_message_content(msg: Any) -> str:
    """安全获取消息内容。"""
    if hasattr(msg, "content"):
        return str(msg.content)
    return str(msg)


def get_message_source(msg: Any) -> str:
    """获取消息来源 agent 名称。"""
    return getattr(msg, "source", "unknown")


def filter_agent_messages(messages: list[Any], source: str) -> list[str]:
    """提取指定 agent 的所有文本消息内容。"""
    return [
        get_message_content(m)
        for m in messages
        if is_text_message(m) and get_message_source(m) == source
    ]
