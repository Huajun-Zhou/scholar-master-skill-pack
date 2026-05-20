"""GET /api/wiki/*, /api/papers, /api/methods, /api/thinking-models — Wiki 内容服务。"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException
from starlette.responses import JSONResponse

router = APIRouter()

_root = Path(__file__).resolve().parent.parent.parent


def _read_md_frontmatter(path: Path) -> dict:
    """读取 Markdown 文件的 frontmatter 和 body。"""
    import yaml
    if not path.is_file():
        return {}
    raw = path.read_text(encoding="utf-8")
    fm = {}
    body = raw
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1]) or {}
            except Exception:
                pass
            body = parts[2].lstrip("\n")
    return {"frontmatter": fm, "body": body, "path": str(path.relative_to(_root))}


# ---- Papers ----

@router.get("/papers")
async def list_papers():
    """列出所有论文注册信息。"""
    reg_path = _root / "data" / "registry" / "paper_registry.jsonl"
    papers = _read_jsonl(reg_path)
    return [{
        "paper_id": p.get("paper_id", ""),
        "title": p.get("title", ""),
        "year": p.get("year"),
        "authors": p.get("authors", []),
        "venue": p.get("venue", ""),
        "n_pages": p.get("n_pages"),
    } for p in papers]


@router.get("/papers/{paper_id}")
async def get_paper(paper_id: str):
    """获取单篇论文的 Paper Card。"""
    wiki_papers = _root / "wiki" / "papers"
    for f in wiki_papers.glob("*.md"):
        page = _read_md_frontmatter(f)
        fm = page.get("frontmatter", {})
        src_papers = fm.get("source_papers", [])
        if paper_id in src_papers or paper_id in fm.get("page_id", ""):
            return page
    raise HTTPException(status_code=404, detail=f"Paper not found: {paper_id}")


# ---- Methods ----

@router.get("/methods")
async def list_methods():
    """列出所有方法卡片。"""
    cards_dir = _root / "method_cards" / "cards"
    methods = []
    for f in sorted(cards_dir.glob("*.md")):
        page = _read_md_frontmatter(f)
        fm = page.get("frontmatter", {})
        methods.append({
            "id": f.stem,
            "title": fm.get("title", f.stem),
            "source_papers": fm.get("source_papers", []),
            "path": str(f.relative_to(_root)),
        })
    return methods


@router.get("/methods/{method_id}")
async def get_method(method_id: str):
    """获取单张方法卡片。"""
    f = _root / "method_cards" / "cards" / f"{method_id}.md"
    if not f.is_file():
        raise HTTPException(status_code=404, detail=f"Method not found: {method_id}")
    return _read_md_frontmatter(f)


# ---- Thinking Models ----

@router.get("/thinking-models")
async def list_thinking_models():
    """列出所有思维模型。"""
    models_dir = _root / "thinking_models" / "models"
    models = []
    for f in sorted(models_dir.glob("*.md")):
        page = _read_md_frontmatter(f)
        fm = page.get("frontmatter", {})
        models.append({
            "id": f.stem,
            "title": fm.get("title", f.stem),
            "source_papers": fm.get("source_papers", []),
            "path": str(f.relative_to(_root)),
        })
    return models


@router.get("/thinking-models/{model_id}")
async def get_thinking_model(model_id: str):
    """获取单个思维模型。"""
    f = _root / "thinking_models" / "models" / f"{model_id}.md"
    if not f.is_file():
        raise HTTPException(status_code=404, detail=f"Model not found: {model_id}")
    return _read_md_frontmatter(f)


# ---- Wiki ----

@router.get("/wiki/index")
async def wiki_index():
    """获取 Wiki 首页。"""
    f = _root / "wiki" / "index.md"
    if not f.is_file():
        return {"error": "Wiki index not found"}
    return _read_md_frontmatter(f)


@router.get("/wiki/{path:path}")
async def wiki_page(path: str):
    """获取任意 Wiki 页面。"""
    f = _root / "wiki" / f"{path}.md"
    if not f.is_file():
        # 尝试直接路径
        f = _root / "wiki" / path
    if not f.is_file():
        raise HTTPException(status_code=404, detail=f"Wiki page not found: {path}")
    return _read_md_frontmatter(f)


# ---- Helpers ----

def _read_jsonl(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    records = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return records
