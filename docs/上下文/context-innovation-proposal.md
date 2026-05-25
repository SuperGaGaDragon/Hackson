# Hackson 创新上下文架构提案：Context OS for Living Agents

版本：v0.1  
日期：2026-05-25  
定位：产品级科研提案

## 1. 核心判断

Hackson 不应该把自己定义成“两个 Agent 的聊天应用”。真正有壁垒的方向是：

> 为长期生活型、多 Agent、可陪伴、可工作的 AI 个体设计一套 Context OS。

这里的 Context OS 指一套围绕模型上下文窗口运行的系统级能力：

- 决定每次模型应该看什么。
- 决定哪些经历会变成记忆。
- 决定人格如何稳定又缓慢成长。
- 决定用户插入一个正在运行的 Agent 世界时，如何自然转场。
- 决定 Work Mode 中任务状态如何长期不漂移。

这不是普通 RAG，也不是简单 summary。它是一个针对“活着的 Agent”的上下文调度系统。

## 2. 产品创新点

### 2.1 从 Chat Session 转向 Living Timeline

普通聊天产品以 session 为中心。Hackson 应以 living timeline 为中心。

传统结构：

```text
user -> chat session -> messages -> summary
```

Hackson 结构：

```text
world -> agents -> events -> memories -> relationships -> conversations
```

区别：

- 聊天只是世界中的一种事件。
- Agent 有自己的经历，不只是在等待用户提问。
- 用户插入 idle 不是新 session，而是进入 timeline 的一个时刻。
- 日记、关系、人格成长都来自 timeline。

产品价值：

- 用户感觉 Agent 在“持续存在”。
- 桌宠和硬件能显示真实状态。
- 后续 Work Mode 可以和生活世界共存。

### 2.2 三层人格模型

Hackson 的人格不能只是 `soul.md`。建议设计为三层：

```text
Core Persona
Adaptive Persona
Episode State
```

Core Persona：

- 用户显式编辑。
- 模板导入。
- 定义基本身份、价值观、语气边界。
- 默认不可被 Agent 自动修改。

Adaptive Persona：

- 来自长期互动。
- 慢速更新。
- 记录“这个 Agent 最近变得更谨慎/更亲近用户/更喜欢争论某类问题”。
- 需要证据累积和版本记录。

Episode State：

- 短期状态。
- 如今天心情、当前兴趣、刚才和另一个 Agent 争论后的余波。
- 可快速变化，不写入核心人格。

创新价值：

- 既能让用户感觉 Agent 成长，又不会失控。
- 支持两个 Agent 形成关系变化。
- 支持用户查看“它为什么变成这样”。

### 2.3 Memory Card + Evidence Chain

每条长期记忆都不应该是裸文本，而应该是 Memory Card。

示例：

```yaml
memory_id: mem_123
owner: agent_a
type: relationship
title: Agent A finds Agent B intellectually challenging
summary: Agent A has repeatedly enjoyed debating with Agent B about philosophy.
evidence:
  - message_id_1
  - message_id_2
  - event_id_7
strength: 0.72
confidence: 0.81
tags: [philosophy, relationship, debate]
created_at: 2026-05-25
updated_at: 2026-05-25
```

关键创新：

- 记忆必须有证据链。
- 记忆可以增强、衰减、冲突、合并。
- 记忆不是 summary 的替代品，而是可检索、可解释、可治理的长期状态。

### 2.4 双轨记忆：System Memory 与 Narrative Memory

陪伴类产品容易把“系统事实”和“文学表达”混在一起。建议分成双轨：

System Memory：

- 给模型使用。
- 结构化。
- 可追溯。
- 语气中立。
- 用于上下文构建。

Narrative Memory：

- 给用户看。
- 日记、回忆、生活片段。
- 可以有文学表达。
- 不作为事实源。

示例：

System Memory：

```text
用户更喜欢中文交流。证据：2026-05-25 用户明确说“你用中文和我交流”。
```

Narrative Memory：

```text
今天我学会了，和他讲话时要用中文。他似乎更希望我们像同伴一样直接交流。
```

创新价值：

- 用户体验更有温度。
- 系统记忆更可靠。
- 日记出错不会污染事实层。

### 2.5 Mode-Aware Context Recipe

每种模式必须有独立上下文配方。

```text
Idle Recipe
Companion 1 Recipe
Companion 2 Recipe
Work Recipe
```

创新点不在于有四个 prompt，而在于 Context Builder 根据 mode 选择不同 memory namespaces、预算和排序策略。

Idle：

- 强 persona。
- 强 Agent-Agent relationship。
- 弱 user memory。
- 低工具状态。

Companion 1：

- 强用户当前消息。
- 强 idle transition。
- 中等 idle history。
- 强用户关系。

Companion 2：

- 强用户当前会话。
- 中等用户长期记忆。
- 弱 idle history。

Work：

- 强任务目标。
- 强工具结果。
- 强项目文档。
- 弱生活人格。

创新价值：

- 避免模式污染。
- 降低 token 成本。
- 让用户插入 idle 的体验自然。

### 2.6 Transition Context：用户插入 Idle 的核心机制

Companion 1 的关键不是检索更多历史，而是生成一个 transition context。

当用户插入 idle，对模型的上下文应包含：

```text
用户刚刚加入了 Agent A 和 Agent B 的 idle 对话。
刚才它们正在讨论：{topic_summary}
最近的情绪状态：{emotional_state}
用户说：{user_message}
现在两个 Agent 应该把注意力转向用户，同时保留刚才话题的连续性。
```

这段 transition context 应由系统生成，而不是让模型自己猜。

创新价值：

- 用户感觉自己真的进入了一个活的场景。
- Agent 不会继续忽略用户。
- 不需要塞入大量 idle 历史。

### 2.7 Memory Governor：记忆治理器

不要让 Agent 直接改长期记忆。建议引入 Memory Governor。

流程：

```text
message/event
  -> extractor
  -> memory candidate
  -> governor
  -> accepted memory / rejected / short-term only / needs user confirmation
```

Governor 判断：

- 是否有证据。
- 是否重要。
- 是否涉及隐私。
- 是否与旧记忆冲突。
- 是否属于正确 namespace。
- 是否需要用户确认。

创新价值：

- 防止假记忆。
- 防止人格漂移。
- 让系统可审计。

### 2.8 Relationship Engine：关系不是摘要，是状态机

两个 Agent 之间、用户与 Agent 之间都应有 Relationship State。

关系不是一句 summary，而是一组可演化状态：

```yaml
familiarity: 0.61
trust: 0.54
tension: 0.22
admiration: 0.37
last_shift_reason: "They had a productive disagreement about whether idle life needs goals."
evidence: [...]
```

关系变化触发条件：

- 高频互动。
- 明确赞同或冲突。
- 用户偏好表达。
- 任务协作成功或失败。
- 日记反思积累。

创新价值：

- Agent 的关系变化可解释。
- idle 对话不再只是随机聊天。
- 多用户群聊和多 Agent 世界可扩展。

### 2.9 Context Package 审计

每次模型调用前，Context Builder 应生成 Context Package。

内容：

- mode
- model runtime config id
- token budget
- included persona blocks
- included recent messages
- included memory cards
- included summaries
- excluded candidates and reasons
- final prompt hash

示例：

```yaml
context_package_id: ctx_456
mode: companion_1
conversation_id: conv_789
included:
  persona: [agent_a_core, agent_b_brief]
  recent_messages: 12
  memories: [mem_1, mem_2, mem_9]
  summaries: [idle_summary_today]
budget:
  max_tokens: 32000
  used_tokens: 11800
reason:
  mem_1: "user-agent relationship relevant"
  mem_2: "current idle topic"
```

创新价值：

- 后期调试上下文问题非常关键。
- 可以分析哪些记忆真的影响输出。
- 用户隐私和企业级合规可拓展。

## 3. 推荐系统架构

### 3.1 总体架构

```text
Frontend
  -> Backend API
    -> Conversation Service
    -> Context Builder
    -> Model Orchestrator
    -> Async Workers
      -> Event Extractor
      -> Summarizer
      -> Reflection Worker
      -> Memory Governor
      -> Relationship Engine
    -> Storage
      -> Message DB
      -> Event DB
      -> Memory DB
      -> Vector Index
      -> Task DB
      -> Secret Store
```

### 3.2 核心服务

Conversation Service：

- 接收用户消息。
- 创建 idle/companion/work conversation。
- 保存原始消息。
- 推送前端实时更新。

Context Builder：

- 根据 mode 选择 recipe。
- 检索和排序记忆。
- 控制 token budget。
- 生成 context package。

Model Orchestrator：

- 调用平台侧统一配置的 model endpoint。V1 demo 不做用户自选模型 endpoint。
- 支持异步并发。
- 处理超时、重试、流式输出。

Async Workers：

- 不阻塞主聊天链路。
- 生成摘要、事件、日记、记忆候选。
- 更新关系状态。

Memory Governor：

- 控制长期记忆写入。
- 冲突检测。
- 隐私策略。
- 人格更新审核。

## 4. 数据分层

建议使用五层上下文存储。

### Layer 0：Raw Log

内容：

- message
- tool call
- system event

特性：

- 不可丢。
- 可重放。
- 不直接塞入长期 prompt。

### Layer 1：Session Compression

内容：

- conversation summary
- idle scene summary
- task progress summary

特性：

- 可重建。
- 面向短中期上下文。

### Layer 2：Structured Event

内容：

- 发生了什么。
- 谁对谁做了什么。
- 重要性和情绪。

特性：

- 关系和记忆更新的输入。

### Layer 3：Memory Card

内容：

- 用户偏好。
- Agent 经历。
- 关系记忆。
- 任务经验。
- 技能。

特性：

- 可检索。
- 有证据。
- 有强度和衰减。

### Layer 4：State

内容：

- persona state
- relationship state
- world state
- task state

特性：

- 每次上下文构建的高优先级输入。
- 需要版本控制。

## 5. V1 落地路线

### Phase 1：Context OS Skeleton

目标：先跑通可审计的上下文主链路。

必须实现：

- Message DB。
- Conversation 表。
- Agent Persona 表。
- Model Runtime Config 表，由平台侧维护，V1 不暴露给用户配置。
- Context Builder。
- mode-aware recipe。
- context package logging。

暂不实现：

- 复杂记忆图谱。
- 自动人格成长。
- 多跳检索。

### Phase 2：Idle to Companion Transition

目标：打磨最核心体验：用户插入 idle。

必须实现：

- idle recent window。
- idle session summary。
- transition context。
- user_joined_idle event。
- Companion 1 recipe。

验收：

- 用户插入后，Agent 明确回应用户。
- Agent 保留刚才话题。
- Agent 语气符合各自 persona。

### Phase 3：Async Memory Pipeline

目标：让 idle 产生可积累的经历。

必须实现：

- event extractor。
- summary worker。
- diary worker。
- memory candidate。
- Memory Governor v0。

验收：

- idle 对话结束后能生成摘要。
- 能生成 Agent 日记。
- 能生成少量 Memory Card。
- Memory Card 有 evidence。

### Phase 4：Relationship State

目标：让两个 Agent 的长期关系可演化。

必须实现：

- relationship table。
- relationship update worker。
- relationship summary injection。

验收：

- 多次 idle 后关系摘要会变化。
- 变化有证据。
- 变化不会覆盖 core persona。

### Phase 5：Work Mode Context Boundary

目标：为 V3 留出空间，但不污染 V1。

必须实现：

- task namespace。
- tool trace schema。
- task summary schema。

暂不需要：

- 完整 24x7 work loop。
- 完整 Codex CLI 自动执行。

## 6. 推荐 Prompt Contract

每次模型输出不要只返回自然语言。建议要求内部返回结构化 envelope。

示例：

```json
{
  "visible_message": "我看到你来了。我们刚才正在争论...",
  "events": [
    {
      "type": "user_joined_idle",
      "summary": "User joined the idle conversation while agents were debating goals."
    }
  ],
  "memory_candidates": [
    {
      "type": "preference",
      "summary": "User prefers Chinese communication.",
      "confidence": 0.95
    }
  ],
  "relationship_signals": [
    {
      "subject": "agent_a",
      "object": "user",
      "signal": "responsiveness",
      "delta": 0.02
    }
  ]
}
```

前端只展示 `visible_message`。后端异步处理其他字段，或者由 worker 从 message 中抽取。

V1 可以先不强制模型直接返回 JSON，避免影响对话质量；但内部系统要逐步走向结构化 contract。

## 7. 创新科研方向

### 7.1 Slow Persona Learning

研究问题：

如何让 Agent 在长期互动中成长，但不发生人格漂移？

可能方案：

- 人格变化必须经过多条 evidence。
- 使用 personality delta，而不是覆盖 persona。
- 每次更新有 version 和 rollback。
- 用户可审批高影响人格变化。

产品表达：

- “它最近变得更喜欢和你讨论产品细节。”
- “它对另一个 Agent 的信任略微上升。”

### 7.2 Contextual Turn-Taking for Multi-Agent Chat

研究问题：

两个 Agent 和用户三方聊天时，谁该说话？什么时候只让一个 Agent 回？什么时候两个都回？

可能方案：

- turn policy model。
- 根据用户点名、话题、关系、最近发言长度决定 speaker。
- 避免两个 Agent 每次都同时长篇回复。

产品表达：

- 更自然的群聊。
- 用户不会被两个 Agent 同时淹没。

### 7.3 Memory Conflict Resolution

研究问题：

用户偏好变化、Agent 反思变化、旧记忆过期时，如何处理冲突？

可能方案：

- memory status: active | contradicted | stale | archived。
- 新记忆不删除旧记忆，只标记 supersedes。
- 回答时优先 active + high confidence + recent。

产品表达：

- “我之前记得你偏好 X，但最近你更常选择 Y。”

### 7.4 World State as Context Anchor

研究问题：

长期 idle 世界如何避免变成无意义聊天？

可能方案：

- world state 保存当前时间、场景、Agent 状态、最近活动。
- idle 每轮围绕 world state 更新。
- 桌宠状态来自 world state，而不是独立动画。

产品表达：

- Agent 看起来在持续生活。
- 桌宠显示和网页对话一致。

### 7.5 Context Evaluation Bench

研究问题：

如何评估上下文系统是否真的有效？

建议建立内部 benchmark：

- 用户插入 idle 后是否正确转场。
- Agent 是否记得用户偏好。
- Agent 是否保持 core persona。
- Agent 是否错误编造记忆。
- Work Mode 是否保持任务目标。
- 长 idle 后是否能总结关系变化。

每个 benchmark 都应该有固定输入、期望行为、评分规则。

## 8. 不建议采用的方案

### 8.1 不建议：全部历史直接塞 prompt

原因：

- 成本高。
- 延迟高。
- lost-in-the-middle。
- 长期不可持续。

### 8.2 不建议：只有一个 soul.md

原因：

- 无法区分用户设定和系统推断。
- 无法版本控制。
- 无法解释人格变化。

### 8.3 不建议：Agent 自由改自己人格

原因：

- 容易人格漂移。
- 用户失控。
- 假记忆会污染核心设定。

### 8.4 不建议：普通向量库作为唯一记忆

原因：

- 不懂关系。
- 不懂来源。
- 不懂冲突。
- 不懂模式隔离。

### 8.5 不建议：Idle 和 Work 共用记忆 namespace

原因：

- 生活对话和任务状态会互相污染。
- 陪伴人格可能影响正式工作。
- 工具失败复盘不该进入情感记忆。

## 9. 最小可行创新

如果 V1 资源有限，建议至少做这四件事：

1. Mode-aware Context Recipe。
2. Transition Context for Companion 1。
3. Memory Card with Evidence。
4. Three-layer Persona。

这四件事足以让 Hackson 和普通双 Agent 聊天 demo 拉开差距。

## 10. 一句话架构愿景

Hackson 的上下文系统不是“帮模型记住聊天记录”，而是“为长期存在的 AI 个体维护一个可解释、可成长、可治理的生活世界”。
