"""
Agent 编排器 -- 初始化所有Agent并连接到EventBus。

这是系统的"大脑"，负责：
1. 创建EventBus实例
2. 初始化5个Agent并注入EventBus
3. 提供对外接口供API层调用
"""

import logging

from config.settings import settings, _get_sessionmaker
from core.event_bus import Event, EventBus, EventType
from core.learner_model import LearnerModel
from db.persistence import PersistenceService
from db.session import create_engine, create_sessionmaker
from services.knowledge_graph_service import KnowledgeGraphService
from services.mistake_service import MistakeService
from agents import (
    AssessmentAgent,
    TutorAgent,
    CurriculumAgent,
    HintAgent,
    EngagementAgent,
)


logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """Agent编排器：管理所有Agent和共享状态。"""

    def __init__(self) -> None:
        self._engine = create_engine(settings.database_url)
        self._sessionmaker = create_sessionmaker(self._engine)
        self.persistence = PersistenceService(self._sessionmaker)
        self.event_bus = EventBus(event_sink=self.persistence.log_event)
        self.learner_models: dict[str, LearnerModel] = {}
        self._current_course_id: str | None = None

        self.assessment = AssessmentAgent(
            name="AssessmentAgent",
            event_bus=self.event_bus,
            learner_models=self.learner_models,
        )
        self.tutor = TutorAgent(
            name="TutorAgent",
            event_bus=self.event_bus,
            learner_models=self.learner_models,
        )
        self.curriculum = CurriculumAgent(
            name="CurriculumAgent",
            event_bus=self.event_bus,
            learner_models=self.learner_models,
        )
        self.hint = HintAgent(
            name="HintAgent",
            event_bus=self.event_bus,
            learner_models=self.learner_models,
        )
        self.engagement = EngagementAgent(
            name="EngagementAgent",
            event_bus=self.event_bus,
            learner_models=self.learner_models,
        )

    async def initialize_knowledge_graph(self, course_id: str) -> dict:
        """初始化课程知识图谱
        
        Args:
            course_id: 课程 ID
            
        Returns:
            dict: {
                "course_id": str,
                "nodes": int,
                "edges": int
            }
        """
        self._current_course_id = course_id
        
        async with self._sessionmaker() as session:
            kg_service = KnowledgeGraphService(session)
            graph = await kg_service.get_graph(course_id)
            self.curriculum.set_knowledge_graph(graph)
            
            graph_dict = graph.to_dict()
            
            logger.info(
                f"[Orchestrator] 知识图谱加载完成: "
                f"course_id={course_id}, "
                f"nodes={len(graph_dict['nodes'])}, "
                f"edges={len(graph_dict['edges'])}"
            )
            
            return {
                "course_id": course_id,
                "nodes": len(graph_dict["nodes"]),
                "edges": len(graph_dict["edges"]),
            }

    async def shutdown(self) -> None:
        await self._engine.dispose()

    async def _ensure_loaded(self, learner_id: str) -> None:
        await self.persistence.touch_learner(learner_id)
        if learner_id not in self.learner_models:
            self.learner_models[learner_id] = await self.persistence.load_learner_model(learner_id)
        if learner_id not in self.curriculum.get_review_items_map():
            items = await self.persistence.load_review_items(learner_id)
            self.curriculum.set_review_items(learner_id, items)

    async def submit_answer(
        self,
        learner_id: str,
        knowledge_id: str,
        is_correct: bool,
        time_spent: float = 0,
        correlation_id: str | None = None,
        exercise_id: str | None = None,
        user_answer: dict | None = None,
    ) -> list[Event]:
        """学生提交答案 -> 触发完整的Agent处理链。"""
        await self._ensure_loaded(learner_id)
        await self.persistence.record_attempt(
            learner_id,
            knowledge_id,
            is_correct,
            time_spent_seconds=time_spent,
            correlation_id=correlation_id,
            exercise_id=exercise_id,
        )
        
        # 记录错题
        if not is_correct and exercise_id:
            async with self._sessionmaker() as session:
                mistake_service = MistakeService(session)
                await mistake_service.record_mistake(
                    learner_id=learner_id,
                    exercise_id=exercise_id,
                    answer=user_answer,
                )
        
        event = Event(
            type=EventType.STUDENT_SUBMISSION,
            source="api",
            learner_id=learner_id,
            data={
                "knowledge_id": knowledge_id,
                "is_correct": is_correct,
                "time_spent_seconds": time_spent,
            },
            correlation_id=correlation_id,
        )
        await self.event_bus.publish(event)
        await self.persistence.save_learner_model(self.learner_models[learner_id])
        await self.persistence.save_review_items(learner_id, self.curriculum.get_review_items(learner_id))
        return self.event_bus.get_history(learner_id=learner_id, limit=20)

    async def ask_question(
        self, learner_id: str, knowledge_id: str, question: str, correlation_id: str | None = None
    ) -> list[Event]:
        """学生提问 -> 触发Assessment + Tutor处理。"""
        await self._ensure_loaded(learner_id)
        event = Event(
            type=EventType.STUDENT_QUESTION,
            source="api",
            learner_id=learner_id,
            data={"knowledge_id": knowledge_id, "question": question},
            correlation_id=correlation_id,
        )
        await self.event_bus.publish(event)
        await self.persistence.save_learner_model(self.learner_models[learner_id])
        await self.persistence.save_review_items(learner_id, self.curriculum.get_review_items(learner_id))
        return self.event_bus.get_history(learner_id=learner_id, limit=20)

    async def send_message(
        self,
        learner_id: str,
        message: str,
        knowledge_id: str = "general",
        correlation_id: str | None = None,
    ) -> list[Event]:
        """学生发送消息 -> 触发Tutor对话。"""
        await self._ensure_loaded(learner_id)
        event = Event(
            type=EventType.STUDENT_MESSAGE,
            source="api",
            learner_id=learner_id,
            data={"message": message, "knowledge_id": knowledge_id},
            correlation_id=correlation_id,
        )
        await self.event_bus.publish(event)
        await self.persistence.save_learner_model(self.learner_models[learner_id])
        await self.persistence.save_review_items(learner_id, self.curriculum.get_review_items(learner_id))
        return self.event_bus.get_history(learner_id=learner_id, limit=20)

    async def get_learner_progress(self, learner_id: str) -> dict:
        """获取学习者进度。"""
        await self.persistence.touch_learner(learner_id)
        model = await self.persistence.load_learner_model(learner_id)
        if not model.knowledge_states:
            return {"learner_id": learner_id, "status": "no_data"}
        return {
            "learner_id": learner_id,
            "progress": model.get_overall_progress(),
            "weak_points": [
                {"id": s.knowledge_id, "mastery": s.mastery}
                for s in model.get_weak_points()
            ],
            "strong_points": [
                {"id": s.knowledge_id, "mastery": s.mastery}
                for s in model.get_strong_points()
            ],
        }
