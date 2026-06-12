"""彩票分析路由"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.models import Analysis, BetItem
from app.schemas import AnalysisOut, BetItemsUpdateReq
from app.auth import verify_key

router = APIRouter(prefix="/api/analysis", tags=["分析"])


@router.get("/{analysis_id}", response_model=AnalysisOut)
async def get_analysis(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_key),
):
    """获取分析结果（含 bet_items 列表）"""
    stmt = (
        select(Analysis)
        .where(Analysis.id == analysis_id)
        .options(selectinload(Analysis.items))
    )
    result = await db.execute(stmt)
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="分析记录不存在")
    return analysis


@router.put("/{analysis_id}/items", response_model=AnalysisOut)
async def update_items(
    analysis_id: str,
    body: BetItemsUpdateReq,
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_key),
):
    """更新修改后的条目明细（全量替换）"""
    stmt = (
        select(Analysis)
        .where(Analysis.id == analysis_id)
        .options(selectinload(Analysis.items))
    )
    result = await db.execute(stmt)
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="分析记录不存在")

    # 删除旧条目
    for item in analysis.items:
        await db.delete(item)

    # 插入新条目
    for item_data in body.items:
        new_item = BetItem(
            analysis_id=analysis.id,
            match_desc=item_data.match_desc or "",
            bet_type=item_data.bet_type or "",
            pick=item_data.pick or "",
            odds=item_data.odds or 0.0,
            status=item_data.status or "pending",
        )
        db.add(new_item)

    await db.commit()

    # 重新加载
    stmt = (
        select(Analysis)
        .where(Analysis.id == analysis_id)
        .options(selectinload(Analysis.items))
    )
    result = await db.execute(stmt)
    return result.scalar_one()
