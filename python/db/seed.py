"""
课程内容导入脚本

用法:
    python -m db.seed \
        --data-file data/seed_math_g7.json
"""

import argparse
import asyncio
import json
import logging
import uuid
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.learner_model import KnowledgeState as KnowledgeStateModel
from db.base import Base
from db.models import (
    Chapter,
    Course,
    Exercise,
    KnowledgeEdge,
    KnowledgePoint,
)
from db.session import create_engine, create_sessionmaker


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CourseContentSeeder:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def seed_from_json(self, json_path: Path, force: bool = False) -> dict:
        """从 JSON 文件导入课程内容"""
        logger.info(f"开始导入课程内容: {json_path}")
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        stats = {
            "course": 0,
            "chapter": 0,
            "knowledge_point": 0,
            "knowledge_edge": 0,
            "exercise": 0,
        }

        course_info = data.get("course", {})
        chapters_data = data.get("chapters", [])

        course_id = await self._import_course(course_info, force)
        stats["course"] = 1

        all_kps = []
        all_edges = []

        for chapter_data in chapters_data:
            chapter_id, kps, edges = await self._import_chapter(
                chapter_data, course_id, force
            )
            stats["chapter"] += 1
            stats["knowledge_point"] += len(kps)
            stats["knowledge_edge"] += len(edges)
            all_kps.extend(kps)
            all_edges.extend(edges)

        stats["exercise"] = await self._import_exercises(all_kps, force)

        await self._session.commit()
        
        logger.info(f"导入完成: {stats}")
        return stats

    async def _import_course(self, course_info: dict, force: bool) -> str:
        """导入课程"""
        code = course_info["code"]
        
        existing = await self._session.execute(
            select(Course).where(Course.code == code)
        )
        course = existing.scalar_one_or_none()
        
        if course:
            if force:
                course.name = course_info["name"]
                course.description = course_info.get("description")
                logger.info(f"更新课程: {code}")
                return course.id
            else:
                logger.info(f"课程已存在，跳过: {code}")
                return course.id
        
        course_id = str(uuid.uuid4())
        course = Course(
            id=course_id,
            code=code,
            name=course_info["name"],
            subject=course_info["subject"],
            grade_level=course_info.get("grade_level"),
            description=course_info.get("description"),
            is_active=True,
        )
        self._session.add(course)
        
        logger.info(f"导入课程: {code} -> {course_id}")
        return course_id

    async def _import_chapter(
        self, chapter_data: dict, course_id: str, force: bool
    ) -> tuple[str, list[dict], list[dict]]:
        """导入章节及其知识点"""
        code = chapter_data["code"]

        existing = await self._session.execute(
            select(Chapter).where(Chapter.course_id == course_id, Chapter.code == code)
        )
        chapter = existing.scalar_one_or_none()
        
        if chapter:
            if force:
                chapter.name = chapter_data["name"]
                chapter.description = chapter_data.get("description")
                chapter_id = chapter.id
                logger.info(f"更新章节: {code}")
            else:
                chapter_id = chapter.id
                logger.info(f"章节已存在，跳过: {code}")
        else:
            chapter_id = str(uuid.uuid4())
            chapter = Chapter(
                id=chapter_id,
                course_id=course_id,
                code=code,
                name=chapter_data["name"],
                order_index=chapter_data.get("order_index", 0),
                description=chapter_data.get("description"),
            )
            self._session.add(chapter)

        logger.info(f"导入章节: {code} -> {chapter_id}")

        kps = []
        edges = []

        for kp_data in chapter_data.get("knowledge_points", []):
            kp_id = str(uuid.uuid4())
            kp_code = kp_data["code"]

            kp = KnowledgePoint(
                id=kp_id,
                chapter_id=chapter_id,
                course_id=course_id,
                code=kp_code,
                name=kp_data["name"],
                difficulty=kp_data.get("difficulty", 0.5),
                description=kp_data.get("description"),
                tags=kp_data.get("tags", []),
                order_index=kp_data.get("order_index", 0),
                is_active=True,
            )
            self._session.add(kp)

            logger.info(f"  导入知识点: {kp_code} -> {kp_id}")

            kps.append({
                "id": kp_id,
                "code": kp_code,
                "prerequisites": kp_data.get("prerequisites", []),
            })

            for prereq_code in kp_data.get("prerequisites", []):
                edges.append({
                    "source_code": prereq_code,
                    "target_code": kp_code,
                })

        return chapter_id, kps, edges

    async def _create_knowledge_edges(
        self, kps: list[dict], course_id: str
    ) -> int:
        """创建知识点依赖关系"""
        edge_count = 0

        code_to_id = {kp["code"]: kp["id"] for kp in kps}

        existing_edges_result = await self._session.execute(
            select(KnowledgeEdge).where(
                KnowledgeEdge.target_kp_id.in_(code_to_id.values())
            )
        )
        existing_edges = set(
            (e.source_kp_id, e.target_kp_id) 
            for e in existing_edges_result.scalars().all()
        )

        for kp in kps:
            for prereq_code in kp["prerequisites"]:
                if prereq_code not in code_to_id:
                    logger.warning(f"找不到前置知识点: {prereq_code} -> {kp['code']}")
                    continue

                source_id = code_to_id[prereq_code]
                target_id = kp["id"]

                if (source_id, target_id) in existing_edges:
                    continue

                edge = KnowledgeEdge(
                    id=str(uuid.uuid4()),
                    source_kp_id=source_id,
                    target_kp_id=target_id,
                    relation_type="prerequisite",
                    strength=1.0,
                )
                self._session.add(edge)
                edge_count += 1
                logger.info(f"  创建依赖关系: {prereq_code} -> {kp['code']}")

        return edge_count

    async def _import_exercises(self, all_kps: list[dict], force: bool) -> int:
        """导入练习题"""
        exercise_count = 0

        code_to_kp = {}
        for kp in all_kps:
            result = await self._session.execute(
                select(KnowledgePoint).where(KnowledgePoint.code == kp["code"])
            )
            kp_obj = result.scalar_one_or_none()
            if kp_obj:
                code_to_kp[kp["code"]] = {
                    "id": kp_obj.id,
                    "chapter_id": kp_obj.chapter_id,
                    "course_id": kp_obj.course_id,
                }

        for kp in all_kps:
            kp_info = code_to_kp.get(kp["code"])
            if not kp_info:
                continue

            kp_id = kp_info["id"]
            chapter_id = kp_info["chapter_id"]
            course_id = kp_info["course_id"]

            for ex_data in kp.get("exercises", []):
                exercise_id = str(uuid.uuid4())
                ex_code = ex_data.get("code") or f"{kp['code']}_ex_{exercise_count + 1}"

                exercise = Exercise(
                    id=exercise_id,
                    knowledge_point_id=kp_id,
                    chapter_id=chapter_id,
                    course_id=course_id,
                    code=ex_code,
                    type=ex_data.get("type", "single_choice"),
                    difficulty=ex_data.get("difficulty", 0.5),
                    content=ex_data.get("content", {}),
                    answer=ex_data.get("answer", {}),
                    analysis=ex_data.get("analysis"),
                    hint_levels=ex_data.get("hint_levels", []),
                    tags=ex_data.get("tags", []),
                    is_active=True,
                )
                self._session.add(exercise)

                exercise_count += 1
                logger.info(f"    导入练习题: {ex_code} -> {exercise_id}")

        return exercise_count


async def main():
    parser = argparse.ArgumentParser(description="导入课程内容数据")
    parser.add_argument(
        "--database-url",
        type=str,
        default="sqlite+aiosqlite:///./edu_agent.db",
        help="数据库连接 URL",
    )
    parser.add_argument(
        "--data-file",
        type=str,
        default="data/seed_math_g7.json",
        help="JSON 数据文件路径",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="强制更新已存在的记录",
    )
    
    args = parser.parse_args()

    engine = create_engine(args.database_url)
    sessionmaker = create_sessionmaker(engine)

    async with sessionmaker() as session:
        seeder = CourseContentSeeder(session)
        stats = await seeder.seed_from_json(
            Path(args.data_file), force=args.force
        )

    await engine.dispose()

    print("\n导入统计:")
    for key, value in stats.items():
        print(f"  {key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())
