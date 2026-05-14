"""
WebSocket 实时通信端点。

支持前端与Agent系统的双向实时通信：
- 学生发送消息/答题 → Agent处理 → 实时推送结果

面试要点：
- WebSocket vs HTTP轮询：全双工、低延迟、持久连接
- 断线重连策略：指数退避 + 心跳检测
"""

import json
import logging
import uuid

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

ws_router = APIRouter()
logger = logging.getLogger(__name__)


class ConnectionManager:
    """WebSocket连接管理器。"""

    def __init__(self):
        self.active_connections: dict[str, WebSocket] = {}

    async def connect(self, learner_id: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[learner_id] = websocket
        logger.info("WebSocket connected: %s", learner_id)

    def disconnect(self, learner_id: str):
        self.active_connections.pop(learner_id, None)
        logger.info("WebSocket disconnected: %s", learner_id)

    async def send_to_learner(self, learner_id: str, data: dict):
        ws = self.active_connections.get(learner_id)
        if ws:
            await ws.send_json(data)


manager = ConnectionManager()

def _to_event_payload(event):
    return {
        "event_id": event.id,
        "type": event.type.value,
        "source": event.source,
        "learner_id": event.learner_id,
        "correlation_id": event.correlation_id,
        "timestamp": event.timestamp.isoformat(),
        "data": event.data,
    }


@ws_router.websocket("/ws/{learner_id}")
async def websocket_endpoint(websocket: WebSocket, learner_id: str):
    await manager.connect(learner_id, websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            data = json.loads(raw)
            action = data.get("action", "")
            correlation_id = data.get("correlation_id") or str(uuid.uuid4())

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
                        "event_id": str(uuid.uuid4()),
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
        logger.exception("WebSocket error for learner %s", learner_id)
        manager.disconnect(learner_id)
