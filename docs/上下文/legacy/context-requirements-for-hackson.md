# Hackson 上下文系统需求文档

版本：v0.1  
日期：2026-05-25  
依据文档：`docs/需求文档v1.md`、`docs/需求文档final.md`、`docs/plan.md`

## 1. 产品定位

Hackson 是一个 Live Multi-Agent World + Physical AI Companion。用户可以创建两个不同性格的 AI Agent，在网页中观察它们的 idle 生活、与它们聊天、让它们协作完成任务，并在后续版本中连接桌宠或硬件设备。

上下文系统是 Hackson 的核心基础设施。它决定：

- Agent 是否能持续保持人格。
- 用户插入 idle 对话时是否自然。
- 两个 Agent 是否能形成长期关系。
- Work Mode 是否能 24x7 推进任务而不丢目标。
- 桌宠是否能展示真实状态而不是装饰动画。

## 2. 模式拆解

### 2.1 Idle Life Mode

产品描述：

两个 Agent 在用户没有主动聊天时进行自主互动，例如闲聊、哲学辩论、读书、发呆、计划、写日记、关系变化。

上下文目标：

- Agent 需要知道自己的身份和对方是谁。
- Agent 需要知道当前 idle 场景、时间、最近发生的事情。
- Agent 需要保留长期关系记忆。
- Agent 需要产生可被用户观看的对话。
- Agent 的 idle 不应无限消耗 token，需要频率、预算和触发条件。

上下文输入：

- Agent A persona。
- Agent B persona。
- 当前世界状态。
- 最近 N 轮 idle 对话。
- 最近重要事件。
- 两个 Agent 的关系摘要。
- 可选主题或系统给出的 idle seed。

上下文输出：

- Agent 发言。
- 结构化事件。
- 可能的关系变化候选。
- 可能的日记候选。
- 需要写入长期记忆的候选。

关键约束：

- Idle 对话不能每轮都写入人格。
- 大部分 idle 闲聊只进入日志和低优先级记忆。
- 只有高重要性事件进入长期关系或人格层。

### 2.2 Companion Mode 1：用户插入 Idle

产品描述：

用户正在观看两个 Agent 的 idle 对话，突然加入一句话。系统从 Idle Life Mode 转入 Companion Mode 1。Agent 必须自然地意识到用户加入，并围绕用户继续交流。

上下文目标：

- 用户要感觉自己是“进入了一个正在发生的世界”，而不是重开聊天。
- Agent 必须理解刚才它们在聊什么。
- Agent 必须把注意力切到用户身上。
- 两个 Agent 都应该知道用户说话改变了对话结构。

上下文输入：

- 用户消息。
- idle 场景快照。
- 最近 idle 对话窗口。
- idle 对话短摘要。
- 当前正在讨论的话题。
- Agent 与用户的关系摘要。
- Agent 之间的关系摘要。
- 用户偏好和长期记忆。

上下文输出：

- Agent 对用户的回应。
- 是否继续三方对话。
- 是否生成“用户插入事件”。
- 是否更新用户关系或 Agent 关系。

关键约束：

- 用户插入后，Agent 不能继续无视用户自说自话。
- 不能把全部 idle 历史塞给模型。
- 需要生成 transition context：一句清晰的场景转场说明。

### 2.3 Companion Mode 2：新开用户聊天

产品描述：

用户主动开启类似 ChatGPT 的聊天窗口，可以与一个或两个 Agent 对话。它不依赖当前 idle 场景，但可以使用长期用户记忆和 Agent 人格。

上下文目标：

- 启动快。
- 围绕用户问题。
- 可选择是否使用长期记忆。
- 与 idle 世界相关但不强绑定。

上下文输入：

- 用户消息。
- 当前会话最近 N 轮。
- 用户 profile。
- 用户与 Agent 的关系摘要。
- Agent persona。
- 可选长期记忆检索结果。

上下文输出：

- Agent 回答。
- 会话事件。
- 用户偏好或事实记忆候选。

关键约束：

- 不应默认带入大量 idle 对话。
- 如果用户问“你们刚刚在聊什么”，才检索 idle 相关上下文。
- 用户可以选择清空当前窗口，但长期 profile 不一定清空。

### 2.4 Work Mode

产品描述：

两个或多个 Agent 分工协作推进任务。比如 Planner 拆任务，Worker 调用 Codex CLI，Reviewer 检查结果。网页显示实时进度，后续桌宠显示任务状态。

上下文目标：

- Agent 不能忘记任务目标。
- 工具调用必须可追踪。
- 多 Agent 分工必须清晰。
- 长时间运行时需要自我压缩和阶段总结。
- 失败需要复盘，成功需要沉淀技能。

上下文输入：

- 项目目标。
- 当前任务状态。
- Agent 角色。
- 最近工具调用结果。
- 当前文件或工作区摘要。
- 决策记录。
- 未完成事项。
- 用户约束。

上下文输出：

- 下一步计划。
- 工具调用请求。
- 任务状态更新。
- 风险和阻塞。
- 复盘记忆。
- 可复用 skill 候选。

关键约束：

- Work Mode 的 task memory 不能污染 Companion Mode 的情感人格。
- 工具执行结果必须入库。
- 每个任务要有明确 state machine。
- 需要防止 Agent 24x7 循环时目标漂移。

## 3. 上下文对象模型

### 3.1 User Profile

保存用户级信息。

字段建议：

- user_id
- username
- display_name
- email
- language_preference
- memory_enabled
- idle_enabled
- privacy_settings
- created_at
- updated_at

### 3.2 Model Runtime Config

保存平台侧 demo 模型运行配置。V1 不做用户自选 endpoint，不在用户设置页暴露 api key、本地模型路径或 provider 选择。该配置属于后端内部运行时配置，用于统一异步推理层调用我们提供的模型服务。

字段建议：

- config_id
- provider
- endpoint
- model_name
- api_key_secret_ref
- max_context_tokens
- max_output_tokens
- timeout_ms
- concurrency_limit
- enabled

### 3.3 Agent Persona

保存 Agent 的人格。需要分层，不能只用一个 `soul.md`。

字段建议：

- agent_id
- owner_user_id
- name
- avatar_ref
- core_persona
- speaking_style
- values
- boundaries
- backstory
- user_editable_notes
- adaptive_persona_summary
- current_mood
- version

人格层级：

- Core Persona：用户编辑或模板选择，默认不能被 Agent 自动覆盖。
- Adaptive Persona：根据长期互动形成的缓慢变化，由系统审核写入。
- Episode State：短期状态，如今天心情、最近关注的话题。
- Speaking Policy：说话风格和禁区，确保产品一致性。

### 3.4 Conversation

保存会话容器。

字段建议：

- conversation_id
- user_id
- mode: idle | companion_1 | companion_2 | work
- participants
- title
- status
- started_at
- ended_at
- parent_idle_session_id

### 3.5 Message

保存原始消息，作为不可丢失事实源。

字段建议：

- message_id
- conversation_id
- sender_type: user | agent | system | tool
- sender_id
- content
- content_type
- token_count
- created_at
- metadata

### 3.6 Event

从消息中抽取的结构化事件。

字段建议：

- event_id
- source_message_ids
- event_type
- actor_ids
- target_ids
- summary
- importance_score
- emotional_valence
- confidence
- occurred_at
- visibility

事件类型示例：

- user_joined_idle
- agent_disagreement
- agent_agreement
- user_preference_revealed
- relationship_shift
- task_created
- task_completed
- tool_call_finished
- promise_made
- boundary_set

### 3.7 Memory Card

长期记忆卡片，是检索和人格成长的基本单元。

字段建议：

- memory_id
- owner_type: user | agent | shared_world | task
- owner_id
- memory_type: fact | preference | episode | relationship | reflection | skill | task
- title
- summary
- evidence_message_ids
- tags
- entities
- importance_score
- recency_score
- strength
- confidence
- decay_policy
- created_at
- updated_at
- expires_at

### 3.8 Relationship State

保存 Agent-Agent、User-Agent 的关系状态。

字段建议：

- relationship_id
- subject_id
- object_id
- relationship_type
- summary
- trust_score
- familiarity_score
- tension_score
- last_interaction_at
- evidence_memory_ids
- version

### 3.9 Diary Entry

用户可见的 Agent 日记，不等同于系统记忆。

字段建议：

- diary_id
- agent_id
- date
- content
- referenced_event_ids
- visibility
- user_visible
- created_at

关键原则：

- 日记可以文学化。
- 系统记忆必须结构化和可追溯。
- 日记不能作为事实源，事实源仍是 message/event/memory。

### 3.10 Task State

Work Mode 的任务状态。

字段建议：

- task_id
- user_id
- objective
- current_phase
- assigned_agents
- state
- plan_summary
- progress_summary
- open_questions
- blockers
- tool_trace_refs
- created_at
- updated_at

## 4. 上下文构建配方

### 4.1 Idle Context Recipe

推荐 prompt 组成：

1. System policy。
2. 当前 mode：idle。
3. Agent 自己的 persona。
4. 对方 Agent 的简短 persona。
5. 当前世界状态。
6. 两者关系摘要。
7. 最近 idle 消息。
8. 相关长期记忆。
9. 当前 idle 目标或话题 seed。
10. 输出格式约束。

不应包含：

- 全部历史。
- 用户私密记忆，除非当前 idle 明确围绕用户。
- Work Mode 的工具细节。

### 4.2 Companion 1 Context Recipe

推荐 prompt 组成：

1. System policy。
2. 当前 mode：user joined idle。
3. transition context：用户刚刚加入，必须回应用户。
4. 用户消息。
5. 最近 idle 片段。
6. idle 片段摘要。
7. Agent 自己 persona。
8. 用户与 Agent 关系摘要。
9. Agent-Agent 关系摘要。
10. 用户相关长期记忆。
11. 输出格式约束。

核心要求：

- 用户消息必须放在高优先级位置。
- 最近 idle 只作为背景。
- Agent 回复必须显式处理用户加入。

### 4.3 Companion 2 Context Recipe

推荐 prompt 组成：

1. System policy。
2. 当前 mode：fresh companion chat。
3. 用户消息。
4. 当前会话最近消息。
5. Agent persona。
6. 用户 profile。
7. 检索到的相关用户记忆。
8. 输出格式约束。

核心要求：

- 默认轻上下文。
- 用户问历史时再查历史。
- 不应自动把 idle 生活强行带入。

### 4.4 Work Mode Context Recipe

推荐 prompt 组成：

1. System policy。
2. 当前 mode：work。
3. 用户目标。
4. 当前任务状态。
5. Agent 角色和权限。
6. 最近任务进展。
7. 工具调用结果摘要。
8. 当前阻塞和开放问题。
9. 相关 skill memory。
10. 输出格式约束。

核心要求：

- 任务目标必须稳定放在前部。
- 工具结果要压缩，但关键错误不能丢。
- 每轮输出必须更新 task state。

## 5. 写入策略

### 5.1 同步写入

必须同步写入：

- 原始 message。
- tool call 请求和结果。
- conversation state。
- task state 的关键状态变更。

原因：这些是事实源，丢失会导致系统不可恢复。

### 5.2 异步写入

可以异步写入：

- summary。
- event extraction。
- memory card。
- diary。
- reflection。
- relationship update。

原因：这些是派生结果，可以延迟生成，也可以重跑。

### 5.3 写入审核

长期记忆写入需要 Memory Governor。

审核条件：

- 是否有明确证据。
- 是否来自用户明确表达。
- 是否只是 Agent 猜测。
- 是否与旧记忆冲突。
- 是否涉及隐私。
- 是否值得长期保存。

写入结果：

- accept：写入长期记忆。
- short_term_only：只保留在会话摘要。
- diary_only：只进入日记。
- reject：不写入。
- needs_user_confirmation：需要用户确认。

## 6. 检索策略

### 6.1 检索维度

检索不应只按 embedding similarity。应同时考虑：

- semantic similarity
- recency
- importance
- memory strength
- owner
- mode
- relationship relevance
- source trust
- conflict status

### 6.2 各模式默认检索

Idle：

- Agent 自己近期记忆。
- Agent-Agent 关系记忆。
- 当前 idle 主题相关记忆。

Companion 1：

- 最近 idle。
- 用户相关记忆。
- 用户与 Agent 关系。
- 当前话题相关记忆。

Companion 2：

- 当前会话。
- 用户 profile。
- 用户明确相关的长期记忆。

Work：

- task memory。
- skill memory。
- tool traces。
- project docs。

## 7. 上下文预算

V1 建议使用固定预算，而不是无限拼接。

示例：

- system and policy：10%
- persona：15%
- current user or mode state：15%
- recent messages：25%
- retrieved memories：20%
- output schema and instructions：5%
- reserve：10%

不同模型 context window 不同，应由后端 Model Runtime Config 提供 max_context_tokens，再由 Context Builder 动态裁剪。V1 demo 中该配置由平台维护，不由用户选择。

## 8. V1 验收标准

Idle Mode：

- 两个 Agent 能连续互动 20 轮以上。
- 最近对话可展示。
- 对话进入数据库。
- 能生成 session summary。
- 能生成低频 diary。

Companion 1：

- 用户插入 idle 后，Agent 能自然回应用户。
- Agent 不丢失刚才 idle 话题。
- Agent 不继续忽视用户。

Companion 2：

- 用户可新建聊天。
- 能使用 Agent persona。
- 能保存和滚动加载聊天历史。

上下文系统：

- 每次模型调用可记录 context package。
- 原始消息和摘要分离。
- 至少支持 persona、recent messages、summary、memory retrieval 四类上下文。
- 异步 summary worker 不阻塞聊天主链路。

## 9. 非目标

V1 暂不做：

- 完整自我人格重写。
- 复杂 GraphRAG。
- 多用户群聊。
- 桌宠控制闭环。
- 完整 Work Mode 24x7。
- 用户自选模型 endpoint / api key / 本地模型路径配置。
- 模型微调。

V1 要为这些能力预留数据结构，但不要一开始实现过重。

## 10. 产品风险

### 风险 1：人格漂移

如果 Agent 能频繁修改自己人格，会导致用户失去掌控感。

缓解：

- core persona 不自动改。
- adaptive persona 慢更新。
- 用户可查看和回滚人格变化。

### 风险 2：假记忆

摘要和反思可能编造不存在的事件。

缓解：

- 所有 memory card 必须引用 source_message_ids。
- 没有证据的内容只能作为 reflection，不能作为 fact。

### 风险 3：token 爆炸

Idle 24x7 会产生大量对话。

缓解：

- idle 频率可控。
- 异步摘要。
- 低价值消息只存原文，不进入长期记忆。

### 风险 4：模式污染

Work Mode 的任务压力污染 Companion Mode 的陪伴人格，或 idle 玩笑污染正式工作任务。

缓解：

- memory_type 隔离。
- context recipe 隔离。
- task memory 和 companion memory 分库或分 namespace。

### 风险 5：用户隐私

V1 中用户不提供模型 endpoint 或 API key，但仍会产生个人偏好、聊天历史和长期记忆等敏感数据。

缓解：

- 平台模型 API key 只存 secret ref，不进入用户数据表，不返回前端。
- 记忆 visibility 分级。
- 用户可删除长期记忆。
- context package 可审计。
