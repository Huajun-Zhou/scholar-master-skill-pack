"""跨页关系图构建（论文-概念-方法-实验-数据集）。

实现：Phase 4。Phase 0 占位。
完整版会引入 Neo4j 选项；MVP 在内存中构建邻接表。
"""
from __future__ import annotations

from typing import Any


def build_graph(papers: list[dict[str, Any]],
                concepts: list[dict[str, Any]]) -> dict[str, Any]:
    """构建邻接表 + 反向索引。Phase 4 实现。"""
    raise NotImplementedError("Phase 4 will implement build_graph().")
