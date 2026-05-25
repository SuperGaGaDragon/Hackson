## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex

# Hackson Backend 产品级架构计划

版本：v0.1  
日期：2026-05-25  
目标读者：第一次接触 Hackson 后端的程序员

## 1. 这份文档解决什么问题

Hackson 后端要支撑三个核心产品能力：

- 用户和 Agent 配置。
- Idle / Companion 对话主链路。
- 上下文构建和模型调用。

这份文档定义后端应该如何分模块、每个模块负责什么、模块之间怎么调用，以及未来扩展到 summary、memory、diary、work mode 时应该放在哪里。

本文档只描述产品级架构，不要求现在一次性实现所有模块。

## 2. 总体架构判断

后端采用“产品能力模块 + 少量基础设施模块”的结构。

推荐原则：

- `core/` 放所有模块共享的基础设施。
- `users/`、`agents/`、`conversations/` 这类目录按产品领域拆。
- `context/` 专门负责“这次模型应该看什么”。
- `model_runtime/` 专门负责“怎么调用模型”。
- `workers/` 放不阻塞主链路的异步任务。
- 不要过早把 `context/` 拆成很多小目录，V1 先做小而深的模块。

## 3. 推荐目录结构

```text
backend/
  main.py
  requirements.txt

  core/
    config.py
    database.py
    security.py
    logging.py

  users/
    routes.py
    schemas.py
    service.py
    repository.py
    model.py
    tests/

  agents/
    routes.py
    schemas.py
    service.py
    repository.py
    model.py
    tests/

  conversations/
    routes.py
    schemas.py
    service.py
    repository.py
    model.py
    tests/

  context/
    builder.py
    recipes.py
    transition.py
    compaction.py
    packages.py
    schemas.py
    tests/

  model_runtime/
    client.py
    orchestrator.py
    config_repository.py
    schemas.py
    tests/

  workers/
    summary_worker.py
    memory_worker.py
    diary_worker.py
    relationship_worker.py

  memory/
    repository.py
    governor.py
    schemas.py
    tests/

  tasks/
    routes.py
    schemas.py
    service.py
    repository.py
    model.py
    tests/
```

V1 不需要一次性创建所有目录。推荐按版本逐步增加。

## 4. 当前已有结构

当前后端已经有：

```text
backend/
  main.py
  core/
  users/
```

当前判断：

- `core/` 的方向正确，继续放配置、数据库连接、安全能力。
- `users/` 的方向正确，继续保持 routes / schemas / service / repository / model 的结构。
- 下一步应该新增 `agents/` 和 `conversations/`，再接 `model_runtime/` 和 `context/`。

## 5. 模块职责

### 5.1 core

职责：

- 读取平台配置。
- 管理 MongoDB 连接生命周期。
- 密码和 JWT 等安全能力。
- 后续可加入 logging、request id、错误类型。

不负责：

- 用户业务。
- Agent 业务。
- prompt 拼接。
- 模型调用业务流程。

### 5.2 users

职责：

- 注册。
- 登录。
- 当前用户查询。
- 用户基础设置。
- `idle_on` 等用户级产品开关。

不负责：

- Agent 人格。
- 模型 endpoint。
- API key。
- 对话消息。
- 长期记忆。

V1 重要约束：

- 用户表不存模型 endpoint。
- 用户表不存模型 API key。
- 用户设置页不暴露本地模型路径。

### 5.3 agents

职责：

- 创建和更新用户拥有的 Agent。
- 保存 Agent 名字、头像、core persona、speaking style、episode state。
- 给 context 模块提供 Agent persona。

不负责：

- 拼 prompt。
- 调模型。
- 保存聊天消息。
- 自动人格成长。

V1 最小字段：

- `id`
- `owner_user_id`
- `name`
- `avatar_url`
- `core_persona`
- `speaking_style`
- `episode_state`
- `created_at`
- `updated_at`

### 5.4 conversations

职责：

- 创建 idle / companion_1 / companion_2 / work conversation。
- 保存和读取 messages。
- 维护 conversation 状态。
- 组织一次用户消息到 Agent 回复的主链路。

主链路：

```text
用户请求或 idle tick
  -> conversations 保存输入 message
  -> context 构建 context package
  -> model_runtime 调用模型
  -> conversations 保存 Agent 回复
  -> 返回前端
```

不负责：

- 具体 prompt 配方。
- 具体模型 provider 细节。
- 异步 summary 和 memory 生成。

### 5.5 context

职责：

- 根据 mode 决定模型这次应该看什么。
- 构建 idle / companion_1 / companion_2 / work 的 context。
- 生成 Transition Context。
- 做 summary + recent messages 的上下文压缩。
- 生成 context package 调试记录。

不负责：

- HTTP route。
- 直接调用模型。
- 保存用户账号。
- 管理 MongoDB 连接。

推荐文件：

- `builder.py`：Context Builder 总入口。
- `recipes.py`：不同 mode 的 context recipe。
- `transition.py`：用户插入 idle 的 Transition Context。
- `compaction.py`：summary + recent messages 的压缩策略。
- `packages.py`：context package 记录、prompt hash、token estimate。
- `schemas.py`：context 输入输出类型。

核心边界：

```text
context 决定“模型看什么”
model_runtime 决定“怎么问模型”
conversations 决定“产品流程怎么走”
```

### 5.6 model_runtime

职责：

- 读取平台侧模型配置。
- 调用模型 endpoint。
- 处理 timeout、retry、streaming。
- 统一不同 provider 的返回格式。

不负责：

- 用户设置模型。
- 用户 API key。
- 拼业务 prompt。
- 保存聊天记录。

推荐文件：

- `client.py`：底层 HTTP 或 SDK 调用。
- `orchestrator.py`：超时、重试、流式、并发控制。
- `config_repository.py`：读取 `model_runtime_configs`。
- `schemas.py`：模型请求和响应类型。

V1 重要约束：

- 模型 endpoint 由后端平台统一配置。
- 前端不暴露 provider 选择。
- 用户数据不包含 API key。

### 5.7 workers

职责：

- 异步生成 summary。
- 异步生成 memory candidate。
- 异步生成 diary。
- 异步更新 relationship summary。

不负责：

- 阻塞聊天主链路。
- 直接处理 HTTP 请求。

V1.0 可以没有 workers。  
V1.2 开始加入 `summary_worker.py`。

### 5.8 memory

职责：

- 保存长期 memory card。
- 审核 memory candidate。
- 给 context 提供少量可用记忆。

不负责：

- 原始消息事实源。
- 自动覆盖 core persona。
- 完整 GraphRAG。

V1.3 再实现。

### 5.9 tasks

职责：

- Work Mode 的任务状态。
- 工具调用记录。
- Planner / Worker / Reviewer 后续协作状态。

V1.5 只预留上下文边界。  
V3.0 再做完整 Work Mode。

## 6. 调用关系

### 6.1 Companion 2 主链路

```text
POST /api/companion/conversations/:id/messages
  -> conversations.routes
  -> conversations.service
  -> messages repository 保存 user message
  -> context.builder.build(mode="companion_2")
  -> model_runtime.orchestrator.generate()
  -> messages repository 保存 agent message
  -> 返回 agent message
```

### 6.2 Idle tick 主链路

```text
POST /api/idle/tick
  -> conversations.routes
  -> conversations.service
  -> context.builder.build(mode="idle")
  -> model_runtime.orchestrator.generate()
  -> messages repository 保存 agent message
  -> 返回 agent message
```

### 6.3 用户插入 Idle 主链路

```text
POST /api/idle/join
  -> conversations.routes
  -> conversations.service 创建或读取 companion_1 conversation
  -> messages repository 保存 user message
  -> context.transition 生成 Transition Context
  -> context.builder.build(mode="companion_1")
  -> model_runtime.orchestrator.generate()
  -> messages repository 保存 agent message
  -> 返回 agent message
```

## 7. 版本落地顺序

### v1.0：主链路骨架

新增或完成：

- `agents/`
- `conversations/`
- `model_runtime/`
- `context/builder.py`
- `context/recipes.py`

目标：

- idle 能跑。
- companion_2 能跑。
- 所有消息入库。
- 模型调用由后端平台配置。

### v1.1：用户插入 Idle

新增或完成：

- `context/transition.py`
- `companion_1` conversation 关联逻辑。
- `/api/idle/join`。

目标：

- 用户从 idle 页面插入后，Agent 明确回应用户。
- Agent 保留刚才 idle 话题。

### v1.2：轻量上下文压缩

新增或完成：

- `context/compaction.py`
- `workers/summary_worker.py`
- `summaries` repository。

目标：

- 长对话不再把全部历史塞进 prompt。
- summary worker 失败不影响聊天主链路。

### v1.3：轻量 Memory

新增或完成：

- `memory/`
- `workers/memory_worker.py`
- context 读取少量 memory。

目标：

- 保存少量带证据的用户偏好或关系记忆。
- 没有 source message id 的 memory 不能写入。

### v1.4：Diary 和 Relationship Summary

新增或完成：

- `workers/diary_worker.py`
- `workers/relationship_worker.py`
- relationship summary 注入 idle recipe。

目标：

- Agent 有可展示日记。
- 两个 Agent 的关系摘要可以轻微变化。
- core persona 不被自动覆盖。

### v1.5：Work Mode 边界

新增或完成：

- `tasks/`
- `work` recipe。
- tool trace 保存结构。

目标：

- Work Mode 内容不进入 companion 默认上下文。
- 为 v3.0 完整 Work Mode 做准备。

## 8. 命名约定

推荐命名：

- 用 `context/compaction.py`，不用 `context/compact.py`。
- 用 `model_runtime/`，不用 `model_worker/` 作为主目录。
- 用 `workers/summary_worker.py` 表示异步任务。
- 用 `model_runtime/orchestrator.py` 表示模型调用编排。

原因：

- `compaction` 表示一类能力，不只是一次动作。
- `model_runtime` 比 `model_worker` 更准确，因为它包括配置、调用、超时、重试、流式输出。
- `workers` 适合放异步派生任务，不适合放同步模型调用主链路。

## 9. 不推荐的结构

不推荐现在就这样拆：

```text
context/
  prompt/
  token/
  retrieval/
  compact/
  memory/
  transition/
```

原因：

- V1 代码量还小。
- 太多小目录会让新程序员找不到主链路。
- 很多模块会变成只转发一层的浅模块。

V1 更适合：

```text
context/
  builder.py
  recipes.py
  transition.py
  compaction.py
  packages.py
  schemas.py
```

后续某个文件变大，再拆成目录。

## 10. 判断标准

新增模块前先问：

- 这个模块是否对应一个产品概念？
- 调用方是否能通过一个小接口获得大量行为？
- 删除它之后，复杂度是消失了，还是散落到很多调用方？
- 它是否能独立测试？
- 它是否让新人更容易理解主链路？

如果答案是否定的，先不要拆。

## 11. 最重要的边界

后端最重要的边界是：

```text
conversations：产品流程怎么走
context：模型这次看什么
model_runtime：怎么问模型
workers：哪些派生结果异步生成
```

只要这四个边界稳定，后续增加 memory、diary、relationship、work mode 都不会把主链路弄乱。
