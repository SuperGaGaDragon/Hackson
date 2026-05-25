# Hackson 上下文系统产品级开发计划

版本：v0.1  
日期：2026-05-25  
目标读者：第一次接触 Hackson 的程序员

## 1. 这份文档解决什么问题

Hackson 的核心体验不是普通聊天框，而是一个持续运行的双 Agent 世界：

- 两个不同性格的 Agent 会在用户不说话时自己聊天，这叫 Idle Mode。
- 用户可以突然加入它们正在发生的对话，这叫 Companion Mode 1。
- 用户也可以新开一个普通聊天窗口，这叫 Companion Mode 2。
- 后续版本中，Agent 可以协作完成任务，这叫 Work Mode。

上下文系统要解决的问题是：每次调用模型时，后端应该把哪些信息放进 prompt，哪些信息不放，如何避免 token 爆炸，如何让 Agent 不忘记自己是谁，也不把不同模式的内容混在一起。

本文档不是科研论文计划，而是产品和工程落地计划。优先目标是让 V1 demo 稳定、可调试、可继续扩展。

## 2. 一句话产品目标

让用户感觉自己不是在打开一个新的聊天框，而是在进入两个 AI 个体正在持续生活的世界。

## 3. 核心词汇

### 3.1 User

使用产品的人。V1 用户只需要账号、基础设置、是否开启 idle 等信息。

V1 不让用户配置模型 endpoint、API key 或本地模型路径。模型配置由后端平台统一维护。

### 3.2 Agent

产品中的 AI 个体。V1 默认两个 Agent。

每个 Agent 至少有：

- 名字。
- 头像。
- 核心人格。
- 说话风格。
- 当前短期状态。

### 3.3 Conversation

一次对话容器。它记录这次对话属于哪种模式。

模式包括：

- `idle`：两个 Agent 自主聊天。
- `companion_1`：用户插入 idle 对话。
- `companion_2`：用户新开聊天。
- `work`：未来任务协作模式。

### 3.4 Message

原始消息。用户、Agent、系统、工具的每条输出都要保存为 message。

Message 是事实源。摘要、记忆、日记都可以重建，但原始 message 不能丢。

### 3.5 Context

一次模型调用前拼给模型看的信息。

Context 不等于全部历史。Context 是后端根据当前模式、当前用户输入、最近消息、Agent 人格、摘要等材料拼出来的输入包。

### 3.6 Context Builder

负责构建 context 的后端模块。

它的输入是：

- 当前 mode。
- 当前 user message 或 idle seed。
- 当前 conversation。
- Agent persona。
- 最近消息。
- 会话摘要。
- 必要的用户或 Agent 记忆。

它的输出是：

- 给模型的 prompt/messages。
- context package 日志，方便调试。

### 3.7 Context Recipe

不同模式的上下文配方。

不能用一个万能 prompt 处理所有模式，因为 idle、用户插入、普通聊天、任务协作需要完全不同的信息优先级。

### 3.8 Summary

对长对话的压缩摘要。

Summary 的作用是降低 token 成本，不是替代原始 message。Summary 可以异步生成，失败后可以重跑。

### 3.9 Memory

长期记忆。V1 不急着做复杂记忆系统。

早期只需要支持少量用户偏好和 Agent 关系摘要。后续再做带证据链的 memory card。

## 4. 总体工程原则

### 原则 1：先实用，再复杂

V1 的目标是跑通产品体验，不是一次性实现完整 Context OS。

必须优先实现：

- 原始消息入库。
- 按模式构建 prompt。
- idle 对话。
- 用户插入 idle 的自然转场。
- 普通 companion 聊天。

暂时不优先实现：

- 完整 GraphRAG。
- 多跳检索。
- Agent 自动改自己人格。
- 复杂关系状态机。
- 完整 Work Mode。

### 原则 2：原始消息必须同步保存

用户发来的消息、Agent 输出、工具结果，都必须先保存到数据库。

摘要、记忆、日记可以异步生成。

### 原则 3：人格不能随便被模型改写

V1 的 Agent 人格分两层即可：

- `core_persona`：用户设置或系统模板，模型不能自动覆盖。
- `episode_state`：短期状态，例如今天情绪、刚才讨论的话题。

后续再加 `adaptive_persona`，用于长期缓慢变化。

### 原则 4：不同模式必须隔离

Idle 的生活闲聊不能污染 Work Mode 的任务状态。

Work Mode 的工具失败复盘也不能污染 Companion Mode 的陪伴人格。

### 原则 5：每次模型调用必须可调试

后端应该记录 context package，说明这次模型调用用了哪些材料。

最少记录：

- mode。
- conversation_id。
- agent_id。
- recent message 数量。
- 使用了哪个 summary。
- 使用了哪些 persona 字段。
- prompt 大致 token 数。

## 5. 推荐后端结构

```text
Frontend
  -> Backend API
    -> Conversation Service
    -> Context Builder
    -> Model Orchestrator
    -> Storage
      -> Users
      -> Agents
      -> Conversations
      -> Messages
      -> Summaries
      -> Context Packages
      -> Model Runtime Config
    -> Async Workers
      -> Summary Worker
      -> Memory Worker
      -> Diary Worker
      -> Relationship Worker
```

V1 只需要实现主链路：

```text
Frontend
  -> Backend API
    -> Conversation Service
    -> Context Builder
    -> Model Orchestrator
    -> Database
```

Async Workers 可以从 v1.2 开始逐步加入。

## 6. 最小数据模型

### 6.1 users

用途：保存用户基础信息和设置。

必要字段：

- `id`
- `username`
- `display_name`
- `email`
- `password_hash`
- `idle_on`
- `created_at`
- `updated_at`

不要存：

- 用户模型 endpoint。
- 用户模型 API key。
- 本地模型路径。

### 6.2 agents

用途：保存两个 Agent 的人格和显示信息。

必要字段：

- `id`
- `owner_user_id`
- `name`
- `avatar_url`
- `core_persona`
- `speaking_style`
- `episode_state`
- `created_at`
- `updated_at`

后续字段：

- `adaptive_persona`
- `persona_version`

### 6.3 conversations

用途：保存一次对话容器。

必要字段：

- `id`
- `user_id`
- `mode`
- `participants`
- `title`
- `status`
- `parent_idle_conversation_id`
- `created_at`
- `updated_at`

`parent_idle_conversation_id` 用于 Companion Mode 1，表示用户是从哪段 idle 对话插入的。

### 6.4 messages

用途：保存原始消息。

必要字段：

- `id`
- `conversation_id`
- `sender_type`
- `sender_id`
- `content`
- `content_type`
- `metadata`
- `created_at`

`sender_type` 可选值：

- `user`
- `agent`
- `system`
- `tool`

### 6.5 summaries

用途：保存会话摘要和 idle 场景摘要。

必要字段：

- `id`
- `conversation_id`
- `summary_type`
- `content`
- `source_message_start_id`
- `source_message_end_id`
- `created_at`
- `updated_at`

`summary_type` 可选值：

- `session`
- `idle_scene`
- `companion`
- `task`

### 6.6 context_packages

用途：记录每次模型调用用了什么上下文，方便调试。

必要字段：

- `id`
- `conversation_id`
- `mode`
- `agent_id`
- `included_message_ids`
- `included_summary_ids`
- `included_agent_ids`
- `token_estimate`
- `prompt_hash`
- `created_at`

### 6.7 model_runtime_configs

用途：后端平台统一维护模型调用配置。

必要字段：

- `id`
- `provider`
- `endpoint`
- `model_name`
- `api_key_secret_ref`
- `max_context_tokens`
- `max_output_tokens`
- `timeout_ms`
- `concurrency_limit`
- `enabled`

这张表不向普通用户设置页暴露。

## 7. 三种 V1 模式如何运行

### 7.1 Idle Mode

目标：两个 Agent 在用户没有主动聊天时自主对话。

输入：

- Agent A persona。
- Agent B persona。
- 最近 N 条 idle messages。
- 当前 idle summary。
- 一个 idle seed，例如“讨论今天想做什么”。

输出：

- Agent A 或 Agent B 的下一句话。
- 新 message 入库。
- 前端实时展示。

V1 简化规则：

- 不需要每轮都生成记忆。
- 不需要每轮都写日记。
- 不允许 Agent 自动改 core persona。
- idle 频率要可控，避免 token 和成本失控。

### 7.2 Companion Mode 1

目标：用户正在看 idle 对话时突然插入，两个 Agent 要自然转向用户。

这是 V1 最重要的差异化体验。

输入：

- 用户消息。
- 当前 idle conversation。
- 最近 N 条 idle messages。
- idle scene summary。
- 两个 Agent persona。

核心机制：Transition Context。

Transition Context 是后端生成的一段明确说明，例如：

```text
用户刚刚加入了 Agent A 和 Agent B 的 idle 对话。
它们刚才正在讨论：{idle_topic_summary}
用户说：{user_message}
现在 Agent 必须把注意力转向用户，同时保留刚才话题的连续性。
```

输出：

- 一个或两个 Agent 对用户的回应。
- `companion_1` conversation 继续保存。
- 原 idle 对话可以暂停，或标记为被用户加入。

V1 验收重点：

- Agent 必须明确回应用户。
- Agent 不能继续无视用户自说自话。
- Agent 要能保留刚才 idle 话题。

### 7.3 Companion Mode 2

目标：用户主动开启一个普通聊天窗口，像 ChatGPT 一样和一个或两个 Agent 对话。

输入：

- 用户消息。
- 当前 companion conversation 的最近 N 条 messages。
- 被选择的 Agent persona。
- 用户基础 profile。

输出：

- Agent 回复。
- 消息入库。
- 前端滚动加载历史。

V1 简化规则：

- 默认不带 idle 历史。
- 用户问“你们刚刚聊什么”时，再查 idle summary。
- 不做复杂长期记忆检索。

## 8. Context Recipe 具体规则

### 8.1 Idle Recipe

优先级从高到低：

1. 系统规则。
2. 当前模式：`idle`。
3. 当前说话 Agent 的 core persona。
4. 另一个 Agent 的简短 persona。
5. 最近 idle messages。
6. idle summary。
7. 当前 idle seed。
8. 输出格式要求。

不要放入：

- 全部历史消息。
- Work Mode 任务状态。
- 用户私密记忆，除非当前话题明确需要。

### 8.2 Companion 1 Recipe

优先级从高到低：

1. 系统规则。
2. 当前模式：`companion_1`。
3. Transition Context。
4. 用户当前消息。
5. 最近 idle messages。
6. idle summary。
7. 两个 Agent 的 persona。
8. 输出格式要求。

关键要求：

- 用户当前消息必须高优先级。
- 最近 idle 只是背景，不是继续无视用户的理由。
- 模型必须知道“用户刚刚加入”。

### 8.3 Companion 2 Recipe

优先级从高到低：

1. 系统规则。
2. 当前模式：`companion_2`。
3. 用户当前消息。
4. 当前聊天最近 messages。
5. Agent persona。
6. 用户基础 profile。
7. 输出格式要求。

关键要求：

- 轻上下文启动。
- 不主动塞 idle 历史。
- 不主动塞 Work Mode 内容。

### 8.4 Work Recipe

V1 不完整实现 Work Mode，但数据和设计要预留。

未来优先级：

1. 系统规则。
2. 当前模式：`work`。
3. 用户目标。
4. 当前 task state。
5. Agent 分工。
6. 最近工具调用结果。
7. 阻塞和开放问题。
8. 输出格式要求。

## 9. 版本计划

## v1.0：上下文主链路骨架

### 目标

跑通最小可用的上下文系统。程序员可以通过后端 API 创建对话、保存消息、构建 prompt、调用模型、返回前端。

### 必须实现

- 用户基础表。
- Agent 表。
- Conversation 表。
- Message 表。
- Model Runtime Config 表。
- 后端统一模型调用层。
- `ContextBuilder` 基础模块。
- `idle` recipe。
- `companion_2` recipe。
- 原始消息同步入库。

### 前端需要支持

- 设置两个 Agent 的名字、头像、核心人格。
- 打开一个 idle 页面。
- 打开一个 companion_2 聊天页面。
- 展示消息历史。

### 不做

- 用户自定义模型 endpoint。
- 长期记忆。
- 自动人格成长。
- 日记。
- 复杂摘要。
- Work Mode。

### 验收标准

- 两个 Agent 能在 idle 页面连续对话至少 10 轮。
- 用户能新开 companion_2 对话并收到回复。
- 所有消息都能在数据库中查到。
- 模型 endpoint 只由后端配置。

## v1.1：用户插入 Idle 的 Transition Context

### 目标

实现 Hackson 最关键的产品体验：用户进入一个正在发生的 Agent 世界。

### 必须实现

- `companion_1` conversation 创建逻辑。
- `parent_idle_conversation_id` 关联。
- 最近 idle messages 读取。
- Transition Context 生成。
- `companion_1` recipe。
- 用户插入事件保存为 message 或 system event。

### 前端需要支持

- 用户在 idle 页面直接输入一句话。
- 页面切换或进入三方对话状态。
- 显示用户插入前后的连续对话。

### 不做

- 复杂 memory retrieval。
- 自动关系变化。
- Agent 自我反思。

### 验收标准

- 用户插入后，Agent 第一轮回复必须明确回应用户。
- Agent 回复能引用或延续刚才 idle 话题。
- Agent 不会继续只和另一个 Agent 说话。
- `companion_1` 的消息和原 idle conversation 能在数据库中关联。

## v1.2：轻量摘要和上下文压缩

### 目标

让 idle 和 companion 可以持续更久，不因为历史太长导致 prompt 爆炸。

### 必须实现

- Summary 表。
- Summary Worker。
- idle session summary。
- companion session summary。
- Context Builder 使用 summary + recent messages。
- 简单 token budget 裁剪。

### 前端需要支持

- 不需要专门展示 summary。
- 只需要继续稳定显示聊天历史。

### 不做

- 复杂长期记忆。
- GraphRAG。
- 记忆冲突检测。

### 验收标准

- idle 对话超过 30 轮后，Context Builder 不再塞入全部历史。
- 最近消息仍然保留在 prompt 中。
- 旧消息通过 summary 进入 prompt。
- Summary Worker 失败时不影响聊天主链路。

## v1.3：轻量 Memory Card

### 目标

开始保存少量长期有用的信息，但保持简单和可控。

### 必须实现

- Memory Card 表。
- Memory Worker v0。
- Memory Governor v0。
- 每条 memory 至少包含 source message id。
- Context Builder 可以按 mode 读取少量 memory。

### Memory Card 最小字段

- `id`
- `owner_type`
- `owner_id`
- `memory_type`
- `summary`
- `source_message_ids`
- `importance_score`
- `confidence`
- `created_at`
- `updated_at`

### V1.3 只允许写入的 memory 类型

- 用户明确偏好。
- 用户明确事实。
- Agent 和用户的关键互动。
- Agent-Agent 的少量关系摘要。

### 不做

- Agent 自动改 core persona。
- 复杂 memory graph。
- 多跳检索。

### 验收标准

- 用户明确说“我喜欢中文交流”后，可以生成一条带证据的 memory。
- 下次 companion_2 对话可以使用这条 memory。
- 没有 source message id 的 memory 不能写入。

## v1.4：日记和关系摘要

### 目标

让两个 Agent 看起来有持续经历，但不让这套系统影响主聊天稳定性。

### 必须实现

- Diary Worker。
- Relationship Summary。
- Agent-Agent 关系摘要注入 idle recipe。
- 用户可在设置页或 Agent 页面查看 diary。

### 不做

- 复杂关系数值状态机。
- 自动人格重写。
- 用户审批人格变化。

### 验收标准

- idle 对话结束后可以生成一篇简短 diary。
- 多次 idle 后，两个 Agent 的关系摘要可以轻微变化。
- 关系摘要有 source messages。
- core persona 不被自动覆盖。

## v1.5：Work Mode 上下文边界预留

### 目标

为未来 Work Mode 做数据和上下文隔离，但不在 V1.5 做完整 24x7 自动工作系统。

### 必须实现

- Task 表。
- Tool Trace 表或 message metadata。
- `work` recipe 草稿。
- task memory namespace。
- Work Mode 内容不进入 companion memory。

### 不做

- 完整 Codex CLI 自动执行闭环。
- 长时间无人值守任务系统。
- 复杂 Planner/Worker/Reviewer 多 Agent 编排。

### 验收标准

- 可以创建一个 task。
- 可以保存工具调用结果。
- Context Builder 能构建 work prompt。
- Work Mode 的消息不会出现在 companion_1 或 companion_2 的默认上下文里。

## v2.0：桌宠和 World State

### 目标

把网页中的 Agent 状态同步到桌宠或桌面伴侣。

### 必须实现

- World State。
- Agent 当前活动状态。
- 桌宠读取最近状态。
- 桌宠展示和网页 idle 状态一致。

### 验收标准

- Agent 在网页里 idle 聊天时，桌宠能展示对应状态。
- 用户插入对话时，桌宠状态能变化。
- 桌宠不生成独立于后端的假状态。

## v3.0：完整 Work Mode

### 目标

让 Agent 分工协作完成任务，并能调用 Codex CLI 或其他工具。

### 必须实现

- Planner / Worker / Reviewer 角色。
- Task state machine。
- Tool execution queue。
- 工具调用审计。
- 任务摘要。
- 失败复盘。
- skill memory。

### 验收标准

- 用户能创建一个工作目标。
- Agent 能拆任务。
- Worker 能请求工具调用。
- Reviewer 能检查结果。
- 前端能实时显示任务进度。
- Work memory 不污染 Companion memory。

## 10. 推荐开发顺序

### 第一阶段：先把消息链路跑通

开发顺序：

1. 数据库 schema。
2. Conversation Service。
3. Message 写入。
4. Model Runtime Config。
5. Model Orchestrator。
6. Context Builder。
7. Idle API。
8. Companion 2 API。

### 第二阶段：做 Hackson 的差异化体验

开发顺序：

1. Idle 页面用户输入。
2. Companion 1 conversation 创建。
3. 读取最近 idle messages。
4. 生成 Transition Context。
5. Agent 回复用户。
6. 前端展示三方对话。

### 第三阶段：做可持续运行

开发顺序：

1. Summary Worker。
2. idle summary。
3. companion summary。
4. token budget。
5. context package logging。

### 第四阶段：做轻量长期感

开发顺序：

1. Memory Card。
2. Memory Worker v0。
3. Diary Worker。
4. Relationship Summary。

## 11. API 草案

### 11.1 创建或更新 Agent

```http
POST /api/agents
PATCH /api/agents/:agentId
```

用途：

- 设置 Agent 名字。
- 设置头像。
- 设置 core persona。
- 设置 speaking style。

### 11.2 获取 idle 对话

```http
GET /api/idle/conversation
```

用途：

- 获取当前用户的 idle conversation。
- 返回最近 messages。

### 11.3 推进 idle 一轮

```http
POST /api/idle/tick
```

用途：

- 后端让两个 Agent 自主推进一轮。
- 保存新 message。
- 返回前端展示。

### 11.4 用户插入 idle

```http
POST /api/idle/join
```

请求：

```json
{
  "idle_conversation_id": "conv_idle_123",
  "message": "你们刚才在讨论什么？"
}
```

用途：

- 创建或继续 companion_1 conversation。
- 构建 Transition Context。
- 调用模型。
- 返回 Agent 回复。

### 11.5 创建 companion_2 聊天

```http
POST /api/companion/conversations
```

用途：

- 新建普通聊天窗口。

### 11.6 发送 companion_2 消息

```http
POST /api/companion/conversations/:conversationId/messages
```

用途：

- 用户发送消息。
- Context Builder 构建普通聊天上下文。
- 模型回复。
- 消息入库。

## 12. Context Builder 伪代码

```ts
async function buildContext(input) {
  const conversation = await getConversation(input.conversationId);
  const mode = conversation.mode;

  const agents = await getConversationAgents(conversation);
  const recentMessages = await getRecentMessages(conversation.id, mode);
  const summary = await getLatestSummary(conversation.id);

  if (mode === "idle") {
    return buildIdleContext({ agents, recentMessages, summary, idleSeed: input.idleSeed });
  }

  if (mode === "companion_1") {
    const idleConversation = await getConversation(conversation.parent_idle_conversation_id);
    const idleRecentMessages = await getRecentMessages(idleConversation.id, "idle");
    const idleSummary = await getLatestSummary(idleConversation.id);
    const transitionContext = buildTransitionContext({
      userMessage: input.userMessage,
      idleRecentMessages,
      idleSummary
    });

    return buildCompanion1Context({
      agents,
      userMessage: input.userMessage,
      transitionContext,
      idleRecentMessages,
      idleSummary
    });
  }

  if (mode === "companion_2") {
    return buildCompanion2Context({
      agents,
      userMessage: input.userMessage,
      recentMessages,
      summary
    });
  }

  if (mode === "work") {
    return buildWorkContext(input);
  }
}
```

## 13. Prompt 输出格式建议

V1 可以先让模型直接输出自然语言，降低实现风险。

但后端内部建议逐步支持结构化 envelope：

```json
{
  "visible_message": "我看到你来了。我们刚才正在讨论今天要不要继续这个话题。",
  "events": [],
  "memory_candidates": [],
  "relationship_signals": []
}
```

前端只展示 `visible_message`。

如果结构化输出影响对话质量，V1 可以先不用强制 JSON，只在异步 worker 中从自然语言里抽取摘要和记忆。

## 14. 非目标清单

V1 明确不做：

- 用户自选模型 endpoint。
- 用户填写 API key。
- 用户填写本地模型路径。
- 完整科研 benchmark。
- 模型微调。
- 完整 GraphRAG。
- 完整自动人格成长。
- Agent 自由改写 core persona。
- 完整 Work Mode。
- 多用户群聊。

这些不是永远不做，而是不能阻塞 V1。

## 15. 程序员接手时应该先看什么

建议阅读顺序：

1. `docs/需求文档final.md`：理解产品三种模式。
2. `docs/上下文/plan.md`：理解工程落地顺序。
3. `docs/上下文/context-requirements-for-hackson.md`：理解更完整的上下文需求。
4. `docs/上下文/context-innovation-proposal.md`：理解长期架构方向。
5. `docs/plan.md`：理解全项目路线。

## 16. 最重要的判断

Hackson V1 的上下文系统不要一开始追求复杂记忆系统。

最重要的是先把这条链路做稳定：

```text
用户或 idle tick
  -> 保存原始消息
  -> 根据 mode 构建 context
  -> 调用模型
  -> 保存 Agent 回复
  -> 前端实时展示
  -> 异步生成 summary
```

只要这条链路稳定，后续的 memory、diary、relationship、work mode 都可以逐步加上去。
