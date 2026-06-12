"""异步数据库引擎与会话 — 自动适配 SQLite / PostgreSQL"""
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.config import settings

url = settings.DATABASE_URL

# Railway 注入的 postgres:// 需要改成 postgresql+asyncpg://
if url.startswith("postgres://"):
    url = url.replace("postgres://", "postgresql+asyncpg://", 1)
elif url.startswith("postgresql://") and "+asyncpg" not in url:
    url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

# SQLite 不支持连接池参数
if url.startswith("sqlite"):
    engine = create_async_engine(url, echo=False)
else:
    engine = create_async_engine(url, echo=False, pool_size=5, max_overflow=10)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
