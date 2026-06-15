"""身份验证：访客/内部模式"""
import hashlib
from fastapi import Header, HTTPException, status
from app.config import settings

# 内部密码（固定值，改这里就行）
INTERNAL_PASSWORD = "longyuan2026"

# 已验证的 token 缓存（简单实现，重启清空）
_valid_tokens: set[str] = set()


def _make_token(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()[:32]


# 预生成正确 token
_correct_token = _make_token(INTERNAL_PASSWORD)


def verify_internal(x_auth_token: str = Header(default="")):
    """依赖注入：校验是否为内部模式"""
    if x_auth_token != _correct_token:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="需要内部权限")


def check_auth(x_auth_token: str = Header(default="")) -> bool:
    """检查是否为内部模式，返回 True/False"""
    return x_auth_token == _correct_token


def get_auth_info():
    """返回认证信息"""
    return {"password_required": True, "token": _correct_token}
