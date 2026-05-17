from datetime import datetime
from typing import Any, List, Optional
from pydantic import BaseModel, Field


class KnowledgePointProgress(BaseModel):
    knowledge_point_id: str
    code: str
    name: str
    mastery: float
    is_mastered: bool
    attempts: int
    correct_count: int
    wrong_streak: int
    last_attempt_at: Optional[datetime] = None


class ChapterProgress(BaseModel):
    chapter_id: str
    chapter_name: str
    progress: float
    knowledge_points: List[KnowledgePointProgress]


class CourseProgress(BaseModel):
    course_id: str
    course_name: str
    overall_progress: float
    total_chapters: int
    completed_chapters: int
    total_knowledge_points: int
    mastered_knowledge_points: int
    chapters: List[ChapterProgress]


class OverallProgress(BaseModel):
    learner_id: str
    total_courses: int
    completed_courses: int
    courses: List[CourseProgress]


class MistakeRecordBrief(BaseModel):
    id: str
    exercise_id: str
    exercise_code: str
    exercise_type: str
    knowledge_point_id: str
    knowledge_point_name: str
    first_wrong_at: datetime
    last_wrong_at: datetime
    wrong_count: int
    is_resolved: bool


class MistakeRecordDetail(MistakeRecordBrief):
    content: dict
    correct_answer: dict
    analysis: Optional[dict] = None
    last_attempt_answer: Any


class PaginatedMistakes(BaseModel):
    learner_id: str
    mistakes: List[MistakeRecordBrief]
    total: int
    page: int
    page_size: int
    total_pages: int


class MistakeStatistics(BaseModel):
    learner_id: str
    total_mistakes: int
    resolved_mistakes: int
    unresolved_mistakes: int
    by_knowledge_point: List[dict]


class LearnerGoalBrief(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    course_id: Optional[str] = None
    status: str
    progress: float
    target_date: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None


class LearnerGoalCreate(BaseModel):
    title: str
    description: Optional[str] = None
    course_id: Optional[str] = None
    target_date: Optional[datetime] = None


class LearnerGoalUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    target_date: Optional[datetime] = None
    progress: Optional[float] = None


class LearnerTaskBrief(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    goal_id: Optional[str] = None
    knowledge_point_id: Optional[str] = None
    exercise_id: Optional[str] = None
    type: str
    status: str
    priority: int
    due_date: Optional[datetime] = None
    order_index: int
    created_at: datetime
    updated_at: datetime


class LearnerTaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    goal_id: Optional[str] = None
    knowledge_point_id: Optional[str] = None
    exercise_id: Optional[str] = None
    type: str = "learn"
    priority: int = 3
    due_date: Optional[datetime] = None


class LearnerTaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[int] = None
    due_date: Optional[datetime] = None
