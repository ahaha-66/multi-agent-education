"""
管理员 API 路由

提供数据导入和管理相关的 REST API
"""

import asyncio
import logging
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.course_schemas import SeedRequest, SeedStatusResponse
from config.settings import get_db_session, settings
from db.seed import CourseContentSeeder


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["管理员"])


@router.post("/seed", response_model=SeedStatusResponse)
async def seed_course_data(
    request: SeedRequest,
    session: AsyncSession = Depends(get_db_session),
):
    """
    导入课程内容数据
    
    Args:
        request: 导入请求
        
    Returns:
        导入状态
    """
    data_file = Path(request.source)
    
    if not data_file.exists():
        raise HTTPException(
            status_code=400,
            detail=f"数据文件不存在: {request.source}"
        )
    
    try:
        seeder = CourseContentSeeder(session)
        stats = await seeder.seed_from_json(data_file, force=request.force)
        
        return SeedStatusResponse(
            status="success",
            message="数据导入成功",
            stats=stats,
        )
    except Exception as e:
        logger.error(f"数据导入失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"数据导入失败: {str(e)}"
        )


@router.get("/seed/default", response_model=SeedStatusResponse)
async def seed_default_data(
    session: AsyncSession = Depends(get_db_session),
):
    """
    导入默认课程数据（data/seed_math_g7.json）
    
    Returns:
        导入状态
    """
    data_file = Path("data/seed_math_g7.json")
    
    if not data_file.exists():
        data_file = Path(__file__).parent.parent / "data" / "seed_math_g7.json"
    
    if not data_file.exists():
        raise HTTPException(
            status_code=400,
            detail="默认数据文件不存在"
        )
    
    try:
        seeder = CourseContentSeeder(session)
        stats = await seeder.seed_from_json(data_file, force=False)
        
        return SeedStatusResponse(
            status="success",
            message="默认数据导入成功",
            stats=stats,
        )
    except Exception as e:
        logger.error(f"数据导入失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"数据导入失败: {str(e)}"
        )
