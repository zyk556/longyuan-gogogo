"""图片上传路由"""
import hashlib
import os
import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, File, UploadFile, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import get_db
from app.models import Image, Analysis, BetItem
from app.schemas import UploadOut
from app.services.mimo import recognize_lottery
from app.auth import verify_key

router = APIRouter(prefix="/api/upload", tags=["上传"])

Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


@router.post("", response_model=UploadOut)
async def upload_image(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    _=Depends(verify_key),
):
    """上传彩票图片 → 存储 → AI 识别 → 返回分析结果"""
    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()

    # 图片去重：已有且有分析结果 → 直接返回
    existing = await db.execute(select(Image).where(Image.file_hash == file_hash))
    existing_image = existing.scalar_one_or_none()
    if existing_image:
        analysis_result = await db.execute(
            select(Analysis).where(Analysis.image_id == existing_image.id)
        )
        analysis = analysis_result.scalar_one_or_none()
        if analysis:
            return UploadOut(
                image_id=existing_image.id,
                url=f"/uploads/{Path(existing_image.file_path).name}",
                analysis_id=analysis.id,
            )
        # 没有分析结果 → 重新调用 AI
        image = existing_image
        file_path = existing_image.file_path
    else:
        # 新图片 → 保存文件
        ext = Path(file.filename).suffix or ".jpg"
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = os.path.join(settings.UPLOAD_DIR, filename)
        with open(file_path, "wb") as f:
            f.write(content)
        image = Image(file_path=file_path, file_hash=file_hash)
        db.add(image)
        await db.flush()

    # 调用 MiMo 识别
    ai_result = await recognize_lottery(file_path)

    analysis_id = None
    if ai_result is not None:
        from datetime import date as date_type
        bet_date = None
        if ai_result.get("bet_date"):
            try:
                bet_date = date_type.fromisoformat(ai_result["bet_date"])
            except ValueError:
                pass

        analysis = Analysis(
            image_id=image.id,
            bet_date=bet_date,
            total_stake=ai_result.get("total_stake"),
            potential_return=ai_result.get("potential_return"),
            raw_json=ai_result,
        )
        db.add(analysis)
        await db.flush()

        for item in ai_result.get("items", []):
            bet_item = BetItem(
                analysis_id=analysis.id,
                match_desc=item.get("match", ""),
                bet_type=item.get("bet_type", ""),
                pick=item.get("pick", ""),
                odds=float(item.get("odds") or 0),
            )
            db.add(bet_item)

        analysis_id = analysis.id

    await db.commit()

    return UploadOut(
        image_id=image.id,
        url=f"/uploads/{Path(image.file_path).name}",
        analysis_id=analysis_id,
    )
