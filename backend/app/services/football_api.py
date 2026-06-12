"""football-data.org 赛程同步服务"""
import logging
from datetime import datetime, date, time
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://api.football-data.org/v4"


async def fetch_worldcup_matches() -> Optional[list[dict]]:
    """
    从 football-data.org 拉取世界杯赛程数据。
    返回解析后的 dict 列表，失败返回 None。
    """
    if not settings.FOOTBALL_API_KEY:
        logger.warning("FOOTBALL_API_KEY 未配置，跳过同步")
        return None

    headers = {"X-Auth-Token": settings.FOOTBALL_API_KEY}
    url = f"{BASE_URL}/competitions/WC/matches"

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(url, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        matches = []
        for m in data.get("matches", []):
            utc_date = m.get("utcDate", "")
            dt = datetime.fromisoformat(utc_date.replace("Z", "+00:00")) if utc_date else None

            home_team = m.get("homeTeam", {}).get("name", "")
            away_team = m.get("awayTeam", {}).get("name", "")
            score = m.get("score", {})
            ft = score.get("fullTime", {})
            status_raw = m.get("status", "SCHEDULED")

            # 映射状态
            status_map = {
                "SCHEDULED": "scheduled",
                "TIMED": "scheduled",
                "IN_PLAY": "live",
                "PAUSED": "live",
                "FINISHED": "finished",
                "POSTPONED": "postponed",
                "CANCELLED": "cancelled",
            }
            status = status_map.get(status_raw, "scheduled")

            # 阶段映射
            stage = m.get("stage", "GROUP_STAGE")
            stage_map = {
                "GROUP_STAGE": m.get("group", "Group A").replace("Group ", ""),
                "ROUND_OF_16": "1/8",
                "QUARTER_FINALS": "1/4",
                "SEMI_FINALS": "半决赛",
                "THIRD_PLACE_PLAY_OFF": "三四名",
                "FINAL": "决赛",
            }
            group_name = stage_map.get(stage, stage)

            matches.append({
                "match_date": dt.date() if dt else date.today(),
                "home_team": home_team,
                "away_team": away_team,
                "group_name": group_name,
                "stadium": m.get("area", {}).get("name", "待定"),
                "kickoff_time": dt.time() if dt else time(12, 0),
                "home_score": ft.get("home"),
                "away_score": ft.get("away"),
                "status": status,
                "external_id": m.get("id"),  # API 返回的比赛 ID，用于更新匹配
            })

        logger.info("拉取到 %d 场比赛", len(matches))
        return matches

    except Exception as e:
        logger.error("拉取赛程失败: %s", e)
        return None
