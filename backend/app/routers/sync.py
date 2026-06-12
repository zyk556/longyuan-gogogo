"""赛程同步路由 — 从 football-data.org 拉取最新比分"""
import logging

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Match
from app.services.football_api import fetch_worldcup_matches
from app.auth import verify_key

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sync", tags=["同步"])


async def _do_sync(db: AsyncSession) -> dict:
    """全量同步：清空旧数据 → 拉取并写入最新数据"""
    api_matches = await fetch_worldcup_matches()
    if not api_matches:
        return {"synced": 0, "message": "拉取失败或未配置 API Key"}

    # 清空旧赛程
    await db.execute(Match.__table__.delete())
    await db.flush()

    # 写入新数据
    for api_m in api_matches:
        db.add(Match(**api_m))

    await db.commit()
    logger.info("同步完成：%d 条记录", len(api_matches))
    return {"synced": len(api_matches), "message": "同步完成"}


@router.post("")
async def sync_matches(
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_key),
):
    """手动触发同步"""
    return await _do_sync(db)


@router.post("/background")
async def sync_matches_background(
    background_tasks: BackgroundTasks,
    _=Depends(verify_key),
):
    """后台异步同步"""
    background_tasks.add_task(_run_background_sync)
    return {"message": "后台同步已启动"}


async def _run_background_sync():
    from app.database import async_session
    async with async_session() as db:
        await _do_sync(db)
