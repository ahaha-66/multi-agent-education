from __future__ import annotations

from datetime import datetime

from sqlalchemy import select, update
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
            existing = await session.get(LearnerProfile, learner_id)
            if existing:
                existing.last_active_at = now
            else:
                session.add(LearnerProfile(
                    learner_id=learner_id,
                    created_at=now,
                    last_active_at=now,
                ))
            await session.commit()

    async def record_attempt(
        self,
        learner_id: str,
        knowledge_id: str,
        is_correct: bool,
        time_spent_seconds: float,
        correlation_id: str | None,
        exercise_id: str | None = None,
    ) -> None:
        async with self._sessionmaker() as session:
            session.add(
                Attempt(
                    learner_id=learner_id,
                    knowledge_id=knowledge_id,
                    exercise_id=exercise_id,
                    is_correct=is_correct,
                    time_spent_seconds=time_spent_seconds,
                    correlation_id=correlation_id,
                )
            )
            await session.commit()

    async def log_event(self, event: Event) -> None:
        payload = event.model_dump(mode="json")
        async with self._sessionmaker() as session:
            existing = await session.get(EventLog, event.id)
            if not existing:
                session.add(EventLog(
                    event_id=event.id,
                    type=event.type.value,
                    source=event.source,
                    learner_id=event.learner_id,
                    timestamp=event.timestamp,
                    correlation_id=event.correlation_id,
                    payload=payload,
                ))
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
                    wrong_streak=row.wrong_streak,
                    last_attempt=row.last_attempt,
                    streak=row.streak,
                )
        model.total_interactions = sum(s.attempts for s in model.knowledge_states.values())
        return model

    async def save_learner_model(self, model: LearnerModel) -> None:
        now = datetime.utcnow()
        async with self._sessionmaker() as session:
            for s in model.knowledge_states.values():
                existing = await session.get(KnowledgeState, (model.learner_id, s.knowledge_id))
                if existing:
                    existing.mastery = s.mastery
                    existing.alpha = s.alpha
                    existing.beta = s.beta
                    existing.attempts = s.attempts
                    existing.correct_count = s.correct_count
                    existing.wrong_streak = s.wrong_streak
                    existing.last_attempt = s.last_attempt
                    existing.streak = s.streak
                    existing.version = existing.version + 1
                    existing.updated_at = now
                else:
                    session.add(KnowledgeState(
                        learner_id=model.learner_id,
                        knowledge_id=s.knowledge_id,
                        mastery=s.mastery,
                        alpha=s.alpha,
                        beta=s.beta,
                        attempts=s.attempts,
                        correct_count=s.correct_count,
                        wrong_streak=s.wrong_streak,
                        last_attempt=s.last_attempt,
                        streak=s.streak,
                        version=1,
                        updated_at=now,
                    ))
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
                    due_at=row.due_at,
                    last_review=row.last_review,
                    total_reviews=row.total_reviews,
                )
        return items

    async def save_review_items(self, learner_id: str, items: dict[str, ReviewItemModel]) -> None:
        now = datetime.utcnow()
        async with self._sessionmaker() as session:
            for item in items.values():
                existing = await session.get(ReviewItem, (learner_id, item.knowledge_id))
                if existing:
                    existing.easiness_factor = item.easiness_factor
                    existing.interval_days = item.interval_days
                    existing.repetition = item.repetition
                    existing.due_at = item.due_at
                    existing.last_review = item.last_review
                    existing.total_reviews = item.total_reviews
                    existing.version = existing.version + 1
                    existing.updated_at = now
                else:
                    session.add(ReviewItem(
                        learner_id=learner_id,
                        knowledge_id=item.knowledge_id,
                        easiness_factor=item.easiness_factor,
                        interval_days=item.interval_days,
                        repetition=item.repetition,
                        due_at=item.due_at,
                        last_review=item.last_review,
                        total_reviews=item.total_reviews,
                        version=1,
                        updated_at=now,
                    ))
            await session.commit()

