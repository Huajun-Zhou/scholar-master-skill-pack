"""模型客户端工厂 — 统一创建 AutoGen model client。"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml
from autogen_ext.models.openai import OpenAIChatCompletionClient


def _find_project_root() -> Path:
    cur = Path(__file__).resolve().parent
    for p in [cur, *cur.parents]:
        if (p / "pyproject.toml").is_file() and (p / "CLAUDE.md").is_file():
            return p
    return cur.parent.parent


def load_models_config() -> dict[str, Any]:
    root = _find_project_root()
    path = root / "config" / "models.yaml"
    if not path.is_file():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def build_model_client(
    model: str | None = None,
    temperature: float | None = None,
    *,
    api_key: str | None = None,
    base_url: str | None = None,
    **kwargs: Any,
) -> OpenAIChatCompletionClient:
    """创建 OpenAI 兼容的模型客户端。

    优先级: 参数 > config/models.yaml > 环境变量 > 默认值

    参数:
        model: 模型名称
        temperature: 温度参数
        api_key: API key（默认从 OPENAI_API_KEY 环境变量读取）
        base_url: API base URL（默认从 OPENAI_BASE_URL 环境变量读取）
    """
    config = load_models_config()
    default = config.get("default", {})

    resolved_model = model or os.getenv("SCHOLAR_MODEL") or default.get("model", "gpt-4.1")
    resolved_temp = temperature if temperature is not None else float(
        os.getenv("SCHOLAR_TEMPERATURE", str(default.get("temperature", 0.2)))
    )
    resolved_max_tokens = kwargs.pop("max_tokens", int(default.get("max_tokens", 8000)))
    resolved_api_key = api_key or os.getenv("OPENAI_API_KEY")
    resolved_base_url = base_url or os.getenv("OPENAI_BASE_URL")

    client_kwargs: dict[str, Any] = {
        "model": resolved_model,
        "temperature": resolved_temp,
        "max_tokens": resolved_max_tokens,
    }
    if resolved_api_key:
        client_kwargs["api_key"] = resolved_api_key
    if resolved_base_url:
        client_kwargs["base_url"] = resolved_base_url

    # 非 OpenAI 官方模型需要 model_info
    if resolved_base_url or not resolved_model.startswith(("gpt-", "o1", "o3", "o4")):
        client_kwargs["model_info"] = {
            "vision": False,
            "function_calling": True,
            "json_output": True,
            "family": "custom",
            "structured_output": True,
        }

    client_kwargs.update(kwargs)

    return OpenAIChatCompletionClient(**client_kwargs)
