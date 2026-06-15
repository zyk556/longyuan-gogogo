"""FastAPI 应用入口"""
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from app.config import settings
from app.database import engine
from app.models import Base
from app.routers import matches, upload, analysis, profit_loss, dashboard, sync

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")

FRONTEND_DIR = Path(__file__).parent.parent / "static"


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logging.info("数据库初始化成功")
    except Exception as e:
        logging.error("数据库初始化失败: %s", e)
    yield
    await engine.dispose()


app = FastAPI(title="龙苑集团-世界杯工具", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 上传目录
Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")

# API 路由
app.include_router(matches.router)
app.include_router(upload.router)
app.include_router(analysis.router)
app.include_router(profit_loss.router)
app.include_router(dashboard.router)
app.include_router(sync.router)


@app.get("/api/health")
async def health():
    return JSONResponse(content={"status": "ok"})


@app.post("/api/login")
async def login(body: dict):
    """验证密码，返回 token"""
    from app.auth import INTERNAL_PASSWORD, _make_token
    password = body.get("password", "")
    if password == INTERNAL_PASSWORD:
        return {"success": True, "token": _make_token(password)}
    return JSONResponse(status_code=401, content={"success": False, "detail": "密码错误"})


# 前端静态文件
if FRONTEND_DIR.exists() and (FRONTEND_DIR / "index.html").exists():
    assets_dir = FRONTEND_DIR / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    @app.get("/{full_path:path}")
    async def serve_frontend(full_path: str):
        file_path = FRONTEND_DIR / full_path
        if file_path.is_file():
            return FileResponse(str(file_path))
        return FileResponse(str(FRONTEND_DIR / "index.html"))
