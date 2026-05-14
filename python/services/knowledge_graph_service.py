"""
知识图谱服务 - 从数据库加载并管理课程知识图谱

核心功能：
1. 从 DB 加载课程知识图谱
2. 提供图查询接口（前置知识点、后续知识点、可学知识点）
3. 拓扑排序
4. 缓存管理
"""

import logging
from collections import deque
from typing import Any

from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import KnowledgeEdge, KnowledgePoint


logger = logging.getLogger(__name__)


class KnowledgeNodeData(BaseModel):
    """知识点数据模型（用于 API 响应）"""
    id: str
    code: str
    name: str
    chapter_id: str
    course_id: str
    difficulty: float = 0.5
    description: str = ""
    tags: list[str] = Field(default_factory=list)
    prerequisites: list[str] = Field(default_factory=list)


class KnowledgeGraphData:
    """
    知识图谱数据结构（从 DB 加载）
    
    支持的功能：
    - 获取前置知识点
    - 获取后续知识点
    - 获取所有前置知识点（递归）
    - 拓扑排序
    - 获取可学的知识点
    """

    def __init__(self) -> None:
        self.nodes: dict[str, KnowledgeNodeData] = {}
        self._adjacency: dict[str, list[str]] = {}  # node_id -> 后继节点列表
        self._reverse_adj: dict[str, list[str]] = {}  # node_id -> 前置节点列表

    def add_node(self, node: KnowledgeNodeData) -> None:
        """添加知识点节点"""
        self.nodes[node.id] = node
        if node.id not in self._adjacency:
            self._adjacency[node.id] = []
        if node.id not in self._reverse_adj:
            self._reverse_adj[node.id] = []

        for prereq_id in node.prerequisites:
            if prereq_id not in self._adjacency:
                self._adjacency[prereq_id] = []
            self._adjacency[prereq_id].append(node.id)
            if node.id not in self._reverse_adj:
                self._reverse_adj[node.id] = []
            self._reverse_adj[node.id].append(prereq_id)

    def get_prerequisites(self, node_id: str) -> list[KnowledgeNodeData]:
        """获取直接前置知识点"""
        prereq_ids = self._reverse_adj.get(node_id, [])
        return [self.nodes[pid] for pid in prereq_ids if pid in self.nodes]

    def get_successors(self, node_id: str) -> list[KnowledgeNodeData]:
        """获取直接后继知识点"""
        succ_ids = self._adjacency.get(node_id, [])
        return [self.nodes[sid] for sid in succ_ids if sid in self.nodes]

    def get_all_prerequisites(self, node_id: str) -> set[str]:
        """获取所有前置知识点（递归）"""
        visited: set[str] = set()
        queue = deque(self._reverse_adj.get(node_id, []))
        
        while queue:
            pid = queue.popleft()
            if pid not in visited:
                visited.add(pid)
                queue.extend(self._reverse_adj.get(pid, []))
        
        return visited

    def topological_sort(self) -> list[str]:
        """拓扑排序 - Kahn算法"""
        in_degree: dict[str, int] = {nid: 0 for nid in self.nodes}
        
        for nid in self.nodes:
            for succ in self._adjacency.get(nid, []):
                if succ in in_degree:
                    in_degree[succ] += 1

        queue = deque([nid for nid, deg in in_degree.items() if deg == 0])
        result: list[str] = []

        while queue:
            nid = queue.popleft()
            result.append(nid)
            for succ in self._adjacency.get(nid, []):
                if succ in in_degree:
                    in_degree[succ] -= 1
                    if in_degree[succ] == 0:
                        queue.append(succ)

        if len(result) != len(self.nodes):
            logger.warning("知识图谱包含环！部分排序返回。")

        return result

    def get_ready_nodes(self, mastered_ids: set[str]) -> list[KnowledgeNodeData]:
        """
        获取当前可学的知识点：
        前置知识全部掌握，但自己还未掌握的知识点
        
        按难度排序返回
        """
        ready = []
        for nid, node in self.nodes.items():
            if nid in mastered_ids:
                continue
            prereqs = set(node.prerequisites)
            if prereqs.issubset(mastered_ids):
                ready.append(node)
        
        return sorted(ready, key=lambda n: n.difficulty)

    def get_learning_path(self, target_id: str, mastered_ids: set[str]) -> list[KnowledgeNodeData]:
        """生成到达目标知识点的学习路径"""
        needed = self.get_all_prerequisites(target_id) - mastered_ids
        if target_id not in mastered_ids:
            needed.add(target_id)

        full_order = self.topological_sort()
        result = []
        for nid in full_order:
            if nid in needed:
                result.append(self.nodes[nid])
        
        return result

    def to_dict(self) -> dict[str, Any]:
        """序列化为字典（用于 API 响应）"""
        nodes = []
        edges = []
        
        for node in self.nodes.values():
            nodes.append({
                "id": node.id,
                "code": node.code,
                "name": node.name,
                "chapter_id": node.chapter_id,
                "course_id": node.course_id,
                "difficulty": node.difficulty,
                "description": node.description,
                "tags": node.tags,
                "prerequisites": node.prerequisites,
            })
            
        for source_id, target_ids in self._adjacency.items():
            for target_id in target_ids:
                edges.append({
                    "source": source_id,
                    "target": target_id,
                    "type": "prerequisite",
                })
                
        return {
            "nodes": nodes,
            "edges": edges,
        }


class KnowledgeGraphService:
    """
    知识图谱服务
    
    从数据库加载课程知识图谱，提供查询接口，支持缓存
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._cache: dict[str, KnowledgeGraphData] = {}

    async def get_graph(self, course_id: str, use_cache: bool = True) -> KnowledgeGraphData:
        """
        获取课程知识图谱
        
        Args:
            course_id: 课程 ID
            use_cache: 是否使用缓存
            
        Returns:
            KnowledgeGraphData: 知识图谱对象
        """
        if use_cache and course_id in self._cache:
            logger.debug(f"从缓存获取知识图谱: {course_id}")
            return self._cache[course_id]

        logger.info(f"从数据库加载知识图谱: {course_id}")
        
        graph = KnowledgeGraphData()

        result = await self._session.execute(
            select(KnowledgePoint).where(
                KnowledgePoint.course_id == course_id,
                KnowledgePoint.is_active == True
            )
        )
        kps = result.scalars().all()

        for kp in kps:
            prerequisites = await self._get_prerequisites(kp.id)
            node = KnowledgeNodeData(
                id=kp.id,
                code=kp.code,
                name=kp.name,
                chapter_id=kp.chapter_id,
                course_id=kp.course_id,
                difficulty=kp.difficulty,
                description=kp.description or "",
                tags=kp.tags or [],
                prerequisites=prerequisites,
            )
            graph.add_node(node)

        logger.info(f"加载知识图谱完成: course={course_id}, nodes={len(graph.nodes)}")
        
        if use_cache:
            self._cache[course_id] = graph
            
        return graph

    async def _get_prerequisites(self, kp_id: str) -> list[str]:
        """获取知识点的所有前置知识点 ID"""
        result = await self._session.execute(
            select(KnowledgeEdge.target_kp_id, KnowledgeEdge.source_kp_id)
            .where(KnowledgeEdge.target_kp_id == kp_id)
        )
        edges = result.all()
        return [edge.source_kp_id for edge in edges]

    def invalidate_cache(self, course_id: str | None = None) -> None:
        """
        失效缓存
        
        Args:
            course_id: 课程 ID，如果为 None 则清空所有缓存
        """
        if course_id:
            if course_id in self._cache:
                del self._cache[course_id]
                logger.info(f"失效知识图谱缓存: {course_id}")
        else:
            self._cache.clear()
            logger.info("清空所有知识图谱缓存")

    async def get_course_catalog(self, course_id: str) -> dict[str, Any]:
        """
        获取课程目录（章节-知识点树形结构）
        
        Returns:
            dict: {
                "course_id": str,
                "chapters": [
                    {
                        "id": str,
                        "name": str,
                        "order_index": int,
                        "knowledge_points": [...]
                    }
                ]
            }
        """
        from db.models import Chapter
        
        result = await self._session.execute(
            select(Chapter)
            .where(Chapter.course_id == course_id)
            .order_by(Chapter.order_index)
        )
        chapters = result.scalars().all()
        
        graph = await self.get_graph(course_id)
        
        chapter_data = []
        for chapter in chapters:
            kps_in_chapter = [
                {
                    "id": node.id,
                    "code": node.code,
                    "name": node.name,
                    "difficulty": node.difficulty,
                    "description": node.description,
                    "tags": node.tags,
                }
                for node in graph.nodes.values()
                if node.chapter_id == chapter.id
            ]
            
            kps_in_chapter.sort(key=lambda x: x.get("code", ""))
            
            chapter_data.append({
                "id": chapter.id,
                "code": chapter.code,
                "name": chapter.name,
                "order_index": chapter.order_index,
                "description": chapter.description,
                "knowledge_points": kps_in_chapter,
            })
            
        return {
            "course_id": course_id,
            "chapters": chapter_data,
        }
