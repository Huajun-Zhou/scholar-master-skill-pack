"""Wiki and knowledge-base REST endpoints."""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request, Query

from services.content_loader import (
    load_all_methods,
    load_all_papers,
    load_all_thinking_models,
    load_evidence,
    load_method,
    load_paper,
    load_thinking_model,
    load_wiki_page,
    search_content,
)

router = APIRouter(prefix="/api", tags=["wiki"])


def _get_root(request: Request) -> Path:
    return request.state.project_root


# ---------------------------------------------------------------------------
# Wiki page
# ---------------------------------------------------------------------------


@router.get("/wiki/{path:path}")
async def get_wiki_page(path: str, request: Request):
    """Fetch a wiki page by relative path.

    Examples:
        ``/api/wiki/index``
        ``/api/wiki/papers/2023-depth-aware-...``
        ``/api/wiki/synthesis/research_lines``
    """
    root = _get_root(request)
    full_path = root / "wiki" / path
    try:
        page = load_wiki_page(str(full_path))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Wiki page not found: {path}")
    return page


# ---------------------------------------------------------------------------
# Papers
# ---------------------------------------------------------------------------


@router.get("/papers")
async def list_papers(request: Request):
    """List all paper cards with summary metadata."""
    root = _get_root(request)
    return {"papers": load_all_papers(root), "total": len(load_all_papers(root))}


@router.get("/papers/{paper_id:path}")
async def get_paper(paper_id: str, request: Request):
    """Fetch a full paper card by paper_id (e.g. ``PAPER_94163AE0``)."""
    root = _get_root(request)
    # paper_id might be passed with .md suffix; strip it
    paper_id = paper_id.removesuffix(".md")
    paper = load_paper(root, paper_id)
    if paper is None:
        # try treating the path as a filename
        fp = root / "wiki" / "papers" / f"{paper_id}.md"
        if fp.is_file():
            page = load_wiki_page(str(fp))
            return page
        raise HTTPException(status_code=404, detail=f"Paper not found: {paper_id}")
    return paper


# ---------------------------------------------------------------------------
# Methods
# ---------------------------------------------------------------------------


@router.get("/methods")
async def list_methods(request: Request):
    """List all method cards with summary metadata."""
    root = _get_root(request)
    return {"methods": load_all_methods(root), "total": len(load_all_methods(root))}


@router.get("/methods/{method_id:path}")
async def get_method(method_id: str, request: Request):
    """Fetch a full method card by method_id.

    The method_id is the filename stem (e.g. ``huber-function-robust-optimization``).
    """
    root = _get_root(request)
    method_id = method_id.removesuffix(".md")
    method = load_method(root, method_id)
    if method is None:
        raise HTTPException(status_code=404, detail=f"Method card not found: {method_id}")
    return method


# ---------------------------------------------------------------------------
# Thinking models
# ---------------------------------------------------------------------------


@router.get("/thinking-models")
async def list_thinking_models(request: Request):
    """List all thinking models with summary metadata."""
    root = _get_root(request)
    return {
        "thinking_models": load_all_thinking_models(root),
        "total": len(load_all_thinking_models(root)),
    }


@router.get("/thinking-models/{model_id:path}")
async def get_thinking_model(model_id: str, request: Request):
    """Fetch a full thinking model by model_id (filename stem)."""
    root = _get_root(request)
    model_id = model_id.removesuffix(".md")
    model = load_thinking_model(root, model_id)
    if model is None:
        raise HTTPException(
            status_code=404, detail=f"Thinking model not found: {model_id}"
        )
    return model


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


@router.get("/search")
async def search(request: Request, q: str = Query("", description="Search query")):
    """Full-text search across all wiki content."""
    root = _get_root(request)
    if not q.strip():
        return {"results": [], "query": q}
    results = search_content(root, q.strip())
    return {"results": results, "total": len(results), "query": q}


# ---------------------------------------------------------------------------
# Evidence
# ---------------------------------------------------------------------------


@router.get("/evidence/{evidence_id:path}")
async def get_evidence(evidence_id: str, request: Request):
    """Resolve an evidence ID to its source claim and context.

    Evidence IDs follow the format ``EVID-PAPER_XXXX-P{page}-C{chunk}``.
    """
    root = _get_root(request)
    evidence_id = evidence_id.strip()
    result = load_evidence(root, evidence_id)
    if result is None:
        raise HTTPException(
            status_code=404, detail=f"Evidence not found: {evidence_id}"
        )
    return result
