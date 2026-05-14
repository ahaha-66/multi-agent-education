"""
练习题推荐服务 - 智能推荐下一道练习题

推荐策略：
1. 如果指定了知识点，按知识点取题
2. 如果有 curriculum 推荐，遵循课程路径
3. 否则按以下规则：
   - 优先选择：未做过、难度适中、知识点未掌握
   - 避免重复：过滤 learner_exercise_history
"""

import logging
import random
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Exercise, LearnerExerciseHistory


logger = logging.getLogger(__name__)


class ExerciseRecommender:
    """练习题推荐器"""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def recommend_next(
        self,
        learner_id: str,
        course_id: str,
        knowledge_point_id: str | None = None,
        exclude_exercise_ids: list[str] | None = None,
        count: int = 1,
    ) -> list[dict[str, Any]]:
        """
        推荐下一道练习题
        
        Args:
            learner_id: 学习者 ID
            course_id: 课程 ID
            knowledge_point_id: 知识点 ID（可选，指定则按知识点取题）
            exclude_exercise_ids: 排除的练习题 ID 列表
            count: 推荐数量
            
        Returns:
            list[dict]: 练习题列表
        """
        exclude_ids = set(exclude_exercise_ids or [])
        
        if knowledge_point_id:
            exercises = await self._get_exercises_by_kp(knowledge_point_id, exclude_ids)
        else:
            exercises = await self._get_all_exercises(course_id, exclude_ids)
            
        if not exercises:
            logger.warning(f"没有找到可推荐的练习题: learner={learner_id}, course={course_id}")
            return []
            
        recommended = self._select_exercises(exercises, count)
        
        logger.info(
            f"推荐练习题: learner={learner_id}, count={len(recommended)}, "
            f"kp={'all' if not knowledge_point_id else knowledge_point_id}"
        )
        
        return recommended

    async def _get_exercises_by_kp(
        self, knowledge_point_id: str, exclude_ids: set[str]
    ) -> list[Exercise]:
        """获取指定知识点的练习题"""
        stmt = (
            select(Exercise)
            .where(
                Exercise.knowledge_point_id == knowledge_point_id,
                Exercise.is_active == True,
                Exercise.id.notin_(exclude_ids) if exclude_ids else True,
            )
            .order_by(Exercise.difficulty)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def _get_all_exercises(
        self, course_id: str, exclude_ids: set[str]
    ) -> list[Exercise]:
        """获取课程所有练习题"""
        stmt = (
            select(Exercise)
            .where(
                Exercise.course_id == course_id,
                Exercise.is_active == True,
                Exercise.id.notin_(exclude_ids) if exclude_ids else True,
            )
            .order_by(Exercise.difficulty)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    def _select_exercises(
        self, exercises: list[Exercise], count: int
    ) -> list[dict[str, Any]]:
        """
        从候选练习题中选择最优的一道
        
        策略：
        1. 如果候选数量 <= count，直接返回
        2. 否则随机选择，避免总是推荐相同题目
        """
        if len(exercises) <= count:
            return [self._exercise_to_dict(ex) for ex in exercises]
            
        selected = random.sample(exercises, count)
        return [self._exercise_to_dict(ex) for ex in selected]

    def _exercise_to_dict(self, exercise: Exercise) -> dict[str, Any]:
        """将练习题转换为字典（隐藏答案）"""
        return {
            "id": exercise.id,
            "code": exercise.code,
            "type": exercise.type,
            "difficulty": exercise.difficulty,
            "content": exercise.content,
            "tags": exercise.tags,
            "hint_levels": [
                {"level": i + 1, "hint": hint.get("hint", "")}
                for i, hint in enumerate(exercise.hint_levels or [])
            ],
        }

    async def verify_answer(
        self, exercise_id: str, user_answer: Any
    ) -> dict[str, Any]:
        """
        验证答案
        
        Args:
            exercise_id: 练习题 ID
            user_answer: 用户提交的答案
            
        Returns:
            dict: {
                "is_correct": bool,
                "correct_answer": Any,
                "analysis": dict | None
            }
        """
        stmt = select(Exercise).where(Exercise.id == exercise_id)
        result = await self._session.execute(stmt)
        exercise = result.scalar_one_or_none()
        
        if not exercise:
            logger.warning(f"找不到练习题: {exercise_id}")
            return {
                "is_correct": False,
                "correct_answer": None,
                "analysis": None,
            }
            
        is_correct = self._check_answer(user_answer, exercise.answer)
        
        return {
            "is_correct": is_correct,
            "correct_answer": exercise.answer,
            "analysis": exercise.analysis,
        }

    def _check_answer(self, user_answer: Any, correct_answer: Any) -> bool:
        """检查答案是否正确"""
        if isinstance(correct_answer, dict) and "value" in correct_answer:
            return str(user_answer).strip().lower() == str(correct_answer["value"]).strip().lower()
            
        if isinstance(correct_answer, list):
            user_str = str(user_answer).strip().lower()
            return any(
                str(ans).strip().lower() == user_str
                for ans in correct_answer
            )
            
        return str(user_answer).strip().lower() == str(correct_answer).strip().lower()

    async def record_attempt(
        self,
        learner_id: str,
        exercise_id: str,
        is_correct: bool,
        correlation_id: str | None = None,
    ) -> None:
        """
        记录练习尝试
        
        Args:
            learner_id: 学习者 ID
            exercise_id: 练习题 ID
            is_correct: 是否正确
            correlation_id: 关联 ID
        """
        from datetime import datetime
        
        stmt = (
            select(LearnerExerciseHistory)
            .where(
                LearnerExerciseHistory.learner_id == learner_id,
                LearnerExerciseHistory.exercise_id == exercise_id,
            )
        )
        result = await self._session.execute(stmt)
        history = result.scalar_one_or_none()
        
        now = datetime.utcnow()
        
        if history:
            history.attempt_count += 1
            history.is_correct = is_correct
            history.last_attempt_at = now
            history.correlation_id = correlation_id
            logger.info(
                f"更新练习历史: learner={learner_id}, exercise={exercise_id}, "
                f"attempts={history.attempt_count}"
            )
        else:
            new_history = LearnerExerciseHistory(
                learner_id=learner_id,
                exercise_id=exercise_id,
                is_correct=is_correct,
                attempt_count=1,
                first_attempt_at=now,
                last_attempt_at=now,
                correlation_id=correlation_id,
            )
            self._session.add(new_history)
            logger.info(
                f"创建练习历史: learner={learner_id}, exercise={exercise_id}"
            )
            
        await self._session.commit()

    async def get_learner_history(
        self, learner_id: str, exercise_ids: list[str] | None = None
    ) -> dict[str, LearnerExerciseHistory]:
        """
        获取学习者的练习历史
        
        Returns:
            dict: {exercise_id: history}
        """
        stmt = select(LearnerExerciseHistory).where(
            LearnerExerciseHistory.learner_id == learner_id
        )
        
        if exercise_ids:
            stmt = stmt.where(LearnerExerciseHistory.exercise_id.in_(exercise_ids))
            
        result = await self._session.execute(stmt)
        histories = result.scalars().all()
        
        return {h.exercise_id: h for h in histories}

    async def get_wrong_exercises(
        self, learner_id: str, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        获取学习者的错题列表
        
        Returns:
            list[dict]: 错题列表
        """
        stmt = (
            select(LearnerExerciseHistory, Exercise)
            .join(Exercise, LearnerExerciseHistory.exercise_id == Exercise.id)
            .where(
                LearnerExerciseHistory.learner_id == learner_id,
                LearnerExerciseHistory.is_correct == False,
            )
            .order_by(LearnerExerciseHistory.last_attempt_at.desc())
            .limit(limit)
        )
        
        result = await self._session.execute(stmt)
        rows = result.all()
        
        wrong_exercises = []
        for history, exercise in rows:
            wrong_exercises.append({
                "exercise_id": exercise.id,
                "code": exercise.code,
                "type": exercise.type,
                "difficulty": exercise.difficulty,
                "content": exercise.content,
                "correct_answer": exercise.answer,
                "analysis": exercise.analysis,
                "attempt_count": history.attempt_count,
                "last_attempt_at": history.last_attempt_at.isoformat() if history.last_attempt_at else None,
            })
            
        return wrong_exercises
