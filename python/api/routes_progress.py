import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from config.settings import get_db_session
from api.schemas.progress_schemas import (
    OverallProgress,
    CourseProgress,
    ChapterProgress,
    MistakeRecordDetail,
    PaginatedMistakes,
    MistakeStatistics,
    LearnerGoalBrief,
    LearnerGoalCreate,
    LearnerGoalUpdate,
    LearnerTaskBrief,
    LearnerTaskCreate,
    LearnerTaskUpdate,
)
from services.progress_service import ProgressService
from services.mistake_service import MistakeService
from services.goal_task_service import GoalTaskService


logger = logging.getLogger(__name__)
router = APIRouter(tags=["Progress, Mistakes, Goals"])


@router.get("/learners/{learner_id}/progress", response_model=OverallProgress)
async def get_overall_progress(
    learner_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = ProgressService(session)
    return await service.get_overall_progress(learner_id)


@router.get("/learners/{learner_id}/progress/courses/{course_id}", response_model=CourseProgress)
async def get_course_progress(
    learner_id: str,
    course_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = ProgressService(session)
    try:
        return await service.get_course_progress(learner_id, course_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/learners/{learner_id}/mistakes", response_model=PaginatedMistakes)
async def list_mistakes(
    learner_id: str,
    course_id: Optional[str] = Query(None),
    chapter_id: Optional[str] = Query(None),
    knowledge_point_id: Optional[str] = Query(None),
    is_resolved: Optional[bool] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: AsyncSession = Depends(get_db_session)
):
    service = MistakeService(session)
    return await service.list_mistakes(
        learner_id,
        course_id=course_id,
        chapter_id=chapter_id,
        knowledge_point_id=knowledge_point_id,
        is_resolved=is_resolved,
        page=page,
        page_size=page_size
    )


@router.get("/learners/{learner_id}/mistakes/statistics", response_model=MistakeStatistics)
async def get_mistake_statistics(
    learner_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = MistakeService(session)
    return await service.get_statistics(learner_id)


@router.get("/learners/{learner_id}/mistakes/{mistake_id}", response_model=MistakeRecordDetail)
async def get_mistake(
    learner_id: str,
    mistake_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = MistakeService(session)
    try:
        return await service.get_mistake(mistake_id, learner_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/learners/{learner_id}/mistakes/{mistake_id}/resolve", response_model=MistakeRecordDetail)
async def resolve_mistake(
    learner_id: str,
    mistake_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = MistakeService(session)
    try:
        mistake = await service.mark_resolved(mistake_id, learner_id)
        return await service.get_mistake(mistake_id, learner_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/learners/{learner_id}/goals", response_model=list[LearnerGoalBrief])
async def list_goals(
    learner_id: str,
    status: Optional[str] = Query(None),
    course_id: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db_session)
):
    service = GoalTaskService(session)
    return await service.list_goals(learner_id, status=status, course_id=course_id)


@router.post("/learners/{learner_id}/goals", response_model=LearnerGoalBrief)
async def create_goal(
    learner_id: str,
    data: LearnerGoalCreate,
    session: AsyncSession = Depends(get_db_session)
):
    service = GoalTaskService(session)
    goal = await service.create_goal(learner_id, data)
    return await service._goal_to_brief(goal)


@router.put("/learners/{learner_id}/goals/{goal_id}", response_model=LearnerGoalBrief)
async def update_goal(
    learner_id: str,
    goal_id: str,
    data: LearnerGoalUpdate,
    session: AsyncSession = Depends(get_db_session)
):
    service = GoalTaskService(session)
    try:
        goal = await service.update_goal(goal_id, learner_id, data)
        return await service._goal_to_brief(goal)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/learners/{learner_id}/goals/{goal_id}/complete", response_model=LearnerGoalBrief)
async def complete_goal(
    learner_id: str,
    goal_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = GoalTaskService(session)
    try:
        goal = await service.complete_goal(goal_id, learner_id)
        return await service._goal_to_brief(goal)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/learners/{learner_id}/tasks", response_model=list[LearnerTaskBrief])
async def list_tasks(
    learner_id: str,
    goal_id: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_db_session)
):
    service = GoalTaskService(session)
    return await service.list_tasks(learner_id, goal_id=goal_id, status=status)


@router.post("/learners/{learner_id}/tasks", response_model=LearnerTaskBrief)
async def create_task(
    learner_id: str,
    data: LearnerTaskCreate,
    session: AsyncSession = Depends(get_db_session)
):
    service = GoalTaskService(session)
    task = await service.create_task(learner_id, data)
    return await service._task_to_brief(task)


@router.post("/learners/{learner_id}/tasks/{task_id}/complete", response_model=LearnerTaskBrief)
async def complete_task(
    learner_id: str,
    task_id: str,
    session: AsyncSession = Depends(get_db_session)
):
    service = GoalTaskService(session)
    try:
        task = await service.complete_task(task_id, learner_id)
        return await service._task_to_brief(task)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
