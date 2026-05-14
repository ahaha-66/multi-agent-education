# 多 Agent 个性化学习系统（Python）技术方案（数学模块 + LLM）

## 1. 背景与目标

本项目基于 FastAPI + asyncio 的事件驱动 Mesh 架构，多个 Agent 通过事件总线协作完成“评估-教学-路径-提示-互动”的学习闭环。当前阶段先聚焦落地一个可上线试点的数学模块，并引入 LLM 提升教学质量，避免仅依赖规则硬编码。

目标分层：

- G1：支持学生从课程选择 → 知识学习 → 练习 → 复习（SM-2）→ 进度/错题本的完整闭环
- G2：具备个性化教学能力（错因诊断、分层讲解、阶梯提示、学习状态识别、下一主题推荐、多轮对话上下文）
- G3：数据持久化与可恢复（服务重启不丢失；事件可追溯；支持导出/备份）
- G4：具备生产化能力（鉴权、限流、CORS 白名单、可观测、可扩展到多实例 WebSocket）

## 2. 范围与假设

### 2.1 MVP 范围（当前锁定）

- 学科/模块：仅数学（Math）
- 题量级别：相对充足的题库规模（建议初始目标：10+ 章节、50+ 知识点、500+ 练习题；后续可持续扩充）
- 模型能力：LLM 必须接入，作为 Tutor/Hint 的主要生成手段；规则引擎作为兜底与控制器而非主输出来源
- 前端形态：REST + WebSocket 事件流（无需在本方案定义具体 UI，但需稳定协议）

### 2.2 非目标（避免范围漂移）

- 暂不引入完整向量数据库与复杂检索基础设施（可先用 PostgreSQL/Redis 实现结构化检索与轻量缓存）
- 暂不做多学科与多版本教材的全量适配（预留 course_version 字段）
- 暂不做完整运营看板（先保证事件入库与导出能力）

## 3. 需求与验收映射

### 3.1 需求 1：完整学习流程支持

- F1.1：学生可浏览课程目录与知识图谱
- F1.2：学生可设定学习目标与阶段任务
- F1.3：学生可做练习题并获得即时反馈
- F1.4：系统自动生成复习计划（SM-2）
- F1.5：学生可查看学习进度与错题本

验收场景：

```
Given 学生已选择数学模块
When 学生浏览知识图谱
Then 返回章节-知识点-练习题结构 (JSON格式)

Given 学生提交练习答案
When 系统评估答案
Then 返回教学反馈 + 复习计划更新

Given 学生学习1周后
When 学生登录系统
Then 显示待复习题目 (基于SM-2计算)
```

### 3.2 需求 2：个性化教学能力

- F2.1：Tutor Agent 根据错题原因提供多层次讲解
- F2.2：Hint Agent 提供阶梯式提示（暗示→引导→答案）
- F2.3：Engagement Agent 识别学生学习状态并给予建议
- F2.4：Curriculum Agent 推荐下一个最优学习主题
- F2.5：支持多轮对话上下文保留

验收场景：

```
Given 学生2次错误回答相同知识点
When 第3次提交答案时
Then Tutor Agent 触发"拆解思路"反馈

Given 学生连续做题30分钟
When 系统检测
Then Engagement Agent 建议"休息5分钟"

Given 学生已掌握"二次函数基础"
When 查询下一学习主题
Then Curriculum Agent 推荐"二次函数应用"
```

### 3.3 需求 3：数据持久化与恢复

- F3.1：LearnerProfile 持久化到数据库
- F3.2：KnowledgeState 实时保存
- F3.3：ReviewItem 与复习计划持久化
- F3.4：学习事件历史可追溯
- F3.5：支持数据导出与备份

验收场景：

```
Given 学生掌握度已更新为0.8
When 后端服务重启
Then 重启后查询学生数据掌握度仍为0.8

Given 学生完成10次练习
When 查询学生事件历史
Then 返回完整事件链，含时间戳与变更记录
```

## 4. 总体架构设计

### 4.1 分层架构

- API 层（FastAPI）
  - 提供 REST 与 WebSocket 入口，负责鉴权、限流、请求校验、返回聚合结果
- 编排层（Orchestrator）
  - 为每次交互生成 correlation_id，构造学生交互事件，发布到事件总线
  - 聚合事件链路（按 correlation_id）形成 REST 响应，并通过 WS 推送事件流
- 事件层（EventBus）
  - 发布-订阅模型，解耦各 Agent
  - 支持事件入库、链路追踪、幂等与去重策略（MVP 可先在应用内实现，后续可迁移到 Redis Stream）
- Agent 层
  - Assessment / Curriculum / Tutor / Hint / Engagement 并发处理事件
- 数据层
  - PostgreSQL：主存储（课程/题库、学习状态、复习计划、事件日志、对话上下文）
  - Redis：缓存（课程目录、热点状态）与限流计数，后续用于 WS 多实例广播

### 4.2 关键设计原则

- 事件驱动为主：核心变更以事件形式记录与传播，便于追溯与扩展
- 状态持久化优先：Learner 状态、复习计划、错题聚合、对话上下文必须落库
- LLM 可控可降级：LLM 是主输出来源，但必须有超时/失败降级、内容安全与成本控制机制

## 5. 数据模型与存储设计（PostgreSQL）

### 5.1 课程与题库（数学模块）

- course：id、name、subject、course_version、created_at
- chapter：id、course_id、title、order_index
- knowledge_point：id、course_id、chapter_id、title、description、difficulty、metadata(JSONB)
- knowledge_edge：course_id、from_knowledge_id、to_knowledge_id（DAG 先修关系）
- exercise：id、knowledge_id、type、stem、options(JSONB)、answer(JSONB)、analysis、difficulty、tags(JSONB)、source

### 5.2 学习者与目标任务

- learner_profile：learner_id、name、grade、created_at、last_active_at
- learner_goal：id、learner_id、course_id、goal_type、target_value、start_at、end_at、status
- learner_task：id、learner_id、goal_id、title、knowledge_id、exercise_set_id、status、due_at、created_at

### 5.3 练习与学习状态

- attempt：id、learner_id、exercise_id、knowledge_id、answer(JSONB)、is_correct、time_spent_seconds、created_at、correlation_id
- knowledge_state：learner_id、knowledge_id、mastery、attempts、correct_attempts、wrong_streak、last_practice_at、updated_at、version
- mistake_book：learner_id、exercise_id、wrong_count、first_wrong_at、last_wrong_at、resolved_at、tags(JSONB)

### 5.4 复习计划（SM-2）

- review_item：id、learner_id、knowledge_id、interval_days、ease_factor、repetitions、due_at、last_review_at、updated_at、version

SM-2 的质量分（quality）映射（MVP，后续可扩展为用户显式评分）：

- 正确且耗时合理：4
- 正确但耗时偏长：3
- 错误：2
- 放弃/查看答案：1

### 5.5 事件溯源与对话上下文

- event_log：event_id、type、source、learner_id、timestamp、correlation_id、payload(JSONB)、status(ok/failed)
- conversation_session：id、learner_id、course_id、created_at、last_active_at
- conversation_message：id、session_id、role(user/assistant/system)、content、created_at、correlation_id、metadata(JSONB)

索引建议：

- event_log：(learner_id, timestamp DESC)、(correlation_id)、(type, timestamp DESC)
- review_item：(learner_id, due_at)、(learner_id, knowledge_id)
- knowledge_state：(learner_id, knowledge_id UNIQUE)
- attempt：(learner_id, created_at DESC)、(learner_id, knowledge_id, created_at DESC)

## 6. API 与协议设计

### 6.1 REST API（/api/v1）

课程与图谱：

- GET /courses
- GET /courses/{course_id}/catalog
- GET /courses/{course_id}/knowledge-graph

目标与任务：

- POST /learners/{learner_id}/goals
- GET /learners/{learner_id}/goals
- POST /learners/{learner_id}/tasks
- GET /learners/{learner_id}/tasks?status=active

练习与提交：

- GET /learners/{learner_id}/exercises/next?course_id=&knowledge_id=
- POST /submit

复习：

- GET /learners/{learner_id}/reviews/due?course_id=&limit=
- POST /learners/{learner_id}/reviews/{review_item_id}/complete

进度与错题：

- GET /progress/{learner_id}?course_id=
- GET /learners/{learner_id}/mistakes?course_id=&knowledge_id=&limit=

事件与导出：

- GET /learners/{learner_id}/events?from=&to=&correlation_id=
- GET /learners/{learner_id}/export?type=progress|events|mistakes

### 6.2 WebSocket（/ws/{learner_id}）

事件 envelope 统一格式：

```json
{
  "event_id": "uuid",
  "type": "tutor.teaching_response",
  "learner_id": "L1",
  "correlation_id": "C123",
  "timestamp": "2026-05-14T10:00:00Z",
  "data": {}
}
```

连接治理：

- 心跳：服务端周期发送 heartbeat 事件，客户端超时重连
- 去重：客户端按 event_id 做幂等展示

## 7. 事件模型与处理链路

### 7.1 correlation_id 策略

- 入口生成：每次 REST/WS action 生成 correlation_id（或透传客户端提供的 id）
- 继承规则：Agent 发布的后续事件必须继承上游 correlation_id
- 事件查询：以 correlation_id 聚合完整事件链用于响应与追溯

### 7.2 关键事件流（提交练习）

1. student.submission（写 attempt 与 event_log）
2. Assessment 更新 mastery、更新 knowledge_state，发布 assessment.mastery_updated
3. Curriculum 基于 mastery 与图谱更新 review_item、推荐 next_topic
4. Tutor/Hint 基于错因与对话上下文生成反馈与提示
5. Engagement 基于行为窗口生成建议（例如 30 分钟连续做题建议休息）

## 8. LLM 技术方案（必须项）

### 8.1 LLM 接入方式

能力形态：在 Tutor/Hint 中以 LLM 生成结构化输出为主，规则负责：

- 选择 prompt 模板与约束
- 控制输出结构与安全
- 控制成本（限流、缓存、降级）

建议模块：

- LLMClient 抽象：支持 OpenAI 与 MiniMax，统一接口（generate/chat）
- Prompt Registry：按场景与版本管理 prompt（tutor_explain_v1、hint_level2_v1 等），支持热更新（可先从文件/DB 读取）
- Response Schema：对 LLM 输出做结构化校验（Pydantic），失败则降级

### 8.2 生成内容的结构化要求（示例）

Tutor 输出（示例字段）：

- diagnosis：错因类型与证据
- explanation：分层讲解（概念→步骤→检查点）
- next_action：下一步建议（继续练习/先复习/换题）
- references：引用的知识点/题目/讲义片段 id（用于可解释性）

Hint 输出：

- hint_level：1/2/3
- hint_text：提示文本
- check_point：让学生自检的点

### 8.3 降级与安全

- 超时降级：LLM 请求超时则回退到模板化回复（保证可用性）
- 内容安全：对 prompt 输入与输出做敏感信息过滤与长度限制
- 成本控制：按 learner/IP 限流；对同题同上下文短期结果做缓存（Redis，短 TTL）

## 9. 个性化策略落地（与验收对齐）

### 9.1 第 3 次错误触发“拆解思路”

触发条件（MVP）：

- 同一 learner_id + knowledge_id 的 wrong_streak 达到 2
- 第 3 次提交触发 Tutor 输出包含 step_by_step 字段（或 explanation 结构化分步）

### 9.2 连续做题 30 分钟建议休息

统计方式（MVP）：

- 基于 attempt.created_at 的滑动窗口计算连续作答时长
- 达到阈值发布 engagement.alert 事件，建议休息 5 分钟

### 9.3 下一主题推荐

推荐规则（MVP）：

- mastery >= 0.8 判定掌握
- 在 DAG 中找“先修已掌握”的可学习节点优先
- 若存在 due 复习项优先推荐复习

## 10. 数据一致性与恢复

### 10.1 写入链路（原则）

- 任何会改变学习状态的交互必须：
  - 先写 attempt 与 event_log（链路可追溯）
  - 再更新 knowledge_state / review_item / mistake_book（事务内或带版本号）

### 10.2 并发控制

- learner 级别串行化策略（推荐）
  - 同一 learner 的 submit/review_complete 在服务端串行执行
- 或乐观锁策略
  - knowledge_state.version/review_item.version 递增，冲突则重试

### 10.3 重启恢复

- Orchestrator 不再依赖内存 learner_models，改为 DB 懒加载 + Redis 缓存（短 TTL）

## 11. 生产化要求（上线清单）

安全：

- 鉴权：MVP 采用 API Key，后续可扩展 JWT
- CORS：白名单配置化（区分 dev/staging/prod）
- 限流：submit/message/review_complete 按 learner 与 IP

可观测：

- 结构化日志字段：learner_id、correlation_id、event_type、latency_ms、llm_provider、llm_latency_ms
- 指标：submit 延迟、事件处理耗时、WS 在线数、LLM 失败率、复习 due 查询耗时

运维：

- 数据备份：Postgres 定期备份；导出接口需鉴权与审计
- 配置管理：密钥不入库，使用环境变量/密钥管理系统

## 12. 交付物与推进顺序（建议）

交付物清单：

- 数据库 DDL 与迁移脚本（含索引）
- API OpenAPI 规范（请求/响应/错误码）
- 事件协议与 data schema（含版本）
- LLM Prompt Registry 与输出 schema
- 验收用例脚本（覆盖 Given/When/Then）

推进顺序（先可用、再效果、再扩展）：

1. 数据落库闭环（attempt/knowledge_state/review_item/event_log）+ due API
2. correlation_id 全链路 + 事件查询 + WS 心跳
3. LLM 接入（Tutor/Hint）+ 降级/限流/缓存
4. 个性化验收规则落地（第 3 次错拆解思路、30 分钟休息、下一主题）
5. 安全与观测完善（鉴权/限流/CORS/指标）

## 13. 风险与预案

- LLM 延迟与成本：限流 + 缓存 + 超时降级；按场景分级调用（必要时只对关键节点调用）
- 数据一致性：learner 串行化或乐观锁；关键写入使用事务
- 多实例 WS：定义投递语义与去重策略（event_id）；必要时引入 Redis Stream
- 内容质量：Prompt 版本化与回滚；输出结构化校验，避免不可控文本直接渲染

