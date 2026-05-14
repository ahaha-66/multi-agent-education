import pytest

from core.event_bus import Event, EventBus, EventType


@pytest.mark.asyncio
async def test_event_bus_history_limits():
    bus = EventBus(max_history_per_learner=3, max_global_history=4)
    for i in range(10):
        await bus.publish(
            Event(
                type=EventType.STUDENT_SUBMISSION,
                source="test",
                learner_id="student_1",
                data={"i": i},
            )
        )

    history_all = bus.get_history()
    history_student = bus.get_history(learner_id="student_1")
    assert len(history_all) == 4
    assert len(history_student) == 3
    assert history_student[-1].data["i"] == 9


@pytest.mark.asyncio
async def test_correlation_id_is_kept_in_history():
    bus = EventBus()
    correlation_id = "corr-1"

    async def handler(event: Event):
        await bus.publish(
            Event(
                type=EventType.TEACHING_RESPONSE,
                source="handler",
                learner_id=event.learner_id,
                correlation_id=event.correlation_id,
                data={"ok": True},
            )
        )

    bus.subscribe(EventType.STUDENT_MESSAGE, handler)
    await bus.publish(
        Event(
            type=EventType.STUDENT_MESSAGE,
            source="test",
            learner_id="student_1",
            correlation_id=correlation_id,
            data={"message": "hi"},
        )
    )

    events = bus.get_history(learner_id="student_1", limit=10)
    assert any(e.correlation_id == correlation_id for e in events)
    assert any(e.type == EventType.TEACHING_RESPONSE and e.correlation_id == correlation_id for e in events)

