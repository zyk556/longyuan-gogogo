"""SQLAlchemy ORM 模型 — 5 张核心表"""
import uuid
from datetime import datetime, date, time

from sqlalchemy import (
    Column, String, Date, Time, Integer, Float, DateTime, ForeignKey, JSON, func
)
from sqlalchemy.orm import DeclarativeBase, relationship


def gen_uuid() -> str:
    return uuid.uuid4().hex


class Base(DeclarativeBase):
    pass


class Match(Base):
    __tablename__ = "matches"

    id = Column(String(32), primary_key=True, default=gen_uuid)
    match_date = Column(Date, nullable=False, index=True)
    home_team = Column(String(50), nullable=False)
    away_team = Column(String(50), nullable=False)
    group_name = Column(String(10), nullable=False)
    stadium = Column(String(100), nullable=False)
    kickoff_time = Column(Time, nullable=False)
    home_score = Column(Integer, nullable=True)
    away_score = Column(Integer, nullable=True)
    status = Column(String(20), nullable=False, default="scheduled")


class Image(Base):
    __tablename__ = "images"

    id = Column(String(32), primary_key=True, default=gen_uuid)
    file_path = Column(String(500), nullable=False)
    file_hash = Column(String(64), nullable=False, unique=True, index=True)
    upload_time = Column(DateTime, nullable=False, server_default=func.now())

    analyses = relationship("Analysis", back_populates="image")


class Analysis(Base):
    __tablename__ = "analysis"

    id = Column(String(32), primary_key=True, default=gen_uuid)
    image_id = Column(String(32), ForeignKey("images.id"), nullable=False)
    bet_date = Column(Date, nullable=True)
    total_stake = Column(Float, nullable=True)
    potential_return = Column(Float, nullable=True)
    raw_json = Column(JSON, nullable=True)
    saved = Column(Integer, nullable=False, default=0)  # 0=未保存 1=已保存
    created_at = Column(DateTime, nullable=False, server_default=func.now())

    image = relationship("Image", back_populates="analyses")
    items = relationship("BetItem", back_populates="analysis", cascade="all, delete-orphan")


class BetItem(Base):
    __tablename__ = "bet_items"

    id = Column(String(32), primary_key=True, default=gen_uuid)
    analysis_id = Column(String(32), ForeignKey("analysis.id"), nullable=False)
    match_desc = Column(String(200), nullable=False)
    bet_type = Column(String(50), nullable=False)
    pick = Column(String(50), nullable=False)
    odds = Column(Float, nullable=False)
    status = Column(String(20), nullable=False, default="pending")

    analysis = relationship("Analysis", back_populates="items")


class ProfitLoss(Base):
    __tablename__ = "profit_loss"

    id = Column(String(32), primary_key=True, default=gen_uuid)
    date = Column(Date, nullable=False, index=True)
    stake = Column(Float, nullable=False, default=0)           # 投注金额
    return_amount = Column(Float, nullable=False, default=0)   # 回报金额
    amount = Column(Float, nullable=False, default=0)          # 盈亏 = 回报 - 投注
    related_analysis_id = Column(String(32), ForeignKey("analysis.id"), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
