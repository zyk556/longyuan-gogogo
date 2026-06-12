"""首页聚合路由"""
from datetime import date, timedelta

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Match, ProfitLoss, Analysis, BetItem
from app.schemas import DashboardOut, MatchOut, ProfitLossOut, AnalysisOut
from app.auth import verify_key

router = APIRouter(prefix="/api/dashboard", tags=["首页"])


@router.get("", response_model=DashboardOut)
async def dashboard(
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_key),
):
    """首页聚合：今日比赛 + 最近盈亏 + 待开奖彩票"""
    today = date.today()

    # 今日比赛
    matches_result = await db.execute(
        select(Match)
        .where(Match.match_date == today)
        .order_by(Match.kickoff_time)
    )
    today_matches = matches_result.scalars().all()

    # 总盈亏
    pl_result = await db.execute(
        select(ProfitLoss).order_by(ProfitLoss.date.desc())
    )
    recent_pl = pl_result.scalars().all()

    # 待开奖（已保存 + status=pending 的分析）
    pending_result = await db.execute(
        select(Analysis)
        .join(BetItem)
        .where(Analysis.saved == 1, BetItem.status == "pending")
        .options(selectinload(Analysis.items))
        .distinct()
        .order_by(Analysis.created_at.desc())
        .limit(10)
    )
    pending_analyses = pending_result.scalars().all()

    return DashboardOut(
        today_matches=today_matches,
        recent_pl=recent_pl,
        pending_analyses=pending_analyses,
    )
