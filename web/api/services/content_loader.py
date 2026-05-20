"""Content loader — reads Markdown files from the Scholar Wiki disk.

All paths are resolved relative to PROJECT_ROOT (the repository root).
Uses the existing scholar_skill_pack.wiki_ops module for frontmatter parsing.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import markdown
import yaml

# Allow import from the project's src/ layout
PROJECT_ROOT_FALLBACK = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT_FALLBACK / "src"))

from scholar_skill_pack.wiki_ops import read_page  # noqa: E402

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

EVIDENCE_PATTERN = re.compile(r"EVID-\w+-\w+-\w+")
PAPER_ID_PATTERN = re.compile(r"PAPER_\w+")

SECTION_HEADING_RE = re.compile(r"^##\s+(.+)$", re.MULTILINE)


def _markdown_to_html(text: str) -> str:
    """Convert Markdown text to HTML."""
    return markdown.markdown(
        text,
        extensions=["fenced_code", "tables", "codehilite", "nl2br"],
    )


def _extract_toc(body: str) -> list[dict[str, Any]]:
    """Build a table-of-contents from ## headings in the Markdown body."""
    toc: list[dict[str, Any]] = []
    for match in SECTION_HEADING_RE.finditer(body):
        heading = match.group(1).strip()
        anchor = heading.lower().replace(" ", "-").replace("(", "").replace(")", "")
        toc.append({"title": heading, "anchor": anchor})
    return toc


def _extract_evidence_ids(text: str) -> list[str]:
    """Extract all evidence IDs from a text body."""
    return sorted(set(EVIDENCE_PATTERN.findall(text)))


def _extract_source_papers(frontmatter: dict[str, Any], body: str) -> list[str]:
    """Collect paper IDs from frontmatter and body text."""
    papers: set[str] = set()
    # from frontmatter
    sp = frontmatter.get("source_papers") or []
    if isinstance(sp, list):
        papers.update(sp)

    # from page_id
    pid = frontmatter.get("page_id", "")
    m = PAPER_ID_PATTERN.search(pid)
    if m:
        papers.add(m.group(0))

    # evidence IDs in body mention the paper
    for evid in _extract_evidence_ids(body):
        # EVID-PAPER_XXXX-P1-C001  => PAPER_XXXX
        parts = evid.split("-")
        if len(parts) >= 2:
            papers.add(parts[1])
    return sorted(papers)


# ===================================================================
# Wiki pages
# ===================================================================


def load_wiki_page(path: str, html: bool = True) -> dict[str, Any]:
    """Load and parse a wiki page by relative path (e.g. ``index`` or ``papers/2023-...``).

    Returns:
        {
            "frontmatter": {...},
            "body": "raw markdown",
            "html": "<converted html>" | None,
            "toc": [...],
            "evidence_ids": [...],
            "source_papers": [...],
            "path": "str",
        }
    """
    p = Path(path)
    if not p.is_file():
        # if path doesn't include .md, try appending it
        if p.suffix != ".md":
            p = p.with_suffix(".md")
    if not p.is_file():
        raise FileNotFoundError(f"Wiki page not found: {path}")

    page = read_page(p)
    body = page.get("body", "")
    result: dict[str, Any] = {
        "frontmatter": page.get("frontmatter", {}),
        "body": body,
        "html": _markdown_to_html(body) if html else None,
        "toc": _extract_toc(body),
        "evidence_ids": _extract_evidence_ids(body),
        "source_papers": _extract_source_papers(page.get("frontmatter", {}), body),
        "path": str(p),
    }
    return result


# ===================================================================
# Papers
# ===================================================================


def _iter_paper_files(root: Path) -> list[Path]:
    papers_dir = root / "wiki" / "papers"
    if not papers_dir.is_dir():
        return []
    return sorted(papers_dir.glob("*.md"))


def load_all_papers(root: Path) -> list[dict[str, Any]]:
    """Return a summary list of all paper cards."""
    summaries: list[dict[str, Any]] = []
    for fp in _iter_paper_files(root):
        try:
            pg = read_page(fp)
        except Exception:
            continue
        fm = pg.get("frontmatter", {})
        body = pg.get("body", "")
        paper_id = fm.get("source_papers", [""])[0] if fm.get("source_papers") else ""
        summaries.append(
            {
                "paper_id": paper_id,
                "page_id": fm.get("page_id", ""),
                "title": fm.get("title", fp.stem),
                "year": fm.get("paper_year"),
                "authors": fm.get("authors", []),
                "venue": fm.get("venue", ""),
                "status": fm.get("status", ""),
                "evidence_level": fm.get("evidence_level", ""),
                "evidence_ids": _extract_evidence_ids(body),
                "confidence": fm.get("confidence", ""),
                "char_count": len(body),
                "file": fp.name,
                "path": str(fp),
            }
        )
    # sort by year desc, then title
    summaries.sort(key=lambda c: (c["year"] or 0, c["title"]), reverse=True)
    return summaries


def load_paper(root: Path, paper_id: str) -> dict[str, Any] | None:
    """Load a full paper card by its paper_id (e.g. ``PAPER_94163AE0``)."""
    for fp in _iter_paper_files(root):
        try:
            pg = read_page(fp)
        except Exception:
            continue
        fm = pg.get("frontmatter", {})
        sp = fm.get("source_papers") or []
        if paper_id in sp or fm.get("page_id", "").endswith(paper_id):
            body = pg.get("body", "")
            return {
                "paper_id": paper_id,
                "page_id": fm.get("page_id", ""),
                "title": fm.get("title", fp.stem),
                "year": fm.get("paper_year"),
                "authors": fm.get("authors", []),
                "venue": fm.get("venue", ""),
                "frontmatter": fm,
                "body": body,
                "html": _markdown_to_html(body),
                "toc": _extract_toc(body),
                "evidence_ids": _extract_evidence_ids(body),
                "source_papers": _extract_source_papers(fm, body),
                "status": fm.get("status", ""),
                "confidence": fm.get("confidence", ""),
                "file": fp.name,
                "path": str(fp),
            }
    return None


# ===================================================================
# Method cards
# ===================================================================


def _iter_method_files(root: Path) -> list[Path]:
    methods_dir = root / "method_cards" / "cards"
    if not methods_dir.is_dir():
        return []
    return sorted(methods_dir.glob("*.md"))


def load_all_methods(root: Path) -> list[dict[str, Any]]:
    """Return a summary list of all method cards."""
    summaries: list[dict[str, Any]] = []
    for fp in _iter_method_files(root):
        try:
            pg = read_page(fp)
        except Exception:
            continue
        fm = pg.get("frontmatter", {})
        body = pg.get("body", "")
        summaries.append(
            {
                "method_id": fm.get("page_id", fp.stem).replace("method-card-", ""),
                "title": fm.get("title", fp.stem),
                "evidence_level": fm.get("evidence_level", ""),
                "source_papers": fm.get("source_papers", []),
                "evidence_ids": _extract_evidence_ids(body),
                "char_count": len(body),
                "file": fp.name,
                "path": str(fp),
            }
        )
    return summaries


def load_method(root: Path, method_id: str) -> dict[str, Any] | None:
    """Load a full method card by its method_id.

    The method_id is the filename stem (e.g. ``huber-function-robust-optimization``).
    Also matches by ``page_id`` prefix.
    """
    for fp in _iter_method_files(root):
        try:
            pg = read_page(fp)
        except Exception:
            continue
        fm = pg.get("frontmatter", {})
        pid = fm.get("page_id", "")
        if fp.stem == method_id or pid.endswith(method_id) or pid == f"method-card-{method_id}":
            body = pg.get("body", "")
            sections = _parse_12_sections(body)
            return {
                "method_id": method_id,
                "page_id": pid,
                "title": fm.get("title", fp.stem),
                "evidence_level": fm.get("evidence_level", ""),
                "source_papers": fm.get("source_papers", []),
                "frontmatter": fm,
                "body": body,
                "html": _markdown_to_html(body),
                "sections": sections,
                "evidence_ids": _extract_evidence_ids(body),
                "file": fp.name,
                "path": str(fp),
            }
    return None


def _parse_12_sections(body: str) -> list[dict[str, Any]]:
    """Parse a method card body into its 12 numbered sections.

    Returns a list of ``{"number": int, "title": str, "content": str}``.
    """
    sections: list[dict[str, Any]] = []
    pattern = re.compile(
        r"^##\s+(\d+)\.\s*(.+?)$\n(.*?)(?=^##\s+\d+\.|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    for m in pattern.finditer(body):
        sections.append(
            {
                "number": int(m.group(1)),
                "title": m.group(2).strip(),
                "content": m.group(3).strip(),
            }
        )
    return sections


# ===================================================================
# Thinking models
# ===================================================================


def _iter_model_files(root: Path) -> list[Path]:
    models_dir = root / "thinking_models" / "models"
    if not models_dir.is_dir():
        return []
    return sorted(models_dir.glob("*.md"))


def load_all_thinking_models(root: Path) -> list[dict[str, Any]]:
    """Return a summary list of all thinking models."""
    summaries: list[dict[str, Any]] = []
    for fp in _iter_model_files(root):
        try:
            pg = read_page(fp)
        except Exception:
            continue
        fm = pg.get("frontmatter", {})
        body = pg.get("body", "")
        summaries.append(
            {
                "model_id": fm.get("page_id", fp.stem).replace("thinking-model-", ""),
                "title": fm.get("title", fp.stem),
                "evidence_level": fm.get("evidence_level", ""),
                "source_papers": fm.get("source_papers", []),
                "confidence": fm.get("confidence", ""),
                "evidence_ids": _extract_evidence_ids(body),
                "char_count": len(body),
                "file": fp.name,
                "path": str(fp),
            }
        )
    return summaries


def load_thinking_model(root: Path, model_id: str) -> dict[str, Any] | None:
    """Load a full thinking model by its model_id (filename stem)."""
    for fp in _iter_model_files(root):
        try:
            pg = read_page(fp)
        except Exception:
            continue
        fm = pg.get("frontmatter", {})
        pid = fm.get("page_id", "")
        if fp.stem == model_id or pid.endswith(model_id) or pid == f"thinking-model-{model_id}":
            body = pg.get("body", "")
            return {
                "model_id": model_id,
                "page_id": pid,
                "title": fm.get("title", fp.stem),
                "evidence_level": fm.get("evidence_level", ""),
                "source_papers": fm.get("source_papers", []),
                "confidence": fm.get("confidence", ""),
                "frontmatter": fm,
                "body": body,
                "html": _markdown_to_html(body),
                "evidence_ids": _extract_evidence_ids(body),
                "file": fp.name,
                "path": str(fp),
            }
    return None


# ===================================================================
# Evidence
# ===================================================================


def load_evidence(root: Path, evidence_id: str) -> dict[str, Any] | None:
    """Resolve an evidence ID to its claim and supporting context.

    Evidence IDs are defined in ``wiki/claims/{paper_id}.jsonl`` files
    and within the body of paper cards / method cards.
    """
    # 1. Search claims files
    claims_dir = root / "wiki" / "claims"
    if claims_dir.is_dir():
        for claims_file in sorted(claims_dir.glob("*.jsonl")):
            try:
                for line in claims_file.read_text(encoding="utf-8").splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    record = json.loads(line)
                    rec_evidence_ids: list[str] = record.get("evidence_ids") or []
                    if evidence_id in rec_evidence_ids:
                        # Normalise claim fields (actual format uses ``text`` and ``id``)
                        return {
                            "evidence_id": evidence_id,
                            "source": "claims",
                            "claim": record.get("text") or record.get("claim", ""),
                            "claim_id": record.get("id", ""),
                            "claim_type": record.get("claim_type", ""),
                            "evidence_level": record.get("evidence_level", "C"),
                            "paper_id": record.get("paper_id", ""),
                            "section": record.get("section", ""),
                            "confidence": record.get("confidence", ""),
                            "detail": record,
                        }
            except Exception:
                continue

    # 2. Search paper card bodies for evidence anchor
    paper_id_match = re.match(r"EVID-(PAPER_\w+)", evidence_id)
    if paper_id_match:
        pid = paper_id_match.group(1)
        paper = load_paper(root, pid)
        if paper:
            body = paper.get("body", "")
            # find the paragraph that contains this evidence_id
            for para in body.split("\n\n"):
                if evidence_id in para:
                    return {
                        "evidence_id": evidence_id,
                        "source": "paper_card",
                        "paper_id": pid,
                        "paper_title": paper.get("title", ""),
                        "context": para.strip()[:500],
                        "full_paper": paper,
                    }

    # 3. Search method cards and thinking models
    for fp in list(_iter_method_files(root)) + list(_iter_model_files(root)):
        try:
            body = fp.read_text(encoding="utf-8")
            if evidence_id in body:
                for para in body.split("\n\n"):
                    if evidence_id in para:
                        return {
                            "evidence_id": evidence_id,
                            "source": "card",
                            "file": fp.name,
                            "context": para.strip()[:500],
                        }
        except Exception:
            continue

    return None


# ===================================================================
# Search
# ===================================================================


def search_content(root: Path, query: str, max_results: int = 20) -> list[dict[str, Any]]:
    """Full-text search across all wiki content, method cards, and thinking models.

    Returns ranked results with relevance snippets.
    """
    query_lower = query.lower()
    results: list[dict[str, Any]] = []

    # Collect all searchable files
    searchable: list[tuple[Path, str, str]] = []  # (path, category, label)

    # wiki pages (excluding papers subdir, handled separately)
    for fp in sorted((root / "wiki").rglob("*.md")):
        if "papers" in fp.parts:
            continue
        searchable.append((fp, "wiki", fp.stem))

    # paper cards
    for fp in _iter_paper_files(root):
        searchable.append((fp, "paper", fp.stem))

    # method cards
    for fp in _iter_method_files(root):
        searchable.append((fp, "method", fp.stem))

    # thinking models
    for fp in _iter_model_files(root):
        searchable.append((fp, "thinking_model", fp.stem))

    for fp, category, label in searchable:
        try:
            pg = read_page(fp)
        except Exception:
            continue
        body = pg.get("body", "")
        fm = pg.get("frontmatter", {})
        full_text = (yaml.dump(fm) if fm else "") + "\n" + body
        full_lower = full_text.lower()
        score = full_lower.count(query_lower)

        if score == 0:
            continue

        # extract a relevant snippet
        snippet = _find_snippet(body, query_lower)

        results.append(
            {
                "score": score,
                "category": category,
                "label": label,
                "title": fm.get("title", label),
                "path": str(fp),
                "snippet": snippet,
                "evidence_ids": _extract_evidence_ids(body),
            }
        )

    results.sort(key=lambda r: -r["score"])
    return results[:max_results]


def _find_snippet(body: str, query_lower: str, window: int = 120) -> str:
    """Extract a relevant text snippet around the first occurrence of query."""
    idx = body.lower().find(query_lower)
    if idx == -1:
        return body[:200]
    start = max(0, idx - window)
    end = min(len(body), idx + len(query_lower) + window)
    snippet = body[start:end]
    if start > 0:
        snippet = "..." + snippet
    if end < len(body):
        snippet = snippet + "..."
    return snippet


# Re-export json for evidence loading
import json  # noqa: E402, F811
