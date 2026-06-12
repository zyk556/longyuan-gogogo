"""赛程路由"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import Match
from app.schemas import MatchOut
from app.auth import verify_key

router = APIRouter(prefix="/api/matches", tags=["赛程"])


@router.get("", response_model=list[MatchOut])
async def list_matches(
    date_: Optional[date] = Query(None, alias="date"),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_key),
):
    """获取赛程列表，可按日期筛选"""
    stmt = select(Match).order_by(Match.match_date, Match.kickoff_time)
    if date_:
        stmt = stmt.where(Match.match_date == date_)
    result = await db.execute(stmt)
    return result.scalars().all()
