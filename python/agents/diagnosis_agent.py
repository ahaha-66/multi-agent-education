"""
Diagnosis Agent（诊断Agent）-- 5G通信问题根因诊断。

核心职责：
1. 接收工程师上报的问题症状 + 上下文信息
2. 通过知识图谱推理，诊断最可能的根本原因
3. 返回诊断结果 + 诊断依据 + 置信度 + 原理讲解

面试要点：
- 多源信息融合：症状、KPI、上下文综合判断
- 概率推理：不是简单规则匹配，而是贝叶斯推理
- 可解释诊断：不仅给答案，还要说明为什么
"""

import json
import logging
from pathlib import Path

from .base_agent import BaseAgent
from core.event_bus import Event, EventType

logger = logging.getLogger(__name__)


class DiagnosisAgent(BaseAgent):
    """诊断Agent：根据症状和上下文诊断5G问题的根本原因。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._load_case_library()
        self._diagnosis_history: dict[str, list[dict]] = {}

    def _load_case_library(self):
        """加载案例库作为诊断知识库。"""
        case_file = Path(__file__).parent.parent / "config" / "5g_case_library.json"
        try:
            with open(case_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.case_library = data.get("case_library", [])
                logger.info(f"Loaded {len(self.case_library)} cases for diagnosis")
        except FileNotFoundError:
            logger.warning(f"Case library not found at {case_file}")
            self.case_library = []

    @property
    def subscribed_events(self) -> list[EventType]:
        return [EventType.PROBLEM_REPORTED, EventType.CONTEXT_PROVIDED]

    async def handle_event(self, event: Event) -> None:
        if event.type == EventType.PROBLEM_REPORTED:
            await self._handle_problem_report(event)
        elif event.type == EventType.CONTEXT_PROVIDED:
            await self._handle_context_update(event)

    async def _handle_problem_report(self, event: Event) -> None:
        """
        处理工程师的问题上报。

        event.data 结构：
        {
            "problem_id": "PRB_20240505_001",
            "title": "城区基站丢包率突增",
            "symptoms": ["丢包率从2%升到15%", "SINR下降"],
            "context": {
                "base_station": "Cell_A",
                "band": "n78",
                "antenna": "64T64R",
                "location": "urban"
            }
        }
        """
        engineer_id = event.learner_id
        data = event.data

        logger.info(f"[Diagnosis] Processing problem report from {engineer_id}")

        # 执行诊断
        problem_id = data.get("problem_id", "unknown")
        symptoms = data.get("symptoms", [])
        context = data.get("context", {})

        diagnosis_result = self._diagnose(symptoms, context)

        # 保存诊断历史
        if engineer_id not in self._diagnosis_history:
            self._diagnosis_history[engineer_id] = []
        self._diagnosis_history[engineer_id].append(diagnosis_result)

        # 发布诊断完成事件
        await self.emit(
            EventType.DIAGNOSIS_COMPLETE,
            engineer_id,
            {
                "problem_id": problem_id,
                "root_cause": diagnosis_result["root_cause"],
                "confidence": diagnosis_result["confidence"],
                "reasoning": diagnosis_result["reasoning"],
                "background_knowledge": diagnosis_result.get("background_knowledge"),
                "next_steps": diagnosis_result.get("next_steps"),
            },
        )

        logger.info(
            f"[Diagnosis] Diagnosed: {diagnosis_result['root_cause']} "
            f"(confidence: {diagnosis_result['confidence']:.1%})"
        )

    async def _handle_context_update(self, event: Event) -> None:
        """处理工程师补充的上下文信息，重新诊断。"""
        engineer_id = event.learner_id
        data = event.data

        logger.info(f"[Diagnosis] Context updated from {engineer_id}, re-diagnosing")

        # 重新诊断（实现类似_handle_problem_report）
        symptoms = data.get("symptoms", [])
        context = data.get("context", {})

        diagnosis_result = self._diagnose(symptoms, context)

        await self.emit(
            EventType.DIAGNOSIS_COMPLETE,
            engineer_id,
            {
                "root_cause": diagnosis_result["root_cause"],
                "confidence": diagnosis_result["confidence"],
                "reasoning": diagnosis_result["reasoning"],
            },
        )

    def _diagnose(self, symptoms: list[str], context: dict) -> dict:
        """
        [核心诊断逻辑] 根据症状和上下文进行诊断。

        这是一个简化的实现，实际应该使用贝叶斯推理或ML模型。
        """
        # 步骤1：从案例库中查找匹配的案例
        candidates = self._find_matching_cases(symptoms, context)

        if not candidates:
            # 降级：只看症状
            candidates = self._find_by_symptoms(symptoms)

        if not candidates:
            # 最后手段：通用诊断
            return self._generic_diagnosis(symptoms, context)

        # 步骤2：选择最匹配的案例
        best_match = max(candidates, key=lambda x: x["match_score"])

        diagnosis = {
            "root_cause": best_match["case"]["diagnosis"]["root_cause"],
            "mechanism": best_match["case"]["diagnosis"]["mechanism"],
            "confidence": best_match["match_score"],
            "reasoning": self._explain_diagnosis(best_match),
            "background_knowledge": best_match["case"]["background_knowledge"],
            "next_steps": best_match["case"]["diagnosis_steps"],
            "related_case_id": best_match["case"]["case_id"],
        }

        return diagnosis

    def _find_matching_cases(self, symptoms: list[str], context: dict) -> list[dict]:
        """从案例库中查找匹配度高的案例。"""
        matches = []

        for case in self.case_library:
            match_score = self._calculate_match_score(case, symptoms, context)

            if match_score > 0.5:  # 至少50%匹配度
                matches.append({"case": case, "match_score": match_score})

        return sorted(matches, key=lambda x: x["match_score"], reverse=True)

    def _calculate_match_score(self, case: dict, symptoms: list[str], context: dict) -> float:
        """
        计算案例与当前问题的匹配度 (0-1)。

        简化实现：关键词匹配 + 上下文相似度。
        """
        score = 0.0

        # 症状匹配
        case_symptoms = case.get("symptoms", [])
        if case_symptoms:
            matched_symptoms = 0
            for symptom in symptoms:
                if any(kw in symptom for kw in case_symptoms):
                    matched_symptoms += 1
            symptom_score = matched_symptoms / len(case_symptoms)
            score += symptom_score * 0.6

        # 上下文匹配（带宽、天气等）
        case_context = case.get("scenario", {})
        if case_context:
            context_matches = 0
            total_fields = 0
            for key in case_context:
                if key in context:
                    if context[key] == case_context[key]:
                        context_matches += 1
                    total_fields += 1
            if total_fields > 0:
                context_score = context_matches / total_fields
                score += context_score * 0.4

        return min(score, 1.0)

    def _find_by_symptoms(self, symptoms: list[str]) -> list[dict]:
        """仅通过症状关键词匹配案例。"""
        matches = []
        for case in self.case_library:
            case_symptoms = case.get("symptoms", [])
            matched = sum(1 for s in symptoms if any(kw in s for kw in case_symptoms))
            if matched > 0:
                score = matched / max(len(symptoms), len(case_symptoms))
                matches.append({"case": case, "match_score": score})

        return sorted(matches, key=lambda x: x["match_score"], reverse=True)[:3]

    def _generic_diagnosis(self, symptoms: list[str], context: dict) -> dict:
        """当无法从案例库匹配时的通用诊断。"""
        return {
            "root_cause": "Unknown (需要更多信息)",
            "confidence": 0.0,
            "reasoning": f"症状: {symptoms}\n上下文: {context}",
            "background_knowledge": {
                "note": "根据提供的信息无法确定根本原因，建议：\n"
                "1. 提供更多症状信息\n"
                "2. 提供网管告警日志\n"
                "3. 提供KPI数据变化趋势"
            },
            "next_steps": ["补充上下文信息", "收集网管日志", "联系技术支持"],
        }

    def _explain_diagnosis(self, match: dict) -> str:
        """生成诊断的解释说明。"""
        case = match["case"]
        score = match["match_score"]

        explanation = (
            f"诊断依据 (匹配度: {score:.1%}):\n"
            f"  • 案例ID: {case['case_id']}\n"
            f"  • 分类: {case['category']}\n"
            f"  • 机制: {case['diagnosis']['mechanism']}\n"
        )

        diagnosis_steps = case.get("diagnosis_steps", [])
        if diagnosis_steps:
            explanation += "\n诊断步骤:\n"
            for step in diagnosis_steps[:3]:  # 只显示前3个步骤
                explanation += f"  {step['step']}. {step['name']}: {step['action']}\n"

        return explanation
