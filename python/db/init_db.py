
"""初始化数据库脚本 - 创建所有表"""
import asyncio

from db.base import Base
from db.models import (
    Chapter,
    Course,
    Exercise,
    KnowledgeEdge,
    KnowledgePoint,
    KnowledgeState,
    MistakeRecord,
)
from db.session import create_engine

async def init_db():
    engine = create_engine("sqlite+aiosqlite:///./edu_agent.db")
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all, checkfirst=True)
        print("所有数据库表创建成功！")
    
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_db())
