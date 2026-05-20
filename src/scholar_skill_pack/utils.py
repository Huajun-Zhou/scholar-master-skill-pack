"""通用工具：项目根定位、路径常量、stable id 生成。"""
from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Optional


def find_project_root(start: Path) -> Optional[Path]:
    """向上查找项目根（同时存在 pyproject.toml + CLAUDE.md）。"""
    cur = start.resolve()
    for p in [cur, *cur.parents]:
        if (p / "pyproject.toml").is_file() and (p / "CLAUDE.md").is_file():
            return p
    return None


def project_paths(root: Path) -> dict[str, Path]:
    """统一路径常量。"""
    return {
        "root": root,
        "raw_papers": root / "data/raw/papers",
        "pdf_text": root / "data/processed/pdf_text",
        "paper_sections": root / "data/processed/paper_sections",
        "chunks": root / "data/processed/chunks",
        "registry": root / "data/registry",
        "wiki": root / "wiki",
        "method_cards": root / "method_cards",
        "thinking_models": root / "thinking_models",
        "scholar_skill": root / "scholar_skill",
        "schemas": root / "schemas",
        "prompts": root / "prompts",
        "reports": root / "reports",
        "eval": root / "eval",
        "config": root / "config",
    }


def slugify(text: str, max_len: int = 60) -> str:
    """简单 slug 化：小写 + 连字符。保留 CJK。"""
    text = (text or "").strip().lower()
    text = re.sub(r"[^a-z0-9一-鿿\s\-]", "", text)
    text = re.sub(r"[\s_\-]+", "-", text)
    text = text.strip("-")
    if len(text) > max_len:
        text = text[:max_len].rstrip("-")
    return text or "untitled"


def stable_id(prefix: str, payload: str, length: int = 8) -> str:
    """基于内容哈希的稳定 id。"""
    h = hashlib.sha1(payload.encode("utf-8")).hexdigest()[:length].upper()
    return f"{prefix}_{h}"


def file_sha1(path: Path, chunk_size: int = 1 << 20) -> str:
    """文件 SHA1（流式，避免大文件占内存）。"""
    h = hashlib.sha1()
    with path.open("rb") as f:
        while True:
            buf = f.read(chunk_size)
            if not buf:
                break
            h.update(buf)
    return h.hexdigest()


def ensure_dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat(timespec="seconds")
