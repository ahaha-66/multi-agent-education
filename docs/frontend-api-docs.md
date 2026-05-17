# 多Agent智能教育系统 - 前端开发文档

## 文档版本
- **版本**: v1.0
- **日期**: 2026-05-17
- **后端分支**: my-dev-branch

---

## 一、系统概述

### 1.1 系统定位
多Agent智能教育系统是一个基于**事件驱动架构**的个性化数学学习平台，采用 5-Agent Mesh 架构实现智能化教学。

### 1.2 核心架构
```
┌─────────────────────────────────────────────────────────┐
│                      前端 (Web/App)                     │
│  - React/Vue SPA                                       │
│  - WebSocket 实时通信                                  │
│  - 状态管理 (Redux/Vuex/Pinia)                        │
└───────────────────────┬─────────────────────────────────┘
                        │ REST API + WebSocket
┌───────────────────────┴─────────────────────────────────┐
│                   FastAPI 网关层                        │
│  - 路由分发                                            │
│  - 认证鉴权 (预留)                                      │
│  - 限流 (预留)                                          │
└───────────────────────┬─────────────────────────────────┘
                        │
┌───────────────────────┴─────────────────────────────────┐
│                    Agent Orchestrator                   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│  │Assess-  │ │Curri-   │ │ Tutor   │ │ Hint    │ │ Engage- │
│  │ment     │ │culum    │ │ Agent   │ │ Agent   │ │ment     │
│  │Agent    │ │Agent    │ │         │ │         │ │Agent    │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
│       │            │           │            │            │
│       └────────────┴───────────┴────────────┴────────────┘
│                              │
│                    ┌─────────┴─────────┐
│                    │    Event Bus     │
│                    │  (事件驱动通信)   │
│                    └─────────┬─────────┘
└──────────────────────────────┼──────────────────────────┘
                               │
┌──────────────────────────────┼──────────────────────────┐
│                       数据库层 (SQLite)                   │
│  - PostgreSQL 迁移完成 (开发用 SQLite)                   │
│  - Alembic 迁移管理                                      │
└──────────────────────────────────────────────────────────┘
```

### 1.3 Agent 功能说明

| Agent | 功能 | 触发时机 |
|-------|------|----------|
| **Assessment Agent** | 评估学生知识点掌握情况（贝叶斯知识追踪 BKT） | 学生提交答案后 |
| **Curriculum Agent** | 规划学习路径（SM-2 间隔重复算法） | 学生开始学习/完成知识点 |
| **Tutor Agent** | 苏格拉底式教学，引导思考 | 学生提问时 |
| **Hint Agent** | 提供分级提示（3级递进） | 学生请求提示时 |
| **Engagement Agent** | 监测学习互动，评估参与度 | 持续监测 |

---

## 二、用户核心场景与功能模块

### 场景 1：学生首次学习

```
用户流程：
1. 学生选择课程（如：七年级数学上册）
2. 系统展示课程目录（章节 → 知识点）
3. 学生点击"开始学习"
4. 系统推送第一道练习题
5. 学生作答 → 系统判定对错
6. 系统记录答案，更新知识点掌握度
7. 根据 SM-2 算法决定下次复习时间
```

**涉及功能模块：**
- 课程列表与详情
- 课程目录（章节-知识点树）
- 知识图谱可视化
- 练习题推送
- 答案提交与判定
- 学习进度追踪

**关键 API：**
```
GET  /api/v1/courses                                    # 课程列表
GET  /api/v1/courses/{course_id}                        # 课程详情
GET  /api/v1/courses/{course_id}/catalog                # 课程目录
GET  /api/v1/courses/{course_id}/knowledge-graph        # 知识图谱
GET  /api/v1/courses/{course_id}/exercises/next        # 获取下一题
POST /api/v1/exercises/verify                          # 提交答案
GET  /api/v1/learners/{learner_id}/progress            # 学习进度
```

---

### 场景 2：学生复习（间隔重复）

```
用户流程：
1. 系统根据 SM-2 算法，在合适时间推送复习提醒
2. 学生点击复习任务
3. 系统展示待复习的知识点/练习题
4. 学生完成复习 → 更新掌握度
5. 系统安排下次复习时间
```

**涉及功能模块：**
- 复习任务推送（通过 WebSocket 或推送通知）
- 练习题复习
- 掌握度更新

**关键 API：**
```
WS   /ws/{learner_id}                                  # WebSocket 实时接收复习任务
POST /api/v1/exercises/verify                          # 提交答案（触发 SM-2 计算）
```

---

### 场景 3：错题本与薄弱点强化

```
用户流程：
1. 学生进入"错题本"页面
2. 系统展示所有错题（按课程/章节/知识点筛选）
3. 学生点击错题 → 查看详情（题目、正确答案、解析）
4. 学生重新作答 → 系统判定是否已掌握
5. 若已掌握 → 从错题本移除（标记 resolved）
```

**涉及功能模块：**
- 错题列表（支持多维度筛选）
- 错题详情
- 错题重做与掌握确认
- 错题统计

**关键 API：**
```
GET  /api/v1/learners/{learner_id}/mistakes                       # 错题列表
GET  /api/v1/learners/{learner_id}/mistakes/{mistake_id}          # 错题详情
POST /api/v1/learners/{learner_id}/mistakes/{mistake_id}/resolve  # 标记已掌握
GET  /api/v1/learners/{learner_id}/mistakes/statistics           # 错题统计
```

---

### 场景 4：学习目标与任务管理

```
用户流程：
1. 学生创建学习目标（如："本周掌握第一章"）
2. 系统自动拆解为具体任务
3. 学生完成任务 → 目标进度更新
4. 目标完成 → 获得成就/激励
```

**涉及功能模块：**
- 学习目标创建与追踪
- 任务创建与完成
- 进度可视化

**关键 API：**
```
GET  /api/v1/learners/{learner_id}/goals              # 目标列表
POST /api/v1/learners/{learner_id}/goals              # 创建目标
PUT  /api/v1/learners/{learner_id}/goals/{goal_id}   # 更新目标
POST /api/v1/learners/{learner_id}/goals/{goal_id}/complete  # 完成目标
GET  /api/v1/learners/{learner_id}/tasks              # 任务列表
POST /api/v1/learners/{learner_id}/tasks              # 创建任务
POST /api/v1/learners/{learner_id}/tasks/{task_id}/complete  # 完成任务
```

---

### 场景 5：学习进度总览

```
用户流程：
1. 学生进入"学习中心"
2. 系统展示：
   - 整体学习进度（百分比）
   - 各课程进度
   - 章节进度
   - 知识点掌握分布图
3. 学生可点击查看详情
```

**涉及功能模块：**
- 整体进度仪表盘
- 课程进度详情
- 章节进度
- 知识点掌握热力图

**关键 API：**
```
GET  /api/v1/learners/{learner_id}/progress                        # 整体进度
GET  /api/v1/learners/{learner_id}/progress/courses/{course_id}   # 课程进度
```

---

## 三、API 完整文档

### 3.1 基础信息

| 项目 | 说明 |
|------|------|
| **Base URL** | `http://localhost:8000` |
| **协议** | REST + WebSocket |
| **数据格式** | JSON |
| **认证** | 预留（当前无需认证） |

### 3.2 REST API

#### 3.2.1 课程相关

**GET /api/v1/courses**
```json
// Response
{
  "data": [
    {
      "id": "course_001",
      "code": "math_g7_s1",
      "name": "七年级数学上册",
      "subject": "数学",
      "grade_level": 7,
      "description": "初中数学基础课程..."
    }
  ]
}
```

**GET /api/v1/courses/{course_id}/catalog**
```json
// Response
{
  "course_id": "course_001",
  "chapters": [
    {
      "id": "chapter_001",
      "name": "第一章 有理数",
      "order_index": 1,
      "knowledge_points": [
        {
          "id": "kp_001",
          "code": "M7S1-01",
          "name": "正数和负数",
          "order_index": 1
        }
      ]
    }
  ]
}
```

**GET /api/v1/courses/{course_id}/knowledge-graph**
```json
// Response
{
  "nodes": [
    {
      "id": "kp_001",
      "code": "M7S1-01",
      "name": "正数和负数",
      "difficulty": 1
    }
  ],
  "edges": [
    {
      "source": "kp_000",
      "target": "kp_001",
      "type": "prerequisite"
    }
  ]
}
```

#### 3.2.2 练习题相关

**GET /api/v1/courses/{course_id}/exercises/next**
```
Query Parameters:
- learner_id (required): 学习者ID
- knowledge_point_id (optional): 指定知识点
- count (optional, default=1): 推荐数量

// Response
{
  "exercises": [
    {
      "id": "ex_001",
      "code": "E001",
      "type": "single_choice",
      "difficulty": 1,
      "content": {
        "stem": "下列数中，正数是？",
        "options": ["-1", "0", "1", "-0.5"]
      },
      "tags": ["有理数", "正负数"],
      "hint_levels": [
        {"level": 1, "hint": "回忆正数和负数的定义"},
        {"level": 2, "hint": "大于0的数是正数"},
        {"level": 3, "hint": "答案是C"}
      ]
    }
  ],
  "recommendation_reason": "基于课程路径和学习进度推荐"
}
```

**POST /api/v1/exercises/verify**
```json
// Request
{
  "exercise_id": "ex_001",
  "answer": "C"
}

// Response
{
  "exercise_id": "ex_001",
  "is_correct": true,
  "correct_answer": "C",
  "analysis": "大于0的数是正数，所以1是正确的答案"
}
```

#### 3.2.3 学习进度

**GET /api/v1/learners/{learner_id}/progress**
```json
// Response
{
  "learner_id": "learner_001",
  "total_courses": 1,
  "completed_courses": 0,
  "courses": [
    {
      "course_id": "course_001",
      "course_name": "七年级数学上册",
      "overall_progress": 0.35,
      "total_chapters": 3,
      "completed_chapters": 1,
      "total_knowledge_points": 15,
      "mastered_knowledge_points": 5,
      "chapters": [
        {
          "chapter_id": "chapter_001",
          "chapter_name": "第一章 有理数",
          "progress": 0.8,
          "knowledge_points": [
            {
              "knowledge_point_id": "kp_001",
              "code": "M7S1-01",
              "name": "正数和负数",
              "mastery": 0.85,
              "is_mastered": true,
              "attempts": 3,
              "correct_count": 3,
              "wrong_streak": 0,
              "last_attempt_at": "2026-05-17T10:30:00Z"
            }
          ]
        }
      ]
    }
  ]
}
```

**GET /api/v1/learners/{learner_id}/progress/courses/{course_id}**
```json
// Response (同 overall_progress 中的单个 course 结构)
{
  "course_id": "course_001",
  "course_name": "七年级数学上册",
  "overall_progress": 0.35,
  ...
}
```

#### 3.2.4 错题本

**GET /api/v1/learners/{learner_id}/mistakes**
```
Query Parameters:
- course_id (optional): 课程筛选
- chapter_id (optional): 章节筛选
- knowledge_point_id (optional): 知识点筛选
- is_resolved (optional): 是否已解决
- page (optional, default=1): 页码
- page_size (optional, default=20): 每页数量

// Response
{
  "learner_id": "learner_001",
  "mistakes": [
    {
      "id": "mistake_001",
      "exercise_id": "ex_005",
      "exercise_code": "E005",
      "exercise_type": "single_choice",
      "knowledge_point_id": "kp_003",
      "knowledge_point_name": "绝对值",
      "first_wrong_at": "2026-05-15T14:20:00Z",
      "last_wrong_at": "2026-05-16T09:15:00Z",
      "wrong_count": 2,
      "is_resolved": false
    }
  ],
  "total": 10,
  "page": 1,
  "page_size": 20,
  "total_pages": 1
}
```

**GET /api/v1/learners/{learner_id}/mistakes/{mistake_id}**
```json
// Response
{
  "id": "mistake_001",
  "exercise_id": "ex_005",
  "exercise_code": "E005",
  "exercise_type": "single_choice",
  "knowledge_point_id": "kp_003",
  "knowledge_point_name": "绝对值",
  "first_wrong_at": "2026-05-15T14:20:00Z",
  "last_wrong_at": "2026-05-16T09:15:00Z",
  "wrong_count": 2,
  "is_resolved": false,
  "content": {
    "stem": "|-5| = ?",
    "options": ["5", "-5", "0", "25"]
  },
  "correct_answer": {"answer": "A"},
  "analysis": "绝对值的定义：数轴上表示数a的点与原点的距离叫做a的绝对值",
  "last_attempt_answer": "B"
}
```

**POST /api/v1/learners/{learner_id}/mistakes/{mistake_id}/resolve**
```json
// Response (返回更新后的错题详情)
{
  "id": "mistake_001",
  ...
  "is_resolved": true
}
```

**GET /api/v1/learners/{learner_id}/mistakes/statistics**
```json
// Response
{
  "learner_id": "learner_001",
  "total_mistakes": 15,
  "resolved_mistakes": 8,
  "unresolved_mistakes": 7,
  "by_knowledge_point": [
    {
      "knowledge_point_id": "kp_003",
      "knowledge_point_name": "绝对值",
      "mistake_count": 5
    }
  ]
}
```

#### 3.2.5 学习目标与任务

**GET /api/v1/learners/{learner_id}/goals**
```
Query Parameters:
- status (optional): pending | active | completed | cancelled
- course_id (optional): 课程筛选

// Response
{
  "data": [
    {
      "id": "goal_001",
      "title": "本周掌握第一章",
      "description": "完成有理数章节的所有练习",
      "course_id": "course_001",
      "status": "active",
      "progress": 0.6,
      "target_date": "2026-05-24T00:00:00Z",
      "created_at": "2026-05-17T08:00:00Z",
      "updated_at": "2026-05-17T10:00:00Z",
      "completed_at": null
    }
  ]
}
```

**POST /api/v1/learners/{learner_id}/goals**
```json
// Request
{
  "title": "本周掌握第一章",
  "description": "完成有理数章节的所有练习",
  "course_id": "course_001",
  "target_date": "2026-05-24T00:00:00Z"
}

// Response
{
  "id": "goal_001",
  "title": "本周掌握第一章",
  ...
}
```

**GET /api/v1/learners/{learner_id}/tasks**
```
Query Parameters:
- goal_id (optional): 目标筛选
- status (optional): pending | in_progress | completed | cancelled

// Response
{
  "data": [
    {
      "id": "task_001",
      "title": "完成知识点：正数和负数",
      "description": null,
      "goal_id": "goal_001",
      "knowledge_point_id": "kp_001",
      "exercise_id": null,
      "type": "learn",
      "status": "completed",
      "priority": 1,
      "due_date": null,
      "order_index": 1,
      "created_at": "2026-05-17T08:00:00Z",
      "updated_at": "2026-05-17T09:30:00Z"
    }
  ]
}
```

### 3.3 WebSocket API

**连接地址**: `ws://localhost:8000/ws/{learner_id}`

**消息格式**:
```json
// 客户端发送
{
  "type": "action",
  "action": "submit_answer",
  "correlation_id": "uuid-xxx",
  "data": {
    "exercise_id": "ex_001",
    "answer": "C"
  }
}

// 服务端推送
{
  "type": "event",
  "event_type": "agent_response",
  "correlation_id": "uuid-xxx",
  "timestamp": "2026-05-17T10:30:00Z",
  "data": {
    "events": [
      {
        "type": "difficulty_adjusted",
        "agent": "assessment",
        "data": {
          "knowledge_id": "kp_001",
          "new_mastery": 0.85
        }
      }
    ]
  }
}
```

**支持的操作类型**:
- `submit_answer` - 提交答案
- `ask_question` - 提问
- `request_hint` - 请求提示
- `send_message` - 发送消息

---

## 四、数据模型

### 4.1 课程相关

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | String | 课程ID |
| `code` | String | 课程代码 |
| `name` | String | 课程名称 |
| `subject` | String | 学科 |
| `grade_level` | Integer | 年级 |
| `description` | String | 描述 |

### 4.2 练习题

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | String | 题目ID |
| `code` | String | 题目编号 |
| `type` | String | 类型：single_choice/multiple_choice/true_false/fill_blank |
| `difficulty` | Integer | 难度 1-5 |
| `content` | JSON | 题目内容 |
| `answer` | JSON | 正确答案 |
| `analysis` | JSON | 解析 |
| `tags` | List[String] | 标签 |

### 4.3 学习进度

| 字段 | 类型 | 说明 |
|------|------|------|
| `mastery` | Float | 掌握度 0-1 |
| `is_mastered` | Boolean | 是否已掌握（≥0.6） |
| `attempts` | Integer | 尝试次数 |
| `correct_count` | Integer | 正确次数 |
| `wrong_streak` | Integer | 连续错误次数 |
| `last_attempt_at` | DateTime | 最近一次尝试时间 |

### 4.4 错题记录

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | String | 记录ID |
| `exercise_id` | String | 练习题ID |
| `first_wrong_at` | DateTime | 首次错误时间 |
| `last_wrong_at` | DateTime | 最近错误时间 |
| `wrong_count` | Integer | 错误次数 |
| `is_resolved` | Boolean | 是否已解决 |
| `resolved_at` | DateTime | 解决时间 |

---

## 五、前端开发注意事项

### 5.1 状态管理建议

```
Store Structure:
├── user
│   ├── id
│   ├── currentCourse
│   └── settings
├── progress
│   ├── overall
│   ├── courses
│   └── knowledgePoints
├── mistakes
│   ├── list
│   ├── filters
│   └── statistics
├── goals
│   ├── list
│   └── activeGoal
├── tasks
│   ├── list
│   └── pendingCount
└── ui
    ├── loading
    └── notifications
```

### 5.2 实时更新策略

1. **WebSocket 连接管理**
   - 页面加载时建立连接
   - 断线自动重连（指数退避）
   - 心跳保活

2. **数据同步**
   - 提交答案后，等待 WebSocket 推送确认
   - 进度更新通过 WebSocket 实时刷新
   - 错题本支持实时更新

### 5.3 性能优化建议

1. **课程目录懒加载**
   - 初始只加载课程列表
   - 点击课程后再加载章节和知识点

2. **知识图谱优化**
   - 使用 Canvas/SVG 绘制
   - 大规模图谱考虑虚拟化

3. **错题本分页**
   - 默认 20 条/页
   - 支持无限滚动加载

---

## 六、错误处理

### 6.1 错误码

| 错误码 | 说明 | 处理建议 |
|--------|------|----------|
| 400 | 请求参数错误 | 检查输入 |
| 404 | 资源不存在 | 刷新页面或返回 |
| 500 | 服务器错误 | 显示友好提示 |

### 6.2 网络错误

- 超时：显示加载超时提示，提供重试按钮
- 断网：缓存用户操作，恢复后重试

---

## 七、后续迭代计划

### Phase 2 (进行中)
- LLM 接入（Tutor Agent 智能对话）
- WebSocket 生产化（心跳、鉴权）

### Phase 3
- 用户认证与权限
- 实时多人协作
- 数据分析与报表

---

## 八、联系方式

| 角色 | 负责人 |
|------|--------|
| 后端负责人 | 根据实际项目调整 |
| 技术支持 | GitHub Issues |

---

*文档更新于 2026-05-17*
