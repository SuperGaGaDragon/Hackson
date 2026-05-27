## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

# Hackson Model Orchestration Version Plan

## 1. Product Direction

The model upgrade should be implemented as a unified Hackson Orchestrator used by `idle`, `companion_1`, and `companion_2`.

The goal is not to expose raw model thinking. The goal is to give each mode a controlled set of model capabilities, policy, budget, tools, memory, and UI events so the final experience moves closer to ChatGPT web quality.

Core principle:

```text
mode request
  -> interactions
  -> context package
  -> Hackson Orchestrator
  -> model_runtime
  -> model text + metadata + events
  -> conversation persistence
  -> frontend rendering
```

The three modes should share the same orchestration pipeline, but not the exact same policy.

## 2. V1: Quality Upgrade

Goal:
- Upgrade output quality for `idle`, `companion_1`, and `companion_2` through one backend orchestration pipeline.
- Keep the frontend and API response shape mostly synchronous at first.
- Prove that unified orchestration improves answer quality before adding streaming UI complexity.

Scope:
- Add a Hackson Orchestrator boundary behind `interactions/`.
- Keep `context/` responsible for prompt inputs.
- Upgrade `model_runtime/` to support a Responses-style provider path while keeping a safe fallback for existing chat-completions behavior.
- Add per-mode orchestration policy:
  - `idle`: low or medium reasoning, low cost, conservative search, no infinite auto-loop spending.
  - `companion_1`: medium reasoning, transition-aware context, optional search if enabled by policy.
  - `companion_2`: medium or high reasoning for complex user turns, closest to normal ChatGPT-like conversation.
- Save model metadata on assistant messages, including model name, prompt hash, token estimate, orchestration policy name, and provider response id when available.

Out of scope:
- Streaming token UI.
- Visible Thinking timeline.
- Web search UI events.
- Citation rendering.
- File tools.
- Code interpreter or sandbox execution.
- Autonomous tool execution.

Release gate:
- Existing backend tests pass.
- Existing frontend build passes.
- Target-machine smoke verifies `idle`, `companion_1`, and `companion_2` still create and save messages correctly.
- Qualitative sample set shows better responses than the current chat-completions baseline.

## 3. V1.1: Experience Upgrade

Goal:
- Add ChatGPT-like interaction feedback without changing the core orchestration contract.

Scope:
- Add streaming support from backend to frontend.
- Render response progress in the UI.
- Render safe product events such as:
  - thinking started
  - reasoning summary available
  - searching
  - citation available
  - completed
  - failed
- Keep raw chain-of-thought hidden.
- Persist tool calls and citations as structured metadata or dedicated records.

Out of scope:
- File analysis.
- Code execution.
- Image generation.
- Long-running autonomous agents.

Release gate:
- Streaming has graceful fallback to synchronous response.
- Rate limits and provider failures stop frontend auto loops.
- No hidden reasoning text is shown.
- Citations, when present, are clickable and tied to model/tool output.

## 4. V1.2: Tool And Memory Upgrade

Goal:
- Let the orchestrator choose from a broader controlled capability menu.

Scope:
- Add policy-controlled web search for modes that need current information.
- Integrate accepted memory cards from the existing memory boundary.
- Add lightweight tool call records for auditability.
- Add search/citation display to relevant frontend surfaces.
- Add policy tests so `work`, `idle`, and companion memory scopes do not pollute each other.

Out of scope:
- Arbitrary shell commands.
- Unreviewed file mutation.
- User-provided API keys.
- Exposing model provider configuration in the frontend.

Release gate:
- Search can be disabled by environment or policy.
- Memory reads are scoped by mode.
- Tool failures degrade to a normal assistant message or a stable API error.

## 5. V2: Full ChatGPT-Like Product Layer

Goal:
- Build a more complete product orchestration layer around model, tools, memory, and UI events.

Scope:
- More advanced routing between fast and deep reasoning policies.
- Better automatic web-search decisions.
- Richer memory read/write workflow with evidence.
- File analysis if product needs it.
- Stronger event timeline and citation UX.
- Evaluation set for answer quality, latency, cost, and mode identity.

Out of scope until explicitly approved:
- Full autonomous tool execution.
- Production deploy actions from the model.
- User-owned model endpoints, provider keys, or local model paths.

Release gate:
- Product quality, cost, latency, and safety are measurable before further tool expansion.
