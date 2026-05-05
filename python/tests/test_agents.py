"""
单元测试 -- 覆盖核心模块和Agent逻辑。

运行方式：
    cd python/
    python -m pytest tests/ -v
"""
import sys
from pathlib import Path
import asyncio
import pytest
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.event_bus import EventBus, Event, EventType
from core.learner_model import LearnerModel, MasteryLevel
from core.spaced_repetition import SpacedRepetition, ReviewItem
from core.knowledge_graph import KnowledgeGraph, KnowledgeNode, build_sample_math_graph


# ─── EventBus Tests ───


@pytest.mark.asyncio
async def test_event_bus_publish_subscribe():
    bus = EventBus()
    received = []

    async def handler(event: Event):
        received.append(event)

    bus.subscribe(EventType.STUDENT_SUBMISSION, handler)

    event = Event(
        type=EventType.STUDENT_SUBMISSION,
        source="test",
        learner_id="student_1",
        data={"knowledge_id": "arithmetic", "is_correct": True},
    )
    await bus.publish(event)

    assert len(received) == 1
    assert received[0].data["is_correct"] is True


@pytest.mark.asyncio
async def test_event_bus_no_handler():
    bus = EventBus()
    event = Event(
        type=EventType.STUDENT_SUBMISSION,
        source="test",
        learner_id="student_1",
    )
    await bus.publish(event)  # Should not raise


@pytest.mark.asyncio
async def test_event_bus_history():
    bus = EventBus()
    for i in range(5):
        await bus.publish(
            Event(
                type=EventType.STUDENT_SUBMISSION,
                source="test",
                learner_id=f"student_{i % 2}",
            )
        )
    assert len(bus.get_history()) == 5
    assert len(bus.get_history(learner_id="student_0")) == 3


# ─── LearnerModel / BKT Tests ───


def test_bkt_correct_answer_increases_mastery():
    model = LearnerModel("student_1")
    state = model.get_state("arithmetic")
    initial = state.mastery

    state = model.update_mastery("arithmetic", is_correct=True)
    assert state.mastery > initial


def test_bkt_wrong_answer_updates_mastery():
    model = LearnerModel("student_1")
    model.update_mastery("arithmetic", is_correct=True)
    model.update_mastery("arithmetic", is_correct=True)
    state_after_correct = model.get_state("arithmetic").mastery

    model.update_mastery("arithmetic", is_correct=False)
    state_after_wrong = model.get_state("arithmetic").mastery
    assert state_after_wrong < state_after_correct


def test_mastery_level_progression():
    model = LearnerModel("student_1")
    state = model.get_state("arithmetic")
    assert state.level == MasteryLevel.NOT_STARTED

    for _ in range(20):
        model.update_mastery("arithmetic", is_correct=True)

    state = model.get_state("arithmetic")
    assert state.level == MasteryLevel.MASTERED


def test_weak_points():
    model = LearnerModel("student_1")
    model.update_mastery("algebra", is_correct=False)
    model.update_mastery("algebra", is_correct=False)
    model.update_mastery("geometry", is_correct=True)
    model.update_mastery("geometry", is_correct=True)

    weak = model.get_weak_points(threshold=0.5)
    assert any(s.knowledge_id == "algebra" for s in weak)


def test_overall_progress():
    model = LearnerModel("student_1")
    model.update_mastery("a", is_correct=True)
    model.update_mastery("b", is_correct=False)

    progress = model.get_overall_progress()
    assert progress["total_knowledge_points"] == 2
    assert progress["total_attempts"] == 2


# ─── SpacedRepetition / SM-2 Tests ───


def test_sm2_correct_increases_interval():
    sr = SpacedRepetition()
    item = ReviewItem(knowledge_id="test")

    item = sr.review(item, quality=5)
    assert item.interval_days == 1
    assert item.repetition == 1

    item = sr.review(item, quality=5)
    assert item.interval_days == 6
    assert item.repetition == 2

    item = sr.review(item, quality=5)
    assert item.interval_days > 6


def test_sm2_bad_quality_resets():
    sr = SpacedRepetition()
    item = ReviewItem(knowledge_id="test")

    item = sr.review(item, quality=5)
    item = sr.review(item, quality=5)
    item = sr.review(item, quality=5)

    item = sr.review(item, quality=1)
    assert item.repetition == 0
    assert item.interval_days == 1


def test_sm2_ef_adjustment():
    sr = SpacedRepetition()
    item = ReviewItem(knowledge_id="test")
    initial_ef = item.easiness_factor

    item = sr.review(item, quality=5)
    assert item.easiness_factor >= initial_ef

    item2 = ReviewItem(knowledge_id="test2")
    item2 = sr.review(item2, quality=2)
    assert item2.easiness_factor < initial_ef


def test_sm2_due_items():
    sr = SpacedRepetition()
    item1 = ReviewItem(knowledge_id="a")
    item2 = ReviewItem(knowledge_id="b")

    due = sr.get_due_items([item1, item2])
    assert len(due) == 2  # Both are due (next_review = now)


# ─── KnowledgeGraph Tests ───


def test_graph_topological_sort():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode(id="a", name="A"))
    graph.add_node(KnowledgeNode(id="b", name="B", prerequisites=["a"]))
    graph.add_node(KnowledgeNode(id="c", name="C", prerequisites=["a", "b"]))

    order = graph.topological_sort()
    assert order.index("a") < order.index("b")
    assert order.index("b") < order.index("c")


def test_graph_ready_nodes():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode(id="a", name="A"))
    graph.add_node(KnowledgeNode(id="b", name="B", prerequisites=["a"]))
    graph.add_node(KnowledgeNode(id="c", name="C", prerequisites=["a"]))

    ready = graph.get_ready_nodes(mastered_ids=set())
    assert ready == ["a"]

    ready = graph.get_ready_nodes(mastered_ids={"a"})
    assert set(ready) == {"b", "c"}


def test_graph_learning_path():
    graph = KnowledgeGraph()
    graph.add_node(KnowledgeNode(id="a", name="A"))
    graph.add_node(KnowledgeNode(id="b", name="B", prerequisites=["a"]))
    graph.add_node(KnowledgeNode(id="c", name="C", prerequisites=["b"]))

    path = graph.get_learning_path("c", mastered_ids=set())
    assert path == ["a", "b", "c"]

    path = graph.get_learning_path("c", mastered_ids={"a"})
    assert path == ["b", "c"]


def test_sample_math_graph():
    graph = build_sample_math_graph()
    assert len(graph.nodes) == 20
    order = graph.topological_sort()
    assert order[0] == "arithmetic"


# ─── Integration Tests: 完整流程演示 ───


@pytest.mark.asyncio
async def test_end_to_end_student_submission_flow():
    """
    集成测试：演示学生答题的完整流程
    
    场景：
    - 学生答题 (arithmetic)
    - Assessment Agent 评估 (BKT更新)
    - Curriculum Agent 规划 (SM-2排期)
    - Tutor Agent 响应 (教学调整)
    - Engagement Agent 监测 (学习状态)
    
    这个测试让你理解 EventBus 如何连接5个Agent
    """
    from api.orchestrator import AgentOrchestrator
    
    print("\n" + "="*60)
    print("🎓 完整的学生答题流程演示")
    print("="*60)
    
    # ① 初始化系统
    orchestrator = AgentOrchestrator()
    learner_id = "student_001"
    knowledge_id = "arithmetic"
    
    print(f"\n[START] 学生 {learner_id} 开始答题")
    print(f"知识点：{knowledge_id}")
    
    # ② 学生第一次提交答题（正确）
    print("\n[SUBMIT] 学生提交答题：正确 ✓")
    events_1 = await orchestrator.submit_answer(
        learner_id=learner_id,
        knowledge_id=knowledge_id,
        is_correct=True,
        time_spent=30.0
    )
    
    print(f"   → EventBus 中产生了 {len(events_1)} 个事件")
    for event in events_1:
        print(f"      - {event.type.value} (来自 {event.source})")
    
    # ③ 检查学习者状态
    learner_model = orchestrator.learner_models[learner_id]
    state_after_1 = learner_model.get_state(knowledge_id)
    print(f"\n[ASSESSMENT] 知识点状态:")
    print(f"   - Mastery: {state_after_1.mastery:.1%}")
    print(f"   - Level: {state_after_1.level.value}")
    print(f"   - Attempts: {state_after_1.attempts}")
    print(f"   - 连续正确: {state_after_1.streak}")
    
    # ④ 学生再回答几次（持续正确）
    print("\n[LOOP] 学生继续答题3次...")
    for i in range(2, 5):
        await orchestrator.submit_answer(
            learner_id=learner_id,
            knowledge_id=knowledge_id,
            is_correct=True,
            time_spent=20.0 + (i-2)*5
        )
        state = learner_model.get_state(knowledge_id)
        print(f"   [{i}] Mastery: {state.mastery:.1%} | "
              f"Level: {state.level.value} | "
              f"Streak: {state.streak}")
    
    # ⑤ 学生回答错误（测试错误处理）
    print("\n[WRONG] 学生回答错误 ✗")
    await orchestrator.submit_answer(
        learner_id=learner_id,
        knowledge_id=knowledge_id,
        is_correct=False,
        time_spent=60.0  # 时间久表示在思考
    )
    state_after_wrong = learner_model.get_state(knowledge_id)
    print(f"   - Mastery 下降到: {state_after_wrong.mastery:.1%}")
    print(f"   - 连续正确计数重置: {state_after_wrong.streak}")
    
    # ⑥ 最终学习进度
    print("\n[PROGRESS] 最终学习进度:")
    progress = learner_model.get_overall_progress()
    print(f"   - 已学知识点数: {progress['total_knowledge_points']}")
    print(f"   - 总尝试数: {progress['total_attempts']}")
    print(f"   - 平均正确率: {progress['average_accuracy']:.1%}")
    
    # ⑦ 断言验证
    print("\n[VERIFY] 系统验证:")
    
    # 应该至少产生过 MASTERY_UPDATED 事件
    assert len(events_1) > 0, "EventBus 应该产生事件"
    print("   ✓ EventBus 正常工作")
    
    # Mastery 应该从初始值上升
    initial_state = LearnerModel(learner_id).get_state(knowledge_id)
    assert state_after_1.mastery > initial_state.mastery, "正答应该提高Mastery"
    print("   ✓ Assessment Agent 正确更新Mastery")
    
    # 错误后 Mastery 应该下降
    assert state_after_wrong.mastery < state_after_1.mastery, "错答应该降低Mastery"
    print("   ✓ BKT算法正确处理错误")
    
    # 连续正确和重置
    assert state_after_1.streak > 0, "应该有连续正确计数"
    assert state_after_wrong.streak == 0, "错答后应该重置连续计数"
    print("   ✓ 连续计数逻辑正确")
    
    print("\n" + "="*60)
    print("✅ 集成测试通过！你已经理解了系统的核心流程")
    print("="*60 + "\n")


@pytest.mark.asyncio
async def test_event_chain_reaction():
    """
    测试事件链式反应：一个事件触发多个Agent的响应
    
    场景：学生答题 → Assessment更新 → Curriculum规划 + Tutor响应 同时触发
    """
    from api.orchestrator import AgentOrchestrator
    
    print("\n" + "="*60)
    print("🔗 事件链式反应演示")
    print("="*60)
    
    orchestrator = AgentOrchestrator()
    learner_id = "student_chain_test"
    knowledge_id = "algebra"
    
    # 初始状态
    initial_history_count = len(orchestrator.event_bus.get_history())
    
    # 触发事件
    print(f"\n[TRIGGER] 学生提交答题")
    events = await orchestrator.submit_answer(
        learner_id=learner_id,
        knowledge_id=knowledge_id,
        is_correct=True,
        time_spent=45.0
    )
    
    final_history_count = len(orchestrator.event_bus.get_history())
    new_events_count = final_history_count - initial_history_count
    
    print(f"\n[RESULT] 事件链式反应:")
    print(f"   - 原始事件: 1 (STUDENT_SUBMISSION)")
    print(f"   - 产生的后续事件: ~{new_events_count - 1} 个")
    print(f"   - 总事件数: {new_events_count}")
    
    # 事件类型分析
    event_types_count = {}
    for evt in events:
        event_types_count[evt.type.value] = event_types_count.get(evt.type.value, 0) + 1
    
    print(f"\n   事件类型分布:")
    for event_type, count in event_types_count.items():
        print(f"      - {event_type}: {count}")
    
    print("\n[INSIGHT] 这演示了 Mesh 架构的威力:")
    print("   - 单个学生答题事件")
    print("   - 自动触发多个 Agent 的并行处理")
    print("   - Agent 之间通过事件总线解耦")
    
    print("="*60 + "\n")
