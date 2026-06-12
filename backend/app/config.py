"""应用配置 — 通过环境变量或 .env 文件加载"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 数据库
    DATABASE_URL: str = "sqlite+aiosqlite:///./worldcup.db"
    # 小米 MiMo 多模态模型
    MIMO_API_URL: str = "https://api.xiaomimimo.com/v1/chat/completions"
    MIMO_MODEL: str = "mimo-v2.5"
    MIMO_API_KEY: str = ""
    # 文件上传
    UPLOAD_DIR: str = "/data/uploads"
    # 共享密钥（空 = 不鉴权）
    SHARED_SECRET: str = ""
    # football-data.org API Key（免费注册）
    FOOTBALL_API_KEY: str = ""
    # 服务端口
    PORT: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
