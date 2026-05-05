"""
Knowledge Agent（知识Agent）-- 5G学习路径和深度学习材料。

核心职责：
1. 根据工程师已解决的问题，推荐下次学习方向
2. 当工程师主动查询时，提供背景知识和最佳实践
3. 管理学习路径的进度
4. 连接具体案例到理论知识点

注意：与教育版Curriculum不同，这里是"可选学习"而非"强制学习路径"。
"""

import json
import logging
from pathlib import Path

from .base_agent import BaseAgent
from core.event_bus import Event, EventType

logger = logging.getLogger(__name__)


class KnowledgeAgent(BaseAgent):
    """知识Agent：管理学习路径和深度学习材料。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._load_knowledge_graph()

    def _load_knowledge_graph(self):
        """加载5G知识图谱。"""
        kg_file = Path(__file__).parent.parent / "config" / "5g_knowledge_graph.json"
        try:
            with open(kg_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.knowledge_graph = data.get("concepts", {})
                logger.info(f"Loaded {len(self.knowledge_graph)} knowledge concepts")
        except FileNotFoundError:
            logger.warning(f"Knowledge graph not found at {kg_file}")
            self.knowledge_graph = {}

    @property
    def subscribed_events(self) -> list[EventType]:
        return [
            EventType.PROBLEM_RESOLVED,
            EventType.KNOWLEDGE_QUERY,
            EventType.COMPETENCY_UPDATED,
        ]

    async def handle_event(self, event: Event) -> None:
        if event.type == EventType.PROBLEM_RESOLVED:
            await self._handle_problem_resolved(event)
        elif event.type == EventType.KNOWLEDGE_QUERY:
            await self._handle_knowledge_query(event)
        elif event.type == EventType.COMPETENCY_UPDATED:
            await self._handle_competency_updated(event)

    async def _handle_problem_resolved(self, event: Event) -> None:
        """工程师解决了一个问题后，推荐学习路径。"""
        engineer_id = event.learner_id
        data = event.data

        logger.info(f"[Knowledge] Planning learning path for {engineer_id}")

        profile = self.get_engineer_profile(engineer_id)

        # 基于能力评估生成推荐
        if profile.dominant_category:
            recommendations = self._generate_recommendations(profile)
        else:
            recommendations = self._get_beginner_path()

        await self.emit(
            EventType.LEARNING_PATH_UPDATED,
            engineer_id,
            {
                "short_term": recommendations.get("short_term"),
                "medium_term": recommendations.get("medium_term"),
                "long_term": recommendations.get("long_term"),
            },
        )

    async def _handle_knowledge_query(self, event: Event) -> None:
        """工程师主动查询知识点。"""
        engineer_id = event.learner_id
        data = event.data

        query = data.get("query", "")
        logger.info(f"[Knowledge] Knowledge query: {query}")

        # 查找相关概念
        results = self._search_knowledge(query)

        await self.emit(
            EventType.LEARNING_MATERIAL_PROVIDED,
            engineer_id,
            {
                "query": query,
                "results": results,
                "related_cases": self._find_related_cases(results),
            },
        )

    async def _handle_competency_updated(self, event: Event) -> None:
        """能力更新后，联动更新学习路径。"""
        engineer_id = event.learner_id
        data = event.data

        competency_id = data.get("competency_id")
        new_level = data.get("new_level")

        logger.info(f"[Knowledge] Competency {competency_id} updated to {new_level}")

        # 如果某处达到expert，解锁下一阶段课程
        if new_level == "expert":
            next_path = self._get_next_path(competency_id)
            if next_path:
                await self.emit(
                    EventType.LEARNING_PATH_UPDATED,
                    engineer_id,
                    {"next_unlock": next_path},
                )

    def _generate_recommendations(self, profile) -> dict:
        """根据工程师能力生成分阶段推荐。"""
        return {
            "short_term": {
                "focus": "强化薄弱项",
                "recommendations": [
                    f"深化 {area} 理论基础"
                    for area in profile.weak_areas[:2]
                ],
            },
            "medium_term": {
                "focus": "挑战强项",
                "recommendations": [
                    f"进阶 {profile.dominant_category} 实战应用",
                    "跨领域问题解决",
                ],
            },
            "long_term": {
                "focus": "系统优化设计",
                "recommendations": [
                    "整体网络优化策略",
                    "多场景综合决策",
                    "新技术应用",
                ],
            },
        }

    def _get_beginner_path(self) -> dict:
        """新手标准学习路径。"""
        return {
            "short_term": {
                "modules": [
                    "5G基础概念",
                    "SINR原理",
                    "干扰分类",
                ],
            },
            "medium_term": {
                "modules": [
                    "干扰诊断实战",
                    "容量评估方法",
                    "覆盖优化",
                ],
            },
            "long_term": {
                "modules": [
                    "多站点协同优化",
                    "NSA/SA规划",
                    "性能预测",
                ],
            },
        }

    def _search_knowledge(self, query: str) -> list[dict]:
        """搜索知识点。"""
        results = []

        for concept_id, concept in self.knowledge_graph.items():
            if query.lower() in concept.get("name", "").lower():
                results.append(
                    {
                        "id": concept_id,
                        "name": concept.get("name"),
                        "description": concept.get("description"),
                        "difficulty": concept.get("difficulty"),
                        "prerequisites": concept.get("prerequisites"),
                    }
                )

        return results

    def _find_related_cases(self, concepts: list[dict]) -> list[str]:
        """查找与概念相关的案例。"""
        # 这会在实际实现中连接到案例库
        related = []
        for concept in concepts:
            related_problems = concept.get("related_problems", [])
            related.extend(related_problems)
        return list(set(related))

    def _get_next_path(self, current_competency: str) -> dict | None:
        """在某个能力达到expert后，返回建议的下一阶段路径。"""
        # 简化实现：基于已有competency推荐related课程
        concept = self.knowledge_graph.get(current_competency)
        if concept:
            return {
                "unlock": f"Advanced: {current_competency}",
                "next_competencies": concept.get("related_problems", []),
            }
        return None
