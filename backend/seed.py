"""初始化脚本：插入 2026 世界杯模拟赛程数据"""
import asyncio
from datetime import date, time

from sqlalchemy import insert, select
from app.database import engine, async_session
from app.models import Base, Match


MATCHES_DATA = [
    # 小组赛第1轮 — 2026年6月11日
    {"match_date": date(2026, 6, 11), "home_team": "墨西哥", "away_team": "加拿大", "group_name": "A", "stadium": "阿兹特克球场", "kickoff_time": time(12, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 6, 11), "home_team": "德国", "away_team": "日本", "group_name": "E", "stadium": "梅赛德斯-奔驰球场", "kickoff_time": time(15, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 6, 11), "home_team": "西班牙", "away_team": "哥斯达黎加", "group_name": "E", "stadium": "卢赛尔球场", "kickoff_time": time(18, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    # 小组赛第1轮 — 2026年6月12日
    {"match_date": date(2026, 6, 12), "home_team": "阿根廷", "away_team": "沙特阿拉伯", "group_name": "C", "stadium": "卢赛尔球场", "kickoff_time": time(12, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 6, 12), "home_team": "法国", "away_team": "澳大利亚", "group_name": "D", "stadium": "贾努布球场", "kickoff_time": time(15, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 6, 12), "home_team": "巴西", "away_team": "塞尔维亚", "group_name": "G", "stadium": "974球场", "kickoff_time": time(18, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 6, 12), "home_team": "英格兰", "away_team": "伊朗", "group_name": "B", "stadium": "哈利法国际球场", "kickoff_time": time(21, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    # 小组赛第1轮 — 2026年6月13日
    {"match_date": date(2026, 6, 13), "home_team": "葡萄牙", "away_team": "加纳", "group_name": "H", "stadium": "教育城球场", "kickoff_time": time(12, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 6, 13), "home_team": "荷兰", "away_team": "塞内加尔", "group_name": "A", "stadium": "阿图玛玛球场", "kickoff_time": time(15, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 6, 13), "home_team": "比利时", "away_team": "加拿大", "group_name": "F", "stadium": "艾哈迈德·本·阿里球场", "kickoff_time": time(18, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 6, 13), "home_team": "克罗地亚", "away_team": "摩洛哥", "group_name": "F", "stadium": "海湾球场", "kickoff_time": time(21, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    # 小组赛第2轮 — 2026年6月14日
    {"match_date": date(2026, 6, 14), "home_team": "日本", "away_team": "哥斯达黎加", "group_name": "E", "stadium": "艾哈迈德·本·阿里球场", "kickoff_time": time(12, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 6, 14), "home_team": "比利时", "away_team": "摩洛哥", "group_name": "F", "stadium": "阿图玛玛球场", "kickoff_time": time(15, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 6, 14), "home_team": "克罗地亚", "away_team": "加拿大", "group_name": "F", "stadium": "哈利法国际球场", "kickoff_time": time(18, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 6, 14), "home_team": "西班牙", "away_team": "德国", "group_name": "E", "stadium": "海湾球场", "kickoff_time": time(21, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    # 小组赛第2轮 — 2026年6月15日
    {"match_date": date(2026, 6, 15), "home_team": "喀麦隆", "away_team": "塞尔维亚", "group_name": "G", "stadium": "贾努布球场", "kickoff_time": time(12, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 6, 15), "home_team": "韩国", "away_team": "加纳", "group_name": "H", "stadium": "教育城球场", "kickoff_time": time(15, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 6, 15), "home_team": "巴西", "away_team": "瑞士", "group_name": "G", "stadium": "974球场", "kickoff_time": time(18, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 6, 15), "home_team": "葡萄牙", "away_team": "乌拉圭", "group_name": "H", "stadium": "卢赛尔球场", "kickoff_time": time(21, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    # 小组赛第3轮 — 2026年6月25日
    {"match_date": date(2026, 6, 25), "home_team": "荷兰", "away_team": "卡塔尔", "group_name": "A", "stadium": "阿图玛玛球场", "kickoff_time": time(15, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 6, 25), "home_team": "厄瓜多尔", "away_team": "塞内加尔", "group_name": "A", "stadium": "哈利法国际球场", "kickoff_time": time(15, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 6, 25), "home_team": "威尔士", "away_team": "英格兰", "group_name": "B", "stadium": "艾哈迈德·本·阿里球场", "kickoff_time": time(19, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 6, 25), "home_team": "伊朗", "away_team": "美国", "group_name": "B", "stadium": "阿图玛玛球场", "kickoff_time": time(19, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    # 淘汰赛模拟
    {"match_date": date(2026, 7, 3), "home_team": "1A", "away_team": "2B", "group_name": "1/8", "stadium": "哈利法国际球场", "kickoff_time": time(17, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 7, 3), "home_team": "1C", "away_team": "2D", "group_name": "1/8", "stadium": "艾哈迈德·本·阿里球场", "kickoff_time": time(21, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 7, 4), "home_team": "1B", "away_team": "2A", "group_name": "1/8", "stadium": "海湾球场", "kickoff_time": time(17, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 7, 4), "home_team": "1E", "away_team": "2F", "group_name": "1/8", "stadium": "974球场", "kickoff_time": time(21, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 7, 5), "home_team": "1G", "away_team": "2H", "group_name": "1/8", "stadium": "卢赛尔球场", "kickoff_time": time(17, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 7, 5), "home_team": "1F", "away_team": "2E", "group_name": "1/8", "stadium": "教育城球场", "kickoff_time": time(21, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 7, 6), "home_team": "1H", "away_team": "2G", "group_name": "1/8", "stadium": "阿兹特克球场", "kickoff_time": time(17, 0), "home_score": None, "away_score": None, "status": "scheduled"},
    {"match_date": date(2026, 7, 6), "home_team": "1D", "away_team": "2C", "group_name": "1/8", "stadium": "贾努布球场", "kickoff_time": time(21, 0), "home_score": None, "away_score": None, "status": "scheduled"},
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        # 检查是否已有数据
        result = await db.execute(select(Match).limit(1))
        if result.scalar_one_or_none():
            print("赛程数据已存在，跳过初始化")
            return

        for m in MATCHES_DATA:
            db.add(Match(**m))
        await db.commit()
        print(f"已插入 {len(MATCHES_DATA)} 条赛程数据")


if __name__ == "__main__":
    asyncio.run(seed())
