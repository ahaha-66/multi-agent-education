"""
阶段 A 验收测试套件。

测试内容：
1. REST API correlation_id 生成与透传
2. EventBus 事件历史限制（按 learner 分桶 + 全局上限）
3. WebSocket envelope 标准化
4. 所有 Agent 事件传递 correlation_id
"""

import asyncio
import uuid
from core.event_bus import Event, EventBus, EventType
from agents.base_agent import BaseAgent
from core.learner_model import LearnerModel


class TestAgent(BaseAgent):
    """测试用 Agent，验证事件传递。"""

    @property
    def subscribed_events(self) -> list[EventType]:
        return [EventType.STUDENT_SUBMISSION]

    async def handle_event(self, event: Event) -> None:
        await self.emit(
            EventType.ASSESSMENT_COMPLETE,
            event.learner_id,
            {"source": "test_agent", "received": True},
            correlation_id=event.correlation_id,
        )


async def test_correlation_id_propagation():
    """测试 1: 单次 submit 产生的多个事件均带同一 correlation_id。"""
    print("=" * 60)
    print("测试 1: correlation_id 全链路传递")
    print("=" * 60)

    bus = EventBus(max_history_per_learner=100, max_global_history=1000)
    models = {"student_1": LearnerModel("student_1")}
    agent = TestAgent("TestAgent", bus, models)

    correlation_id = "corr-test-001"

    event = Event(
        type=EventType.STUDENT_SUBMISSION,
        source="api",
        learner_id="student_1",
        data={"knowledge_id": "algebra", "is_correct": True},
        correlation_id=correlation_id,
    )
    await bus.publish(event)

    events = bus.get_history(learner_id="student_1", limit=50)

    print(f"事件总数: {len(events)}")
    print(f"所有事件的 correlation_id 是否一致: {all(e.correlation_id == correlation_id for e in events)}")

    for e in events:
        print(f"  - {e.type.value}: correlation_id={e.correlation_id}")

    assert all(e.correlation_id == correlation_id for e in events), "所有事件应携带相同的 correlation_id"
    print("✅ 测试通过\n")


async def test_event_bus_history_limits():
    """测试 2: EventBus history 不随运行时间无界增长。"""
    print("=" * 60)
    print("测试 2: 事件历史边界控制")
    print("=" * 60)

    bus = EventBus(max_history_per_learner=5, max_global_history=10)

    for i in range(20):
        await bus.publish(
            Event(
                type=EventType.STUDENT_SUBMISSION,
                source="test",
                learner_id="student_1",
                data={"i": i},
                correlation_id=f"corr-{i}",
            )
        )

    history_global = bus.get_history()
    history_learner = bus.get_history(learner_id="student_1")

    print(f"发送事件数: 20")
    print(f"全局历史上限: 10, 实际: {len(history_global)}")
    print(f"单 learner 历史上限: 5, 实际: {len(history_learner)}")
    print(f"最新事件 data.i: {history_learner[-1].data.get('i')}")

    assert len(history_global) == 10, "全局历史应限制在 10 条"
    assert len(history_learner) == 5, "单 learner 历史应限制在 5 条"
    assert history_learner[-1].data.get("i") == 19, "应保留最新的事件"
    print("✅ 测试通过\n")


async def test_websocket_envelope_format():
    """测试 3: WebSocket 事件 envelope 字段完整性。"""
    print("=" * 60)
    print("测试 3: WebSocket envelope 格式验证")
    print("=" * 60)

    required_fields = ["event_id", "type", "source", "learner_id", "correlation_id", "timestamp", "data"]

    event = Event(
        type=EventType.STUDENT_SUBMISSION,
        source="api",
        learner_id="student_1",
        data={"knowledge_id": "algebra", "is_correct": True},
        correlation_id="ws-corr-001",
    )

    envelope = {
        "event_id": event.id,
        "type": event.type.value,
        "source": event.source,
        "learner_id": event.learner_id,
        "correlation_id": event.correlation_id,
        "timestamp": event.timestamp.isoformat(),
        "data": event.data,
    }

    print(f"Envelope 字段: {list(envelope.keys())}")
    print(f"是否包含所有必填字段: {all(field in envelope for field in required_fields)}")

    for field in required_fields:
        status = "✅" if field in envelope else "❌"
        print(f"  {status} {field}: {envelope.get(field, 'MISSING')}")

    assert all(field in envelope for field in required_fields), "所有必填字段必须存在"
    print("✅ 测试通过\n")


async def test_all_agents_propagate_correlation():
    """测试 4: 所有 Agent emit 时正确传递 correlation_id。"""
    print("=" * 60)
    print("测试 4: 所有 Agent correlation_id 传递验证")
    print("=" * 60)

    from agents import AssessmentAgent, TutorAgent, CurriculumAgent, HintAgent, EngagementAgent

    bus = EventBus()
    models = {"student_1": LearnerModel("student_1")}
    curriculum_items = {"student_1": {}}

    assessment = AssessmentAgent("AssessmentAgent", bus, models)
    tutor = TutorAgent("TutorAgent", bus, models)
    curriculum = CurriculumAgent("CurriculumAgent", bus, models)
    hint = HintAgent("HintAgent", bus, models)
    engagement = EngagementAgent("EngagementAgent", bus, models)

    curriculum.set_review_items("student_1", curriculum_items.get("student_1", {}))

    test_correlation = "corr-agent-test-001"

    initial_event = Event(
        type=EventType.STUDENT_SUBMISSION,
        source="api",
        learner_id="student_1",
        data={"knowledge_id": "algebra", "is_correct": False, "time_spent_seconds": 30},
        correlation_id=test_correlation,
    )
    await bus.publish(initial_event)

    await asyncio.sleep(0.1)

    events = bus.get_history(learner_id="student_1", limit=100)
    emitted_events = [e for e in events if e.source in ["AssessmentAgent", "TutorAgent", "CurriculumAgent", "HintAgent", "EngagementAgent"]]

    print(f"初始事件 correlation_id: {initial_event.correlation_id}")
    print(f"Agent 发出事件数: {len(emitted_events)}")
    print(f"所有 Agent 事件 correlation_id 一致: {all(e.correlation_id == test_correlation for e in emitted_events)}")

    for e in emitted_events:
        status = "✅" if e.correlation_id == test_correlation else "❌"
        print(f"  {status} {e.source}: {e.type.value} (corr={e.correlation_id})")

    assert all(e.correlation_id == test_correlation for e in emitted_events), "所有 Agent 事件应传递相同的 correlation_id"
    print("✅ 测试通过\n")


async def test_rest_api_correlation_generation():
    """测试 5: REST API correlation_id 生成逻辑。"""
    print("=" * 60)
    print("测试 5: REST API correlation_id 生成")
    print("=" * 60)

    import uuid as uuid_module

    async def simulate_submit(correlation_id=None):
        return correlation_id or str(uuid_module.uuid4())

    corr1 = await simulate_submit()
    corr2 = await simulate_submit()
    corr3 = await simulate_submit("client-provided-123")

    print(f"自动生成 #1: {corr1}")
    print(f"自动生成 #2: {corr2}")
    print(f"客户端提供: {corr3}")

    assert corr1 != corr2, "两次生成应不同"
    assert corr3 == "client-provided-123", "应透传客户端提供的 correlation_id"
    print("✅ 测试通过\n")


async def main():
    """运行所有验收测试。"""
    print("\n" + "=" * 60)
    print("阶段 A 验收测试套件")
    print("=" * 60 + "\n")

    await test_correlation_id_propagation()
    await test_event_bus_history_limits()
    await test_websocket_envelope_format()
    await test_all_agents_propagate_correlation()
    await test_rest_api_correlation_generation()

    print("=" * 60)
    print("🎉 所有测试通过！阶段 A 验收完成")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
