# 工程推进规划（基于现有实现逐步完善）

本规划以现有 Python 实现为基线（FastAPI + EventBus + 5 Agents），对照 [技术方案](file:///workspace/docs/tech-solution-math-llm.md) 的目标与验收，将工作拆分为可迭代交付的阶段任务。每一阶段都包含：交付内容、关键改造点、验证方式与对代码的落点建议。

## 0. 当前实现基线与差距

现有能力（已具备）：

- 事件驱动 Mesh：进程内 EventBus 发布/订阅（[event_bus.py](file:///workspace/python/core/event_bus.py)）
- Agent 原型：Assessment/BKT、Curriculum/SM-2、Tutor/Hint/Engagement（[agents](file:///workspace/python/agents)）
- API 原型：submit/question/message、progress、knowledge-graph、WS（[routes.py](file:///workspace/python/api/routes.py)、[websocket.py](file:///workspace/python/api/websocket.py)）

主要差距（需补齐）：

- 缺少“数学模块”的课程/章节/知识点/练习题实体与接口（当前只围绕 knowledge_id）
- Learner/复习/错题/对话/事件链路均未持久化（当前全内存，重启丢失）
- correlation_id 未贯穿，事件历史无界，无法满足事件追溯验收
- LLM 未接入（Tutor/Hint 仅模板），无法满足“必须加 LLM”
- WS 未实现心跳与标准 envelope，且仅支持单连接映射（learner_id -> ws）
- 生产化缺口：鉴权、限流、CORS 白名单、结构化日志与指标

## 1. 阶段 A：工程底座与契约先行（不改业务语义）

交付内容：

- 明确工程目录与模块边界：db / repo / services / llm / schemas
- 统一对外协议：REST 响应 envelope、WS 事件 envelope、错误码策略
- correlation_id 贯穿方案落地到接口与事件模型（仅生成/透传，先不落库）

关键任务：

- API 层新增 Request ID/correlation_id 生成与透传
  - REST：每次请求生成 correlation_id（或透传客户端提供）
  - WS：每条 action 消息生成 correlation_id（或透传）
- Event/Agent emit：所有下游事件继承 correlation_id
  - 需要改造 [BaseAgent.emit](file:///workspace/python/agents/base_agent.py) 与 [AgentOrchestrator](file:///workspace/python/api/orchestrator.py)
- WS 事件 envelope 标准化（event_id/type/correlation_id/timestamp/data）
  - 改造 [websocket.py](file:///workspace/python/api/websocket.py)
- 事件历史治理（MVP）：EventBus history 上限 + 按 learner 分桶
  - 改造 [event_bus.py](file:///workspace/python/core/event_bus.py)

验证方式：

- 单次 submit 产生的多个事件均带同一 correlation_id
- EventBus history 不随运行时间无界增长
- WS 推送字段满足 envelope 规范

## 2. 阶段 B：数据库与持久化最小闭环（先满足需求 3 的核心验收）

交付内容：

- PostgreSQL 持久化：learner_profile / knowledge_state / review_item / attempt / event_log
- 服务重启恢复：progress 与 review due 查询正确
- 事件追溯：按 learner_id 时间窗查询；按 correlation_id 查完整链路

关键任务：

- 新增 db 模块与连接管理（async SQLAlchemy engine/session）
- ORM 模型与 repo（最小集合）
  - attempt：记录作答（后续承接 exercise_id）
  - knowledge_state：保存 mastery、attempts、wrong_streak、version
  - review_item：保存 SM-2 状态（interval/ease/repetitions/due_at、version）
  - event_log：保存事件（payload JSONB、status）
  - learner_profile：最小字段（learner_id/created_at/last_active_at）
- Orchestrator 的“写入链路”重构（以 DB 为准，不再依赖内存 dict）
  - submit：先写 attempt + event_log(student.submission) → 发布事件 → Agents 更新后写回 state/review/event_log
  - progress：从 DB 聚合（不依赖内存 learner_models）
- SM-2 质量分映射：从“mastery 映射”切到“作答质量（correct/耗时）映射”
  - 当前 [CurriculumAgent._mastery_to_quality](file:///workspace/python/agents/curriculum_agent.py) 需要迁移到基于 attempt 的评分策略

验证方式：

- 重启前 mastery 更新为 0.8；重启后查询仍为 0.8（需求 3 验收）
- 完成 10 次练习后，可查询事件链路（含时间戳与变更记录）
- due 查询返回符合 SM-2 的待复习列表

## 3. 阶段 C：数学模块内容体系与题库（满足需求 1 的结构化浏览）

交付内容：

- 课程目录与知识图谱来自 DB（而非 sample graph）
- 练习题实体（exercise）与“下一题/按知识点取题”能力
- 课程内容可持续扩充：导入脚本与版本字段

关键任务：

- 引入课程内容实体：course/chapter/knowledge_point/knowledge_edge/exercise
- 设计数学模块数据导入方式
  - 初期：提供 seed 脚本，从 JSON/CSV 导入（避免手写 SQL）
  - 约束：exercise 必须包含标准答案与解析字段（analysis），方便 LLM 引用与解释
- API 扩展
  - /courses、/courses/{id}/catalog、/courses/{id}/knowledge-graph
  - /learners/{id}/exercises/next（按 curriculum 推荐或按知识点）
- CurriculumAgent 改造：knowledge_graph 来源切换为 DB/缓存（而不是 [build_sample_math_graph](file:///workspace/python/core/knowledge_graph.py#L141-L172)）

验证方式：

- 课程目录接口返回“章节-知识点-练习题”结构 JSON（需求 1 验收）
- 题量扩充后仍能稳定分页/抽题（避免一次性返回大 payload）

## 4. 阶段 D：学习目标/阶段任务、错题本与进度聚合（补齐需求 1）

交付内容：

- 学习目标与阶段任务：可创建、查询、状态变更
- 错题本：按 exercise 聚合，支持过滤与分页
- 进度：按课程/章节/知识点维度聚合展示

关键任务：

- 新增表：learner_goal、learner_task、mistake_book
- submit 链路补齐错题聚合写入
  - 首次错记录 first_wrong_at；累加 wrong_count；可选 resolved 规则
- progress 聚合逻辑：从 knowledge_state + 内容维表聚合

验证方式：

- 提交错误答案后错题本可查，wrong_count 递增
- progress 可按 course_id 输出章节维度概览（不要求前端，但要求数据结构稳定）

## 5. 阶段 E：LLM 接入与可控生成（满足“必须加 LLM”，并可上线）

交付内容：

- LLMClient 抽象（OpenAI/MiniMax）
- Prompt Registry 与输出 schema（Pydantic 校验）
- Tutor/Hint 以 LLM 生成结构化反馈为主，模板为兜底
- 成本与可靠性：超时降级、短期缓存、基础限流

关键任务：

- 新增 llm 模块
  - provider 适配、超时重试策略、错误分类
- Prompt Registry
  - 场景：tutor_explain、tutor_step_by_step、hint_level1/2/3、engagement_message（可选）
  - 版本化：prompt_name + version
- 输出 schema
  - Tutor：diagnosis/explanation/next_action/references 等结构
  - Hint：hint_level/hint_text/check_point 等结构
- TutorAgent 改造（当前仅模板，且 attempts 计数在内存 [tutor_agent.py](file:///workspace/python/agents/tutor_agent.py#L58-L107)）
  - 第 3 次错误触发“拆解思路”：从 DB 读 wrong_streak/attempt 历史决定调用 tutor_step_by_step prompt
- HintAgent 改造：hint_history 从内存迁移到 DB（至少按 learner+knowledge/exercise 记录）

验证方式：

- 断开 LLM/超时：仍能返回模板兜底且不报错
- 第 3 次错误触发分步讲解输出（需求 2 验收）
- 提示按阶梯升级且重启不丢失等级

## 6. 阶段 F：WebSocket 生产化与多实例预留（补齐实时体验与扩展性）

交付内容：

- WS 心跳、断线清理、重连协同
- 多连接支持（同 learner 多端连接）或明确单连接策略
- 多实例广播方案定稿（Redis PubSub/Stream）

关键任务：

- WS manager 支持连接列表（learner_id -> set[ws]）或 session 维度
- 心跳：服务端周期发送 heartbeat 事件
- 广播：引入 Redis 通道作为后续多实例基础（可先只实现接口与开关）

验证方式：

- 连接稳定性：断线后自动清理；重连后继续收事件
- envelope 字段一致、可去重（event_id）

## 7. 阶段 G：安全、可观测、测试与发布检查（上线门槛）

交付内容：

- 鉴权（API Key MVP）、限流、CORS 白名单配置化
- 结构化日志（带 learner_id/correlation_id），核心指标与告警钩子
- 集成测试覆盖验收场景，形成回归基线

关键任务：

- 中间件：鉴权、限流、请求日志与 correlation_id 注入
- 日志：输出关键字段（避免记录敏感信息与原始答案）
- 测试：
  - submit → 事件链路 → 状态落库 → 重启恢复
  - due 列表正确
  - 第 3 次错误触发分步讲解
- 发布检查清单：环境变量、DB 迁移、seed 导入、备份策略

验证方式：

- 未授权请求被拒
- 高并发 submit 不导致状态错乱（至少 learner 级别串行/乐观锁可用）
- 一键启动（docker-compose）可复现实验数据与验收脚本

