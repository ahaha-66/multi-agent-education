"""
API Schemas - 课程内容相关的数据模型

用于请求验证和响应格式化
"""

from typing import Any

from pydantic import BaseModel, Field


class CourseInfo(BaseModel):
    """课程基本信息"""
    id: str
    code: str
    name: str
    subject: str
    grade_level: int | None = None
    description: str | None = None


class KnowledgePointBrief(BaseModel):
    """知识点简要信息"""
    id: str
    code: str
    name: str
    difficulty: float
    description: str | None = None
    tags: list[str] = Field(default_factory=list)


class ChapterCatalog(BaseModel):
    """课程目录（章节-知识点结构）"""
    id: str
    code: str
    name: str
    order_index: int
    description: str | None = None
    knowledge_points: list[KnowledgePointBrief] = Field(default_factory=list)


class CourseCatalogResponse(BaseModel):
    """课程目录响应"""
    course_id: str
    chapters: list[ChapterCatalog]


class KnowledgeNodeSchema(BaseModel):
    """知识图谱节点"""
    id: str
    code: str
    name: str
    chapter_id: str
    course_id: str
    difficulty: float
    description: str
    tags: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)


class KnowledgeEdgeSchema(BaseModel):
    """知识图谱边"""
    source: str
    target: str
    type: str = "prerequisite"


class KnowledgeGraphResponse(BaseModel):
    """知识图谱响应"""
    nodes: list[KnowledgeNodeSchema]
    edges: list[KnowledgeEdgeSchema]


class ExerciseContent(BaseModel):
    """练习题内容"""
    stem: str
    options: list[dict[str, str]] | None = None


class ExerciseHint(BaseModel):
    """练习题提示"""
    level: int
    hint: str


class ExerciseBrief(BaseModel):
    """练习题简要信息"""
    id: str
    code: str
    type: str
    difficulty: float
    content: ExerciseContent
    tags: list[str] = Field(default_factory=list)
    hint_levels: list[ExerciseHint] = Field(default_factory=list)


class ExerciseRecommendationResponse(BaseModel):
    """练习题推荐响应"""
    exercises: list[ExerciseBrief]
    recommendation_reason: str | None = None


class AnswerVerificationRequest(BaseModel):
    """答案验证请求"""
    exercise_id: str
    answer: Any


class AnswerVerificationResponse(BaseModel):
    """答案验证响应"""
    is_correct: bool
    correct_answer: Any
    analysis: dict | None = None


class ExerciseDetail(BaseModel):
    """练习题详情（含答案）"""
    id: str
    code: str
    type: str
    difficulty: float
    content: ExerciseContent
    answer: dict
    analysis: dict | None = None
    tags: list[str] = Field(default_factory=list)
    hint_levels: list[dict] = Field(default_factory=list)


class SeedRequest(BaseModel):
    """数据导入请求"""
    source: str = Field(description="数据源路径")
    force: bool = Field(default=False, description="是否强制更新")


class SeedStatusResponse(BaseModel):
    """导入状态响应"""
    status: str
    message: str
    stats: dict[str, int] | None = None
