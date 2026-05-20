"""JSON Schema 校验。

包装 jsonschema，按 schemas/{name}.schema.json 校验对象。
实现：Phase 1。
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

SCHEMAS = {
    "paper_card", "evidence", "method_card",
    "thinking_model", "wiki_page", "qa_eval",
}


def validate(obj: dict[str, Any], schema_name: str, schemas_dir: Path) -> list[str]:
    """返回错误列表，空列表表示通过。Phase 1 实现。"""
    raise NotImplementedError("Phase 1 will implement validate().")
