## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

# Hackson Orchestrator V1 Implementation Plan

## 1. Purpose

This document is the implementation manual for the V1 model orchestration upgrade.

The goal is to improve `idle`, `companion_1`, and `companion_2` output quality through one backend orchestration pipeline while keeping the first release small, testable, and reversible.

V1 is not a full ChatGPT clone. V1 proves that unified orchestration plus Responses-style reasoning policy improves the product before adding streaming UI, tool timelines, citations, or broader tool execution.

## 2. Required Reading

Read these files before implementation:

1. `agents/restrictions.md`
2. `agents/frontend_restrictions.md`
3. `README.md`
4. `api.md`
5. `docs/backend-architecture.md`
6. `docs/model升级/goal.md`
7. `docs/model升级/version.md`
8. `backend/README.md`
9. `backend/interactions/README.md`
10. `backend/context/README.md`
11. `backend/model_runtime/README.md`
12. `backend/conversations/README.md`
13. `frontend/README.md`
14. `frontend/src/features/idle/README.md`
15. `frontend/src/features/chat/README.md`

Important repository rules:

- Check `git status --short` before work.
- Do not stop existing target-machine services.
- Use a new port for target-machine smoke verification.
- Every new folder needs a `README.md`.
- Every new source file needs the project header.
- Keep secrets in ignored `.env` files, never tracked examples.
- Update root `api.md` only after API behavior is verified.
- Frontend copy must stay short.

## 3. Current Baseline

Current model path:

```text
interactions
  -> context_builder.build(...)
  -> model_runtime.generate(ModelGenerateRequest)
  -> OpenAICompatibleClient
  -> POST /chat/completions
  -> assistant text
  -> conversations.append_message(...)
```

Current strengths:

- `context/` already owns mode-aware prompt construction.
- `interactions/` already owns `idle`, `companion_1`, and `companion_2` product flow.
- `model_runtime/` already centralizes model config, provider call, and stable error mapping.
- Tests already use fake model runtimes, so orchestration can be tested without network calls.

Current gaps:

- No first-class Hackson Orchestrator boundary.
- No per-mode reasoning policy.
- No Responses API request/response shape.
- No provider response id in saved metadata.
- No structured reasoning summary or tool event metadata.
- No quality baseline set for comparing old and new output.

## 4. Product Definition

### 4.1 V1 User Outcome

Users should feel that all three conversation modes are smarter, more coherent, and more aware of the mode context:

- `idle`: two Agents continue naturally, avoid repetitive loops, and stay anchored to the selected topic.
- `companion_1`: the selected Agent clearly understands the user joined an ongoing idle conversation.
- `companion_2`: the selected Agent behaves closer to a high-quality ChatGPT-style companion chat.

### 4.2 V1 Non Goals

Do not implement these in V1:

- Streaming token UI.
- Visible Thinking timeline.
- Search status UI.
- Citation UI.
- File upload or file search.
- Code interpreter or Python sandbox.
- Image generation.
- Autonomous shell commands.
- User-owned model endpoint or API key settings.
- Raw chain-of-thought display.

### 4.3 Product Safety Rules

- The model may decide how to answer inside a mode policy.
- The model must not decide what hidden tools exist.
- The backend policy decides allowed tools, reasoning effort, timeout, token budget, and metadata.
- Raw reasoning chain-of-thought must never be shown or stored as user-visible text.
- `idle` auto behavior must remain conservative because it can generate repeated calls.
- Model provider failures must keep returning stable API errors such as `model_rate_limited` and `model_unavailable`.

## 5. Target Architecture

### 5.1 V1 Shape

```text
React UI
  -> FastAPI interaction route
    -> InteractionService
      -> ConversationService
      -> ContextBuilder
      -> HacksonOrchestrator
        -> OrchestrationPolicy
        -> ModelRuntime
          -> ResponsesClient or OpenAICompatibleClient fallback
      -> ConversationService.append_message(...)
```

### 5.2 Responsibility Split

`interactions/`:

- Owns product flow and message saving.
- Builds the context package through `context/`.
- Calls the orchestrator instead of calling `model_runtime` directly.
- Maps orchestrator/model failures to stable HTTP errors.

`context/`:

- Owns what the model sees.
- Does not know provider type, tools, or reasoning effort.
- Continues to produce deterministic `ContextPackage` records.

`orchestration/` or `model_runtime/orchestration`:

- Owns Hackson-specific mode policy.
- Converts `ContextPackage` plus mode into a model generation request.
- Chooses reasoning effort, max output tokens, temperature, and V1 tool policy.
- Returns normalized assistant text and metadata.

`model_runtime/`:

- Owns provider config and provider wire calls.
- Supports a Responses-style path for OpenAI API.
- Keeps existing OpenAI-compatible chat-completions fallback.
- Does not know idle, companion, or frontend business rules.

`conversations/`:

- Remains the source of truth for messages.
- Stores assistant message metadata from the orchestrator.

## 6. Proposed File Plan

### 6.1 Add Backend Orchestrator Module

Create:

```text
backend/orchestration/
  README.md
  __init__.py
  policies.py
  service.py
  schemas.py
  tests/
    README.md
    test_orchestration_policy.py
    test_orchestration_service.py
```

Reason:

- `model_runtime/` should remain provider-focused.
- Hackson mode policy is product logic, not provider logic.
- A dedicated module makes the boundary visible to future agents.

### 6.2 backend/orchestration/README.md

Document:

- Module goal.
- Responsibility split with `interactions/`, `context/`, and `model_runtime/`.
- V1 policies for `idle`, `companion_1`, and `companion_2`.
- V1 non-goals.

### 6.3 backend/orchestration/schemas.py

Define internal schemas:

- `OrchestrationMode`: `idle`, `companion_1`, `companion_2`, `work`.
- `ReasoningEffort`: `minimal`, `low`, `medium`, `high`.
- `ToolPolicy`: disabled for V1; search reserved for V1.1/V1.2.
- `OrchestrationPolicy`: policy name, reasoning effort, max output tokens, temperature, timeout budget, tool policy.
- `OrchestrationRequest`: context package, mode, user id, conversation id, target agent id.
- `OrchestrationResponse`: text, model name, provider, provider response id, policy name, reasoning effort, metadata.

### 6.4 backend/orchestration/policies.py

Implement deterministic policy selection:

```text
idle -> idle_quality_v1
companion_1 -> companion_join_quality_v1
companion_2 -> companion_chat_quality_v1
work -> fallback_chat_v1
```

Initial policy:

| Mode | Reasoning | Max output | Temperature | Tools |
| --- | --- | --- | --- | --- |
| idle | low | 360 | 0.4 | disabled |
| companion_1 | medium | 520 | 0.45 | disabled |
| companion_2 | medium | 700 | 0.5 | disabled |
| work fallback | medium | 700 | 0.3 | disabled |

Escalation rule:

- V1 may use `medium` for `companion_2` by default.
- V1 should not auto-upgrade to `high` until quality baseline proves the latency/cost tradeoff is worth it.
- `idle` should not use `high` in auto cadence.

### 6.5 backend/orchestration/service.py

Implement:

```text
generate(request)
  -> choose policy
  -> convert context package messages to model runtime request
  -> call model_runtime.generate(...)
  -> return normalized orchestration response
```

The service must not:

- Save messages.
- Build context.
- Call MongoDB.
- Read user secrets.
- Expose raw reasoning content.

### 6.6 Extend backend/model_runtime/schemas.py

Extend `ModelGenerateRequest` and `ModelGenerateResponse` conservatively:

- Request:
  - `reasoning_effort`
  - `tool_policy`
  - `metadata`
  - `use_responses_api`
- Response:
  - `provider_response_id`
  - `reasoning_summary`
  - `tool_events`
  - `raw_metadata`

All new fields should be optional so existing fake clients and chat-completions fallback can keep working.

### 6.7 Extend backend/model_runtime/config_repository.py

Add platform env flags:

- `HACKSON_MODEL_API_MODE`: `chat_completions` or `responses`.
- `HACKSON_MODEL_RESPONSES_ENABLED`: optional boolean override.

Default:

- Keep current behavior unless Responses mode is explicitly enabled or the code path is proven safe in tests.

### 6.8 Add Responses Client Path

Preferred minimal implementation:

- Use existing `httpx` dependency.
- Add `ResponsesClient` or add a second method to provider client.
- Call `/responses` for Responses API mode.
- Extract:
  - output text
  - response id
  - model name if returned
  - reasoning summary if safely available

Fallback behavior:

- If config is chat-completions mode, continue using `OpenAICompatibleClient`.
- If Responses API returns provider/network error, map to `ModelRuntimeError` with the same stable error style.

### 6.9 Update backend/interactions/service.py

Change only the model call seam:

Before:

```text
_generate(package) -> model_runtime.generate(...)
```

After:

```text
_generate(package, mode, user_id, conversation_id, target_agent_id)
  -> orchestrator.generate(...)
```

Save metadata:

- `prompt_hash`
- `token_estimate`
- `model_name`
- `provider`
- `provider_response_id`
- `orchestration_policy`
- `reasoning_effort`
- `tool_policy`

Keep API response shape compatible:

- `agentMessage.content` remains final assistant text.
- `context` can add optional fields only after route response schemas are updated and tests pass.

### 6.10 Dependency Wiring

Update:

- `backend/interactions/routes.py`
- `backend/tasks/routes.py` only if Work path still uses `InteractionService`.
- Unit tests using fake model runtime should shift to fake orchestrator or keep a compatibility adapter.

Do not update frontend in V1 unless the backend response schema adds optional fields that the UI should ignore safely.

## 7. Quality Baseline

Create a small manual evaluation document before coding or as the first implementation commit:

```text
docs/model升级/eval.md
```

Minimum sample set:

`idle`:

- Continue a topic without repeating the last two turns.
- Keep two Agent voices distinct.
- Follow a user-selected topic direction.

`companion_1`:

- User joins an ongoing idle topic and asks a clarifying question.
- Agent answers the user directly while preserving idle context.
- Agent does not talk as if the user never joined.

`companion_2`:

- User asks for architectural advice.
- User asks for creative writing help.
- User asks for a structured plan.

Scoring:

- coherence: 1-5
- mode fit: 1-5
- context use: 1-5
- repetition: 1-5, where 5 means no harmful repetition
- latency note
- cost note when available

V1 release should compare current baseline against orchestrated output using the same prompts.

## 8. Implementation Order

### Loop 0: Documentation And Baseline

1. Confirm `docs/model升级/version.md`.
2. Write this `plan.md`.
3. Write `diary.md`.
4. Add `eval.md` before code changes.

Exit criteria:

- A new developer can identify scope, non-goals, target files, and release gates.

### Loop 1: Pure Orchestration Unit

1. Add `backend/orchestration/README.md`.
2. Add schemas and policies.
3. Add policy tests.
4. Add orchestration service with fake runtime.

Tests:

```text
python -m pytest backend/orchestration/tests
```

Exit criteria:

- Policy selection is deterministic.
- Service converts context package to model request.
- No network calls in tests.

### Loop 2: Runtime Schema And Fallback

1. Extend model runtime schemas with optional fields.
2. Keep current chat-completions tests passing.
3. Add tests proving old fake runtime remains compatible.

Tests:

```text
python -m pytest backend/model_runtime/tests backend/interactions/tests
```

Exit criteria:

- Existing behavior still works without Responses mode.
- No public API break.

### Loop 3: Responses API Non-Streaming Path

1. Add Responses client path.
2. Add response extraction tests with fixture JSON.
3. Add HTTP error mapping tests.
4. Add config tests for API mode selection.

Tests:

```text
python -m pytest backend/model_runtime/tests
```

Exit criteria:

- Responses path can be tested without live API calls.
- Provider response id and text are normalized.
- Provider errors map to stable runtime errors.

### Loop 4: Wire Interactions Through Orchestrator

1. Inject orchestrator into `InteractionService`.
2. Replace direct model runtime call.
3. Preserve current API response shape.
4. Save orchestration metadata on assistant messages.
5. Update interaction tests.

Tests:

```text
python -m pytest backend/interactions/tests
```

Exit criteria:

- `idle`, `companion_1`, and `companion_2` route/service tests pass.
- Rate limit mapping still returns `model_rate_limited`.
- Generic provider failure still returns `model_unavailable`.

### Loop 5: Local App Verification

Run backend test groups:

```text
python -m pytest backend/model_runtime/tests backend/orchestration/tests backend/context/tests backend/interactions/tests
```

Run frontend build if response schema or UI behavior changed:

```text
npm --prefix frontend run build
```

Exit criteria:

- Tests pass locally.
- Frontend build passes if touched.

### Loop 6: Target-Machine Smoke

Rules:

- Do not stop existing services.
- Use a new smoke port.
- Use a separate smoke database.
- Do not write `api.md` until verified.

Smoke checks:

- Register/login.
- Create idle topic.
- Run one idle tick.
- Send one idle user message.
- Join into `companion_1`.
- Continue `companion_1`.
- Create or reuse `companion_2`.
- Send one `companion_2` message.
- Confirm saved metadata includes orchestration policy fields.

Exit criteria:

- Smoke service returns `/health`.
- No existing target service is stopped.
- Verified APIs behave as before from the frontend perspective.
- `api.md` updated only after successful verification.

## 9. Test Matrix

Backend unit:

- `backend/orchestration/tests`
- `backend/model_runtime/tests`
- `backend/context/tests`
- `backend/interactions/tests`

Backend app:

- `backend/tests`

Frontend:

- `npm --prefix frontend run build`
- Browser smoke only if UI changes.

Target:

- New port smoke backend.
- New MongoDB database.
- Public service untouched until explicit promotion approval.

## 10. Rollback Strategy

Code-level rollback:

- Keep chat-completions fallback.
- Keep config flag for API mode.
- Default to current behavior until Responses mode is verified.

Runtime rollback:

- On target smoke failure, stop only the new smoke service.
- Do not touch `hackson-domain-8145.service`.
- Do not touch legacy `8130`.

Product rollback:

- If quality does not improve, keep orchestrator boundary but switch policy to fallback chat-completions mode.
- Use `eval.md` to identify whether failure is context, policy, provider, or prompt.

## 11. Open Decisions Before Coding

These should be resolved before implementation starts:

1. Should V1 default production mode remain chat-completions until target smoke passes? Recommended: yes.
2. Should `companion_2` start with `medium` or `high` reasoning? Recommended: `medium`.
3. Should `idle` ever use web search in V1? Recommended: no.
4. Should `reasoning_summary` be stored in metadata in V1? Recommended: store only if provider returns a safe summary field; never store raw reasoning.
5. Should Work Mode use the orchestrator in V1? Recommended: not as a goal; keep compatibility only if `InteractionService` wiring requires it.

## 12. V1 Done Definition

V1 is done when:

- All three modes use the unified Hackson Orchestrator in backend code.
- Chat-completions fallback still works.
- Responses-style mode is available through platform config.
- Assistant messages store orchestration metadata.
- Existing API response shape remains compatible.
- Backend tests pass.
- Frontend build passes if touched.
- Target-machine smoke passes on a new port and separate database.
- `api.md` and relevant README files are updated after verification.
- `diary.md` records the engineering path and verification result.
