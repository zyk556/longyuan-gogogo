"""简单共享密钥鉴权"""
from fastapi import Header, HTTPException, status
from app.config import settings


async def verify_key(x_api_key: str = Header(default="")):
    """依赖注入：校验 X-API-Key 请求头"""
    if not settings.SHARED_SECRET:
        return  # 未配置密钥时跳过鉴权
    if x_api_key != settings.SHARED_SECRET:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="密钥无效")
