"""首页聚合路由"""
from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Match, ProfitLoss, Analysis, BetItem

router = APIRouter(prefix="/api/dashboard", tags=["首页"])

START_DATE = date(2026, 6, 10)


@router.get("")
async def dashboard(
    db: AsyncSession = Depends(get_db),
):
    """首页聚合：今日比赛 + 总盈亏（6.10起）+ 我的彩票总数"""
    today = date.today()

    # 今日比赛
    matches_result = await db.execute(
        select(Match)
        .where(Match.match_date == today)
        .order_by(Match.kickoff_time)
    )
    today_matches = matches_result.scalars().all()

    # 总盈亏（6.10 起）
    pl_result = await db.execute(
        select(ProfitLoss)
        .where(ProfitLoss.date >= START_DATE)
        .order_by(ProfitLoss.date.desc())
    )
    recent_pl = pl_result.scalars().all()

    # 我的彩票（已保存的全部）
    analyses_result = await db.execute(
        select(Analysis)
        .where(Analysis.saved == 1)
        .options(selectinload(Analysis.items))
        .order_by(Analysis.created_at.desc())
    )
    pending_analyses = analyses_result.scalars().all()

    return {
        "today_matches": today_matches,
        "recent_pl": recent_pl,
        "pending_analyses": pending_analyses,
    }
