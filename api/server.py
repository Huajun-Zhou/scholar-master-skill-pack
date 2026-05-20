"""Academic Master Skill Pack — FastAPI Server.

启动:
    cd academic-master-skill-pack
    PYTHONPATH=src python api/server.py

然后前端 (Next.js) 通过 localhost:3000 → localhost:8000 代理访问 API。
"""

from __future__ import annotations

import sys
from pathlib import Path

# 确保 src/ 在 Python 路径中
_src = Path(__file__).resolve().parent.parent / "src"
if str(_src) not in sys.path:
    sys.path.insert(0, str(_src))

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes import chat, reports, search, wiki, workflow
from ws.workflow import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """启动/关闭时的生命周期管理。"""
    print(f"[server] 知识资产加载中...")
    from scholar_core.retrieval import list_all_papers
    papers = list_all_papers()
    print(f"[server] {len(papers)} 篇论文就绪")
    yield


app = FastAPI(
    title="Academic Master Skill Pack API",
    version="0.2.0",
    description="陈志远教授 Scholar Skill API — 提供问答、研究设计、论文审查、Wiki 检索",
    lifespan=lifespan,
)

# CORS — 开发时允许 localhost，生产时允许 Vercel 等部署平台
import os
_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins if _origins[0] != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(chat.router, prefix="/api")
app.include_router(workflow.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(wiki.router, prefix="/api")
app.include_router(search.router, prefix="/api")
app.include_router(ws_router)

# 根路径
@app.get("/")
def root():
    return {"service": "Academic Master Skill Pack API", "version": "0.2.0"}


# 健康检查
@app.get("/api/health")
def health():
    from scholar_core.retrieval import list_all_papers
    return {
        "status": "ok",
        "papers": len(list_all_papers()),
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
