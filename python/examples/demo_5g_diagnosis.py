"""
5G通信诊断系统快速演示

这个脚本展示如何使用新的Agent系统来处理一个真实的5G诊断问题。
"""

import asyncio
import json
from pathlib import Path

from agents import DiagnosisAgent, SolutionAdvisorAgent, GrowthAgent
from core import EventBus, EventType, EngineerProfile
from core.event_bus import Event


async def demo_5g_diagnosis():
    """演示：诊断一个5G干扰问题"""

    print("=" * 80)
    print("🚀 5G通信诊断系统演示")
    print("=" * 80)
    print()

    # 1. 初始化系统
    print("【初始化】创建事件总线和Agent...")
    event_bus = EventBus()
    engineer_profiles: dict[str, EngineerProfile] = {}

    diagnosis_agent = DiagnosisAgent("Diagnosis", event_bus, engineer_profiles)
    solution_agent = SolutionAdvisorAgent("Solution", event_bus, engineer_profiles)
    growth_agent = GrowthAgent("Growth", event_bus, engineer_profiles)

    print("✓ 系统初始化完成\n")

    # 2. 工程师上报问题
    print("【问题上报】工程师上报一个问题...")
    problem_data = {
        "problem_id": "PRB_20240505_001",
        "title": "城区基站丢包率突增",
        "symptoms": ["丢包率从2% 升到 15%", "SINR下降"],
        "context": {
            "base_station": "Cell_A",
            "band": "n78 (3.5GHz)",
            "antenna": "64T64R Massive MIMO",
            "environment": "urban",
            "weather": "sunny",
        },
    }

    print(f"   问题ID: {problem_data['problem_id']}")
    print(f"   标题: {problem_data['title']}")
    print(f"   症状: {problem_data['symptoms']}")
    print()

    # 3. 发布问题事件
    problem_event = Event(
        type=EventType.PROBLEM_REPORTED,
        source="WebUI",
        learner_id="engineer_001",
        data=problem_data,
    )

    print("【诊断】Diagnosis Agent开始诊断...")
    await event_bus.publish(problem_event)

    # 模拟诊断过程
    await asyncio.sleep(0.5)

    # 获取诊断结果
    engineer = engineer_profiles.get("engineer_001")
    if engineer:
        print("✓ 诊断完成！")
        print()

        # 4. 显示诊断结果
        print("【诊断结果】")
        print("-" * 80)

        case_lib_path = Path(__file__).parent / "config" / "5g_case_library.json"
        if case_lib_path.exists():
            with open(case_lib_path, "r", encoding="utf-8") as f:
                case_data = json.load(f)
                case = case_data["case_library"][0]  # 获取第一个案例

                print(f"根本原因: {case['diagnosis']['root_cause']}")
                print(f"置信度: {case['diagnosis']['confidence']:.0%}")
                print(f"机制: {case['diagnosis']['mechanism']}")
                print()

                # 5. 显示诊断步骤
                print("【诊断步骤】")
                for step in case["diagnosis_steps"][:3]:
                    print(f"  {step['step']}. {step['name']}")
                    print(f"     {step['action']}")
                print()

                # 6. 显示背景知识
                print("【背景知识】")
                bg_k = case["background_knowledge"]
                print(f"   概念: {bg_k['concept']}")
                print(f"   公式: {bg_k['formula']}")
                print(f"   解释: {bg_k['explanation']}")
                print()

                # 7. 显示解决方案
                print("【解决方案】")
                print("-" * 80)
                for solution in case["solutions"]:
                    print(f"\n   {solution['type'].upper()}")
                    print(f"   名称: {solution['name']}")
                    print(f"   时间: {solution['time_to_implement']}")
                    print(f"   效果: {solution['effectiveness']}")
                    if solution.get("side_effects"):
                        print(f"   副作用: {solution['side_effects']}")

        print()
        print("=" * 80)
        print("✨ 演示完成!")
        print("=" * 80)
        print()
        print("📚 后续建议：")
        print("  1. 工程师选择快速缓解或永久方案")
        print("  2. Debug Agent提供验证步骤")
        print("  3. 工程师执行并反馈结果")
        print("  4. Growth Agent更新能力评估")
        print()


if __name__ == "__main__":
    asyncio.run(demo_5g_diagnosis())
