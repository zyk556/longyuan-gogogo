"""小米 MiMo 多模态视觉模型调用服务"""
import base64
import json
import logging
import mimetypes
from pathlib import Path
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = (
    "你是一个中国体育彩票（竞彩足球）解析专家。请仔细识别图片中所有投注条目，返回JSON。\n\n"
    "支持的玩法类型包括：\n"
    "- 胜平负：pick 填 主胜/平局/客胜，match 填 \"主队 vs 客队\"\n"
    "- 让球胜平负：pick 填 主胜/平局/客胜，match 必须写明让球数，如 \"荷兰-1 vs 日本+2\"\n"
    "- 比分：pick 填具体比分如 2:1、1:0 等\n"
    "- 总进球数（大小球）：pick 填 大2.5/小2.5 等\n"
    "- 半全场：pick 填 胜胜/胜负/平平 等\n"
    "- 混合投注：多场比赛组合\n\n"
    "返回格式：\n"
    '{"bet_date":"YYYY-MM-DD","items":['
    '{"match":"主队 vs 客队","bet_type":"玩法类型","pick":"投注选择","odds":2.10},'
    '{"match":"主队 vs 客队","bet_type":"比分","pick":"2:1","odds":8.50}'
    '],"total_stake":50.00,"potential_return":128.50}\n\n'
    "注意：\n"
    "- 比分玩法的 bet_type 填\"比分\"，pick 填比分如\"2:1\"\n"
    "- odds 为数字，无法识别时填 null\n"
    "- 如果某个字段看不清，尽量猜测，不要跳过该条目\n"
    "- 总是返回有效 JSON，不要包含其他文字"
)


def _file_to_base64_url(file_path: str) -> str:
    """将本地文件转为 data:{mime};base64,{data} 格式"""
    mime, _ = mimetypes.guess_type(file_path)
    if not mime:
        mime = "image/jpeg"
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"


def _normalize_result(raw: dict) -> dict:
    """统一 MiMo 返回的各种格式为标准格式"""
    # 如果已经是标准格式
    if "items" in raw and isinstance(raw["items"], list):
        return raw

    items = []

    # 格式2：中文字段名（已选比赛）
    matches = raw.get("已选比赛") or raw.get("matches") or raw.get("选中比赛") or []
    for m in matches:
        match_desc = m.get("对阵") or m.get("match") or m.get("比赛") or ""
        bet_type = m.get("玩法") or m.get("bet_type") or raw.get("投注详情", {}).get("玩法") or ""
        pick = m.get("选择") or m.get("pick") or m.get("比分") or m.get("结果") or ""
        odds = m.get("赔率") or m.get("odds") or None

        # 比分玩法特殊处理
        if pick and ":" in str(pick) and not bet_type:
            bet_type = "比分"

        items.append({
            "match": match_desc,
            "bet_type": str(bet_type),
            "pick": str(pick),
            "odds": float(odds) if odds else None,
        })

    # 格式3：单场投注
    if not items and raw.get("对阵"):
        items.append({
            "match": raw["对阵"],
            "bet_type": raw.get("玩法", ""),
            "pick": raw.get("选择") or raw.get("比分", ""),
            "odds": float(raw.get("赔率", 0) or 0),
        })

    # 提取金额
    detail = raw.get("投注详情") or raw
    total_stake = raw.get("total_stake") or detail.get("总金额") or detail.get("投注金额")
    potential_return = raw.get("potential_return") or detail.get("预测奖金") or detail.get("预计奖金")

    # 提取日期
    bet_date = raw.get("bet_date") or raw.get("销售日期")
    if not bet_date:
        sales = raw.get("销售信息") or {}
        bet_date = sales.get("销售日期")

    return {
        "bet_date": bet_date,
        "items": items,
        "total_stake": float(total_stake) if total_stake else None,
        "potential_return": float(potential_return) if potential_return else None,
    }


async def recognize_lottery(file_path: str) -> Optional[dict]:
    """
    调用 MiMo 多模态模型识别彩票图片。
    file_path: 本地图片路径
    返回解析后的 JSON dict，失败时返回 None。
    """
    if not settings.MIMO_API_KEY:
        logger.error("MIMO_API_KEY 未配置！请在环境变量中设置")
        return None
    logger.info("开始识别图片: %s (key=%s...)", file_path, settings.MIMO_API_KEY[:8])

    try:
        image_url = _file_to_base64_url(file_path)
    except FileNotFoundError:
        logger.error("图片文件不存在: %s", file_path)
        return None
    except Exception as e:
        logger.error("读取图片失败: %s", e)
        return None

    payload = {
        "model": settings.MIMO_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "请识别这张体育彩票的内容，返回JSON"},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            },
        ],
        "temperature": 0.1,
        "max_completion_tokens": 16384,
    }

    headers = {
        "api-key": settings.MIMO_API_KEY,
        "Content-Type": "application/json",
    }

    try:
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.post(settings.MIMO_API_URL, json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"].get("content") or ""
        reasoning = data["choices"][0]["message"].get("reasoning_content") or ""
        finish = data["choices"][0].get("finish_reason", "unknown")
        logger.info("MiMo 响应: finish=%s content_len=%d reasoning_len=%d", finish, len(content), len(reasoning))
        if not content.strip():
            logger.warning("MiMo 返回空内容! finish_reason=%s reasoning=%s", finish, reasoning[:200])
            return None
        # 尝试从 markdown code block 或纯文本中提取 JSON
        if "```" in content:
            parts = content.split("```")
            content = parts[1] if len(parts) > 1 else parts[0]
            if content.startswith("json"):
                content = content[4:]
        # 提取第一个 JSON 对象
        start = content.find("{")
        end = content.rfind("}") + 1
        if start >= 0 and end > start:
            content = content[start:end]
        result = json.loads(content.strip())
        result = _normalize_result(result)
        logger.info("MiMo 识别成功: %s", result.get("bet_date"))
        return result
    except Exception as e:
        logger.error("MiMo 识别失败: %s", e)
        return None
