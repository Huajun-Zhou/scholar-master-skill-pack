"""GET /api/search — 全局搜索。"""

from __future__ import annotations

from fastapi import APIRouter, Query

from scholar_core.retrieval import (
    retrieve_method_cards,
    retrieve_thinking_models,
    search_scholar_wiki,
)

router = APIRouter()


@router.get("/search")
async def global_search(q: str = Query(..., description="搜索关键词"), top_k: int = 10):
    """跨 Wiki、方法卡片、思维模型全局搜索。"""
    wiki = search_scholar_wiki(q, top_k=top_k)
    methods = retrieve_method_cards(q, top_k=5)
    models = retrieve_thinking_models(q, top_k=5)

    results = []

    for w in wiki[:5]:
        results.append({
            "type": "wiki",
            "id": w.page_id,
            "title": w.title,
            "snippet": w.content[:200],
            "path": w.path,
            "evidence_level": w.evidence_level,
        })

    for m in methods[:3]:
        results.append({
            "type": "method",
            "id": m.name,
            "title": m.name,
            "snippet": m.definition[:200],
            "path": m.path,
            "source_papers": m.source_papers,
        })

    for m in models[:2]:
        results.append({
            "type": "model",
            "id": m.name,
            "title": m.name,
            "snippet": m.description[:200],
            "path": m.path,
        })

    return {"query": q, "results": results, "total": len(results)}
