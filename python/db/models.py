import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Float, Index, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base


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

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learner_id: Mapped[str] = mapped_column(String, index=True)
    knowledge_id: Mapped[str] = mapped_column(String, index=True)
    exercise_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    time_spent_seconds: Mapped[float] = mapped_column(Float, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    correlation_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)


class EventLog(Base):
    __tablename__ = "event_log"

    event_id: Mapped[str] = mapped_column(String, primary_key=True)
    type: Mapped[str] = mapped_column(String, index=True)
    source: Mapped[str] = mapped_column(String)
    learner_id: Mapped[str] = mapped_column(String, index=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, index=True)
    correlation_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)
    status: Mapped[str] = mapped_column(String, default="ok")
    payload: Mapped[dict] = mapped_column(JSONB, default=dict)


class Course(Base):
    __tablename__ = "course"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    code: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    subject: Mapped[str] = mapped_column(String, index=True)
    version: Mapped[str] = mapped_column(String, default="1.0")
    grade_level: Mapped[int | None] = mapped_column(Integer, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow
    )


class Chapter(Base):
    __tablename__ = "chapter"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    course_id: Mapped[str] = mapped_column(String, index=True)
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
    chapter_id: Mapped[str] = mapped_column(String, index=True)
    course_id: Mapped[str] = mapped_column(String, index=True)
    code: Mapped[str] = mapped_column(String, unique=True, index=True)
    name: Mapped[str] = mapped_column(String)
    difficulty: Mapped[float] = mapped_column(Float, default=0.5)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list)
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
    )


class KnowledgeEdge(Base):
    __tablename__ = "knowledge_edge"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    source_kp_id: Mapped[str] = mapped_column(String, index=True)
    target_kp_id: Mapped[str] = mapped_column(String, index=True)
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
    knowledge_point_id: Mapped[str] = mapped_column(String, index=True)
    chapter_id: Mapped[str] = mapped_column(String, index=True)
    course_id: Mapped[str] = mapped_column(String, index=True)
    code: Mapped[str] = mapped_column(String, unique=True, index=True)
    type: Mapped[str] = mapped_column(String, default="single_choice")
    difficulty: Mapped[float] = mapped_column(Float, default=0.5)
    content: Mapped[dict] = mapped_column(JSONB, default=dict)
    answer: Mapped[dict] = mapped_column(JSONB, default=dict)
    analysis: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    hint_levels: Mapped[list[dict]] = mapped_column(JSONB, default=list)
    tags: Mapped[list[str]] = mapped_column(JSONB, default=list)
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
    )


class LearnerExerciseHistory(Base):
    __tablename__ = "learner_exercise_history"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    learner_id: Mapped[str] = mapped_column(String, index=True)
    exercise_id: Mapped[str] = mapped_column(String, index=True)
    is_correct: Mapped[bool] = mapped_column(Boolean, default=False)
    attempt_count: Mapped[int] = mapped_column(Integer, default=1)
    last_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    first_attempt_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    correlation_id: Mapped[str | None] = mapped_column(String, nullable=True, index=True)

    __table_args__ = (
        Index("ix_learner_exercise_learner_id", "learner_id"),
        Index("ix_learner_exercise_exercise_id", "exercise_id"),
    )
