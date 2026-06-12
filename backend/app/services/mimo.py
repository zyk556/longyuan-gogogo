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
    "你是一个体育彩票解析专家。请提取图片中所有彩票条目，返回JSON。"
    '格式：{"bet_date":"YYYY-MM-DD","items":[{"match":"主队 vs 客队",'
    '"bet_type":"胜平负","pick":"主胜","odds":2.10}],"total_stake":50.00,'
    '"potential_return":128.50}'
)


def _file_to_base64_url(file_path: str) -> str:
    """将本地文件转为 data:{mime};base64,{data} 格式"""
    mime, _ = mimetypes.guess_type(file_path)
    if not mime:
        mime = "image/jpeg"
    with open(file_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return f"data:{mime};base64,{b64}"


async def recognize_lottery(file_path: str) -> Optional[dict]:
    """
    调用 MiMo 多模态模型识别彩票图片。
    file_path: 本地图片路径
    返回解析后的 JSON dict，失败时返回 None。
    """
    if not settings.MIMO_API_KEY:
        logger.warning("MIMO_API_KEY 未配置，跳过 AI 识别")
        return None

    image_url = _file_to_base64_url(file_path)

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
        "max_completion_tokens": 2048,
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

        content = data["choices"][0]["message"]["content"]
        # 尝试从 markdown code block 或纯文本中提取 JSON
        if "```" in content:
            content = content.split("```")[1]
            if content.startswith("json"):
                content = content[4:]
        result = json.loads(content.strip())
        logger.info("MiMo 识别成功: %s", result.get("bet_date"))
        return result
    except Exception as e:
        logger.error("MiMo 识别失败: %s", e)
        return None
