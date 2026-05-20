"""Evidence Ledger 操作。

evidence_id 格式：EVID-{paper_id}-P{page}-C{chunk}
实现：Phase 2。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def make_evidence_id(paper_id: str, page: int, chunk: int) -> str:
    return f"EVID-{paper_id}-P{page}-C{chunk:02d}"


def read_claims(claims_path: Path) -> list[dict[str, Any]]:
    """读取 wiki/claims/{paper_id}.jsonl。"""
    if not claims_path.is_file():
        return []
    claims: list[dict[str, Any]] = []
    with claims_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                claims.append(json.loads(line))
    return claims


def append_claim(claims_path: Path, claim: dict[str, Any]) -> None:
    """原子追加 claim 记录。"""
    claims_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = claims_path.with_suffix(claims_path.suffix + ".tmp")
    existing = read_claims(claims_path)
    existing.append(claim)
    with tmp.open("w", encoding="utf-8") as f:
        for c in existing:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    tmp.replace(claims_path)


def write_claims(claims_path: Path, claims: list[dict[str, Any]]) -> None:
    """全量写入 claims（原子替换）。"""
    claims_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = claims_path.with_suffix(claims_path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for c in claims:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    tmp.replace(claims_path)


def validate_claim(claim: dict[str, Any]) -> list[str]:
    """校验单条 claim 的必填字段，返回错误列表。"""
    errors: list[str] = []
    for key in ("claim_id", "claim", "claim_type", "evidence_ids"):
        if not claim.get(key):
            errors.append(f"缺少必填字段: {key}")
    if claim.get("claim_type") not in (
        "problem", "method", "experiment", "result", "limitation", "transfer"
    ):
        errors.append(f"无效 claim_type: {claim.get('claim_type')}")
    return errors


def claims_summary(claims_path: Path) -> dict[str, Any]:
    """统计 claims 文件的概况。"""
    claims = read_claims(claims_path)
    type_counts: dict[str, int] = {}
    level_counts: dict[str, int] = {"A": 0, "B": 0, "C": 0}
    for c in claims:
        type_counts[c.get("claim_type", "unknown")] = (
            type_counts.get(c.get("claim_type", "unknown"), 0) + 1
        )
        level = c.get("evidence_level", "C")
        level_counts[level] = level_counts.get(level, 0) + 1
    return {
        "total": len(claims),
        "by_type": type_counts,
        "by_level": level_counts,
        "a_coverage": round(level_counts["A"] / len(claims), 3) if claims else 0,
    }
