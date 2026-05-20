"""输出解析 — 从 agent 消息中提取结构化内容。"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def extract_final_report(messages: list[Any]) -> str:
    """从消息列表中提取包含 FINAL_REPORT 标记的消息内容。"""
    for msg in reversed(messages):
        content = str(msg) if not hasattr(msg, "content") else str(msg.content)
        if "FINAL_REPORT" in content:
            return content
    # fallback: 返回最后一条消息
    if messages:
        last = messages[-1]
        return str(last) if not hasattr(last, "content") else str(last.content)
    return ""


def extract_agent_outputs(messages: list[Any]) -> dict[str, str]:
    """按 agent 分组提取输出。

    返回: {agent_name: content}
    """
    outputs: dict[str, str] = {}
    for msg in messages:
        source = getattr(msg, "source", "unknown")
        content = str(getattr(msg, "content", ""))
        if source not in outputs:
            outputs[source] = content
        else:
            outputs[source] = outputs[source] + "\n\n" + content
    return outputs


def save_run_artifacts(run_dir: Path, agent_outputs: dict[str, str],
                       metadata: dict[str, Any]) -> list[Path]:
    """将 agent 输出保存为独立文件。

    返回: 写入的文件路径列表
    """
    run_dir.mkdir(parents=True, exist_ok=True)
    saved: list[Path] = []

    # 保存每个 agent 的输出
    for agent_name, content in agent_outputs.items():
        safe_name = re.sub(r"[^\w\-]", "_", agent_name)
        path = run_dir / f"{safe_name}.md"
        path.write_text(content, encoding="utf-8")
        saved.append(path)

    # 保存 metadata
    meta_path = run_dir / "metadata.json"
    with meta_path.open("w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    saved.append(meta_path)

    return saved
