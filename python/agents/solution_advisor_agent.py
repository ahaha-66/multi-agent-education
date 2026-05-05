"""
Solution Advisor Agent（方案顾问Agent）-- 5G问题的解决方案建议和实施指导。

核心职责：
1. 根据诊断结果，推荐合适的解决方案
2. 提供分阶段的实施步骤（快速缓解 vs 永久解决）
3. 编织学习内容：既给方案，也解释为什么
4. 识别工程师的理解深度，动态调整指导力度

面试要点：
- 多层级方案（Quick fix → Permanent solution）
- 原理讲解与实践指导结合
- 引导而非指令：问工程师"你怎么看"而不是命令"你这样做"
"""

import json
import logging
from pathlib import Path

from .base_agent import BaseAgent
from core.event_bus import Event, EventType

logger = logging.getLogger(__name__)


class SolutionAdvisorAgent(BaseAgent):
    """方案顾问Agent：根据诊断提供解决方案和实施指导。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._load_case_library()
        self._engineer_understanding: dict[str, dict] = {}

    def _load_case_library(self):
        """加载案例库以获取解决方案信息。"""
        case_file = Path(__file__).parent.parent / "config" / "5g_case_library.json"
        try:
            with open(case_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.case_library = {
                    case["case_id"]: case for case in data.get("case_library", [])
                }
                logger.info(f"Loaded {len(self.case_library)} cases with solutions")
        except FileNotFoundError:
            logger.warning(f"Case library not found at {case_file}")
            self.case_library = {}

    @property
    def subscribed_events(self) -> list[EventType]:
        return [
            EventType.DIAGNOSIS_COMPLETE,
            EventType.ENGINEER_READY_FOR_SOLUTION,
        ]

    async def handle_event(self, event: Event) -> None:
        if event.type == EventType.DIAGNOSIS_COMPLETE:
            await self._handle_diagnosis(event)
        elif event.type == EventType.ENGINEER_READY_FOR_SOLUTION:
            await self._handle_solution_request(event)

    async def _handle_diagnosis(self, event: Event) -> None:
        """
        收到诊断结果后，推荐解决方案。

        event.data 包含: root_cause, confidence, reasoning, related_case_id
        """
        engineer_id = event.learner_id
        data = event.data

        logger.info(f"[SolutionAdvisor] Generating solution for {engineer_id}")

        root_cause = data.get("root_cause", "Unknown")
        related_case_id = data.get("related_case_id")

        # 从案例库获取解决方案
        if related_case_id and related_case_id in self.case_library:
            case = self.case_library[related_case_id]
            solutions = case.get("solutions", [])
        else:
            solutions = self._generic_solutions(root_cause)

        # 分类方案（快速 vs 永久）
        quick_fix = next((s for s in solutions if s["type"] == "immediate_mitigation"), None)
        permanent = next((s for s in solutions if s["type"] == "permanent_solution"), None)

        # 准备对工程师的建议
        recommendation = {
            "root_cause": root_cause,
            "quick_fix": quick_fix,
            "permanent_solution": permanent,
            "learning_content": self._prepare_learning_material(root_cause, related_case_id),
            "verification_checklist": self._prepare_verification_steps(solutions),
        }

        # 发布方案推荐事件
        await self.emit(
            EventType.SOLUTION_RECOMMENDED,
            engineer_id,
            recommendation,
        )

        logger.info(f"[SolutionAdvisor] Solution recommended for {root_cause}")

    async def _handle_solution_request(self, event: Event) -> None:
        """处理工程师对详细指导的请求。"""
        engineer_id = event.learner_id
        data = event.data

        solution_type = data.get("solution_type", "quick_fix")  # quick_fix or permanent
        problem_id = data.get("problem_id")

        # 根据工程师的理解水平提供不同深度的指导
        understanding_level = self._assess_understanding(engineer_id)

        guidance = self._generate_implementation_guidance(
            solution_type=solution_type,
            understanding_level=understanding_level,
            problem_id=problem_id,
        )

        await self.emit(
            EventType.IMPLEMENTATION_GUIDANCE,
            engineer_id,
            guidance,
        )

        logger.info(
            f"[SolutionAdvisor] Implementation guidance provided "
            f"(level: {understanding_level})"
        )

    def _generic_solutions(self, root_cause: str) -> list[dict]:
        """当无法找到具体案例时，生成通用解决方案建议。"""
        return [
            {
                "type": "information_gathering",
                "name": "信息收集与诊断",
                "steps": [
                    {
                        "step": 1,
                        "action": "收集网管告警",
                        "detail": f"根因: {root_cause}，收集相关告警和日志",
                    },
                    {
                        "step": 2,
                        "action": "数据验证",
                        "detail": "确认症状和数据一致性",
                    },
                ],
                "time_to_implement": "30分钟",
                "effectiveness": "N/A",
            }
        ]

    def _prepare_learning_material(self, root_cause: str, case_id: str | None) -> dict:
        """准备学习材料 - 为工程师解释为什么这样做。"""
        if case_id and case_id in self.case_library:
            case = self.case_library[case_id]
            return {
                "concept": case.get("background_knowledge", {}).get("concept"),
                "formula": case.get("background_knowledge", {}).get("formula"),
                "explanation": case.get("background_knowledge", {}).get("explanation"),
                "related_concepts": case.get("related_concepts", []),
            }
        else:
            # 通用讲解模板
            return {
                "concept": f"{root_cause}的原理",
                "explanation": f"关于{root_cause}的基础原理和影响。",
                "next_learning": "建议深入学习相关知识点。",
            }

    def _prepare_verification_steps(self, solutions: list[dict]) -> list[dict]:
        """为工程师准备验证清单。"""
        verification_steps = []

        for solution in solutions:
            if solution.get("verification"):
                verification_steps.append(
                    {
                        "solution": solution["name"],
                        "expected_results": solution["verification"].get("expected_results"),
                        "monitoring_period": solution["verification"].get("monitoring_period"),
                    }
                )

        return verification_steps

    def _assess_understanding(self, engineer_id: str) -> str:
        """
        评估工程师的理解水平。

        返回: "beginner" / "intermediate" / "advanced"
        基于历史问题解决的深度。
        """
        profile = self.get_engineer_profile(engineer_id)

        if not profile.problem_history:
            return "beginner"

        # 简单启发式：根据平均诊断准确度
        if profile.overall_accuracy > 0.75:
            return "advanced"
        elif profile.overall_accuracy > 0.50:
            return "intermediate"
        else:
            return "beginner"

    def _generate_implementation_guidance(
        self,
        solution_type: str,
        understanding_level: str,
        problem_id: str,
    ) -> dict:
        """
        根据工程师水平生成不同深度的实施指导。

        Beginner: 详细步骤 + 工具使用说明
        Intermediate: 步骤概览 + 关键点提示
        Advanced: 要点梗概 + 决策权衡说明
        """
        if understanding_level == "beginner":
            return {
                "style": "详细步骤式",
                "description": "为初学者提供每一步的详细操作说明",
                "includes": ["工具使用", "截图参考", "常见错误"],
            }
        elif understanding_level == "intermediate":
            return {
                "style": "框架式",
                "description": "提供关键步骤框架，工程师自行填充细节",
                "includes": ["步骤框架", "关键点提示", "工具推荐"],
            }
        else:
            return {
                "style": "决策式",
                "description": "只提供高层决策和权衡分析",
                "includes": ["方案对比", "成本效益", "最佳实践"],
            }
