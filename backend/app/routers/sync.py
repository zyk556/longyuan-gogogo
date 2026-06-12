"""赛程同步路由 — 从 football-data.org 拉取最新比分"""
import logging
from datetime import date

from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Match
from app.services.football_api import fetch_worldcup_matches
from app.auth import verify_key

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sync", tags=["同步"])


async def _do_sync(db: AsyncSession):
    """执行同步逻辑"""
    api_matches = await fetch_worldcup_matches()
    if not api_matches:
        return {"synced": 0, "message": "拉取失败或未配置 API Key"}

    synced = 0
    for api_m in api_matches:
        home = api_m["home_team"]
        away = api_m["away_team"]
        m_date = api_m["match_date"]

        # 尝试通过 主队+客队+日期 匹配已有记录
        result = await db.execute(
            select(Match).where(
                Match.match_date == m_date,
                Match.home_team == home,
                Match.away_team == away,
            )
        )
        existing = result.scalar_one_or_none()

        if existing:
            # 更新比分和状态
            existing.home_score = api_m["home_score"]
            existing.away_score = api_m["away_score"]
            existing.status = api_m["status"]
            if api_m["stadium"] and api_m["stadium"] != "待定":
                existing.stadium = api_m["stadium"]
            synced += 1
        else:
            # 新比赛，插入
            db.add(Match(
                match_date=m_date,
                home_team=home,
                away_team=away,
                group_name=api_m["group_name"],
                stadium=api_m["stadium"],
                kickoff_time=api_m["kickoff_time"],
                home_score=api_m["home_score"],
                away_score=api_m["away_score"],
                status=api_m["status"],
            ))
            synced += 1

    await db.commit()
    logger.info("同步完成：%d 条记录", synced)
    return {"synced": synced, "message": "同步完成"}


@router.post("")
async def sync_matches(
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_key),
):
    """手动触发同步（前台）"""
    result = await _do_sync(db)
    return result


@router.post("/background")
async def sync_matches_background(
    background_tasks: BackgroundTasks,
    _=Depends(verify_key),
):
    """后台异步同步（不阻塞请求）"""
    background_tasks.add_task(_run_background_sync)
    return {"message": "后台同步已启动"}


async def _run_background_sync():
    from app.database import async_session
    async with async_session() as db:
        await _do_sync(db)
