"""盈亏记账路由"""
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import ProfitLoss
from app.schemas import ProfitLossCreate, ProfitLossUpdate, ProfitLossOut
from app.auth import verify_internal

router = APIRouter(prefix="/api/profit-loss", tags=["记账"])


@router.post("", response_model=ProfitLossOut)
async def create_pl(
    body: ProfitLossCreate,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_internal),
):
    """添加盈亏记录"""
    pl = ProfitLoss(
        date=body.date,
        stake=body.stake,
        return_amount=body.return_amount,
        amount=body.return_amount - body.stake,
        related_analysis_id=body.related_analysis_id,
    )
    db.add(pl)
    await db.commit()
    await db.refresh(pl)
    return pl


@router.get("", response_model=list[ProfitLossOut])
async def list_pl(
    start: Optional[date] = Query(None),
    end: Optional[date] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    """查询盈亏列表"""
    stmt = select(ProfitLoss).order_by(ProfitLoss.date.desc())
    if start:
        stmt = stmt.where(ProfitLoss.date >= start)
    if end:
        stmt = stmt.where(ProfitLoss.date <= end)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.put("/{pl_id}", response_model=ProfitLossOut)
async def update_pl(
    pl_id: str,
    body: ProfitLossUpdate,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_internal),
):
    """修改盈亏记录"""
    result = await db.execute(select(ProfitLoss).where(ProfitLoss.id == pl_id))
    pl = result.scalar_one_or_none()
    if not pl:
        raise HTTPException(status_code=404, detail="记录不存在")
    data = body.model_dump(exclude_unset=True)
    if "stake" in data:
        pl.stake = data["stake"]
    if "return_amount" in data:
        pl.return_amount = data["return_amount"]
    if "date" in data:
        pl.date = data["date"]
    if "related_analysis_id" in data:
        pl.related_analysis_id = data["related_analysis_id"]
    pl.amount = pl.return_amount - pl.stake
    await db.commit()
    await db.refresh(pl)
    return pl


@router.delete("/{pl_id}")
async def delete_pl(
    pl_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_internal),
):
    """删除盈亏记录"""
    result = await db.execute(select(ProfitLoss).where(ProfitLoss.id == pl_id))
    pl = result.scalar_one_or_none()
    if not pl:
        raise HTTPException(status_code=404, detail="记录不存在")
    await db.delete(pl)
    await db.commit()
    return {"detail": "已删除"}
