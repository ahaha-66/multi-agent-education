"""REST API 路由。"""

import uuid

from fastapi import APIRouter, Request
from pydantic import BaseModel

router = APIRouter(tags=["education"])


class SubmitAnswerRequest(BaseModel):
    learner_id: str
    knowledge_id: str
    is_correct: bool
    time_spent_seconds: float = 0
    correlation_id: str | None = None


class AskQuestionRequest(BaseModel):
    learner_id: str
    knowledge_id: str
    question: str
    correlation_id: str | None = None


class SendMessageRequest(BaseModel):
    learner_id: str
    message: str
    knowledge_id: str = "general"
    correlation_id: str | None = None


def _to_event_payload(e):
    return {
        "event_id": e.id,
        "type": e.type.value,
        "source": e.source,
        "learner_id": e.learner_id,
        "correlation_id": e.correlation_id,
        "timestamp": e.timestamp.isoformat(),
        "data": e.data,
    }


@router.get("/health")
async def health_check():
    return {"status": "ok", "service": "multi-agent-education", "agents": 5}


@router.post("/submit")
async def submit_answer(req: SubmitAnswerRequest, request: Request):
    """学生提交答题结果。"""
    orch = request.app.state.orchestrator
    correlation_id = req.correlation_id or str(uuid.uuid4())
    events = await orch.submit_answer(
        req.learner_id,
        req.knowledge_id,
        req.is_correct,
        req.time_spent_seconds,
        correlation_id=correlation_id,
    )
    return {
        "status": "processed",
        "correlation_id": correlation_id,
        "events_triggered": len(events),
        "events": [_to_event_payload(e) for e in events[-10:]],
    }


@router.post("/question")
async def ask_question(req: AskQuestionRequest, request: Request):
    """学生提问。"""
    orch = request.app.state.orchestrator
    correlation_id = req.correlation_id or str(uuid.uuid4())
    events = await orch.ask_question(
        req.learner_id,
        req.knowledge_id,
        req.question,
        correlation_id=correlation_id,
    )
    return {
        "status": "processed",
        "correlation_id": correlation_id,
        "events_triggered": len(events),
        "events": [_to_event_payload(e) for e in events[-10:]],
    }


@router.post("/message")
async def send_message(req: SendMessageRequest, request: Request):
    """学生发送消息（对话）。"""
    orch = request.app.state.orchestrator
    correlation_id = req.correlation_id or str(uuid.uuid4())
    events = await orch.send_message(
        req.learner_id,
        req.message,
        req.knowledge_id,
        correlation_id=correlation_id,
    )
    return {
        "status": "processed",
        "correlation_id": correlation_id,
        "events_triggered": len(events),
        "events": [_to_event_payload(e) for e in events[-10:]],
    }


@router.get("/progress/{learner_id}")
async def get_progress(learner_id: str, request: Request):
    """获取学生学习进度。"""
    orch = request.app.state.orchestrator
    return orch.get_learner_progress(learner_id)


@router.get("/knowledge-graph")
async def get_knowledge_graph(request: Request):
    """获取知识图谱结构。"""
    orch = request.app.state.orchestrator
    graph = orch.curriculum.knowledge_graph
    return {
        "nodes": [
            {
                "id": n.id,
                "name": n.name,
                "difficulty": n.difficulty,
                "prerequisites": n.prerequisites,
                "tags": n.tags,
            }
            for n in graph.nodes.values()
        ],
        "learning_order": graph.topological_sort(),
    }
