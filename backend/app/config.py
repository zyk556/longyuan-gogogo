"""应用配置 — 通过环境变量或 .env 文件加载"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # 数据库（本地默认 SQLite，Railway 自动注入 PostgreSQL）
    DATABASE_URL: str = "sqlite+aiosqlite:///./worldcup.db"
    # 小米 MiMo 多模态模型
    MIMO_API_URL: str = "https://api.xiaomimimo.com/v1/chat/completions"
    MIMO_MODEL: str = "mimo-v2.5"
    MIMO_API_KEY: str = ""
    # football-data.org
    FOOTBALL_API_KEY: str = ""
    # 文件上传
    UPLOAD_DIR: str = "./uploads"
    # 服务端口（Railway 通过 PORT 注入）
    PORT: int = 8000

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
