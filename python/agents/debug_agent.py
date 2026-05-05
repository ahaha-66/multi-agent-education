"""
Debug Agent（调试Agent）-- 方案验证和工具指导。

核心职责：
1. 提供工具使用指南（频谱仪、网管系统等）
2. 给出验证步骤清单
3. 帮助工程师诊断实施过程中的问题
"""

import logging

from .base_agent import BaseAgent
from core.event_bus import Event, EventType

logger = logging.getLogger(__name__)


class DebugAgent(BaseAgent):
    """调试Agent：方案验证和工具指导。"""

    @property
    def subscribed_events(self) -> list[EventType]:
        return [
            EventType.SOLUTION_VALIDATED,
            EventType.VERIFICATION_STARTED,
        ]

    async def handle_event(self, event: Event) -> None:
        if event.type == EventType.SOLUTION_VALIDATED:
            await self._handle_verification(event)
        elif event.type == EventType.VERIFICATION_STARTED:
            await self._handle_verification_request(event)

    async def _handle_verification(self, event: Event) -> None:
        """提供验证步骤和工具指导。"""
        engineer_id = event.learner_id
        data = event.data

        solution_type = data.get("solution_type", "quick_fix")
        root_cause = data.get("root_cause", "")

        logger.info(f"[Debug] Providing verification guidance")

        verification_steps = self._generate_verification_steps(solution_type, root_cause)

        await self.emit(
            EventType.VERIFICATION_STEP_RESULT,
            engineer_id,
            {
                "steps": verification_steps,
                "tools_needed": self._get_tools(solution_type),
                "success_criteria": self._get_success_criteria(solution_type),
                "monitoring_duration": self._get_monitoring_duration(solution_type),
            },
        )

    async def _handle_verification_request(self, event: Event) -> None:
        """处理工程师的验证请求。"""
        engineer_id = event.learner_id
        data = event.data

        step_result = data.get("step_result")
        problem_id = data.get("problem_id")

        logger.info(f"[Debug] Verification step result received")

        # 评价结果是否正确
        is_correct = self._evaluate_result(step_result)

        if is_correct:
            feedback = "✓ 正确。继续下一步。"
        else:
            feedback = "✗ 有偏差。检查：" + self._get_diagnostics(step_result)

        await self.emit(
            EventType.VERIFICATION_COMPLETE,
            engineer_id,
            {
                "is_correct": is_correct,
                "feedback": feedback,
                "next_action": self._get_next_action(is_correct),
            },
        )

    def _generate_verification_steps(self, solution_type: str, root_cause: str) -> list[dict]:
        """生成验证步骤清单。"""
        if solution_type == "quick_fix":
            return [
                {
                    "step": 1,
                    "name": "参数生效检查",
                    "action": "登入网管，查看参数是否已更新",
                },
                {
                    "step": 2,
                    "name": "KPI监控",
                    "action": "观察丢包率、SINR等指标3-5分钟",
                },
                {
                    "step": 3,
                    "name": "副作用评估",
                    "action": "检查覆盖、邻小区干扰是否恶化",
                },
            ]
        else:  # permanent_solution
            return [
                {
                    "step": 1,
                    "name": "硬件更换验证",
                    "action": "确认新硬件已安装，序列号记录",
                },
                {
                    "step": 2,
                    "name": "性能测试",
                    "action": "用频谱仪和KPI工具验证性能恢复",
                },
                {
                    "step": 3,
                    "name": "72小时稳定性监控",
                    "action": "确保3天内未再出现问题",
                },
            ]

    def _get_tools(self, solution_type: str) -> list[str]:
        """获取需要的工具列表。"""
        if solution_type == "quick_fix":
            return ["网管系统", "KPI监控面板"]
        else:
            return ["频谱仪", "网管系统", "KPI监控"]

    def _get_success_criteria(self, solution_type: str) -> dict:
        """获取成功标准。"""
        return {
            "packet_loss_rate": "< 2%",
            "sinr": "> 5dB",
            "user_complaints": "下降",
        }

    def _get_monitoring_duration(self, solution_type: str) -> str:
        """获取监控周期。"""
        if solution_type == "quick_fix":
            return "30分钟"
        else:
            return "72小时"

    def _evaluate_result(self, step_result: dict) -> bool:
        """评价工程师的验证结果是否正确。"""
        # 简化实现：检查关键指标是否在预期范围内
        return True  # 实际应该有更复杂的逻辑

    def _get_diagnostics(self, step_result: dict) -> str:
        """获取诊断信息。"""
        return "参数是否真的改了？网管缓存？基站重启？"

    def _get_next_action(self, is_correct: bool) -> str:
        """获取下一步行动。"""
        if is_correct:
            return "验证成功，标记问题为已解决"
        else:
            return "重新检查，或联系技术支持"
