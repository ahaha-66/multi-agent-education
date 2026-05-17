import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Index, Integer, String, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


def _uuid_str() -> str:
    return str(uuid.uuid4())


class LearnerProfile(Base):
    __tablename__ = "learner_profile"

    learner_id: Mapped[str] = mapped_column(String, primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    last_active_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )


class KnowledgeState(Base):
    __tablename__ = "knowledge_state"

    learner_id: Mapped[str] = mapped_column(String, primary_key=True)
    knowledge_id: Mapped[str] = mapped_column(String, primary_key=True)

    mastery: Mapped[float] = mapped_column(Float, default=0.1)
    alpha: Mapped[float] = mapped_column(Float, default=1.0)
    beta: Mapped[float] = mapped_column(Float, default=9.0)
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    correct_count: Mapped[int] = mapped_column(Integer, default=0)
    wrong_streak: Mapped[int] = mapped_column(Integer, default=0)
    last_attempt: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    streak: Mapped[int] = mapped_column(Integer, default=0)
    version: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (Index("ix_knowledge_state_learner_id", "learner_id"),)


class ReviewItem(Base):
    __tablename__ = "review_item"

    learner_id: Mapped[str] = mapped_column(String, primary_key=True)
    knowledge_id: Mapped[str] = mapped_column(String, primary_key=True)

    easiness_factor: Mapped[float] = mapped_column(Float, default=2.5)
    interval_days: Mapped[float] = mapped_column(Float, default=0)
    repetition: Mapped[int] = mapped_column(Integer, default=0)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    last_review: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    total_reviews: Mapped[int] = mapped_column(Integer, default=0)
    version: Mapped[int] = mapped_column(Integer, default=1)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (Index("ix_review_item_learner_id_due_at", "learner_id", "due_at"),)


class Attempt(Base):
    __tablename__ = "attempt"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid_str)
    learner_id: Mapped[str] = mapped_column(String)
    knowledge_id: Mapped[str] = mapped_column(String)
    exercise_id: Mapped[str | None] = mapped_column(String, nullable=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    time_spent_seconds: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    correlation_id: Mapped[str | None] = mapped_column(String, nullable=True)

    __table_args__ = (
        Index("ix_attempt_learner_id", "learner_id"),
        Index("ix_attempt_knowledge_id", "knowledge_id"),
        Index("ix_attempt_exercise_id", "exercise_id"),
        Index("ix_attempt_created_at", "created_at"),
        Index("ix_attempt_correlation_id", "correlation_id"),
    )


class EventLog(Base):
    __tablename__ = "event_log"

    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    type: Mapped[str] = mapped_column(String)
    source: Mapped[str] = mapped_column(String)
    learner_id: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    correlation_id: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="ok")
    payload: Mapped[dict] = mapped_column(JSON, default=dict)

    __table_args__ = (
        Index("ix_event_log_type", "type"),
        Index("ix_event_log_learner_id", "learner_id"),
        Index("ix_event_log_timestamp", "timestamp"),
        Index("ix_event_log_correlation_id", "correlation_id"),
    )


class Course(Base):
    __tablename__ = "course"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String)
    subject: Mapped[str] = mapped_column(String)
    version: Mapped[str] = mapped_column(String, default="1.0")
    grade_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        Index("ix_course_code", "code"),
        Index("ix_course_subject", "subject"),
    )


class Chapter(Base):
    __tablename__ = "chapter"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    course_id: Mapped[str] = mapped_column(String)
    code: Mapped[str] = mapped_column(String)
    name: Mapped[str] = mapped_column(String)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (Index("ix_chapter_course_id", "course_id"),)


class KnowledgePoint(Base):
    __tablename__ = "knowledge_point"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    chapter_id: Mapped[str] = mapped_column(String)
    course_id: Mapped[str] = mapped_column(String)
    code: Mapped[str] = mapped_column(String, unique=True)
    name: Mapped[str] = mapped_column(String)
    difficulty: Mapped[float] = mapped_column(Float, default=0.5)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    version: Mapped[str] = mapped_column(String, default="1.0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        Index("ix_knowledge_point_chapter_id", "chapter_id"),
        Index("ix_knowledge_point_course_id", "course_id"),
        Index("ix_knowledge_point_code", "code"),
    )


class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edge"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    source_kp_id: Mapped[str] = mapped_column(String)
    target_kp_id: Mapped[str] = mapped_column(String)
    relation_type: Mapped[str] = mapped_column(String, default="prerequisite")
    strength: Mapped[float] = mapped_column(Float, default=1.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_knowledge_edge_source", "source_kp_id"),
        Index("ix_knowledge_edge_target", "target_kp_id"),
    )


class Exercise(Base):
    __tablename__ = "exercise"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    knowledge_point_id: Mapped[str] = mapped_column(String)
    chapter_id: Mapped[str] = mapped_column(String)
    course_id: Mapped[str] = mapped_column(String)
    code: Mapped[str] = mapped_column(String, unique=True)
    type: Mapped[str] = mapped_column(String, default="single_choice")
    difficulty: Mapped[float] = mapped_column(Float, default=0.5)
    content: Mapped[dict] = mapped_column(JSON, default=dict)
    answer: Mapped[dict] = mapped_column(JSON, default=dict)
    analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    hint_levels: Mapped[list] = mapped_column(JSON, default=list)
    tags: Mapped[list] = mapped_column(JSON, default=list)
    version: Mapped[str] = mapped_column(String, default="1.0")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )

    __table_args__ = (
        Index("ix_exercise_kp_id", "knowledge_point_id"),
        Index("ix_exercise_chapter_id", "chapter_id"),
        Index("ix_exercise_course_id", "course_id"),
        Index("ix_exercise_code", "code"),
    )


class LearnerExerciseHistory(Base):
    __tablename__ = "learner_exercise_history"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid_str)
    learner_id: Mapped[str] = mapped_column(String)
    exercise_id: Mapped[str] = mapped_column(String)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    attempt_count: Mapped[int] = mapped_column(Integer, default=1)
    last_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    first_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    correlation_id: Mapped[str | None] = mapped_column(String, nullable=True)

    __table_args__ = (
        Index("ix_learner_exercise_learner_id", "learner_id"),
        Index("ix_learner_exercise_exercise_id", "exercise_id"),
        Index("ix_learner_exercise_correlation_id", "correlation_id"),
    )


class LearnerGoal(Base):
    __tablename__ = "learner_goal"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid_str)
    learner_id: Mapped[str] = mapped_column(String)
    course_id: Mapped[str | None] = mapped_column(String, nullable=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    target_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[str] = mapped_column(String, default="pending")
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        Index("ix_learner_goal_learner_id", "learner_id"),
        Index("ix_learner_goal_status", "status"),
    )


class LearnerTask(Base):
    __tablename__ = "learner_task"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid_str)
    goal_id: Mapped[str | None] = mapped_column(String, nullable=True)
    learner_id: Mapped[str] = mapped_column(String)
    knowledge_point_id: Mapped[str | None] = mapped_column(String, nullable=True)
    exercise_id: Mapped[str | None] = mapped_column(String, nullable=True)
    title: Mapped[str] = mapped_column(String)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    type: Mapped[str] = mapped_column(String, default="learn")
    status: Mapped[str] = mapped_column(String, default="pending")
    priority: Mapped[int] = mapped_column(Integer, default=3)
    due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    order_index: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_learner_task_goal_id", "goal_id"),
        Index("ix_learner_task_learner_id", "learner_id"),
        Index("ix_learner_task_kp_id", "knowledge_point_id"),
        Index("ix_learner_task_exercise_id", "exercise_id"),
        Index("ix_learner_task_status", "status"),
    )


class MistakeRecord(Base):
    __tablename__ = "mistake_record"
    id: Mapped[str] = mapped_column(String, primary_key=True, default=_uuid_str)
    learner_id: Mapped[str] = mapped_column(String)
    exercise_id: Mapped[str] = mapped_column(String)
    knowledge_point_id: Mapped[str] = mapped_column(String)
    first_wrong_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    last_wrong_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    wrong_count: Mapped[int] = mapped_column(Integer, default=1)
    last_attempt_answer: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    is_resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)

    __table_args__ = (
        Index("ix_mistake_record_learner_id", "learner_id"),
        Index("ix_mistake_record_exercise_id", "exercise_id"),
        Index("ix_mistake_record_kp_id", "knowledge_point_id"),
    )
