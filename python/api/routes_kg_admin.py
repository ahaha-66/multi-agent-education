"""
知识图谱管理 API 路由

提供知识图谱初始化和管理相关的 REST API
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["知识图谱管理"])


class KnowledgeGraphInitRequest(BaseModel):
    """知识图谱初始化请求"""
    course_id: str


class KnowledgeGraphInitResponse(BaseModel):
    """知识图谱初始化响应"""
    course_id: str
    nodes: int
    edges: int
    message: str


@router.post("/knowledge-graph/init", response_model=KnowledgeGraphInitResponse)
async def init_knowledge_graph(
    request: KnowledgeGraphInitRequest,
    app_request: Request,
):
    """
    初始化课程知识图谱
    
    将指定课程的知识图谱加载到 CurriculumAgent 中，
    使其能够进行学习路径规划和推荐。
    
    Args:
        request: 包含课程 ID 的请求
        
    Returns:
        知识图谱初始化结果
    """
    orchestrator = getattr(app_request.app.state, "orchestrator", None)
    
    if not orchestrator:
        raise HTTPException(
            status_code=500,
            detail="Orchestrator 未初始化"
        )
    
    try:
        result = await orchestrator.initialize_knowledge_graph(request.course_id)
        
        logger.info(f"知识图谱初始化成功: course_id={request.course_id}")
        
        return KnowledgeGraphInitResponse(
            course_id=result["course_id"],
            nodes=result["nodes"],
            edges=result["edges"],
            message="知识图谱初始化成功"
        )
    except Exception as e:
        logger.error(f"知识图谱初始化失败: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"知识图谱初始化失败: {str(e)}"
        )


@router.get("/knowledge-graph/status")
async def get_knowledge_graph_status(app_request: Request):
    """
    获取知识图谱状态
    
    返回当前已加载的知识图谱信息
    """
    orchestrator = getattr(app_request.app.state, "orchestrator", None)
    
    if not orchestrator:
        raise HTTPException(
            status_code=500,
            detail="Orchestrator 未初始化"
        )
    
    course_id = orchestrator._current_course_id
    curriculum = orchestrator.curriculum
    graph = curriculum.knowledge_graph if hasattr(curriculum, 'knowledge_graph') else None
    
    if not graph:
        return {
            "status": "not_initialized",
            "course_id": None,
            "nodes": 0,
            "edges": 0,
        }
    
    graph_dict = graph.to_dict()
    
    return {
        "status": "initialized",
        "course_id": course_id,
        "nodes": len(graph_dict["nodes"]),
        "edges": len(graph_dict["edges"]),
    }
