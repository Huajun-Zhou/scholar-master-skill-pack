"""Source / Paper Registry 维护（jsonl，按 id upsert）。"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def _read_all(path: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        return []
    out: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                out.append(json.loads(line))
    return out


def _write_all(path: Path, records: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    with tmp.open("w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tmp.replace(path)


def upsert_source(registry_path: Path, record: dict[str, Any]) -> None:
    records = _read_all(registry_path)
    sid = record["source_id"]
    found = False
    for i, r in enumerate(records):
        if r.get("source_id") == sid:
            records[i] = {**r, **record}
            found = True
            break
    if not found:
        records.append(record)
    _write_all(registry_path, records)


def upsert_paper(registry_path: Path, record: dict[str, Any]) -> None:
    records = _read_all(registry_path)
    pid = record["paper_id"]
    found = False
    for i, r in enumerate(records):
        if r.get("paper_id") == pid:
            records[i] = {**r, **record}
            found = True
            break
    if not found:
        records.append(record)
    _write_all(registry_path, records)


def list_sources(registry_path: Path) -> list[dict[str, Any]]:
    return _read_all(registry_path)


def list_papers(registry_path: Path) -> list[dict[str, Any]]:
    return _read_all(registry_path)


def append_extraction_run(path: Path, record: dict[str, Any]) -> None:
    """extraction_runs.jsonl 是 append-only。"""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
