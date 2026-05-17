# 阶段 D：学习目标、错题本与进度聚合 - 实施计划

## 一、阶段目标与验收标准

### 1.1 核心目标

完善学习数据闭环，实现：
1. **学习目标与阶段任务**：支持学习目标设定、追踪和完成
2. **错题本**：自动聚合错题，支持错题复习、标记掌握
3. **进度聚合**：按课程/章节/知识点多维度展示学习进度

### 1.2 验收场景

```
场景 1：错题记录
Given 学生提交错误答案
When 系统处理完成
Then 错题本新增记录，wrong_count 递增，first_wrong_at 记录

场景 2：错题查询
Given 学生查看错题本
When 请求按课程/章节过滤
Then 返回对应维度的错题列表，支持分页

场景 3：进度查询
Given 请求学生进度
When 按课程查询
Then 返回课程整体进度、各章节进度、各知识点掌握情况
```

---

## 二、数据模型设计

### 2.1 新增表结构

#### LearnerGoal（学习目标表）
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | String | 目标ID（主键） |
| `learner_id` | String | 学习者ID |
| `course_id` | String | 课程ID（可选，null表示通用） |
| `title` | String | 目标标题 |
| `description` | String | 目标描述 |
| `target_date` | DateTime | 目标完成日期（可选） |
| `status` | String | 状态：pending/active/completed/cancelled |
| `progress` | Float | 完成度 0-1 |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |
| `completed_at` | DateTime | 完成时间（可选） |

#### LearnerTask（学习任务表）
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | String | 任务ID（主键） |
| `goal_id` | String | 关联目标ID（可选） |
| `learner_id` | String | 学习者ID |
| `knowledge_point_id` | String | 知识点ID（可选） |
| `exercise_id` | String | 练习题ID（可选） |
| `title` | String | 任务标题 |
| `description` | String | 任务描述 |
| `type` | String | 类型：learn/practice/review |
| `status` | String | 状态：pending/in_progress/completed/cancelled |
| `priority` | Integer | 优先级 1-5 |
| `due_date` | DateTime | 截止日期（可选） |
| `order_index` | Integer | 排序索引 |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

#### MistakeRecord（错题记录表）
| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | String | 记录ID（主键） |
| `learner_id` | String | 学习者ID |
| `exercise_id` | String | 练习题ID |
| `knowledge_point_id` | String | 知识点ID |
| `first_wrong_at` | DateTime | 首次错误时间 |
| `last_wrong_at` | DateTime | 最近错误时间 |
| `wrong_count` | Integer | 错误次数 |
| `last_attempt_answer` | JSON | 最近一次错误答案 |
| `is_resolved` | Boolean | 是否已解决 |
| `resolved_at` | DateTime | 解决时间（可选） |
| `created_at` | DateTime | 创建时间 |
| `updated_at` | DateTime | 更新时间 |

### 2.2 现有表修改

无需修改，复用现有的 `LearnerExerciseHistory` 表

---

## 三、核心服务模块

### 3.1 ProgressService（进度聚合服务）

```python
class ProgressService:
    """学习进度聚合服务"""
    
    async def get_course_progress(
        self,
        learner_id: str,
        course_id: str
    ) -> CourseProgress:
        """获取课程整体进度
        返回：
        - 课程信息
        - 总进度百分比
        - 各章节进度
        - 知识点掌握分布
        """
    
    async def get_chapter_progress(
        self,
        learner_id: str,
        chapter_id: str
    ) -> ChapterProgress:
        """获取章节进度"""
    
    async def get_knowledge_point_detail(
        self,
        learner_id: str,
        knowledge_point_id: str
    ) -> KnowledgePointDetail:
        """获取知识点详细情况"""
```

### 3.2 MistakeService（错题服务）

```python
class MistakeService:
    """错题本服务"""
    
    async def record_mistake(
        self,
        learner_id: str,
        exercise_id: str,
        answer: Any
    ) -> MistakeRecord:
        """记录错题"""
    
    async def mark_resolved(
        self,
        mistake_id: str,
        learner_id: str
    ) -> MistakeRecord:
        """标记错题已掌握"""
    
    async def list_mistakes(
        self,
        learner_id: str,
        course_id: str | None = None,
        chapter_id: str | None = None,
        knowledge_point_id: str | None = None,
        is_resolved: bool | None = None,
        page: int = 1,
        page_size: int = 20
    ) -> PaginatedMistakes:
        """查询错题列表（支持多维度过滤）"""
    
    async def get_mistake(
        self,
        mistake_id: str,
        learner_id: str
    ) -> MistakeRecordDetail:
        """获取单条错题详情"""
```

### 3.3 GoalTaskService（目标与任务服务）

```python
class GoalTaskService:
    """学习目标与任务服务"""
    
    async def create_goal(
        self,
        learner_id: str,
        title: str,
        description: str = "",
        course_id: str | None = None,
        target_date: datetime | None = None
    ) -> LearnerGoal:
        """创建学习目标"""
    
    async def list_goals(
        self,
        learner_id: str,
        status: str | None = None,
        course_id: str | None = None
    ) -> list[LearnerGoal]:
        """查询目标列表"""
    
    async def update_goal(
        self,
        goal_id: str,
        learner_id: str,
        **kwargs
    ) -> LearnerGoal:
        """更新目标"""
    
    async def complete_goal(
        self,
        goal_id: str,
        learner_id: str
    ) -> LearnerGoal:
        """完成目标"""
    
    async def create_task(
        self,
        learner_id: str,
        title: str,
        type: str,
        **kwargs
    ) -> LearnerTask:
        """创建任务"""
    
    async def list_tasks(
        self,
        learner_id: str,
        goal_id: str | None = None,
        status: str | None = None
    ) -> list[LearnerTask]:
        """查询任务列表"""
    
    async def complete_task(
        self,
        task_id: str,
        learner_id: str
    ) -> LearnerTask:
        """完成任务"""
```

---

## 四、API 接口设计

### 4.1 错题本 API

```python
# 路径：api/routes_progress.py

GET /api/v1/learners/{learner_id}/mistakes
    - 查询错题列表
    - 参数：course_id, chapter_id, knowledge_point_id, is_resolved, page, page_size
    - 返回：分页错题列表

GET /api/v1/learners/{learner_id}/mistakes/{mistake_id}
    - 获取错题详情

POST /api/v1/learners/{learner_id}/mistakes/{mistake_id}/resolve
    - 标记错题已解决

GET /api/v1/learners/{learner_id}/mistakes/statistics
    - 错题统计（按课程/知识点统计）
```

### 4.2 进度 API

```python
GET /api/v1/learners/{learner_id}/progress
    - 获取总体学习进度（所有课程）

GET /api/v1/learners/{learner_id}/progress/courses/{course_id}
    - 获取课程学习进度

GET /api/v1/learners/{learner_id}/progress/chapters/{chapter_id}
    - 获取章节学习进度

GET /api/v1/learners/{learner_id}/progress/knowledge-points/{kp_id}
    - 获取知识点详细进度
```

### 4.3 目标与任务 API

```python
GET /api/v1/learners/{learner_id}/goals
    - 获取目标列表

POST /api/v1/learners/{learner_id}/goals
    - 创建学习目标

PUT /api/v1/learners/{learner_id}/goals/{goal_id}
    - 更新目标

POST /api/v1/learners/{learner_id}/goals/{goal_id}/complete
    - 完成目标

GET /api/v1/learners/{learner_id}/tasks
    - 获取任务列表

POST /api/v1/learners/{learner_id}/tasks
    - 创建任务

PUT /api/v1/learners/{learner_id}/tasks/{task_id}
    - 更新任务

POST /api/v1/learners/{learner_id}/tasks/{task_id}/complete
    - 完成任务
```

---

## 五、任务分解与里程碑

### 任务列表

| ID | 任务 | 优先级 | 预估工时 | 依赖 |
|----|------|--------|----------|------|
| **T1** | 设计并创建阶段D表模型（LearnerGoal/LearnerTask/MistakeRecord） | P0 | 1h | 无 |
| **T2** | 编写Alembic迁移脚本 | P0 | 0.5h | T1 |
| **T3** | 实现ProgressService（进度聚合） | P0 | 2h | T1, T2 |
| **T4** | 实现MistakeService（错题服务） | P0 | 2h | T1, T2 |
| **T5** | 实现GoalTaskService（目标任务服务） | P1 | 2h | T1, T2 |
| **T6** | 修改submit链路：自动记录错题 | P0 | 1h | T4 |
| **T7** | 实现进度API | P0 | 1.5h | T3 |
| **T8** | 实现错题本API | P0 | 1.5h | T4 |
| **T9** | 实现目标任务API | P1 | 1.5h | T5 |
| **T10** | 编写Pydantic Schema | P0 | 0.5h | 无 |
| **T11** | 集成测试 | P1 | 2h | T6-T9 |
| **T12** | 文档更新 | P2 | 1h | 全 |

### 里程碑

```
Milestone 1：数据层完成
- T1-T2 完成
- 所有表模型和迁移脚本就绪

Milestone 2：服务层完成
- T3-T5 完成
- ProgressService/MistakeService/GoalTaskService 就绪

Milestone 3：API与集成完成
- T6-T9 完成
- submit链路自动记录错题，所有API可用

Milestone 4：收尾
- T11-T12 完成
- 集成测试通过，文档完整
```

---

## 六、集成点设计

### 6.1 submit_answer 链路集成

在 `Orchestrator.submit_answer()` 中，当 `is_correct=False` 时：
```python
async def submit_answer(...):
    # ...现有逻辑...
    if not is_correct and exercise_id:
        await self.mistake_service.record_mistake(
            learner_id,
            exercise_id,
            answer
        )
    # ...保存...
```

### 6.2 ProgressService 与知识图谱集成

通过 `KnowledgeGraphService` 获取课程的完整知识结构，然后结合 `KnowledgeState` 计算进度。

---

## 七、数据Pydantic Schema

### CourseProgress（课程进度）
```python
class CourseProgress(BaseModel):
    course_id: str
    course_name: str
    overall_progress: float  # 0-1 整体进度
    total_chapters: int
    completed_chapters: int
    total_knowledge_points: int
    mastered_knowledge_points: int  # mastery >= 0.6
    chapters: list[ChapterProgress]
```

### ChapterProgress（章节进度）
```python
class ChapterProgress(BaseModel):
    chapter_id: str
    chapter_name: str
    progress: float
    knowledge_points: list[KnowledgePointProgress]
```

### KnowledgePointProgress（知识点进度）
```python
class KnowledgePointProgress(BaseModel):
    knowledge_point_id: str
    code: str
    name: str
    mastery: float
    is_mastered: bool
    attempts: int
    correct_count: int
    wrong_streak: int
    last_attempt_at: datetime | None
```

### MistakeRecordDetail（错题详情）
```python
class MistakeRecordDetail(BaseModel):
    id: str
    exercise_id: str
    exercise_code: str
    exercise_type: str
    content: dict
    correct_answer: dict
    analysis: dict | None
    knowledge_point_id: str
    knowledge_point_name: str
    first_wrong_at: datetime
    last_wrong_at: datetime
    wrong_count: int
    last_attempt_answer: Any
    is_resolved: bool
```

---

## 八、文件清单

| 文件 | 用途 |
|------|------|
| `db/models.py` | 新增 LearnerGoal/LearnerTask/MistakeRecord 模型 |
| `migrations/versions/20260517_stage_d_*.py` | Alembic迁移脚本 |
| `services/progress_service.py` | ProgressService 实现 |
| `services/mistake_service.py` | MistakeService 实现 |
| `services/goal_task_service.py` | GoalTaskService 实现 |
| `db/persistence.py` | 新增阶段D表的CRUD方法 |
| `api/schemas/progress_schemas.py` | 进度/错题/目标的Pydantic Schema |
| `api/routes_progress.py` | 阶段D的API路由 |
| `api/main.py` | 注册新路由 |
| `api/orchestrator.py` | 集成阶段D服务 |
| `docs/stage-d-plan.md` | 本规划文档 |

---

## 九、风险与应对

| 风险 | 影响 | 概率 | 应对策略 |
|------|------|------|----------|
| 进度聚合查询性能 | 中 | 中 | 合理设计索引，未来可考虑缓存 |
| 目标/任务功能复杂度高 | 中 | 低 | 先做MVP，后续增强 |
| 与现有submit链路冲突 | 低 | 低 | 增量修改，保持兼容 |
