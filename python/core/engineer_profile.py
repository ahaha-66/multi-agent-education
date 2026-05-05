"""
工程师个人资料模型 - 5G通信诊断系统版。

与教育版LearnerModel不同：
- 记录"问题解决能力"而非"知识点学习进度"
- 用"诊断准确度、解决速度"而非"考试分数"评估
- 职业发展导向（晋升、认证）而非学分导向

面试要点：
- 适用场景转换：从教育到企业工程师评估
- 多维度能力模型设计
- 职业成长的数据化表示
"""

import logging
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class EngineerLevel(str, Enum):
    """工程师职级（基于能力体系）。"""

    TRAINEE = "trainee"  # 实习/新手
    JUNIOR = "junior"  # 初级（1-2年）
    INTERMEDIATE = "intermediate"  # 中级（2-5年）
    SENIOR = "senior"  # 资深（5+年）
    EXPERT = "expert"  # 专家


class CompetencyLevel(str, Enum):
    """单项能力等级。"""

    UNKNOWN = "unknown"  # 未接触
    BEGINNER = "beginner"  # 初学（0-30%）
    INTERMEDIATE = "intermediate"  # 中等（30-60%）
    PROFICIENT = "proficient"  # 熟练（60-85%）
    EXPERT = "expert"  # 专家（85-100%）


class ProblemRecord(BaseModel):
    """单个问题的解决记录。"""

    problem_id: str
    case_id: str  # 关联的案例ID
    category: str  # 干扰诊断 / 容量评估 / 覆盖优化等
    difficulty: str  # easy / medium / hard
    
    # 解决过程
    reported_time: datetime
    start_time: datetime
    resolved_time: datetime
    
    # 诊断准确性
    diagnosis_correct: bool
    diagnosis_accuracy: float  # 0-1
    root_cause_identified: bool
    
    # 时间效率
    time_to_diagnose: int  # 分钟
    time_to_resolve: int  # 分钟
    
    # 学习收获
    key_learnings: list[str] = []
    concepts_mastered: list[str] = []
    mistakes: list[str] = []
    
    # 辅助情况
    hints_requested: int = 0
    mentor_assists: int = 0


class CompetencyRecord(BaseModel):
    """单项能力的评估记录。"""

    competency_id: str
    name: str
    category: str  # 干扰诊断 / 容量评估 等
    
    level: CompetencyLevel = CompetencyLevel.UNKNOWN
    mastery_score: float = 0.0  # 0-1
    
    # 统计
    problems_solved: int = 0
    success_rate: float = 0.0  # 诊断准确度
    average_solve_time: int = 0  # 平均解决时间（分钟）
    
    # 時間戳
    first_attempt: datetime | None = None
    last_attempt: datetime | None = None
    last_updated: datetime | None = None


class EngineerProfile(BaseModel):
    """工程师个人资料 - 替代LearnerModel。"""

    engineer_id: str
    name: str = "Unknown Engineer"
    role: str = "5G Network Optimization Engineer"
    
    # 职级
    current_level: EngineerLevel = EngineerLevel.JUNIOR
    joining_date: datetime = Field(default_factory=datetime.now)
    
    # 能力评估
    competencies: dict[str, CompetencyRecord] = Field(default_factory=dict)
    
    # 问题解决历史
    problem_history: list[ProblemRecord] = Field(default_factory=list)
    
    # 学习进度（可选的深度学习路径）
    learning_path: dict[str, Any] = Field(default_factory=dict)
    
    # 统计指标
    @property
    def total_problems_solved(self) -> int:
        """总共解决过多少个问题。"""
        return len(self.problem_history)
    
    @property
    def overall_accuracy(self) -> float:
        """总体诊断准确度。"""
        if not self.problem_history:
            return 0.0
        correct = sum(1 for p in self.problem_history if p.diagnosis_correct)
        return correct / len(self.problem_history)
    
    @property
    def average_solve_time(self) -> int:
        """平均解决时间（分钟）。"""
        if not self.problem_history:
            return 0
        total_time = sum(p.time_to_resolve for p in self.problem_history)
        return total_time // len(self.problem_history)
    
    @property
    def dominant_category(self) -> str | None:
        """最强的能力方向。"""
        if not self.competencies:
            return None
        return max(
            self.competencies.items(),
            key=lambda x: x[1].mastery_score
        )[0]
    
    @property
    def weak_areas(self) -> list[str]:
        """薄弱的能力方向。"""
        return [
            cid for cid, comp in self.competencies.items()
            if comp.level in [CompetencyLevel.UNKNOWN, CompetencyLevel.BEGINNER]
        ]
    
    # 核心方法
    
    def add_problem(self, record: ProblemRecord) -> None:
        """添加问题解决记录。"""
        self.problem_history.append(record)
        logger.info(
            "[%s] Problem added: %s (accuracy: %.1f%%)",
            self.engineer_id,
            record.problem_id,
            record.diagnosis_accuracy * 100
        )
    
    def update_competency(
        self,
        competency_id: str,
        name: str,
        category: str,
        is_correct: bool,
        solve_time: int
    ) -> None:
        """更新某项能力的掌握度。"""
        if competency_id not in self.competencies:
            self.competencies[competency_id] = CompetencyRecord(
                competency_id=competency_id,
                name=name,
                category=category,
                first_attempt=datetime.now()
            )
        
        record = self.competencies[competency_id]
        
        # 更新统计
        record.problems_solved += 1
        record.average_solve_time = (
            (record.average_solve_time * (record.problems_solved - 1) + solve_time)
            // record.problems_solved
        )
        
        # 更新准确度
        old_success = record.problems_solved - 1
        if old_success > 0:
            record.success_rate = (
                (record.success_rate * old_success + (1.0 if is_correct else 0.0))
                / record.problems_solved
            )
        else:
            record.success_rate = 1.0 if is_correct else 0.0
        
        # 根据成功率确定等级
        if record.success_rate >= 0.85 and record.problems_solved >= 3:
            record.level = CompetencyLevel.EXPERT
            record.mastery_score = 0.95
        elif record.success_rate >= 0.60 and record.problems_solved >= 2:
            record.level = CompetencyLevel.PROFICIENT
            record.mastery_score = 0.70
        elif record.success_rate >= 0.40:
            record.level = CompetencyLevel.INTERMEDIATE
            record.mastery_score = 0.45
        else:
            record.level = CompetencyLevel.BEGINNER
            record.mastery_score = 0.15
        
        record.last_attempt = datetime.now()
        record.last_updated = datetime.now()
        
        logger.info(
            "[%s] Competency updated: %s → %s (accuracy: %.1f%%)",
            self.engineer_id,
            competency_id,
            record.level.value,
            record.success_rate * 100
        )
    
    def get_recommended_next_cases(self, num: int = 3) -> list[str]:
        """根据能力评估，推荐下一阶段的案例。"""
        recommendations = []
        
        # 策略1：强化弱项
        if self.weak_areas:
            for weak_category in self.weak_areas[:1]:
                recommendations.append(f"easy_{weak_category}")
        
        # 策略2：挑战强项
        if self.dominant_category:
            recommendations.append(f"medium_{self.dominant_category}")
            recommendations.append(f"hard_{self.dominant_category}")
        
        # 策略3：平衡其他类别
        other_categories = set(
            c.category for c in self.competencies.values()
        ) - {self.dominant_category}
        for cat in list(other_categories)[:1]:
            recommendations.append(f"easy_{cat}")
        
        return recommendations[:num]
    
    def should_promote(self) -> bool:
        """是否应该晋升？"""
        # 条件：总体准确度>80% + 解决问题>10 + 有expert级能力
        return (
            self.overall_accuracy > 0.80
            and self.total_problems_solved > 10
            and any(
                c.level == CompetencyLevel.EXPERT
                for c in self.competencies.values()
            )
        )
    
    def get_certification_eligible(self) -> list[str]:
        """获取可申请的认证列表。"""
        eligible = []
        
        for competency_id, comp in self.competencies.items():
            if comp.level == CompetencyLevel.EXPERT and comp.problems_solved >= 5:
                eligible.append(f"{comp.name}_certification")
        
        return eligible
