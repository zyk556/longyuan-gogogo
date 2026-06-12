"""Pydantic 请求/响应模型"""
from __future__ import annotations
from datetime import date, time, datetime
from typing import Optional
from pydantic import BaseModel


# ── Match ───────────────────────────────────────────────
class MatchOut(BaseModel):
    id: str
    match_date: date
    home_team: str
    away_team: str
    group_name: str
    stadium: str
    kickoff_time: time
    home_score: Optional[int] = None
    away_score: Optional[int] = None
    status: str

    model_config = {"from_attributes": True}


# ── Image / Upload ──────────────────────────────────────
class UploadOut(BaseModel):
    image_id: str
    url: str
    analysis_id: Optional[str] = None


# ── BetItem ─────────────────────────────────────────────
class BetItemOut(BaseModel):
    id: str
    match_desc: str
    bet_type: str
    pick: str
    odds: float
    status: str

    model_config = {"from_attributes": True}


class BetItemUpdate(BaseModel):
    match_desc: Optional[str] = None
    bet_type: Optional[str] = None
    pick: Optional[str] = None
    odds: Optional[float] = None
    status: Optional[str] = None


class BetItemsUpdateReq(BaseModel):
    items: list[BetItemUpdate]


# ── Analysis ────────────────────────────────────────────
class AnalysisOut(BaseModel):
    id: str
    image_id: str
    bet_date: Optional[date] = None
    total_stake: Optional[float] = None
    potential_return: Optional[float] = None
    raw_json: Optional[dict] = None
    created_at: datetime
    items: list[BetItemOut] = []

    model_config = {"from_attributes": True}


# ── ProfitLoss ──────────────────────────────────────────
class ProfitLossCreate(BaseModel):
    date: date
    amount: float
    note: Optional[str] = None
    related_analysis_id: Optional[str] = None


class ProfitLossUpdate(BaseModel):
    date: Optional[date] = None
    amount: Optional[float] = None
    note: Optional[str] = None


class ProfitLossOut(BaseModel):
    id: str
    date: date
    amount: float
    note: Optional[str] = None
    related_analysis_id: Optional[str] = None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Dashboard ───────────────────────────────────────────
class DashboardOut(BaseModel):
    today_matches: list[MatchOut]
    recent_pl: list[ProfitLossOut]
    pending_analyses: list[AnalysisOut]
