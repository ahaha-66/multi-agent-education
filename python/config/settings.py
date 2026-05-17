"""应用配置管理，通过环境变量加载。"""

from contextlib import asynccontextmanager
from typing import AsyncIterator
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, async_sessionmaker

from db.session import create_engine, create_sessionmaker


class Settings(BaseSettings):
    # LLM
    openai_api_key: str = ""
    openai_model: str = "gpt-4o"
    minimax_api_key: str = ""
    minimax_model: str = "MiniMax-M2.7"

    # Database
    database_url: str = "sqlite+aiosqlite:///./edu_agent.db"
    redis_url: str = "redis://localhost:6379/0"

    # Server
    api_port: int = 8000
    log_level: str = "INFO"

    model_config = {"env_file": "../.env", "env_file_encoding": "utf-8"}


settings = Settings()

# 全局单例
_engine: AsyncEngine | None = None
_sessionmaker: async_sessionmaker[AsyncSession] | None = None


def _get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    global _engine, _sessionmaker
    if _sessionmaker is None:
        _engine = create_engine(settings.database_url)
        _sessionmaker = create_sessionmaker(_engine)
    return _sessionmaker


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """获取数据库会话（FastAPI依赖注入）"""
    maker = _get_sessionmaker()
    async with maker() as session:
        yield session
