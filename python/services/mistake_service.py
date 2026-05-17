from datetime import datetime
from typing import Any, Dict, List, Optional
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import (
    MistakeRecord,
    Exercise,
    KnowledgePoint,
)
from api.schemas.progress_schemas import (
    MistakeRecordBrief,
    MistakeRecordDetail,
    PaginatedMistakes,
    MistakeStatistics,
)


class MistakeService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def record_mistake(
        self,
        learner_id: str,
        exercise_id: str,
        answer: Any = None
    ) -> MistakeRecord:
        exercise_result = await self.session.execute(
            select(Exercise).where(Exercise.id == exercise_id)
        )
        exercise = exercise_result.scalar_one_or_none()
        
        if not exercise:
            raise ValueError(f"Exercise not found: {exercise_id}")
        
        existing_result = await self.session.execute(
            select(MistakeRecord)
            .where(
                and_(
                    MistakeRecord.learner_id == learner_id,
                    MistakeRecord.exercise_id == exercise_id
                )
            )
        )
        existing = existing_result.scalar_one_or_none()
        
        now = datetime.utcnow()
        
        if existing:
            existing.wrong_count += 1
            existing.last_wrong_at = now
            existing.last_attempt_answer = answer
            existing.updated_at = now
            await self.session.commit()
            await self.session.refresh(existing)
            return existing
        else:
            mistake = MistakeRecord(
            learner_id=learner_id,
            exercise_id=exercise_id,
            knowledge_point_id=exercise.knowledge_point_id,
            first_wrong_at=now,
            last_wrong_at=now,
            last_attempt_answer=answer
        )
        self.session.add(mistake)
        await self.session.commit()
        await self.session.refresh(mistake)
        return mistake

    async def mark_resolved(
        self,
        mistake_id: str,
        learner_id: str
    ) -> MistakeRecord:
        result = await self.session.execute(
            select(MistakeRecord)
            .where(
                and_(
                    MistakeRecord.id == mistake_id,
                    MistakeRecord.learner_id == learner_id
                )
            )
        )
        mistake = result.scalar_one_or_none()
        
        if not mistake:
            raise ValueError(f"Mistake not found: {mistake_id}")
        
        now = datetime.utcnow()
        mistake.is_resolved = True
        mistake.resolved_at = now
        mistake.updated_at = now
        await self.session.commit()
        await self.session.refresh(mistake)
        return mistake

    async def list_mistakes(
        self,
        learner_id: str,
        course_id: Optional[str] = None,
        chapter_id: Optional[str] = None,
        knowledge_point_id: Optional[str] = None,
        is_resolved: Optional[bool] = None,
        page: int = 1,
        page_size: int = 20
    ) -> PaginatedMistakes:
        stmt = select(MistakeRecord).where(MistakeRecord.learner_id == learner_id)
        
        if knowledge_point_id:
            stmt = stmt.where(MistakeRecord.knowledge_point_id == knowledge_point_id)
        
        if is_resolved is not None:
            stmt = stmt.where(MistakeRecord.is_resolved == is_resolved)
        
        if course_id or chapter_id:
            stmt = stmt.join(Exercise, Exercise.id == MistakeRecord.exercise_id)
            if course_id:
                stmt = stmt.where(Exercise.course_id == course_id)
            if chapter_id:
                stmt = stmt.where(Exercise.chapter_id == chapter_id)
        
        total_result = await self.session.execute(
            select(func.count(MistakeRecord.id))
            .select_from(MistakeRecord)
            .where(MistakeRecord.learner_id == learner_id)
        )
        total = total_result.scalar_one_or_none() or 0
        
        offset = (page - 1) * page_size
        stmt = stmt.order_by(MistakeRecord.last_wrong_at.desc()).offset(offset).limit(page_size)
        
        result = await self.session.execute(stmt)
        mistakes = list(result.scalars().all())
        
        mistake_briefs = []
        for mistake in mistakes:
            brief = await self._to_brief(mistake)
            mistake_briefs.append(brief)
        
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        
        return PaginatedMistakes(
            learner_id=learner_id,
            mistakes=mistake_briefs,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages
        )

    async def get_mistake(
        self,
        mistake_id: str,
        learner_id: str
    ) -> MistakeRecordDetail:
        result = await self.session.execute(
            select(MistakeRecord)
            .where(
                and_(
                    MistakeRecord.id == mistake_id,
                    MistakeRecord.learner_id == learner_id
                )
            )
        )
        mistake = result.scalar_one_or_none()
        
        if not mistake:
            raise ValueError(f"Mistake not found: {mistake_id}")
        
        return await self._to_detail(mistake)

    async def get_statistics(
        self,
        learner_id: str
    ) -> MistakeStatistics:
        total_result = await self.session.execute(
            select(func.count(MistakeRecord.id))
            .where(MistakeRecord.learner_id == learner_id)
        )
        total = total_result.scalar_one_or_none() or 0
        
        resolved_result = await self.session.execute(
            select(func.count(MistakeRecord.id))
            .where(
                and_(
                    MistakeRecord.learner_id == learner_id,
                    MistakeRecord.is_resolved == True
                )
            )
        )
        resolved = resolved_result.scalar_one_or_none() or 0
        
        by_kp_result = await self.session.execute(
            select(
                MistakeRecord.knowledge_point_id,
                func.count(MistakeRecord.id)
            )
            .where(MistakeRecord.learner_id == learner_id)
            .group_by(MistakeRecord.knowledge_point_id)
        )
        by_kp = []
        for kp_id, count in by_kp_result.all():
            kp_result = await self.session.execute(
                select(KnowledgePoint).where(KnowledgePoint.id == kp_id)
            )
            kp = kp_result.scalar_one_or_none()
            kp_name = kp.name if kp else kp_id
            by_kp.append({
                "knowledge_point_id": kp_id,
                "knowledge_point_name": kp_name,
                "mistake_count": count
            })
        
        return MistakeStatistics(
            learner_id=learner_id,
            total_mistakes=total,
            resolved_mistakes=resolved,
            unresolved_mistakes=total - resolved,
            by_knowledge_point=by_kp
        )

    async def _to_brief(self, mistake: MistakeRecord) -> MistakeRecordBrief:
        exercise_result = await self.session.execute(
            select(Exercise).where(Exercise.id == mistake.exercise_id)
        )
        exercise = exercise_result.scalar_one_or_none()
        
        kp_result = await self.session.execute(
            select(KnowledgePoint).where(KnowledgePoint.id == mistake.knowledge_point_id)
        )
        kp = kp_result.scalar_one_or_none()
        
        return MistakeRecordBrief(
            id=mistake.id,
            exercise_id=mistake.exercise_id,
            exercise_code=exercise.code if exercise else "",
            exercise_type=exercise.type if exercise else "",
            knowledge_point_id=mistake.knowledge_point_id,
            knowledge_point_name=kp.name if kp else "",
            first_wrong_at=mistake.first_wrong_at,
            last_wrong_at=mistake.last_wrong_at,
            wrong_count=mistake.wrong_count,
            is_resolved=mistake.is_resolved
        )

    async def _to_detail(self, mistake: MistakeRecord) -> MistakeRecordDetail:
        brief = await self._to_brief(mistake)
        
        exercise_result = await self.session.execute(
            select(Exercise).where(Exercise.id == mistake.exercise_id)
        )
        exercise = exercise_result.scalar_one_or_none()
        
        content = exercise.content if exercise else {}
        correct_answer = exercise.answer if exercise else {}
        analysis = exercise.analysis if exercise else None
        
        return MistakeRecordDetail(
            **brief.model_dump(),
            content=content,
            correct_answer=correct_answer,
            analysis=analysis,
            last_attempt_answer=mistake.last_attempt_answer
        )
