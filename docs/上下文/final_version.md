## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-29
Lst Modified by: Codex

# Context Runtime Final Version Roadmap

## 1. Legacy Notice

Everything under `docs/上下文/legacy/` is archived.

The archived research, requirements, and V1 slice documents are historical reference only. They MUST NOT be used as the execution source for new Context Runtime implementation.

The active execution source is this document plus:

- `architecture.md`
- `state_machine.md`
- `context_package.md`
- `ui_contract.md`
- `implementation_plan.md`
- linked documents under `issues/`

Current issue notes:

- `issues/issue1-context-package-storage.md`
- `issues/issue2-full-prompt-logging.md`
- `issues/issue3-background-idle-budget.md`
- `issues/issue4-companion1-memory-scope.md`
- `issues/issue6-idle-interruption-queue.md`
- `issues/issue7-idle-human-relationship-dialogue.md`
- `issues/issue11-account-agent-continuity.md`
- `issues/issue12-idle-collaborative-convergence.md`
- `issues/issue14-idle-brainstorm-to-work-mission.md`

## 2. Product North Star

Context Runtime makes Hackson feel like a living two-Agent world instead of a set of disconnected chat boxes.

Every model turn must be built from explicit, auditable materials: current mode, user intent, Agent identity, visible recent history, compact summaries, governed memory, and runtime policy. The backend decides what the model can see. The model writes visible turns or structured derived candidates. Raw messages remain the source of truth.

Core loop:

```text
User action or idle cadence
  -> load conversation state
  -> select current mode and target Agent
  -> build auditable context package
  -> generate one model result
  -> persist visible message or derived candidate
  -> enqueue background derivation
  -> expose debug and user-facing state
```

## 3. Hard Product Constraints

- Raw Message records are the historical source of truth.
- Topic direction MUST be steering metadata, not a fake user message.
- Context Package construction MUST be deterministic for the same inputs.
- Context Package records MUST be auditable by prompt hash, included source ids, and budget decisions.
- Full prompt text MAY be stored only through user-controlled Full Prompt Logging.
- Account memory MUST be available across Idle, Companion, and Work because Nora and Vale are account-level Agents.
- Mode-private memory and raw Work trace MUST stay isolated unless a governed worker promotes it into account memory.
- User facts and preferences MUST require user-authored evidence before becoming long-term memory.
- Agent core persona MUST NOT be overwritten by model output.
- Default Agent Origin Stories SHOULD be detailed editable profile material, not transient demo status lines.
- Raw Work Mode task trace MUST NOT enter Idle or Companion prompts by default.
- Idle Auto MUST have stable failure behavior and MUST NOT loop provider failures.
- Idle input MUST stay available during generation by queueing Idle Interruption.
- Idle Agents MUST respond as a relationship-aware pair, not as alternating advice generators.
- Idle Agents MUST use Collaborative Convergence Protocol so disagreement stops when it no longer changes action, risk, or decision criteria.
- Raw chain-of-thought MUST NOT be stored or shown.

## 4. Version Summary

| Version | Name | Product Result | Runtime Result | Release Gate |
| --- | --- | --- | --- | --- |
| V1.0 | Auditable Context Package | Idle, Say, Join, and Companion turns expose traceable context inputs. | Persisted context package records, deterministic recipe metadata, token budget notes. | A failed or bad turn can be reproduced from persisted context package metadata and source ids. |
| V1.1 | Server-Owned Idle Cadence | Idle can run with backend-owned cadence, locks, budget, retry state, and user-controlled Background Idle. | Idle runner state, Background Idle setting, per-conversation turn lock, idempotent tick requests. | Multi-tab and retry smoke cannot create duplicate next turns; browser-closed generation happens only when enabled. |
| V1.2 | Persisted Summary Runtime | Long conversations use rebuildable persisted summaries instead of only synchronous compact snippets. | Summary worker runner, source ranges, summary selection policy. | Idle over 50 turns keeps latest raw turns and old material through persisted summary. |
| V1.3 | Governed Memory Runtime | User preferences, relationship summaries, account memory, and mode-private memory become usable and controllable. | Memory worker runner, memory governance, account-continuity retrieval, user-visible memory controls. | A user-authored preference becomes account memory with evidence and can be disabled or deleted. |
| V1.4 | Relationship And Diary Layer | Idle produces durable Agent relationship state and user-visible diary artifacts without destabilizing chat. | Relationship worker, diary worker, evidence references, low-priority background jobs. | Idle relationship memory improves continuity but cannot rewrite core persona. |
| V1.5 | Context Evaluation Gate | Context changes are scored before release. | Fixed eval set for mode fit, speaker boundary, topic adherence, repetition, memory use, latency. | CI or smoke command reports pass/fail against the fixed context eval set. |
| V1.6 | Human Idle Interaction | User can interrupt while Agents generate, and Idle replies use relationship-aware turn intent plus convergence rules. | Idle Say lock/idempotency, queued interjection UI, relationship stance, turn intent, collaborative convergence, anti-advice eval. | User input during generation is accepted and the next turn responds to it; eval catches advice-list and endless-disagreement regressions. |
| V1.7 | Idle Brainstorm To Mission | Idle can turn visible discussion into an editable Brainstorm Card and user-confirmed draft Work Mission. | Deterministic Idle card endpoint with source message ids; frontend promotion flow through existing Work Mission API. | A user can build a card, edit title/goal, choose or create a Project, and create a draft Mission with Idle source provenance. |

## 5. V1.0 Auditable Context Package

V1.0 proves that every model-backed product turn can be explained.

Decision:

- V1.0 release gate is Auditable Context Package.
- V1.0 is not Server-Owned Idle Cadence.
- V1.0 is not Governed Memory Runtime.
- Server cadence and memory follow only after context can be reproduced and diagnosed.

Required surfaces:

- Idle Tick.
- Idle Say.
- Idle Join into Companion 1.
- Companion 1 follow-up.
- Companion 2 message.

Required backend result:

- A `context_packages` record or equivalent persistence boundary.
- Prompt hash.
- Mode.
- Conversation id.
- Target Agent id.
- Included message ids.
- Included summary ids.
- Included memory ids.
- Included Agent ids.
- Token estimate and budget policy.
- Recipe version.
- Safe debug notes.
- Optional full prompt text when the user enables Full Prompt Logging.

Prompt storage decision:

- V1.0 supports Full Prompt Logging.
- Full Prompt Logging stores complete model-visible prompt text.
- Full Prompt Logging must be user-controlled.
- Full Prompt Logging defaults on for new users to support early product debugging.
- Users must be able to turn Full Prompt Logging off before later packages are created.
- Full prompt text is retained for 30 days by default.
- Turning Full Prompt Logging off does not delete existing full prompt text.
- Users need a separate Delete Prompt Logs action that removes retained full prompt text while keeping package metadata.
- Me is the user-facing control surface for viewing the setting and managing retained prompt logs.
- Users can edit profile, Agent profiles, and Full Prompt Logging setting in Me.
- Users can view and delete retained full prompt text in Me, but they cannot edit historical prompt text.
- Auditable Context Package metadata is still stored even when Full Prompt Logging is disabled.
- Internal operators need enough persisted information to reproduce context and diagnose poor outputs without relying solely on full prompt text.

See `issues/issue1-context-package-storage.md` and `issues/issue2-full-prompt-logging.md`.

## 6. V1.1 Server-Owned Idle Cadence

Idle Auto cannot remain only a browser timer if the product promise is a living world.

Decision:

- Background Idle defaults off.
- Active browser sessions may use server-owned cadence.
- Browser-closed generation requires Background Idle enabled by the user.

V1.1 introduces backend-owned runner state:

- idle runner enabled or disabled.
- Background Idle user setting.
- cadence interval.
- last scheduled turn.
- next eligible turn.
- failure cooldown.
- daily or session budget.
- per-conversation turn lock.

Frontend remains the control surface. Backend owns truth for whether the next turn is allowed. Browser-closed idle generation is allowed only when the user enables Background Idle and the server budget/cooldown policy allows it.

See `issues/issue3-background-idle-budget.md`.

## 7. V1.2 Persisted Summary Runtime

Summary is a derived layer, not a replacement for raw messages.

Required rules:

- Summary records reference source message ranges.
- Summary worker failures never break chat.
- Context recipes include latest relevant summary plus raw recent messages.
- Synchronous compact snippets may remain as fallback only.
- Summary text must preserve speaker boundaries.

## 8. V1.3 Governed Memory Runtime

Memory must be useful and user-governed.

Decision:

- V1.0 does not need user-facing Memory Control.
- V1.3 must ship Memory Control before governed memory is treated as a public product feature.
- Nora and Vale use Account Agent Continuity: account memory enters Idle, Companion, and Work.
- Legacy Companion user memories and Idle relationship memories remain readable as account-continuity input until migrated.
- Raw Work trace and task-private memory stay out of Idle and Companion until promoted into account memory.

See `issues/issue4-companion1-memory-scope.md` and `issues/issue11-account-agent-continuity.md`.

Allowed first memory types:

- user preference.
- user fact.
- Agent-user interaction summary.
- Agent-Agent relationship summary.

Required controls:

- list memory.
- disable memory.
- delete memory.
- show evidence source ids internally.
- keep raw Work trace and task-private memory out of Companion and Idle by default.

## 9. Latency Targets

V1 targets are product budgets, not hard infrastructure guarantees:

| Flow | Target | Notes |
| --- | --- | --- |
| Idle Tick | p50 under 6s, p95 under 20s | Auto must stop or cooldown on provider failure. |
| Idle Say | p50 under 8s, p95 under 25s | User sees pending line only after generation strategy is safe. |
| Idle Join to Companion 1 | p50 under 10s, p95 under 30s | Transition quality matters more than raw speed. |
| Companion 1 follow-up | p50 under 8s, p95 under 25s | Uses child history plus bounded parent background. |
| Companion 2 | p50 under 8s, p95 under 25s | Similar to high-quality direct chat. |

## 10. V1.6 Human Idle Interaction

The product should feel like the user is near two people who can be interrupted.

Required behavior:

- Composer remains enabled while Idle Tick is generating.
- A user line sent during generation becomes a visible pending Idle Interruption.
- The current Agent reply may complete, but the queued interjection is sent immediately after.
- Backend serializes Idle Say with the same transcript lock used by Idle Tick.
- Idle Say supports idempotency keys.
- Idle prompt includes Relationship Stance and Turn Intent.
- Idle prompt includes Collaborative Convergence Protocol.
- Idle prompt forbids stacked frameworks, repeated exercises, and generic advice lists unless the user explicitly asks.

See `issues/issue6-idle-interruption-queue.md`, `issues/issue7-idle-human-relationship-dialogue.md`, and `issues/issue12-idle-collaborative-convergence.md`.

## 11. V1.7 Idle Brainstorm To Mission

Idle should not end as a loose transcript when the discussion has become actionable.

Decision:

- Add an Idle Brainstorm Card that is separate from context summaries.
- Build the first card from visible raw Idle messages, not hidden prompt material.
- Require source message ids for traceability.
- Treat the suggested Mission as editable draft material.
- Let the user choose an existing Work Project or create a new one before promotion.
- Create a draft Work Mission through the existing Work API.
- Store Idle provenance in Mission metadata.

See `issues/issue14-idle-brainstorm-to-work-mission.md`.

## 12. Implementation Decisions

- `ContextRuntime` is a facade around existing `ContextBuilder`, source loaders, package persistence, and budget policy.
- `context_packages` should be an independent persistence collection, not embedded only in message metadata.
- Assistant message metadata stores `context_package_id`, `prompt_hash`, and safe model metadata.
- Full prompt text is stored in the context package record only when Full Prompt Logging is enabled.
- V1.0 can ship prompt log view/delete in Me; Memory Control waits until V1.3.
- V1.6 treats interruption as queued user intent instead of provider cancellation.

## 12. 代办

- Execute `implementation_plan.md` Loop 1 before starting cadence or memory work.
- Add issue notes when implementation reveals a new architectural risk.
