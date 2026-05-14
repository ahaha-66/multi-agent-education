"""
课程内容 API 路由

提供课程、章节、知识点、练习题相关的 REST API
"""

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from api.schemas.course_schemas import (
    CourseInfo,
    CourseCatalogResponse,
    KnowledgeGraphResponse,
    ExerciseRecommendationResponse,
    AnswerVerificationRequest,
    AnswerVerificationResponse,
    ExerciseBrief,
    ExerciseHint,
    ExerciseContent,
)
from config.settings import get_db_session
from db.models import Course
from services.knowledge_graph_service import KnowledgeGraphService
from services.exercise_recommender import ExerciseRecommender


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1", tags=["课程内容"])


@router.get("/courses", response_model=list[CourseInfo])
async def list_courses(
    subject: Annotated[str | None, Query(description="学科筛选")] = None,
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取课程列表
    
    Args:
        subject: 学科筛选（可选）
        
    Returns:
        课程列表
    """
    stmt = select(Course).where(Course.is_active == True)
    
    if subject:
        stmt = stmt.where(Course.subject == subject)
        
    result = await session.execute(stmt)
    courses = result.scalars().all()
    
    return [
        CourseInfo(
            id=course.id,
            code=course.code,
            name=course.name,
            subject=course.subject,
            grade_level=course.grade_level,
            description=course.description,
        )
        for course in courses
    ]


@router.get("/courses/{course_id}", response_model=CourseInfo)
async def get_course(
    course_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取课程详情
    
    Args:
        course_id: 课程 ID
        
    Returns:
        课程详情
    """
    result = await session.execute(
        select(Course).where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    return CourseInfo(
        id=course.id,
        code=course.code,
        name=course.name,
        subject=course.subject,
        grade_level=course.grade_level,
        description=course.description,
    )


@router.get("/courses/{course_id}/catalog", response_model=CourseCatalogResponse)
async def get_course_catalog(
    course_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取课程目录（章节-知识点树形结构）
    
    Args:
        course_id: 课程 ID
        
    Returns:
        课程目录
    """
    result = await session.execute(
        select(Course).where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    kg_service = KnowledgeGraphService(session)
    catalog = await kg_service.get_course_catalog(course_id)
    
    return CourseCatalogResponse(**catalog)


@router.get("/courses/{course_id}/knowledge-graph", response_model=KnowledgeGraphResponse)
async def get_course_knowledge_graph(
    course_id: str,
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取课程知识图谱
    
    Args:
        course_id: 课程 ID
        
    Returns:
        知识图谱（节点和边）
    """
    result = await session.execute(
        select(Course).where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    kg_service = KnowledgeGraphService(session)
    graph = await kg_service.get_graph(course_id)
    graph_dict = graph.to_dict()
    
    return KnowledgeGraphResponse(**graph_dict)


@router.get("/courses/{course_id}/exercises/next", response_model=ExerciseRecommendationResponse)
async def get_next_exercise(
    course_id: str,
    learner_id: Annotated[str, Query(description="学习者 ID")],
    knowledge_point_id: Annotated[str | None, Query(description="指定知识点 ID")] = None,
    count: Annotated[int, Query(description="推荐数量", ge=1, le=10)] = 1,
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取下一道练习题
    
    Args:
        course_id: 课程 ID
        learner_id: 学习者 ID
        knowledge_point_id: 指定知识点 ID（可选）
        count: 推荐数量
        
    Returns:
        练习题列表
    """
    result = await session.execute(
        select(Course).where(Course.id == course_id)
    )
    course = result.scalar_one_or_none()
    
    if not course:
        raise HTTPException(status_code=404, detail="课程不存在")
    
    recommender = ExerciseRecommender(session)
    
    exclude_ids = []
    if learner_id:
        history = await recommender.get_learner_history(learner_id)
        exclude_ids = list(history.keys())
    
    exercises = await recommender.recommend_next(
        learner_id=learner_id,
        course_id=course_id,
        knowledge_point_id=knowledge_point_id,
        exclude_exercise_ids=exclude_ids,
        count=count,
    )
    
    exercise_briefs = []
    for ex in exercises:
        exercise_briefs.append(ExerciseBrief(
            id=ex["id"],
            code=ex["code"],
            type=ex["type"],
            difficulty=ex["difficulty"],
            content=ExerciseContent(**ex["content"]) if ex["content"] else ExerciseContent(stem=""),
            tags=ex.get("tags", []),
            hint_levels=[
                ExerciseHint(level=h["level"], hint=h["hint"])
                for h in ex.get("hint_levels", [])
            ],
        ))
    
    recommendation_reason = None
    if knowledge_point_id:
        recommendation_reason = f"基于指定知识点 {knowledge_point_id} 推荐"
    else:
        recommendation_reason = "基于课程路径和学习进度推荐"
    
    return ExerciseRecommendationResponse(
        exercises=exercise_briefs,
        recommendation_reason=recommendation_reason,
    )


@router.post("/exercises/verify", response_model=AnswerVerificationResponse)
async def verify_answer(
    request: AnswerVerificationRequest,
    learner_id: Annotated[str, Query(description="学习者 ID")] = None,
    session: AsyncSession = Depends(get_db_session),
):
    """
    验证答案
    
    Args:
        request: 答案验证请求
        learner_id: 学习者 ID（可选）
        
    Returns:
        验证结果
    """
    recommender = ExerciseRecommender(session)
    result = await recommender.verify_answer(
        exercise_id=request.exercise_id,
        user_answer=request.answer,
    )
    
    if learner_id and request.answer:
        await recommender.record_attempt(
            learner_id=learner_id,
            exercise_id=request.exercise_id,
            is_correct=result["is_correct"],
        )
    
    return AnswerVerificationResponse(**result)


@router.get("/learners/{learner_id}/wrong-exercises")
async def get_wrong_exercises(
    learner_id: str,
    limit: Annotated[int, Query(description="返回数量", ge=1, le=100)] = 10,
    session: AsyncSession = Depends(get_db_session),
):
    """
    获取学习者的错题列表
    
    Args:
        learner_id: 学习者 ID
        limit: 返回数量
        
    Returns:
        错题列表
    """
    recommender = ExerciseRecommender(session)
    wrong_exercises = await recommender.get_wrong_exercises(learner_id, limit)
    
    return {
        "learner_id": learner_id,
        "wrong_exercises": wrong_exercises,
        "total": len(wrong_exercises),
    }
