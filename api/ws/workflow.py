"""WebSocket /ws/workflow/{run_id} — 实时 agent 流。

客户端可以连接到 WebSocket 以接收工作流执行的实时更新。
每个工作流运行都有一个唯一的 run_id。
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()

_run_dir = Path(__file__).resolve().parent.parent.parent / "reports" / "autogen_runs"


@router.websocket("/ws/workflow/{run_id}")
async def workflow_ws(websocket: WebSocket, run_id: str):
    """WebSocket endpoint — 实时推送工作流执行状态。

    客户端消息:
        - 连接建立后自动开始推送

    服务端推送消息:
        {"type": "status", "status": "connecting"|"running"|"completed"|"error"}
        {"type": "agent_message", "source": "...", "content": "..."}
        {"type": "gate_result", "passed": true/false, "summary": "..."}
        {"type": "file_update", "file": "...", "size": N}
        {"type": "done", "run_id": "..."}
    """
    await websocket.accept()
    run_path = _run_dir / run_id

    try:
        await websocket.send_json({
            "type": "status",
            "status": "connected",
            "run_id": run_id,
        })

        # 轮询检测输出文件的变化
        seen_files: set[str] = set()
        seen_sizes: dict[str, int] = {}

        import asyncio
        for _ in range(300):  # 最多等 5 分钟
            if not run_path.is_dir():
                await asyncio.sleep(1)
                continue

            current_files = set()
            for f in sorted(run_path.iterdir()):
                if f.suffix == ".md" and f.name != "input.md":
                    current_files.add(f.name)
                    size = f.stat().st_size

                    if f.name not in seen_files:
                        seen_files.add(f.name)
                        seen_sizes[f.name] = size
                        content = f.read_text()[:1000]
                        await websocket.send_json({
                            "type": "agent_message",
                            "source": f.stem,
                            "content": content,
                        })
                    elif size > seen_sizes.get(f.name, 0):
                        seen_sizes[f.name] = size
                        content = f.read_text()[:1000]
                        await websocket.send_json({
                            "type": "agent_message",
                            "source": f.stem,
                            "content": content,
                            "updated": True,
                        })

            # 检查是否完成（有 final_writer 输出包含 FINAL_REPORT）
            fw_path = run_path / "final_writer.md"
            if fw_path.is_file():
                content = fw_path.read_text()
                if "FINAL_REPORT" in content:
                    # 检查 gate 状态
                    gate_path = run_path / "gate_history.json"
                    gate_passed = None
                    if gate_path.is_file():
                        try:
                            gh = json.loads(gate_path.read_text())
                            if gh:
                                gate_passed = gh[-1].get("passed")
                        except Exception:
                            pass

                    await websocket.send_json({
                        "type": "gate_result",
                        "passed": gate_passed,
                    })
                    await websocket.send_json({
                        "type": "done",
                        "run_id": run_id,
                    })
                    break

            # 检查 error
            err_path = run_path / "error.txt"
            if err_path.is_file():
                await websocket.send_json({
                    "type": "status",
                    "status": "error",
                    "message": err_path.read_text()[:500],
                })
                break

            await asyncio.sleep(2)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.send_json({
            "type": "status",
            "status": "error",
            "message": str(e),
        })
