from datetime import datetime
from typing import Dict, List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import (
    Course,
    Chapter,
    KnowledgePoint,
    KnowledgeState,
)
from api.schemas.progress_schemas import (
    CourseProgress,
    ChapterProgress,
    KnowledgePointProgress,
    OverallProgress,
)


class ProgressService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_overall_progress(
        self,
        learner_id: str
    ) -> OverallProgress:
        stmt = select(Course).where(Course.is_active == True)
        result = await self.session.execute(stmt)
        courses = list(result.scalars().all())
        
        course_progresses = []
        completed_courses = 0
        
        for course in courses:
            cp = await self.get_course_progress(learner_id, course.id)
            course_progresses.append(cp)
            if cp.overall_progress >= 1.0:
                completed_courses += 1
        
        return OverallProgress(
            learner_id=learner_id,
            total_courses=len(courses),
            completed_courses=completed_courses,
            courses=course_progresses
        )

    async def get_course_progress(
        self,
        learner_id: str,
        course_id: str
    ) -> CourseProgress:
        course_result = await self.session.execute(
            select(Course).where(Course.id == course_id)
        )
        course = course_result.scalar_one_or_none()
        
        if not course:
            raise ValueError(f"Course not found: {course_id}")
        
        chapter_result = await self.session.execute(
            select(Chapter)
            .where(Chapter.course_id == course_id)
            .order_by(Chapter.order_index)
        )
        chapters = list(chapter_result.scalars().all())
        
        chapter_progresses = []
        total_kps = 0
        mastered_kps = 0
        completed_chapters = 0
        
        for chapter in chapters:
            chapter_p = await self.get_chapter_progress(learner_id, chapter.id)
            chapter_progresses.append(chapter_p)
            total_kps += len(chapter_p.knowledge_points)
            mastered_kps += sum(1 for kp in chapter_p.knowledge_points if kp.is_mastered)
            if chapter_p.progress >= 1.0:
                completed_chapters += 1
        
        overall_progress = 0.0
        if total_kps > 0:
            overall_progress = mastered_kps / total_kps
        
        return CourseProgress(
            course_id=course_id,
            course_name=course.name,
            overall_progress=overall_progress,
            total_chapters=len(chapters),
            completed_chapters=completed_chapters,
            total_knowledge_points=total_kps,
            mastered_knowledge_points=mastered_kps,
            chapters=chapter_progresses
        )

    async def get_chapter_progress(
        self,
        learner_id: str,
        chapter_id: str
    ) -> ChapterProgress:
        chapter_result = await self.session.execute(
            select(Chapter).where(Chapter.id == chapter_id)
        )
        chapter = chapter_result.scalar_one_or_none()
        
        if not chapter:
            raise ValueError(f"Chapter not found: {chapter_id}")
        
        kp_result = await self.session.execute(
            select(KnowledgePoint)
            .where(
                KnowledgePoint.chapter_id == chapter_id,
                KnowledgePoint.is_active == True
            )
            .order_by(KnowledgePoint.order_index)
        )
        knowledge_points = list(kp_result.scalars().all())
        
        kp_progresses = []
        mastered_count = 0
        
        for kp in knowledge_points:
            kp_p = await self._get_knowledge_point_progress(
                learner_id, kp
            )
            kp_progresses.append(kp_p)
            if kp_p.is_mastered:
                mastered_count += 1
        
        progress = 0.0
        if knowledge_points:
            progress = mastered_count / len(knowledge_points)
        
        return ChapterProgress(
            chapter_id=chapter_id,
            chapter_name=chapter.name,
            progress=progress,
            knowledge_points=kp_progresses
        )

    async def _get_knowledge_point_progress(
        self,
        learner_id: str,
        kp: KnowledgePoint
    ) -> KnowledgePointProgress:
        kp_id = kp.id
        
        state_result = await self.session.execute(
            select(KnowledgeState)
            .where(
                KnowledgeState.learner_id == learner_id,
                KnowledgeState.knowledge_id == kp_id
            )
        )
        state = state_result.scalar_one_or_none()
        
        mastery = state.mastery if state else 0.1
        is_mastered = mastery >= 0.6
        attempts = state.attempts if state else 0
        correct_count = state.correct_count if state else 0
        wrong_streak = state.wrong_streak if state else 0
        last_attempt_at = state.last_attempt if state else None
        
        return KnowledgePointProgress(
            knowledge_point_id=kp_id,
            code=kp.code,
            name=kp.name,
            mastery=mastery,
            is_mastered=is_mastered,
            attempts=attempts,
            correct_count=correct_count,
            wrong_streak=wrong_streak,
            last_attempt_at=last_attempt_at
        )
