"""
服务层模块

包含所有业务服务：
- knowledge_graph_service: 知识图谱服务
- exercise_recommender: 练习题推荐服务
"""

from .knowledge_graph_service import KnowledgeGraphService, KnowledgeGraphData, KnowledgeNodeData
from .exercise_recommender import ExerciseRecommender

__all__ = [
    "KnowledgeGraphService",
    "KnowledgeGraphData",
    "KnowledgeNodeData",
    "ExerciseRecommender",
]
