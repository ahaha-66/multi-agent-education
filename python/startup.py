"""启动脚本 - 使用 SQLite 数据库"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool
from db.base import Base
from db.models import LearnerProfile, KnowledgeState, ReviewItem, Attempt, EventLog

DATABASE_URL = "sqlite+aiosqlite:///./edu_agent.db"


async def init_db():
    """初始化数据库表"""
    engine = create_async_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    print("✅ 数据库表创建成功")
    return engine


if __name__ == "__main__":
    asyncio.run(init_db())
