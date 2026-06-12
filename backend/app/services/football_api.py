"""football-data.org 赛程同步服务 — 中文队名 + 北京时间"""
import logging
from datetime import datetime, date, time, timedelta, timezone
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

BASE_URL = "https://api.football-data.org/v4"
BJT = timezone(timedelta(hours=8))  # 北京时间

# 英文队名 → 中文
TEAM_CN = {
    "Mexico": "墨西哥", "South Africa": "南非", "Korea Republic": "韩国",
    "Czechia": "捷克", "Canada": "加拿大", "Bosnia and Herzegovina": "波黑",
    "United States": "美国", "Paraguay": "巴拉圭", "Qatar": "卡塔尔",
    "Switzerland": "瑞士", "Brazil": "巴西", "Morocco": "摩洛哥",
    "Colombia": "哥伦比亚", "New Zealand": "新西兰", "Senegal": "塞内加尔",
    "England": "英格兰", "Japan": "日本", "Germany": "德国",
    "Argentina": "阿根廷", "France": "法国", "Australia": "澳大利亚",
    "Denmark": "丹麦", "Spain": "西班牙", "Croatia": "克罗地亚",
    "Belgium": "比利时", "Portugal": "葡萄牙", "Uruguay": "乌拉圭",
    "Netherlands": "荷兰", "Italy": "意大利", "Ecuador": "厄瓜多尔",
    "Serbia": "塞尔维亚", "Poland": "波兰", "Norway": "挪威",
    "Chile": "智利", "Egypt": "埃及", "Nigeria": "尼日利亚",
    "Ghana": "加纳", "Cameroon": "喀麦隆", "Tunisia": "突尼斯",
    "Saudi Arabia": "沙特阿拉伯", "IR Iran": "伊朗", "Iran": "伊朗",
    "Wales": "威尔士", "Scotland": "苏格兰", "Ireland": "爱尔兰",
    "Ukraine": "乌克兰", "Turkey": "土耳其", "Austria": "奥地利",
    "Hungary": "匈牙利", "Romania": "罗马尼亚", "Greece": "希腊",
    "Algeria": "阿尔及利亚", "Côte d'Ivoire": "科特迪瓦",
    "Ivory Coast": "科特迪瓦", "Mali": "马里", "South Korea": "韩国",
    "Costa Rica": "哥斯达黎加", "Panama": "巴拿马", "Jamaica": "牙买加",
    "Honduras": "洪都拉斯", "Haiti": "海地", "Cuba": "古巴",
    "UAE": "阿联酋", "Jordan": "约旦", "Indonesia": "印尼",
    "Bolivia": "玻利维亚", "Peru": "秘鲁", "China PR": "中国",
    "Iraq": "伊拉克", "Uzbekistan": "乌兹别克斯坦",
    "Palestine": "巴勒斯坦", "Lebanon": "黎巴嫩",
}

STATUS_MAP = {
    "SCHEDULED": "scheduled", "TIMED": "scheduled",
    "IN_PLAY": "live", "PAUSED": "live", "FINISHED": "finished",
    "POSTPONED": "postponed", "CANCELLED": "cancelled",
    "SUSPENDED": "live", "AWARDED": "finished",
}


def _cn(name: str) -> str:
    return TEAM_CN.get(name, name)


def _to_bjt(utc_dt: datetime) -> datetime:
    """UTC 时间转北京时间"""
    return utc_dt.astimezone(BJT)


async def fetch_worldcup_matches() -> Optional[list[dict]]:
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
            utc_date = m.get("utcDate")
            if not utc_date:
                continue
            dt_utc = datetime.fromisoformat(utc_date.replace("Z", "+00:00"))
            dt_bjt = _to_bjt(dt_utc)

            home_data = m.get("homeTeam") or {}
            away_data = m.get("awayTeam") or {}
            home_team = _cn(home_data.get("name", ""))
            away_team = _cn(away_data.get("name", ""))
            if not home_team or not away_team:
                continue

            score = m.get("score") or {}
            ft = score.get("fullTime") or {}
            home_score = ft.get("home")
            away_score = ft.get("away")

            status_raw = m.get("status", "SCHEDULED")
            status = STATUS_MAP.get(status_raw, "scheduled")

            stage = m.get("stage", "GROUP_STAGE")
            group_raw = m.get("group")
            if stage == "GROUP_STAGE" and group_raw:
                group_name = group_raw.replace("GROUP_", "").replace("Group ", "")
            elif stage in ("LAST_32", "ROUND_OF_16"):
                group_name = "1/8"
            elif stage == "QUARTER_FINALS":
                group_name = "1/4"
            elif stage == "SEMI_FINALS":
                group_name = "半决赛"
            elif stage == "THIRD_PLACE_PLAY_OFF":
                group_name = "三四名"
            elif stage == "FINAL":
                group_name = "决赛"
            else:
                group_name = stage or "未知"

            stadium = (m.get("area") or {}).get("name", "待定")

            matches.append({
                "match_date": dt_bjt.date(),
                "home_team": home_team,
                "away_team": away_team,
                "group_name": group_name,
                "stadium": stadium,
                "kickoff_time": dt_bjt.time(),
                "home_score": home_score,
                "away_score": away_score,
                "status": status,
            })

        logger.info("拉取到 %d 场比赛", len(matches))
        return matches

    except Exception as e:
        logger.error("拉取赛程失败: %s", e)
        return None
