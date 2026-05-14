from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from core.event_bus import Event
from core.learner_model import BKTParams, KnowledgeState as KnowledgeStateModel, LearnerModel
from core.spaced_repetition import ReviewItem as ReviewItemModel
from db.models import Attempt, EventLog, KnowledgeState, LearnerProfile, ReviewItem


class PersistenceService:
    def __init__(self, sessionmaker: async_sessionmaker[AsyncSession]) -> None:
        self._sessionmaker = sessionmaker

    async def touch_learner(self, learner_id: str) -> None:
        now = datetime.utcnow()
        async with self._sessionmaker() as session:
            stmt = (
                insert(LearnerProfile)
                .values(learner_id=learner_id, created_at=now, last_active_at=now)
                .on_conflict_do_update(
                    index_elements=[LearnerProfile.learner_id],
                    set_={"last_active_at": now},
                )
            )
            await session.execute(stmt)
            await session.commit()

    async def record_attempt(
        self,
        learner_id: str,
        knowledge_id: str,
        is_correct: bool,
        time_spent_seconds: float,
        correlation_id: str | None,
    ) -> None:
        async with self._sessionmaker() as session:
            session.add(
                Attempt(
                    learner_id=learner_id,
                    knowledge_id=knowledge_id,
                    is_correct=is_correct,
                    time_spent_seconds=time_spent_seconds,
                    correlation_id=correlation_id,
                )
            )
            await session.commit()

    async def log_event(self, event: Event) -> None:
        payload = event.model_dump(mode="json")
        async with self._sessionmaker() as session:
            stmt = insert(EventLog).values(
                event_id=event.id,
                type=event.type.value,
                source=event.source,
                learner_id=event.learner_id,
                timestamp=event.timestamp,
                correlation_id=event.correlation_id,
                payload=payload,
            )
            stmt = stmt.on_conflict_do_nothing(index_elements=[EventLog.event_id])
            await session.execute(stmt)
            await session.commit()

    async def load_learner_model(self, learner_id: str) -> LearnerModel:
        model = LearnerModel(learner_id, bkt_params=BKTParams())
        async with self._sessionmaker() as session:
            rows = (
                await session.execute(
                    select(KnowledgeState).where(KnowledgeState.learner_id == learner_id)
                )
            ).scalars()
            for row in rows:
                model.knowledge_states[row.knowledge_id] = KnowledgeStateModel(
                    knowledge_id=row.knowledge_id,
                    mastery=row.mastery,
                    alpha=row.alpha,
                    beta=row.beta,
                    attempts=row.attempts,
                    correct_count=row.correct_count,
                    last_attempt=row.last_attempt,
                    streak=row.streak,
                )
        model.total_interactions = sum(s.attempts for s in model.knowledge_states.values())
        return model

    async def save_learner_model(self, model: LearnerModel) -> None:
        now = datetime.utcnow()
        rows = []
        for s in model.knowledge_states.values():
            rows.append(
                {
                    "learner_id": model.learner_id,
                    "knowledge_id": s.knowledge_id,
                    "mastery": s.mastery,
                    "alpha": s.alpha,
                    "beta": s.beta,
                    "attempts": s.attempts,
                    "correct_count": s.correct_count,
                    "last_attempt": s.last_attempt,
                    "streak": s.streak,
                    "updated_at": now,
                }
            )
        if not rows:
            return
        async with self._sessionmaker() as session:
            stmt = insert(KnowledgeState).values(rows)
            stmt = stmt.on_conflict_do_update(
                index_elements=[KnowledgeState.learner_id, KnowledgeState.knowledge_id],
                set_={
                    "mastery": stmt.excluded.mastery,
                    "alpha": stmt.excluded.alpha,
                    "beta": stmt.excluded.beta,
                    "attempts": stmt.excluded.attempts,
                    "correct_count": stmt.excluded.correct_count,
                    "last_attempt": stmt.excluded.last_attempt,
                    "streak": stmt.excluded.streak,
                    "updated_at": stmt.excluded.updated_at,
                },
            )
            await session.execute(stmt)
            await session.commit()

    async def load_review_items(self, learner_id: str) -> dict[str, ReviewItemModel]:
        items: dict[str, ReviewItemModel] = {}
        async with self._sessionmaker() as session:
            rows = (
                await session.execute(select(ReviewItem).where(ReviewItem.learner_id == learner_id))
            ).scalars()
            for row in rows:
                items[row.knowledge_id] = ReviewItemModel(
                    knowledge_id=row.knowledge_id,
                    easiness_factor=row.easiness_factor,
                    interval_days=row.interval_days,
                    repetition=row.repetition,
                    next_review=row.next_review,
                    last_review=row.last_review,
                    total_reviews=row.total_reviews,
                )
        return items

    async def save_review_items(self, learner_id: str, items: dict[str, ReviewItemModel]) -> None:
        now = datetime.utcnow()
        rows = []
        for item in items.values():
            rows.append(
                {
                    "learner_id": learner_id,
                    "knowledge_id": item.knowledge_id,
                    "easiness_factor": item.easiness_factor,
                    "interval_days": item.interval_days,
                    "repetition": item.repetition,
                    "next_review": item.next_review,
                    "last_review": item.last_review,
                    "total_reviews": item.total_reviews,
                    "updated_at": now,
                }
            )
        if not rows:
            return
        async with self._sessionmaker() as session:
            stmt = insert(ReviewItem).values(rows)
            stmt = stmt.on_conflict_do_update(
                index_elements=[ReviewItem.learner_id, ReviewItem.knowledge_id],
                set_={
                    "easiness_factor": stmt.excluded.easiness_factor,
                    "interval_days": stmt.excluded.interval_days,
                    "repetition": stmt.excluded.repetition,
                    "next_review": stmt.excluded.next_review,
                    "last_review": stmt.excluded.last_review,
                    "total_reviews": stmt.excluded.total_reviews,
                    "updated_at": stmt.excluded.updated_at,
                },
            )
            await session.execute(stmt)
            await session.commit()

