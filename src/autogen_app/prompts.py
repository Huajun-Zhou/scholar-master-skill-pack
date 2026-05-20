"""Agent Prompt 加载 — 从 prompts/ 目录读取 agent system message。"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from autogen_ext.models.openai import OpenAIChatCompletionClient


def _find_project_root() -> Path:
    cur = Path(__file__).resolve().parent
    for p in [cur, *cur.parents]:
        if (p / "pyproject.toml").is_file() and (p / "CLAUDE.md").is_file():
            return p
    return cur.parent.parent


def load_prompt(name: str) -> str:
    """读取 prompts/{name} 文件内容。"""
    root = _find_project_root()
    # 支持带或不带 .md 后缀
    filename = name if name.endswith(".md") else f"{name}.md"
    path = root / "prompts" / filename
    if not path.is_file():
        # fallback: 尝试以 agent name 查找
        path = root / "prompts" / f"{name}_agent.md"
    if not path.is_file():
        return f"[Prompt not found: {name}]"
    return path.read_text(encoding="utf-8").strip()


def load_global_policy() -> str:
    """加载全局策略（所有 agent 共享）。"""
    return load_prompt("global_policy")


def make_system_message(agent_name: str, extra: str = "") -> str:
    """组合全局策略 + agent prompt + 额外指令。"""
    parts = [load_global_policy(), "", "---", "", load_prompt(agent_name)]
    if extra:
        parts.extend(["", "---", "", extra])
    return "\n".join(parts)


def get_model_client(model: str | None = None,
                     temperature: float | None = None,
                     **kwargs: Any) -> OpenAIChatCompletionClient:
    """快捷方法：获取模型客户端。"""
    from autogen_app.model_clients import build_model_client
    return build_model_client(model=model, temperature=temperature, **kwargs)
