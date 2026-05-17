from datetime import datetime
from typing import List, Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import LearnerGoal, LearnerTask
from api.schemas.progress_schemas import (
    LearnerGoalBrief,
    LearnerGoalCreate,
    LearnerGoalUpdate,
    LearnerTaskBrief,
    LearnerTaskCreate,
    LearnerTaskUpdate,
)


class GoalTaskService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_goal(
        self,
        learner_id: str,
        data: LearnerGoalCreate
    ) -> LearnerGoal:
        now = datetime.utcnow()
        goal = LearnerGoal(
            learner_id=learner_id,
            title=data.title,
            description=data.description,
            course_id=data.course_id,
            target_date=data.target_date,
            status="pending",
            progress=0.0,
            created_at=now,
            updated_at=now
        )
        self.session.add(goal)
        await self.session.commit()
        await self.session.refresh(goal)
        return goal

    async def list_goals(
        self,
        learner_id: str,
        status: Optional[str] = None,
        course_id: Optional[str] = None
    ) -> List[LearnerGoalBrief]:
        stmt = select(LearnerGoal).where(LearnerGoal.learner_id == learner_id)
        
        if status:
            stmt = stmt.where(LearnerGoal.status == status)
        if course_id:
            stmt = stmt.where(LearnerGoal.course_id == course_id)
        
        stmt = stmt.order_by(LearnerGoal.created_at.desc())
        
        result = await self.session.execute(stmt)
        goals = list(result.scalars().all())
        
        return [await self._goal_to_brief(g) for g in goals]

    async def update_goal(
        self,
        goal_id: str,
        learner_id: str,
        data: LearnerGoalUpdate
    ) -> LearnerGoal:
        result = await self.session.execute(
            select(LearnerGoal)
            .where(
                and_(
                    LearnerGoal.id == goal_id,
                    LearnerGoal.learner_id == learner_id
                )
            )
        )
        goal = result.scalar_one_or_none()
        
        if not goal:
            raise ValueError(f"Goal not found: {goal_id}")
        
        if data.title is not None:
            goal.title = data.title
        if data.description is not None:
            goal.description = data.description
        if data.target_date is not None:
            goal.target_date = data.target_date
        if data.progress is not None:
            goal.progress = max(0.0, min(1.0, data.progress))
        
        goal.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(goal)
        return goal

    async def complete_goal(
        self,
        goal_id: str,
        learner_id: str
    ) -> LearnerGoal:
        result = await self.session.execute(
            select(LearnerGoal)
            .where(
                and_(
                    LearnerGoal.id == goal_id,
                    LearnerGoal.learner_id == learner_id
                )
            )
        )
        goal = result.scalar_one_or_none()
        
        if not goal:
            raise ValueError(f"Goal not found: {goal_id}")
        
        now = datetime.utcnow()
        goal.status = "completed"
        goal.progress = 1.0
        goal.completed_at = now
        goal.updated_at = now
        await self.session.commit()
        await self.session.refresh(goal)
        return goal

    async def create_task(
        self,
        learner_id: str,
        data: LearnerTaskCreate
    ) -> LearnerTask:
        now = datetime.utcnow()
        task = LearnerTask(
            learner_id=learner_id,
            title=data.title,
            description=data.description,
            goal_id=data.goal_id,
            knowledge_point_id=data.knowledge_point_id,
            exercise_id=data.exercise_id,
            type=data.type,
            status="pending",
            priority=data.priority,
            due_date=data.due_date,
            order_index=0,
            created_at=now,
            updated_at=now
        )
        self.session.add(task)
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def list_tasks(
        self,
        learner_id: str,
        goal_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[LearnerTaskBrief]:
        stmt = select(LearnerTask).where(LearnerTask.learner_id == learner_id)
        
        if goal_id:
            stmt = stmt.where(LearnerTask.goal_id == goal_id)
        if status:
            stmt = stmt.where(LearnerTask.status == status)
        
        stmt = stmt.order_by(
            LearnerTask.priority, LearnerTask.order_index, LearnerTask.created_at
        )
        
        result = await self.session.execute(stmt)
        tasks = list(result.scalars().all())
        
        return [await self._task_to_brief(t) for t in tasks]

    async def update_task(
        self,
        task_id: str,
        learner_id: str,
        data: LearnerTaskUpdate
    ) -> LearnerTask:
        result = await self.session.execute(
            select(LearnerTask)
            .where(
                and_(
                    LearnerTask.id == task_id,
                    LearnerTask.learner_id == learner_id
                )
            )
        )
        task = result.scalar_one_or_none()
        
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        if data.title is not None:
            task.title = data.title
        if data.description is not None:
            task.description = data.description
        if data.priority is not None:
            task.priority = data.priority
        if data.due_date is not None:
            task.due_date = data.due_date
        
        task.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def complete_task(
        self,
        task_id: str,
        learner_id: str
    ) -> LearnerTask:
        result = await self.session.execute(
            select(LearnerTask)
            .where(
                and_(
                    LearnerTask.id == task_id,
                    LearnerTask.learner_id == learner_id
                )
            )
        )
        task = result.scalar_one_or_none()
        
        if not task:
            raise ValueError(f"Task not found: {task_id}")
        
        task.status = "completed"
        task.updated_at = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(task)
        return task

    async def _goal_to_brief(self, goal: LearnerGoal) -> LearnerGoalBrief:
        return LearnerGoalBrief(
            id=goal.id,
            title=goal.title,
            description=goal.description,
            course_id=goal.course_id,
            status=goal.status,
            progress=goal.progress,
            target_date=goal.target_date,
            created_at=goal.created_at,
            updated_at=goal.updated_at,
            completed_at=goal.completed_at
        )

    async def _task_to_brief(self, task: LearnerTask) -> LearnerTaskBrief:
        return LearnerTaskBrief(
            id=task.id,
            title=task.title,
            description=task.description,
            goal_id=task.goal_id,
            knowledge_point_id=task.knowledge_point_id,
            exercise_id=task.exercise_id,
            type=task.type,
            status=task.status,
            priority=task.priority,
            due_date=task.due_date,
            order_index=task.order_index,
            created_at=task.created_at,
            updated_at=task.updated_at
        )
