"""
Growth Agent（成长Agent）-- 职业发展追踪和反馈。

核心职责：
1. 追踪工程师的问题解决能力
2. 提供周期性的成长反馈和报告
3. 识别里程碑和晋升机会
4. 维护技能认证体系
"""

import logging
from datetime import datetime

from .base_agent import BaseAgent
from core.engineer_profile import EngineerLevel
from core.event_bus import Event, EventType

logger = logging.getLogger(__name__)


class GrowthAgent(BaseAgent):
    """成长Agent：职业发展追踪和反馈。"""

    @property
    def subscribed_events(self) -> list[EventType]:
        return [
            EventType.PROBLEM_RESOLVED,
            EventType.COMPETENCY_UPDATED,
            EventType.SOLUTION_VALIDATED,
        ]

    async def handle_event(self, event: Event) -> None:
        if event.type == EventType.PROBLEM_RESOLVED:
            await self._handle_problem_resolved(event)
        elif event.type == EventType.COMPETENCY_UPDATED:
            await self._handle_competency_updated(event)
        elif event.type == EventType.SOLUTION_VALIDATED:
            await self._handle_solution_validated(event)

    async def _handle_problem_resolved(self, event: Event) -> None:
        """工程师解决了一个问题后，更新成长记录。"""
        engineer_id = event.learner_id
        data = event.data

        logger.info(f"[Growth] Problem resolved for {engineer_id}")

        profile = self.get_engineer_profile(engineer_id)

        # 更新能力评估
        category = data.get("category", "unknown")
        is_correct = data.get("is_correct", False)
        solve_time = data.get("solve_time", 0)

        profile.update_competency(
            competency_id=category,
            name=category,
            category=category,
            is_correct=is_correct,
            solve_time=solve_time,
        )

        # 检查里程碑
        milestone = self._check_milestones(profile)
        if milestone:
            await self.emit(
                EventType.MILESTONE_ACHIEVED,
                engineer_id,
                {
                    "milestone": milestone,
                    "timestamp": datetime.now().isoformat(),
                },
            )

        # 检查晋升资格
        if profile.should_promote():
            await self.emit(
                EventType.ENGINEER_LEVEL_UP,
                engineer_id,
                {
                    "current_level": profile.current_level.value,
                    "suggested_level": self._suggest_next_level(profile).value,
                },
            )

        logger.info(f"[Growth] {engineer_id}: {len(profile.problem_history)} problems solved")

    async def _handle_competency_updated(self, event: Event) -> None:
        """能力更新，提供反馈。"""
        engineer_id = event.learner_id
        data = event.data

        competency_id = data.get("competency_id")
        new_level = data.get("new_level")

        logger.info(f"[Growth] {engineer_id}: {competency_id} → {new_level}")

    async def _handle_solution_validated(self, event: Event) -> None:
        """解决方案已验证，记录实际影响。"""
        engineer_id = event.learner_id
        data = event.data

        logger.info(f"[Growth] Solution validated for {engineer_id}")

    def _check_milestones(self, profile) -> str | None:
        """检查是否达成里程碑。"""
        total_solved = profile.total_problems_solved
        accuracy = profile.overall_accuracy

        milestones = [
            ("first_5", 5, "首次解决5个问题"),
            ("accuracy_80", total_solved, "诊断准确度达到80%", accuracy >= 0.80),
            ("first_expert", total_solved, "首次获得专家级能力", any(
                c.level.value == "expert" for c in profile.competencies.values()
            )),
            ("multi_domain", len(profile.competencies), "掌握多个领域", 
             len(profile.competencies) >= 3),
        ]

        for milestone_name, progress, description, *extra_condition in milestones:
            if extra_condition:
                if extra_condition[0]:
                    return description
            elif progress >= int(milestone_name.split("_")[1] if "_" in milestone_name else 0):
                pass

        # 简化版本
        if total_solved == 5:
            return "首次解决5个问题"
        elif total_solved == 10:
            return "解决10个问题纪念碑"
        elif accuracy >= 0.80 and total_solved >= 3:
            return "诊断准确度达到80%"
        elif len([c for c in profile.competencies.values() if c.level.value == "expert"]) >= 1:
            return "获得首个专家级能力"

        return None

    def _suggest_next_level(self, profile) -> EngineerLevel:
        """建议下一个职级。"""
        current = profile.current_level

        if current == EngineerLevel.TRAINEE:
            return EngineerLevel.JUNIOR
        elif current == EngineerLevel.JUNIOR:
            return EngineerLevel.INTERMEDIATE
        elif current == EngineerLevel.INTERMEDIATE:
            return EngineerLevel.SENIOR
        else:
            return EngineerLevel.EXPERT

    async def generate_growth_report(self, engineer_id: str) -> dict:
        """生成周期性成长报告。"""
        profile = self.get_engineer_profile(engineer_id)

        report = {
            "engineer_id": engineer_id,
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_problems_solved": profile.total_problems_solved,
                "overall_accuracy": profile.overall_accuracy,
                "average_solve_time": profile.average_solve_time,
                "current_level": profile.current_level.value,
            },
            "competencies": {
                cid: {
                    "name": comp.name,
                    "level": comp.level.value,
                    "mastery_score": comp.mastery_score,
                    "problems_solved": comp.problems_solved,
                    "success_rate": comp.success_rate,
                }
                for cid, comp in profile.competencies.items()
            },
            "strengths": [c.name for c in profile.competencies.values() if c.level.value == "expert"],
            "improvement_areas": profile.weak_areas,
            "recommended_next_cases": profile.get_recommended_next_cases(),
            "promotion_eligible": profile.should_promote(),
        }

        return report
