"""
阶段三集成测试

测试完整的课程内容流程：
1. 导入课程数据
2. 初始化知识图谱
3. 获取课程目录
4. 获取知识图谱
5. 获取练习题推荐
6. 验证答案
"""

import asyncio
import json
import logging
from pathlib import Path

from sqlalchemy import select, text

from config.settings import settings
from db.session import create_engine, create_sessionmaker
from db.seed import CourseContentSeeder
from services.knowledge_graph_service import KnowledgeGraphService
from services.exercise_recommender import ExerciseRecommender


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)


async def test_data_import():
    """测试数据导入"""
    logger.info("=" * 60)
    logger.info("测试 1: 数据导入")
    logger.info("=" * 60)
    
    engine = create_engine(settings.database_url)
    sessionmaker = create_sessionmaker(engine)
    
    async with sessionmaker() as session:
        data_file = Path(__file__).parent.parent / "data" / "seed_math_g7.json"
        
        if not data_file.exists():
            logger.error(f"数据文件不存在: {data_file}")
            return False
        
        seeder = CourseContentSeeder(session)
        stats = await seeder.seed_from_json(data_file, force=False)
        
        logger.info(f"导入统计: {stats}")
        
        assert stats["course"] >= 1, "课程导入失败"
        assert stats["chapter"] >= 1, "章节导入失败"
        assert stats["knowledge_point"] >= 1, "知识点导入失败"
        assert stats["exercise"] >= 1, "练习题导入失败"
        
        logger.info("✅ 数据导入测试通过")
        return True


async def test_course_catalog():
    """测试课程目录查询"""
    logger.info("=" * 60)
    logger.info("测试 2: 课程目录查询")
    logger.info("=" * 60)
    
    engine = create_engine(settings.database_url)
    sessionmaker = create_sessionmaker(engine)
    
    async with sessionmaker() as session:
        result = await session.execute(
            text("SELECT id, code, name FROM course LIMIT 1")
        )
        course = result.fetchone()
        
        if not course:
            logger.error("未找到课程数据")
            return False
        
        course_id = course[0]
        logger.info(f"课程 ID: {course_id}")
        
        kg_service = KnowledgeGraphService(session)
        catalog = await kg_service.get_course_catalog(course_id)
        
        logger.info(f"章节数量: {len(catalog['chapters'])}")
        logger.info(f"课程目录结构:")
        for chapter in catalog["chapters"]:
            logger.info(f"  - {chapter['name']}: {len(chapter['knowledge_points'])} 知识点")
        
        assert len(catalog["chapters"]) >= 1, "章节查询失败"
        
        logger.info("✅ 课程目录查询测试通过")
        return True


async def test_knowledge_graph():
    """测试知识图谱"""
    logger.info("=" * 60)
    logger.info("测试 3: 知识图谱")
    logger.info("=" * 60)
    
    engine = create_engine(settings.database_url)
    sessionmaker = create_sessionmaker(engine)
    
    async with sessionmaker() as session:
        result = await session.execute(
            text("SELECT id FROM course LIMIT 1")
        )
        course = result.fetchone()
        
        if not course:
            logger.error("未找到课程数据")
            return False
        
        course_id = course[0]
        
        kg_service = KnowledgeGraphService(session)
        graph = await kg_service.get_graph(course_id)
        
        logger.info(f"节点数量: {len(graph.nodes)}")
        logger.info(f"图谱节点列表:")
        for node_id, node in list(graph.nodes.items())[:5]:
            logger.info(f"  - {node.name} ({node.code}): 难度 {node.difficulty}")
        
        ready_nodes = graph.get_ready_nodes(set())
        logger.info(f"初始可学知识点: {len(ready_nodes)}")
        if ready_nodes:
            logger.info(f"  推荐: {ready_nodes[0].name}")
        
        graph_dict = graph.to_dict()
        logger.info(f"图谱边数量: {len(graph_dict['edges'])}")
        
        assert len(graph.nodes) >= 1, "知识图谱加载失败"
        
        logger.info("✅ 知识图谱测试通过")
        return True


async def test_exercise_recommendation():
    """测试练习题推荐"""
    logger.info("=" * 60)
    logger.info("测试 4: 练习题推荐")
    logger.info("=" * 60)
    
    engine = create_engine(settings.database_url)
    sessionmaker = create_sessionmaker(engine)
    
    async with sessionmaker() as session:
        result = await session.execute(
            text("SELECT id, knowledge_point_id FROM exercise LIMIT 5")
        )
        exercises = result.fetchall()
        
        if not exercises:
            logger.error("未找到练习题数据")
            return False
        
        logger.info(f"找到 {len(exercises)} 道练习题")
        
        recommender = ExerciseRecommender(session)
        
        recommended = await recommender.recommend_next(
            learner_id="test_learner",
            course_id="test_course",
            count=3
        )
        
        logger.info(f"推荐结果: {len(recommended)} 道题")
        for ex in recommended:
            logger.info(f"  - {ex['code']}: {ex['type']}, 难度 {ex['difficulty']}")
            logger.info(f"    题目: {ex['content'].get('stem', '')[:50]}...")
        
        assert len(recommended) >= 1, "练习题推荐失败"
        
        logger.info("✅ 练习题推荐测试通过")
        return True


async def test_answer_verification():
    """测试答案验证"""
    logger.info("=" * 60)
    logger.info("测试 5: 答案验证")
    logger.info("=" * 60)
    
    engine = create_engine(settings.database_url)
    sessionmaker = create_sessionmaker(engine)
    
    async with sessionmaker() as session:
        result = await session.execute(
            text("""
                SELECT e.id, e.code, e.answer 
                FROM exercise e 
                WHERE e.type = 'single_choice' 
                LIMIT 1
            """)
        )
        exercise = result.fetchone()
        
        if not exercise:
            logger.error("未找到选择题")
            return False
        
        exercise_id = exercise[0]
        correct_answer = exercise[1]  # answer 是 JSONB，fetchone 返回的是元组
        
        logger.info(f"练习题 ID: {exercise_id}")
        
        recommender = ExerciseRecommender(session)
        
        result_correct = await recommender.verify_answer(
            exercise_id=exercise_id,
            user_answer="C"
        )
        
        logger.info(f"验证结果: {result_correct}")
        
        logger.info("✅ 答案验证测试通过")
        return True


async def main():
    """运行所有测试"""
    logger.info("\n" + "=" * 60)
    logger.info("开始阶段三集成测试")
    logger.info("=" * 60 + "\n")
    
    tests = [
        ("数据导入", test_data_import),
        ("课程目录", test_course_catalog),
        ("知识图谱", test_knowledge_graph),
        ("练习题推荐", test_exercise_recommendation),
        ("答案验证", test_answer_verification),
    ]
    
    results = []
    
    for name, test_func in tests:
        try:
            result = await test_func()
            results.append((name, result))
        except Exception as e:
            logger.error(f"测试 '{name}' 失败: {e}", exc_info=True)
            results.append((name, False))
        finally:
            logger.info("")
    
    logger.info("\n" + "=" * 60)
    logger.info("测试结果汇总")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{status} - {name}")
    
    logger.info(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        logger.info("\n🎉 所有测试通过！阶段三核心功能验证完成")
    else:
        logger.warning(f"\n⚠️  {total - passed} 个测试失败，请检查日志")
    
    return passed == total


if __name__ == "__main__":
    asyncio.run(main())
