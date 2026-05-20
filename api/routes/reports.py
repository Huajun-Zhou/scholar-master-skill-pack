"""GET /api/reports — 运行报告列表与详情。"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()

_run_dir = Path(__file__).resolve().parent.parent.parent / "reports" / "autogen_runs"


@router.get("/reports")
async def list_reports():
    """列出所有历史运行报告。"""
    if not _run_dir.is_dir():
        return {"reports": []}

    items = []
    for run_path in sorted(_run_dir.iterdir(), key=lambda p: p.name, reverse=True):
        if not run_path.is_dir():
            continue
        meta_path = run_path / "metadata.json"
        meta = {}
        if meta_path.is_file():
            try:
                meta = json.loads(meta_path.read_text())
            except Exception:
                pass

        items.append({
            "run_id": run_path.name,
            "workflow": meta.get("workflow", "unknown"),
            "created_at": meta.get("created_at", ""),
            "n_messages": meta.get("n_messages", 0),
            "agents_responded": meta.get("agents_responded", []),
            "gate_passed": meta.get("gate_passed", None),
            "gate_history": meta.get("gate_history", []),
        })

    return {"reports": items}


@router.get("/reports/{run_id}")
async def get_report(run_id: str):
    """获取单次运行的完整报告。"""
    run_path = _run_dir / run_id
    if not run_path.is_dir():
        raise HTTPException(status_code=404, detail=f"Report not found: {run_id}")

    result: dict = {
        "run_id": run_id,
        "artifacts": {},
        "agent_conversation": [],
    }

    # 读取所有产物文件
    for f in sorted(run_path.iterdir()):
        if f.suffix == ".md" and f.name != "input.md":
            result["artifacts"][f.stem] = f.read_text()
        elif f.suffix == ".json" and f.name != "metadata.json":
            try:
                result["artifacts"][f.stem] = json.loads(f.read_text())
            except Exception:
                pass

    # 元数据
    meta_path = run_path / "metadata.json"
    if meta_path.is_file():
        result["metadata"] = json.loads(meta_path.read_text())

    # 构建 agent 对话 — 支持 committee 和 legacy 两种文件命名
    agent_files: list[tuple[str, str]] = [
        # Committee files
        ("methodologist", "01_proposal.md"),
        ("evidence_inspector", "02a_evidence_audit.md"),
        ("skeptic_reviewer", "02b_skeptic_attack.md"),
        ("methodologist", "03_revision.md"),
        ("synthesizer", "04_final_output.md"),
        # Legacy pipeline files
        ("task_decomposer", "task_decomposer.md"),
        ("scholar_mentor", "scholar_mentor.md"),
        ("method_mapper", "method_mapper.md"),
        ("thinking_model_agent", "thinking_model_agent.md"),
        ("research_designer", "research_designer.md"),
        ("evidence_auditor", "evidence_auditor.md"),
        ("risk_reviewer", "risk_reviewer.md"),
        ("revision_planner", "revision_planner.md"),
        ("final_writer", "final_writer.md"),
    ]

    for agent_name, filename in agent_files:
        fpath = run_path / filename
        if fpath.is_file():
            result["agent_conversation"].append({
                "agent": agent_name,
                "content": fpath.read_text()[:5000],
            })

    # 如果有 gate_history，附上
    gate_path = run_path / "gate_history.json"
    if gate_path.is_file():
        try:
            result["gate_history"] = json.loads(gate_path.read_text())
        except Exception:
            pass

    return result
