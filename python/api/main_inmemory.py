"""
使用内存持久化的 API 入口 - 用于测试演示
"""

import logging
import sys
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi import Request

from core.event_bus import EventBus
from core.learner_model import LearnerModel
from agents import AssessmentAgent, TutorAgent, CurriculumAgent, HintAgent, EngagementAgent
from db.in_memory_persistence import InMemoryPersistenceService
from db.session import create_engine, create_sessionmaker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
    stream=sys.stdout,
)


class InMemoryOrchestrator:
    """内存版本的编排器"""

    def __init__(self, persistence: InMemoryPersistenceService) -> None:
        self.persistence = persistence
        self.event_bus = EventBus(event_sink=persistence.log_event)
        self.learner_models: dict[str, LearnerModel] = {}

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

    async def shutdown(self) -> None:
        pass

    async def _ensure_loaded(self, learner_id: str) -> None:
        await self.persistence.touch_learner(learner_id)
        if learner_id not in self.learner_models:
            self.learner_models[learner_id] = await self.persistence.load_learner_model(learner_id)
        if learner_id not in self.curriculum.get_review_items_map():
            items = await self.persistence.load_review_items(learner_id)
            self.curriculum.set_review_items(learner_id, items)

    async def submit_answer(self, learner_id: str, knowledge_id: str, is_correct: bool,
                           time_spent: float = 0, correlation_id: str | None = None,
                           exercise_id: str | None = None):
        from core.event_bus import Event, EventType
        await self._ensure_loaded(learner_id)
        await self.persistence.record_attempt(
            learner_id, knowledge_id, is_correct, time_spent,
            correlation_id=correlation_id, exercise_id=exercise_id
        )
        event = Event(
            type=EventType.STUDENT_SUBMISSION,
            source="api",
            learner_id=learner_id,
            data={"knowledge_id": knowledge_id, "is_correct": is_correct, "time_spent_seconds": time_spent},
            correlation_id=correlation_id,
        )
        await self.event_bus.publish(event)
        await self.persistence.save_learner_model(self.learner_models[learner_id])
        await self.persistence.save_review_items(learner_id, self.curriculum.get_review_items(learner_id))
        return self.event_bus.get_history(learner_id=learner_id, limit=20)

    async def ask_question(self, learner_id: str, knowledge_id: str, question: str,
                          correlation_id: str | None = None):
        from core.event_bus import Event, EventType
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

    async def send_message(self, learner_id: str, message: str, knowledge_id: str = "general",
                          correlation_id: str | None = None):
        from core.event_bus import Event, EventType
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
        await self.persistence.touch_learner(learner_id)
        model = await self.persistence.load_learner_model(learner_id)
        if not model.knowledge_states:
            return {"learner_id": learner_id, "status": "no_data"}
        return {
            "learner_id": learner_id,
            "progress": model.get_overall_progress(),
            "weak_points": [{"id": s.knowledge_id, "mastery": s.mastery} for s in model.get_weak_points()],
            "strong_points": [{"id": s.knowledge_id, "mastery": s.mastery} for s in model.get_strong_points()],
        }


orchestrator: InMemoryOrchestrator | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global orchestrator
    persistence = InMemoryPersistenceService()
    orchestrator = InMemoryOrchestrator(persistence)
    app.state.orchestrator = orchestrator
    app.state.persistence = persistence
    logging.getLogger(__name__).info("Agent orchestrator started with 5 agents (in-memory mode)")
    yield
    await orchestrator.shutdown()
    logging.getLogger(__name__).info("Shutting down")


app = FastAPI(
    title="多Agent智能教育系统 - 测试版",
    description=(
        "5-Agent Mesh+事件驱动架构的个性化学习系统（内存模式）\n\n"
        "**Agent列表：**\n"
        "- Assessment Agent：知识点评估\n"
        "- Tutor Agent：苏格拉底式教学\n"
        "- Curriculum Agent：学习路径规划\n"
        "- Hint Agent：分级提示\n"
        "- Engagement Agent：互动监测"
    ),
    version="1.0.0-test",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "service": "multi-agent-education", "agents": 5}


@app.post("/api/v1/submit")
async def submit_answer(request_data: dict, request: Request):
    from api.routes import _to_event_payload
    orch = request.app.state.orchestrator
    import uuid
    correlation_id = request_data.get("correlation_id") or str(uuid.uuid4())
    events = await orch.submit_answer(
        request_data["learner_id"],
        request_data["knowledge_id"],
        request_data["is_correct"],
        request_data.get("time_spent_seconds", 0),
        correlation_id=correlation_id,
    )
    return {
        "status": "processed",
        "correlation_id": correlation_id,
        "events_triggered": len(events),
        "events": [_to_event_payload(e) for e in events[-10:]],
    }


@app.post("/api/v1/question")
async def ask_question(request_data: dict, request: Request):
    from api.routes import _to_event_payload
    orch = request.app.state.orchestrator
    import uuid
    correlation_id = request_data.get("correlation_id") or str(uuid.uuid4())
    events = await orch.ask_question(
        request_data["learner_id"],
        request_data["knowledge_id"],
        request_data["question"],
        correlation_id=correlation_id,
    )
    return {
        "status": "processed",
        "correlation_id": correlation_id,
        "events_triggered": len(events),
        "events": [_to_event_payload(e) for e in events[-10:]],
    }


@app.post("/api/v1/message")
async def send_message(request_data: dict, request: Request):
    from api.routes import _to_event_payload
    orch = request.app.state.orchestrator
    import uuid
    correlation_id = request_data.get("correlation_id") or str(uuid.uuid4())
    events = await orch.send_message(
        request_data["learner_id"],
        request_data["message"],
        request_data.get("knowledge_id", "general"),
        correlation_id=correlation_id,
    )
    return {
        "status": "processed",
        "correlation_id": correlation_id,
        "events_triggered": len(events),
        "events": [_to_event_payload(e) for e in events[-10:]],
    }


@app.get("/api/v1/progress/{learner_id}")
async def get_progress(learner_id: str, request: Request):
    orch = request.app.state.orchestrator
    return await orch.get_learner_progress(learner_id)


@app.get("/api/v1/knowledge-graph")
async def get_knowledge_graph(request: Request):
    orch = request.app.state.orchestrator
    graph = orch.curriculum.knowledge_graph
    return {
        "nodes": [
            {"id": n.id, "name": n.name, "difficulty": n.difficulty,
             "prerequisites": n.prerequisites, "tags": n.tags}
            for n in graph.nodes.values()
        ],
        "learning_order": graph.topological_sort(),
    }


from fastapi import WebSocket, WebSocketDisconnect
from api.websocket import manager, _to_event_payload
import json
import uuid as uuid_module


@app.websocket("/ws/{learner_id}")
async def websocket_endpoint(websocket: WebSocket, learner_id: str):
    await manager.connect(learner_id, websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            action = data.get("action", "")
            correlation_id = data.get("correlation_id") or str(uuid_module.uuid4())

            orch = websocket.app.state.orchestrator

            if action == "submit":
                events = await orch.submit_answer(
                    learner_id,
                    data.get("knowledge_id", ""),
                    data.get("is_correct", False),
                    data.get("time_spent_seconds", 0),
                    correlation_id=correlation_id,
                )
            elif action == "question":
                events = await orch.ask_question(
                    learner_id,
                    data.get("knowledge_id", ""),
                    data.get("question", ""),
                    correlation_id=correlation_id,
                )
            elif action == "message":
                events = await orch.send_message(
                    learner_id,
                    data.get("message", ""),
                    data.get("knowledge_id", "general"),
                    correlation_id=correlation_id,
                )
            else:
                await manager.send_to_learner(
                    learner_id,
                    {
                        "event_id": str(uuid_module.uuid4()),
                        "type": "ws.error",
                        "source": "ws",
                        "learner_id": learner_id,
                        "correlation_id": correlation_id,
                        "timestamp": None,
                        "data": {"message": f"Unknown action: {action}"},
                    },
                )
                continue

            for event in events[-10:]:
                await manager.send_to_learner(learner_id, _to_event_payload(event))

    except WebSocketDisconnect:
        manager.disconnect(learner_id)
    except Exception:
        import logging
        logging.exception("WebSocket error for learner %s", learner_id)
        manager.disconnect(learner_id)


@app.get("/debug/events")
async def get_all_events(request: Request):
    persistence = request.app.state.persistence
    return {"events": persistence.get_all_events()}


@app.get("/debug/events/{learner_id}")
async def get_learner_events(learner_id: str, request: Request):
    persistence = request.app.state.persistence
    return {"events": persistence.get_events_by_learner(learner_id)}


@app.get("/debug/state/{learner_id}")
async def get_learner_state(learner_id: str, request: Request):
    orch = request.app.state.orchestrator
    model = await orch.persistence.load_learner_model(learner_id)
    return {
        "learner_id": learner_id,
        "knowledge_states": {
            kid: {
                "mastery": state.mastery,
                "attempts": state.attempts,
                "correct_count": state.correct_count,
                "wrong_streak": state.wrong_streak,
                "streak": state.streak,
            }
            for kid, state in model.knowledge_states.items()
        }
    }


if __name__ == "__main__":
    uvicorn.run("api.main_inmemory:app", host="0.0.0.0", port=8000, reload=True)
