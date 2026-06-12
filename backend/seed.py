"""初始化脚本：基于真实 CSV 插入 2026 美加墨世界杯赛程"""
import asyncio
import csv
import re
from datetime import date, time

from sqlalchemy import select
from app.database import engine, async_session
from app.models import Base, Match

CSV_PATH = r"f:\悦天禾集团\表格_20260612.csv"


def parse_csv():
    """解析 CSV，返回 matches 行列表"""
    matches = []
    year = 2026
    current_date = None

    with open(CSV_PATH, "r", encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        header = next(reader)  # 日期,星期,对阵双方,小组,开赛时间(北京)

        for row in reader:
            if len(row) < 5:
                continue
            date_raw, weekday, teams, group_raw, time_raw = [c.strip() for c in row[:5]]

            # 解析日期（可能为空表示同上一行）
            if date_raw:
                m = re.search(r"(\d+)\s*月\s*(\d+)\s*日", date_raw)
                if m:
                    current_date = date(year, int(m.group(1)), int(m.group(2)))
            if current_date is None:
                continue

            # 解析时间
            tm = re.match(r"(\d{1,2}):(\d{2})", time_raw)
            if tm:
                kickoff = time(int(tm.group(1)), int(tm.group(2)))
            else:
                kickoff = time(12, 0)

            # 解析对阵 "墨西哥 VS 南非"
            parts = re.split(r"\s*VS\s*", teams, flags=re.IGNORECASE)
            if len(parts) != 2:
                continue
            home_team = parts[0].strip()
            away_team = parts[1].strip()

            # 解析小组 "A 组"
            group_name = re.sub(r"\s*组", "", group_raw).strip()

            matches.append({
                "match_date": current_date,
                "home_team": home_team,
                "away_team": away_team,
                "group_name": group_name,
                "stadium": "待定",
                "kickoff_time": kickoff,
                "home_score": None,
                "away_score": None,
                "status": "scheduled",
            })

    return matches


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        result = await db.execute(select(Match).limit(1))
        if result.scalar_one_or_none():
            await db.execute(Match.__table__.delete())
            await db.commit()

        matches = parse_csv()
        for m in matches:
            db.add(Match(**m))
        await db.commit()
        print(f"已插入 {len(matches)} 条 2026 美加墨世界杯赛程")


if __name__ == "__main__":
    asyncio.run(seed())
