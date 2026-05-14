"""
内存版本的持久化服务 - 用于测试和演示
无需 PostgreSQL，直接使用内存存储
"""

import uuid
from datetime import datetime
from typing import Any
from core.event_bus import Event
from core.learner_model import LearnerModel, BKTParams, KnowledgeState as KnowledgeStateModel
from core.spaced_repetition import ReviewItem as ReviewItemModel


class InMemoryPersistenceService:
    """内存版本的持久化服务，用于测试演示"""

    def __init__(self) -> None:
        self._learners: dict[str, dict] = {}
        self._knowledge_states: dict[str, dict[tuple[str, str], dict]] = {}
        self._review_items: dict[str, dict[tuple[str, str], dict]] = {}
        self._attempts: list[dict] = []
        self._events: list[dict] = []

    async def touch_learner(self, learner_id: str) -> None:
        now = datetime.utcnow()
        if learner_id not in self._learners:
            self._learners[learner_id] = {
                "learner_id": learner_id,
                "created_at": now,
                "last_active_at": now,
            }
        else:
            self._learners[learner_id]["last_active_at"] = now

    async def record_attempt(
        self,
        learner_id: str,
        knowledge_id: str,
        is_correct: bool,
        time_spent_seconds: float,
        correlation_id: str | None,
        exercise_id: str | None = None,
    ) -> None:
        self._attempts.append({
            "id": str(uuid.uuid4()),
            "learner_id": learner_id,
            "knowledge_id": knowledge_id,
            "exercise_id": exercise_id,
            "is_correct": is_correct,
            "time_spent_seconds": time_spent_seconds,
            "created_at": datetime.utcnow(),
            "correlation_id": correlation_id,
        })

    async def log_event(self, event: Event) -> None:
        self._events.append({
            "event_id": event.id,
            "type": event.type.value,
            "source": event.source,
            "learner_id": event.learner_id,
            "timestamp": event.timestamp,
            "correlation_id": event.correlation_id,
            "payload": event.model_dump(mode="json"),
        })

    async def load_learner_model(self, learner_id: str) -> LearnerModel:
        model = LearnerModel(learner_id, bkt_params=BKTParams())
        if learner_id in self._knowledge_states:
            for (lid, kid), state in self._knowledge_states[learner_id].items():
                model.knowledge_states[kid] = KnowledgeStateModel(
                    knowledge_id=kid,
                    mastery=state["mastery"],
                    alpha=state["alpha"],
                    beta=state["beta"],
                    attempts=state["attempts"],
                    correct_count=state["correct_count"],
                    wrong_streak=state["wrong_streak"],
                    last_attempt=state["last_attempt"],
                    streak=state["streak"],
                )
        model.total_interactions = sum(s.attempts for s in model.knowledge_states.values())
        return model

    async def save_learner_model(self, model: LearnerModel) -> None:
        if learner_id := model.learner_id:
            if learner_id not in self._knowledge_states:
                self._knowledge_states[learner_id] = {}
            for s in model.knowledge_states.values():
                self._knowledge_states[learner_id][(learner_id, s.knowledge_id)] = {
                    "mastery": s.mastery,
                    "alpha": s.alpha,
                    "beta": s.beta,
                    "attempts": s.attempts,
                    "correct_count": s.correct_count,
                    "wrong_streak": s.wrong_streak,
                    "last_attempt": s.last_attempt,
                    "streak": s.streak,
                }

    async def load_review_items(self, learner_id: str) -> dict[str, ReviewItemModel]:
        items: dict[str, ReviewItemModel] = {}
        if learner_id in self._review_items:
            for (lid, kid), item_data in self._review_items[learner_id].items():
                items[kid] = ReviewItemModel(
                    knowledge_id=kid,
                    easiness_factor=item_data["easiness_factor"],
                    interval_days=item_data["interval_days"],
                    repetition=item_data["repetition"],
                    due_at=item_data["due_at"],
                    last_review=item_data["last_review"],
                    total_reviews=item_data["total_reviews"],
                )
        return items

    async def save_review_items(self, learner_id: str, items: dict[str, ReviewItemModel]) -> None:
        if learner_id not in self._review_items:
            self._review_items[learner_id] = {}
        for kid, item in items.items():
            self._review_items[learner_id][(learner_id, kid)] = {
                "easiness_factor": item.easiness_factor,
                "interval_days": item.interval_days,
                "repetition": item.repetition,
                "due_at": item.due_at,
                "last_review": item.last_review,
                "total_reviews": item.total_reviews,
            }

    def get_all_events(self) -> list[dict]:
        """获取所有事件，用于调试"""
        return self._events.copy()

    def get_events_by_learner(self, learner_id: str) -> list[dict]:
        """按学习者获取事件"""
        return [e for e in self._events if e["learner_id"] == learner_id]

    def get_events_by_correlation(self, correlation_id: str) -> list[dict]:
        """按 correlation_id 获取事件链"""
        return [e for e in self._events if e["correlation_id"] == correlation_id]

    def clear(self) -> None:
        """清空所有数据"""
        self._learners.clear()
        self._knowledge_states.clear()
        self._review_items.clear()
        self._attempts.clear()
        self._events.clear()
