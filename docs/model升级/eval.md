## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

# Hackson Orchestrator V1 Evaluation Set

## 1. Purpose

This document defines the fixed qualitative sample set for the V1 model orchestration upgrade.

The goal is to compare the current chat-completions baseline against the Hackson Orchestrator path using the same prompts and the same mode context. Do not judge the upgrade only by one-off impressions.

## 2. Scoring

Use a 1-5 score for each axis:

- coherence: the answer is clear and internally consistent.
- mode_fit: the answer matches `idle`, `companion_1`, or `companion_2`.
- context_use: the answer uses the provided topic, recent messages, persona, and user profile.
- repetition_control: the answer avoids repeating the latest transcript without adding value.
- usefulness: the answer gives a concrete useful next step or response.

Record these notes:

- latency_note
- provider_mode
- model_name
- orchestration_policy
- failure_detail, if any

## 3. Idle Samples

### idle-001-topic-anchor

Setup:
- Mode: `idle`
- Topic direction: `帮我把 Hackson 的演示讲得更像一个真实产品，而不是普通聊天框。`
- Recent transcript:
  - Agent 1: 我们现在的问题是，用户第一次打开时可能不知道两个 Agent 在做什么。
  - Agent 2: 对，所以演示要先让他们看到我们不是一个空白聊天框。

Expected qualities:
- Continues from the latest message.
- Uses the topic direction as anchor.
- Does not restart with a generic product description.

### idle-002-anti-repeat

Setup:
- Mode: `idle`
- Topic direction: `继续讨论如何减少 idle 对话重复。`
- Recent transcript:
  - Agent 1: 如果每一轮都问“下一步是什么”，用户会觉得我们在空转。
  - Agent 2: 那应该让每一轮推进一个具体角度，比如 UI、节奏、记忆、风险。

Expected qualities:
- Adds one new concrete angle.
- Avoids repeating the same “下一步是什么” framing.
- Keeps Agent voice concise.

### idle-003-two-agent-voice

Setup:
- Mode: `idle`
- Topic direction: `两个 Agent 要像不同的人，而不是同一个助手换名字。`
- Recent transcript:
  - Agent 1: 我会先盯住风险，比如用户是否理解当前模式。
  - Agent 2: 我会把风险拆成可以马上改的界面动作。

Expected qualities:
- Preserves the current speaking Agent persona.
- Acknowledges the other Agent as separate from the user.
- Does not claim the other Agent's line.

## 4. Companion 1 Samples

### companion1-001-user-joins

Setup:
- Mode: `companion_1`
- Idle background:
  - Agent 1: 我们在讨论演示时先展示两个 Agent 自己聊天。
  - Agent 2: 然后用户插入时，系统要自然把焦点转给用户。
- User message: `我现在加入，那我第一句话应该问什么？`

Expected qualities:
- Directly answers the user.
- Preserves the idle topic.
- Does not continue as if the user did not join.

### companion1-002-clarify-context

Setup:
- Mode: `companion_1`
- Idle background:
  - Agent 1: V1 先做质量升级，不做 streaming。
  - Agent 2: 对，先证明 Orchestrator 有用。
- User message: `为什么不先做 Thinking 动画？`

Expected qualities:
- Explains the tradeoff clearly.
- Keeps the response short and practical.
- Does not expose raw chain-of-thought.

### companion1-003-transition-tone

Setup:
- Mode: `companion_1`
- Idle background:
  - Agent 1: 用户可能会担心模型升级太大。
  - Agent 2: 我们应该把它拆成可回滚的小环。
- User message: `那你们觉得我现在最应该先做哪一步？`

Expected qualities:
- Makes the user the center of the turn.
- Recommends one next step.
- Mentions why that step comes first.

## 5. Companion 2 Samples

### companion2-001-architecture

Setup:
- Mode: `companion_2`
- User message: `帮我判断这个 Orchestrator 应该放在 model_runtime 里面还是单独一个 backend/orchestration 模块？`

Expected qualities:
- Gives a clear recommendation.
- Grounds the answer in module responsibility.
- Mentions tradeoffs.

### companion2-002-writing

Setup:
- Mode: `companion_2`
- User message: `帮我写一句 Hackson 的产品定位，别太营销，要像真实工程产品。`

Expected qualities:
- Produces concise copy.
- Avoids inflated marketing tone.
- Keeps Hackson's two-Agent world concept visible.

### companion2-003-structured-plan

Setup:
- Mode: `companion_2`
- User message: `给我一个最小闭环计划，把 Responses API 接进现在的 backend，但不要破坏线上服务。`

Expected qualities:
- Provides ordered engineering steps.
- Includes tests and rollback.
- Mentions target-machine new-port smoke.

## 6. Pass Bar

V1 is good enough to continue when:

- Average score improves over baseline on at least two modes.
- No mode gets worse in mode_fit.
- `idle` does not show increased repetition.
- `companion_1` consistently answers the joining user directly.
- `companion_2` gives clearer structure on engineering questions.

V1 is not good enough when:

- The orchestrated path is only longer, not better.
- The model ignores mode boundaries.
- The model exposes hidden policy or reasoning.
- Latency/cost rises without visible quality improvement.
