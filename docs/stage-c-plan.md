# 阶段三实施方案：数学模块内容体系与题库

## 一、阶段目标与验收标准

### 1.1 核心目标

将学习系统从"围绕 knowledge_id 的内存运行"升级为"基于真实课程内容结构的数据驱动"，实现：

1. **结构化课程内容**：课程 → 章节 → 知识点 → 练习题的完整层级
2. **持久化知识图谱**：从内存 sample graph 切换到数据库，支持动态扩充
3. **题库能力**：按知识点推荐下一题，支持题目版本管理

### 1.2 验收场景

```
场景 1：课程目录浏览
Given 学生已选择数学模块
When 学生浏览知识图谱
Then 返回章节-知识点-练习题结构 (JSON格式)

场景 2：练习题获取
Given 学生开始学习某个知识点
When 学生请求下一道练习题
Then 系统按 curriculum 推荐或按知识点取题返回

场景 3：内容扩充
Given 管理员导入新课程内容
When 内容验证通过
Then 新章节/知识点/题目可用且不丢失原有数据
```

## 二、需求详述

### 2.1 数据模型设计

#### 2.1.1 课程内容实体

```python
# 课程 (Course)
- id: str (UUID)
- code: str (如 "math_g7")
- name: str (如 "七年级数学")
- subject: str (如 "math")
- version: str (如 "2024v1")
- grade_level: int (如 7)
- description: str
- is_active: bool
- created_at, updated_at

# 章节 (Chapter)
- id: str
- course_id: str (FK)
- code: str (如 "ch1")
- name: str (如 "有理数")
- order_index: int
- description: str

# 知识点 (KnowledgePoint)
- id: str
- chapter_id: str (FK)
- code: str (如 "kp_1_1")
- name: str (如 "正数和负数")
- difficulty: float (0.0-1.0)
- description: str
- tags: list[str]
- version: str
- order_index: int

# 知识点依赖关系 (KnowledgeEdge)
- id: str
- source_kp_id: str (FK)
- target_kp_id: str (FK)
- relation_type: str (如 "prerequisite", "related")
- strength: float (0.0-1.0, 表示依赖强度)

# 练习题 (Exercise)
- id: str
- knowledge_point_id: str (FK)
- chapter_id: str (FK, 冗余便于查询)
- code: str (如 "ex_1_1_001")
- type: str (如 "single_choice", "fill_blank", "solution")
- difficulty: float (0.0-1.0)
- content: dict (JSON, 题目内容)
- answer: dict (JSON, 标准答案)
- analysis: dict (JSON, 解析)
- hint_levels: list[dict] (阶梯提示)
- tags: list[str]
- version: str
- is_active: bool
- created_at, updated_at
```

#### 2.1.2 原有表扩展

- `learner_profile` 增加 `current_course_id` 字段
- `knowledge_state` 增加 `course_id` 字段（可选，用于跨课程学习）
- 新增 `learner_exercise_history` 表（记录学生做过的题目，避免重复）

### 2.2 API 接口设计

#### 2.2.1 课程相关接口

```
GET /api/v1/courses
- 返回所有可用课程列表
- Response: { courses: [{id, code, name, subject, grade_level}] }

GET /api/v1/courses/{course_id}
- 返回课程详情
- Response: { id, code, name, description, chapters: [...] }

GET /api/v1/courses/{course_id}/catalog
- 返回课程目录（章节-知识点树形结构）
- Response: { course_id, chapters: [{ id, name, knowledge_points: [...] }] }

GET /api/v1/courses/{course_id}/knowledge-graph
- 返回知识图谱（用于前端可视化）
- Response: { nodes: [...], edges: [...] }
```

#### 2.2.2 练习题相关接口

```
GET /api/v1/courses/{course_id}/exercises/next
- Query: knowledge_point_id (可选)
- Query: count (默认1)
- 功能：按 curriculum 推荐或指定知识点获取下一题
- Response: { exercises: [...], recommendation_reason: str }

GET /api/v1/exercises/{exercise_id}
- 返回题目详情（含答案和解析）
- 注意：答案和解析在提交后返回，或通过特殊参数控制

POST /api/v1/exercises/verify
- 验证答案（可选，前端也可本地验证）
- Request: { exercise_id, answer }
- Response: { is_correct, correct_answer, analysis }
```

#### 2.2.3 管理员接口

```
POST /api/v1/admin/seed
- 触发数据导入（从 JSON/CSV）
- Request: { source: str, force: bool }
- Response: { imported: { chapters: N, knowledge_points: N, exercises: N } }

GET /api/v1/admin/seed/status
- 返回导入任务状态
```

### 2.3 内容导入机制

#### 2.3.1 JSON 格式规范

```json
{
  "course": {
    "code": "math_g7",
    "name": "七年级数学",
    "subject": "math",
    "grade_level": 7
  },
  "chapters": [
    {
      "code": "ch1",
      "name": "有理数",
      "order_index": 1,
      "knowledge_points": [
        {
          "code": "kp_1_1",
          "name": "正数和负数",
          "difficulty": 0.2,
          "prerequisites": [],
          "exercises": [
            {
              "type": "single_choice",
              "content": {
                "stem": "下列各数中是正数的是...",
                "options": ["A. -1", "B. 0", "C. 1", "D. -2"]
              },
              "answer": {"value": "C" },
              "analysis": { "text": "考察正负数的定义..." },
              "difficulty": 0.1
            }
          ]
        }
      ]
    }
  ]
}
```

#### 2.3.2 导入约束

- 唯一性约束：`code` 字段全局唯一
- 版本控制：相同 `code` 可重复导入，版本号递增
- 原子性：一次导入要么全成功，要么全回滚
- 验证规则：
  - 章节 `code` 不能重复
  - 知识点 `code` 不能重复
  - 题目 `code` 不能重复
  - 前置知识点必须存在

## 三、关键技术方案

### 3.1 知识图谱重构

#### 3.1.1 架构调整

```
当前架构：
build_sample_math_graph() → 内存 KnowledgeGraph 对象
                                     ↓
                              CurriculumAgent 使用

目标架构：
DB (knowledge_point + knowledge_edge)
         ↓
KnowledgeGraphService (从 DB 加载，构建内存 DAG)
         ↓
CurriculumAgent 使用 (通过服务接口)
```

#### 3.1.2 核心服务

```python
class KnowledgeGraphService:
    """知识图谱服务：从 DB 加载并提供图查询能力"""

    def __init__(self, db_session):
        self._session = db_session
        self._cache: dict[str, KnowledgeGraph] = {}

    def get_graph(self, course_id: str) -> KnowledgeGraph:
        """获取课程知识图谱（带缓存）"""

    def get_prerequisites(self, kp_id: str) -> list[KnowledgePoint]:
        """获取前置知识点"""

    def get_ready_kps(self, course_id: str, mastered_ids: set[str]) -> list[KnowledgePoint]:
        """获取当前可学的知识点"""

    def invalidate_cache(self, course_id: str):
        """失效缓存（内容更新后调用）"""
```

### 3.2 题库推荐算法

#### 3.2.1 推荐策略

```python
class ExerciseRecommender:
    """练习题推荐器"""

    def recommend_next(
        self,
        learner_id: str,
        course_id: str,
        knowledge_point_id: str | None = None
    ) -> list[Exercise]:
        """
        推荐下一道题

        策略优先级：
        1. 如果指定 knowledge_point_id，按知识点取题
        2. 如果有 curriculum 推荐，遵循课程路径
        3. 否则按以下规则：
           - 优先选择：未做过、难度适中、知识点未掌握
           - 避免重复：过滤 learner_exercise_history
        """

    def _filter_by_mastery(self, exercises: list[Exercise], learner_model: LearnerModel) -> list[Exercise]:
        """根据 mastery 过滤：优先选择薄弱知识点"""

    def _avoid_duplicates(self, exercises: list[Exercise], history: list[str]) -> list[Exercise]:
        """过滤已做过的题目"""
```

### 3.3 数据迁移策略

#### 3.3.1 迁移步骤

```
1. 创建新表（course, chapter, knowledge_point, knowledge_edge, exercise, learner_exercise_history）
2. 导入初始数据（seed script）
3. 修改代码使用新服务
4. 删除旧的 sample data 引用
5. 保留旧表迁移脚本（可选）
```

#### 3.3.2 兼容性考虑

- 阶段 C 完成后，`knowledge_state.knowledge_id` 仍然兼容
- API response 中 `knowledge_point_id` 和 `knowledge_id` 可以共存
- 建议：短期保留 `knowledge_id` 别名，长期废弃

## 四、任务拆解

### 4.1 任务列表

| 任务 | 描述 | 优先级 | 预估工时 | 依赖 |
|------|------|--------|----------|------|
| T1 | 设计并创建课程内容表（course, chapter, knowledge_point, knowledge_edge, exercise） | P0 | 2h | 无 |
| T2 | 实现 Alembic 迁移脚本 | P0 | 1h | T1 |
| T3 | 创建 Course/Chapter/KnowledgePoint ORM 模型 | P0 | 1h | T1 |
| T4 | 实现 JSON 导入器（seed script） | P0 | 4h | T3 |
| T5 | 创建初始课程数据 JSON | P1 | 8h | T4 |
| T6 | 实现 KnowledgeGraphService | P0 | 3h | T3, T5 |
| T7 | 修改 CurriculumAgent 使用新服务 | P0 | 2h | T6 |
| T8 | 实现 Exercise ORM 模型 | P0 | 1h | T1 |
| T9 | 实现 ExerciseRecommender | P0 | 4h | T6, T8 |
| T10 | 创建课程相关 API（courses, catalog, knowledge-graph） | P0 | 3h | T6, T7 |
| T11 | 创建练习题相关 API（next, verify） | P0 | 2h | T9 |
| T12 | 创建管理员导入 API | P1 | 2h | T4 |
| T13 | 创建 learner_exercise_history 表和服务 | P1 | 2h | T9 |
| T14 | 集成测试和修复 | P1 | 4h | T10, T11 |
| T15 | 文档更新（API 文档、数据字典） | P2 | 2h | 全 |

### 4.2 里程碑

```
Milestone 1 (第1-2天): 数据层完成
- T1, T2, T3, T4 完成
- 课程内容表和导入器就绪

Milestone 2 (第3-4天): 服务层完成
- T6, T7, T8, T9 完成
- 知识图谱服务和推荐器就绪

Milestone 3 (第5-6天): API 层完成
- T10, T11, T12, T13 完成
- 所有接口可用

Milestone 4 (第7天): 收尾
- T14, T15 完成
- 集成测试通过
- 文档完成
```

## 五、风险与应对

### 5.1 风险识别

| 风险 | 影响 | 概率 | 应对策略 |
|------|------|------|----------|
| 初始数据准备耗时 | 高 | 中 | 优先准备核心章节（3-5章），其余延后 |
| JSON 格式变更 | 中 | 低 | 使用 Pydantic 严格校验，版本化管理 |
| 性能问题（大量题目查询） | 中 | 中 | 增加缓存层，按 course_id 缓存图结构 |
| 与阶段 B 代码冲突 | 中 | 中 | 分支开发，充分测试后再合并 |

### 5.2 测试策略

#### 5.2.1 单元测试

- KnowledgeGraphService 的图查询逻辑
- ExerciseRecommender 的推荐算法
- JSON 导入器的解析和验证

#### 5.2.2 集成测试

- 导入完整课程数据后，API 返回正确结构
- 知识图谱查询性能（1000+ 知识点）
- 推荐算法在边界情况下的行为

#### 5.2.3 验收测试

```python
def test_course_catalog_api():
    response = client.get("/api/v1/courses/math_g7/catalog")
    assert response.status_code == 200
    data = response.json()
    assert "chapters" in data
    assert len(data["chapters"]) > 0

def test_exercise_recommendation():
    # 模拟 learner_1 刚学完 "kp_1_1"
    response = client.get(
        "/api/v1/courses/math_g7/exercises/next",
        params={"learner_id": "learner_1"}
    )
    assert response.status_code == 200
    exercises = response.json()["exercises"]
    assert len(exercises) > 0
    assert exercises[0]["knowledge_point_id"] != "kp_1_1"
```

## 六、后续阶段依赖

阶段 C 是后续阶段的基础：

- **阶段 D**：依赖课程结构实现进度聚合和错题本
- **阶段 E**：依赖 Exercise 实体获取题目内容给 LLM
- **阶段 F**：依赖 exercise_history 实现更精准的推荐

建议：阶段 C 完成后，核心数据结构应该稳定，避免大幅重构。

## 七、附录

### 7.1 初始数据范围建议

建议准备 **3 章完整数据** 作为 MVP：

1. **第1章 有理数**（基础）
   - 约 5-8 个知识点
   - 每个知识点 5-10 道题
   - 约 30-50 道题

2. **第2章 代数式**（进阶）
   - 约 5-8 个知识点
   - 每个知识点 5-10 道题
   - 约 30-50 道题

3. **第3章 一元一次方程**（核心）
   - 约 4-6 个知识点
   - 每个知识点 8-12 道题（含应用题）
   - 约 40-60 道题

**总计**：约 15-22 个知识点，100-160 道题

### 7.2 参考资料

- [工程规划文档](file:///workspace/docs/engineering-plan.md)
- [技术方案文档](file:///workspace/docs/tech-solution-math-llm.md)
- [当前知识图谱实现](file:///workspace/python/core/knowledge_graph.py)
- [当前 ORM 模型](file:///workspace/python/db/models.py)
