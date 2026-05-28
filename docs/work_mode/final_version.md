## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Work Mode Final Version Roadmap

## 1. Legacy Notice

Everything under `docs/work_mode/legacy/` is archived.

The archived V0 and V0.5 documents are historical reference only. They MUST NOT be used as the execution source for new Work Mode implementation.

The active execution source is this document plus:

- `architecture.md`
- `tool_protocol.md`
- `state_machine.md`
- `context_design.md`
- `ui_contract.md`
- `implementation_plan.md`
- linked documents under `issues/`

## 2. Product North Star

Work Mode is a model-driven Mission Runtime.

The user creates a Mission. A Lead Agent drives the Mission. The Lead Agent sees available tools, chooses exactly one tool per model turn, observes the tool result, and continues until the Mission is completed, blocked, stopped, failed, or paused for retry.

The backend does not hard-code the Mission workflow. The backend owns tool schemas, validation, persistence, budgets, permissions, and UI event contracts.

The frontend does not render model-generated React. It renders persisted events, work windows, Products, and Artifacts using fixed React components.

Core loop:

```text
Mission goal
  -> Lead Agent model turn
  -> one validated tool call
  -> backend executes tool
  -> event/product/artifact/window is persisted
  -> observation returns to Lead Agent
  -> repeat
```

## 3. Hard Product Constraints

- The model MUST choose a tool every turn.
- Plain assistant text MUST be rejected as an invalid model turn.
- Natural language output MUST appear only inside tool arguments.
- The model MUST NOT define new tools.
- The model MUST NOT emit React components.
- The model MUST NOT execute shell, file, browser, Codex CLI, or computer-control tools in V1.0.
- The backend MUST validate tool schema before execution.
- The backend MUST persist the tool result before the next model turn.
- V1.0 MUST use one tool call per Lead model turn.
- V1.0 child work windows MUST run sequentially, not in parallel.
- V1.0 full product acceptance MUST include the full 8000 CJK character novel smoke.

## 4. Version Summary

| Version | Name | Product Result | Runtime Result | Release Gate |
| --- | --- | --- | --- | --- |
| V1.0 | Pure API Text Mission Loop | The user can ask for a long-form text Mission, such as an 8000-character Chinese novel, and watch the Lead Agent plan, delegate, inspect, produce Products, and finish. | Provider-agnostic JSON Action protocol, one tool per turn, sequential delegate windows, Product + Artifact lineage, no computer tools. | Full 8000 CJK character novel smoke completes with visible windows and final Product. |
| V1.1 | Native Tool Calling Adapter | Same product behavior with provider-native tool calls where available. | Backend tool schema stays stable; native tool calling adapter is added; JSON Action remains fallback. | Same full smoke passes through native tool calling and JSON fallback. |
| V1.2 | Streaming Progress | Users see model/tool progress before each turn fully completes. | Streaming is added without changing the tool contract. | Streaming has polling fallback and does not expose raw chain-of-thought. |
| V1.3 | Parallel Window Runtime | Lead can create multiple windows and the runtime can execute them in parallel when policy allows. | Window scheduler, partial failure handling, per-window budgets, and resume semantics. | Parallel smoke creates multiple windows and completes deterministically. |
| V1.5 | Read-Only Computer Context | The Lead can inspect approved repo/file context without mutation. | `search_files` and `read_file` style tools under read-only sandbox and strict scope. | Read-only tools cannot access secrets or paths outside approved workspace. |
| V2.0 | Codex CLI Controlled Execution | Work Mode can perform code-oriented Missions through controlled Codex/computer tools. | Codex CLI or equivalent executor runs under workspace sandbox, approval policy, diff/test capture, and event persistence. | Code Mission produces diff summary, tests, approval cards, and final report without bypassing gates. |
| V2.5 | Approval And Apply | User can approve, apply, discard, or retry changes. | Write actions require approval where policy demands it; rollback/discard are product flows. | Dangerous actions never run without explicit approval. |
| V3.0 | Multi-Agent Mission Runtime | User can configure more worker roles beyond the two account Agents. | Agent roster, reviewer/editor roles, project-scoped memory, and richer delegation. | Custom roles cannot bypass the same tool validation and permission system. |

## 5. V1.0 Pure API Text Mission Loop

### 5.1 Goal

V1.0 proves the core agentic Work Mode loop without touching the computer.

The first product task is writing. The canonical release smoke is:

```text
Title: 写一个8000字小说
Goal: 写一个8000字中文小说，题材自定，要求分章节，有大纲，有最终成稿。
Lead: agent_1
Delegate: agent_2
```

The Lead Agent should decide whether to plan, delegate chapter drafts, inspect prior Products, produce final text, or finish. The backend MUST NOT hard-code the order.

### 5.2 V1.0 Toolbox

V1.0 model-visible tools:

- `mission_plan`
- `work_product`
- `inspect_product`
- `delegate_agent`
- `ask_user`
- `finish_mission`
- `block_mission`

V1.0 backend-internal tools:

- `load_mission_state`
- `validate_tool_call`
- `persist_event`
- `persist_product`
- `persist_artifact`
- `persist_work_window`
- `enforce_budget`
- `resume_from_observation`

Backend-internal tools MUST NOT be shown to the model as available tools.

### 5.3 Agent Roles

V1.0 uses only the authenticated user's two editable Agent profiles:

- Mission Lead MUST be `agent_1` or `agent_2`.
- Delegate target MUST be the non-lead Agent.
- The Lead MAY call the same delegate Agent multiple times.
- Each `delegate_agent` call MUST create a new visible work window.
- Delegate windows MUST run sequentially in V1.0.
- Delegate windows MUST NOT finish the Mission.
- Delegate windows MUST NOT delegate recursively.
- Delegate windows MUST execute exactly one structured model call in V1.0.

### 5.4 Product And Artifact Lineage

V1.0 introduces a logical Product layer.

- A Mission MAY contain multiple Products.
- A Product is the user-visible logical deliverable.
- An Artifact is one immutable output, version, chapter, section, inspection result, or candidate under a Product.
- `work_product` MAY create a new Product or append an Artifact to an existing Product.
- V1.0 MUST NOT overwrite prior Artifacts.
- `finish_mission` MUST reference at least one existing final Product id.
- `finish_mission` SHOULD reference final Artifact ids when available.

Implementation MAY store Product identity in `work_artifacts.metadata.productId` for the first iteration, but the public contract MUST still speak in Product + Artifact terms.

## 6. Runtime Choice

V1.0 target runtime SHOULD be the normal API model runtime, not Codex CLI.

V1.0 MUST remain provider-agnostic by using the JSON Action protocol first.

Codex CLI MAY be used as a temporary provider fallback if the API provider is not stable, but Codex CLI is not the V1.0 product target. Codex CLI belongs naturally in V2.0 computer-control execution.

V1.1 MUST implement provider-native tool calling where available, while preserving the same backend tool schema and JSON Action fallback.

See `issues/issue1-native-tool-calling.md`.

## 7. Context Strategy

V1.0 context MUST include:

- Mission goal.
- Lead Agent profile.
- Available tools and schemas.
- Current Mission status.
- Product manifest.
- Recent events.
- Last tool observation.
- Recent Artifact content within budget.

V1.0 context MUST NOT blindly include every Artifact full text once total content exceeds budget.

Lead Agent can use `inspect_product` to retrieve bounded Product or Artifact content.

See `context_design.md` and `issues/issue2-context-budget.md`.

## 8. UI Strategy

The UI MUST show the process, not only the final result.

V1.0 UI surfaces:

- Current Activity.
- Work Windows.
- Product Panel.
- Mission Progress.
- Diagnostics.
- Control Panel.

The Mission Console MUST render Work Windows and Product before the Progress audit trail. Large text events MUST be collapsed by default. Users MUST be able to expand Work Windows and Diagnostics. The Product Panel is the canonical full-content reading surface and MUST expose Artifact lineage instead of only the latest Artifact.

See `ui_contract.md`, `issues/issue3-delegate-window.md`, and `issues/issue9-work-ui-information-architecture.md`.

## 9. Failure And Resume Strategy

V1.0 distinguishes:

- `waiting_input`: model asked the user a question.
- `paused_retryable`: provider timeout, rate limit, or transient runtime failure.
- `blocked`: model intentionally called `block_mission`.
- `failed`: runtime/system failure or repeated invalid model turns.
- `stopped`: user explicitly stopped the Mission.
- `completed`: model called `finish_mission` and backend validation passed.

Transient provider failures MUST NOT destroy Mission progress.

See `state_machine.md` and `issues/issue4-retry-resume.md`.

## 10. Streaming Strategy

V1.0 MUST NOT require streaming.

V1.0 UI uses Mission event polling. A model turn becomes visible only after a validated tool action is persisted.

V1.2 adds streaming progress without changing the tool protocol.

See `issues/issue5-streaming.md`.

## 11. Acceptance Smoke

The V1.0 release gate is the full 8000 CJK character novel smoke. A fast smoke MAY exist for local debugging, but MUST NOT replace the full smoke.

The full smoke MUST verify:

- Mission completes.
- Lead calls `mission_plan` at least once.
- Lead calls `delegate_agent` at least twice.
- Delegate windows are visible and expandable.
- At least one Product exists.
- At least three Artifacts exist.
- `finish_mission` references a final Product.
- Final Artifact CJK character count is at least 8000.
- Final Artifact is not only an outline.
- UI shows timeline, windows, Product, and terminal status.

See `issues/issue6-full-smoke.md`.

## 12. Implementation Source Order

Engineers MUST read these documents in order:

1. `README.md`
2. `final_version.md`
3. `architecture.md`
4. `tool_protocol.md`
5. `state_machine.md`
6. `context_design.md`
7. `ui_contract.md`
8. `implementation_plan.md`
9. linked `issues/*.md`

Legacy documents are optional history only.

## 13. Open Risks

Known risks:

- Native tool calling migration: `issues/issue1-native-tool-calling.md`
- Context budget and artifact retrieval: `issues/issue2-context-budget.md`
- Delegate window visibility and state: `issues/issue3-delegate-window.md`
- Retry/resume behavior: `issues/issue4-retry-resume.md`
- Streaming later without breaking tool contract: `issues/issue5-streaming.md`
- Full smoke cost, duration, and deterministic validation: `issues/issue6-full-smoke.md`
- Long model turn progress and timeout UX: `issues/issue7-long-turn-progress.md`
- Delegate result tolerance after real-model wrapper misses: `issues/issue8-delegate-result-tolerance.md`
- Work UI hierarchy, Product lineage, and diagnostics clarity: `issues/issue9-work-ui-information-architecture.md`
