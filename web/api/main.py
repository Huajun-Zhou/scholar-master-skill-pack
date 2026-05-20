"""FastAPI backend for the Scholar Skill Web UI.

Provides REST endpoints and SSE streaming chat over the Scholar Wiki,
Method Cards, Thinking Models, and Evidence Registry.
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import wiki as wiki_router
from routers import chat as chat_router

# ---------------------------------------------------------------------------
# Project root discovery
# ---------------------------------------------------------------------------

PROJECT_ROOT = Path(
    os.environ.get(
        "SCHOLAR_PROJECT_ROOT",
        Path(__file__).resolve().parent.parent.parent,  # web/../ = project root
    )
)
if not (PROJECT_ROOT / "wiki").is_dir():
    # fallback: walk up until we find wiki/
    for parent in Path(__file__).resolve().parents:
        if (parent / "wiki").is_dir():
            PROJECT_ROOT = parent
            break

# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------

app = FastAPI(
    title="Scholar Skill API",
    description="Backend API for the Academic Master Skill Pack Web UI",
    version="0.1.0",
)

# -- CORS ------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.environ.get("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -- State injection via middleware ----------------------------------------
@app.middleware("http")
async def inject_project_root(request, call_next):
    """Attach project root to request.state for downstream routers."""
    request.state.project_root = PROJECT_ROOT
    response = await call_next(request)
    return response


# -- Mount routers ----------------------------------------------------------
app.include_router(wiki_router.router)
app.include_router(chat_router.router)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------


@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "project_root": str(PROJECT_ROOT),
        "wiki_pages": len(list((PROJECT_ROOT / "wiki").rglob("*.md"))),
        "papers": len(list((PROJECT_ROOT / "wiki/papers").glob("*.md"))),
    }
