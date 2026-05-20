"""POST /api/workflow/{ask,design,critique} — 触发 AutoGen 工作流。

使用子进程执行，避免 FastAPI BackgroundTasks 的事件循环冲突。
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()

_root = Path(__file__).resolve().parent.parent.parent
_run_dir = _root / "reports" / "autogen_runs"
_run_dir.mkdir(parents=True, exist_ok=True)


def _generate_run_id(workflow: str) -> str:
    from datetime import datetime, timezone
    ts = datetime.now(timezone.utc).isoformat().replace(":", "").replace("-", "")[:15]
    return f"{workflow}-{ts}"


def _launch_subprocess(run_id: str, cmd: list[str]):
    """启动子进程执行工作流，写入输出到运行目录。"""
    import os
    run_path = _run_dir / run_id
    run_path.mkdir(parents=True, exist_ok=True)

    log_path = run_path / "run.log"
    err_path = run_path / "error.txt"

    # 构建环境变量: 继承当前环境 + 设置 PYTHONPATH
    env = {**os.environ}
    src_path = str(_root / "src")
    existing_path = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = f"{src_path}:{existing_path}" if existing_path else src_path

    try:
        with open(log_path, "w") as logout, open(err_path, "w") as errout:
            subprocess.Popen(
                cmd,
                stdout=logout,
                stderr=errout,
                cwd=str(_root),
                env=env,
            )
    except Exception as e:
        (run_path / "error.txt").write_text(f"启动子进程失败: {e}")


def _save_input(run_id: str, data: dict):
    """保存用户输入。"""
    run_path = _run_dir / run_id
    run_path.mkdir(parents=True, exist_ok=True)
    (run_path / "input.json").write_text(json.dumps(data, ensure_ascii=False, indent=2))


@router.post("/workflow/ask")
async def workflow_ask(req: dict):
    """触发 ask_scholar 工作流。

    Request: {"question": "..."}
    Response: {"run_id": "...", "status": "started"}
    """
    question = req.get("question", "")
    if not question:
        raise HTTPException(status_code=400, detail="question is required")

    run_id = _generate_run_id("ask")
    _save_input(run_id, req)

    cmd = [
        sys.executable, "-m", "autogen_app.cli", "ask", question,
        "--output-dir", str(_run_dir),
        "--run-id", run_id,
    ]
    _launch_subprocess(run_id, cmd)
    return {"run_id": run_id, "status": "started", "workflow": "ask_scholar"}


@router.post("/workflow/design")
async def workflow_design(req: dict):
    """触发 design_research 工作流。

    Request: {"topic": "...", "target_journal": "..."}
    """
    topic = req.get("topic", "")
    if not topic:
        raise HTTPException(status_code=400, detail="topic is required")

    run_id = _generate_run_id("design")
    _save_input(run_id, req)

    cmd = [
        sys.executable, "-m", "autogen_app.cli", "design", topic,
        "--output-dir", str(_run_dir),
        "--run-id", run_id,
    ]
    journal = req.get("target_journal", "")
    if journal:
        cmd.extend(["--target-journal", journal])

    _launch_subprocess(run_id, cmd)
    return {"run_id": run_id, "status": "started", "workflow": "design_research"}


@router.post("/workflow/critique")
async def workflow_critique(req: dict):
    """触发 critique_paper 工作流。

    Request: {"paper_path": "...", "target_journal": "..."}
    """
    paper_path = req.get("paper_path", "")
    if not paper_path:
        raise HTTPException(status_code=400, detail="paper_path is required")

    run_id = _generate_run_id("critique")
    _save_input(run_id, req)

    cmd = [
        sys.executable, "-m", "autogen_app.cli", "critique", paper_path,
        "--output-dir", str(_run_dir),
    ]
    journal = req.get("target_journal", "")
    if journal:
        cmd.extend(["--target-journal", journal])

    _launch_subprocess(run_id, cmd)
    return {"run_id": run_id, "status": "started", "workflow": "critique_paper"}


@router.post("/workflow/committee")
async def workflow_committee(req: dict):
    """触发学者委员会辩论（直接异步执行，不用子进程）。

    Request: {"topic": "...", "target_journal": "..."}
    """
    topic = req.get("topic", "")
    if not topic:
        raise HTTPException(status_code=400, detail="topic is required")

    run_id = _generate_run_id("committee")
    _save_input(run_id, req)

    import asyncio
    from autogen_app.committee.debate import run_committee

    asyncio.create_task(
        run_committee(
            topic=topic,
            target_journal=req.get("target_journal", ""),
            output_dir=str(_run_dir),
        )
    )
    return {"run_id": run_id, "status": "started", "workflow": "scholar_committee"}
