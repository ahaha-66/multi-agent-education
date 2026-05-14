# 阶段三数据层使用说明

## 概述

阶段三已实现课程内容数据层，包括：
- 6 张新数据表（course, chapter, knowledge_point, knowledge_edge, exercise, learner_exercise_history）
- 完整的课程数据 JSON（3章完整数据）
- 数据导入脚本

## 数据表结构

### 1. Course（课程表）
- `code`: 课程代码（唯一），如 "math_g7"
- `name`: 课程名称
- `subject`: 学科，如 "math"
- `grade_level`: 年级
- `description`: 描述

### 2. Chapter（章节表）
- `course_id`: 所属课程
- `code`: 章节代码
- `name`: 章节名称
- `order_index`: 排序索引

### 3. KnowledgePoint（知识点表）
- `code`: 知识点代码（唯一）
- `chapter_id`: 所属章节
- `course_id`: 所属课程
- `difficulty`: 难度系数（0-1）
- `tags`: 标签列表

### 4. KnowledgeEdge（知识点依赖关系表）
- `source_kp_id`: 前置知识点 ID
- `target_kp_id`: 目标知识点 ID
- `relation_type`: 关系类型（默认 "prerequisite"）
- `strength`: 依赖强度（0-1）

### 5. Exercise（练习题表）
- `knowledge_point_id`: 所属知识点
- `chapter_id`: 所属章节
- `course_id`: 所属课程
- `code`: 题目代码（唯一）
- `type`: 题目类型（single_choice, fill_blank, solution）
- `content`: 题目内容（JSON）
- `answer`: 答案（JSON）
- `analysis`: 解析（JSON）
- `hint_levels`: 阶梯提示（JSON 数组）

### 6. LearnerExerciseHistory（学习者练习历史表）
- `learner_id`: 学习者 ID
- `exercise_id`: 练习题 ID
- `is_correct`: 是否正确
- `attempt_count`: 尝试次数
- `first_attempt_at`: 首次尝试时间
- `last_attempt_at`: 最后尝试时间

## 使用步骤

### 1. 运行数据库迁移

确保 PostgreSQL 数据库已启动：

```bash
cd python

# 运行迁移
alembic upgrade head
```

这将创建以下表：
- course
- chapter
- knowledge_point
- knowledge_edge
- exercise
- learner_exercise_history

### 2. 导入课程数据

```bash
cd python

# 导入七年级数学数据
python -m db.seed --data-file data/seed_math_g7.json

# 如果需要强制更新已存在的数据
python -m db.seed --data-file data/seed_math_g7.json --force
```

导入统计：
- 1 个课程（七年级数学上册）
- 3 个章节（有理数、代数式、一元一次方程）
- 15 个知识点
- 100+ 道练习题

### 3. 验证数据

```bash
# 检查数据库中的数据
psql $DATABASE_URL -c "SELECT COUNT(*) FROM course;"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM chapter;"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM knowledge_point;"
psql $DATABASE_URL -c "SELECT COUNT(*) FROM exercise;"
```

## 当前课程内容

### 七年级数学上册（math_g7）

#### 第1章：有理数
- 正数和负数
- 有理数的分类
- 数轴
- 绝对值
- 有理数的大小比较

#### 第2章：代数式
- 用字母表示数
- 代数式的概念
- 单项式
- 多项式
- 整式的加减

#### 第3章：一元一次方程
- 一元一次方程的概念
- 等式的性质
- 解一元一次方程（移项）
- 一元一次方程的应用

## 下一步

数据层完成后，接下来需要：

1. **实现服务层**（里程碑2）
   - 创建 `KnowledgeGraphService`
   - 创建 `ExerciseRecommender`
   - 修改 `CurriculumAgent` 使用新服务

2. **实现 API 层**（里程碑3）
   - 创建课程相关 API
   - 创建练习题相关 API
   - 创建管理员导入 API

详见：[阶段三实施方案](../docs/stage-c-plan.md)
