from .base_agent import BaseAgent
from .diagnosis_agent import DiagnosisAgent
from .solution_advisor_agent import SolutionAdvisorAgent
from .knowledge_agent import KnowledgeAgent
from .debug_agent import DebugAgent
from .growth_agent import GrowthAgent

# 保留旧的导出以兼容性
from .assessment_agent import AssessmentAgent
from .tutor_agent import TutorAgent
from .curriculum_agent import CurriculumAgent
from .hint_agent import HintAgent
from .engagement_agent import EngagementAgent

__all__ = [
    "BaseAgent",
    "DiagnosisAgent",
    "SolutionAdvisorAgent",
    "KnowledgeAgent",
    "DebugAgent",
    "GrowthAgent",
    # 旧版本
    "AssessmentAgent",
    "TutorAgent",
    "CurriculumAgent",
    "HintAgent",
    "EngagementAgent",
]

