## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 19: Lead And Delegate Timeout Budget

## Problem
Public Work testing showed a Mission with a valid final Product could still look stuck because the Lead Agent was waiting inside a model turn after `inspect_product`.

The root product problem is not only provider timeout length. It is that different Work Mode roles have different latency expectations:

- Lead Agent turns select the next tool and should return quickly.
- Delegate Agent turns may write long prose and need a larger generation budget.
- Search/tool provider calls need their own small bounded timeout.

Using one global model timeout for all of these roles makes a Lead planning/selection turn wait as long as a long writing turn. That is not a product-grade experience.

## Decision
Work Mode V1 must support per-request model timeout overrides.

Required defaults:

- Lead Agent tool-selection timeout: `180` seconds.
- Delegate Agent one-shot work timeout: `900` seconds.
- Search provider timeout remains `10` seconds.
- Global model runtime timeout remains the fallback when no role-specific override is passed.

The timeout split is a scheduling budget, not a workflow decision. The model still chooses tools. The backend only constrains how long each role may block the runtime.

## Product Rules
- Production timeouts MUST remain finite.
- A Lead timeout MUST become `paused_retryable` after bounded retry budget is exhausted.
- Delegate timeout after a visible Work Window opens MUST mark that window failed before the Mission pauses retryably.
- Finished Products and Artifacts MUST remain readable after timeout or restart.
- This patch MUST NOT expose raw model tokens or hidden reasoning.

## Environment Contract
- `HACKSON_WORK_MODE_V1_LEAD_TIMEOUT_SECONDS` controls Lead tool-selection model calls.
- `HACKSON_WORK_MODE_V1_DELEGATE_TIMEOUT_SECONDS` controls Delegate model calls.
- `HACKSON_WORK_MODE_V1_SEARCH_TIMEOUT_SECONDS` controls backend Web Search provider calls.

Invalid or non-positive timeout env values fall back to defaults.

## Non-Goals
- Do not remove heartbeats.
- Do not implement streaming in this issue.
- Do not switch to provider-native tool calling.
- Do not hard-code novel-writing steps.

## Acceptance
- Unit tests prove request-level timeout overrides reach the Codex CLI provider.
- Unit tests prove request-level timeout overrides reach OpenAI-compatible and Responses providers.
- Unit tests prove `ToolActionClient` passes the Lead timeout override.
- Unit tests prove `DelegateResultClient` passes the Delegate timeout override.
- Target-machine tests pass for `model_runtime` and `work_mode`.
- Public runtime shows a Lead turn can pause retryably inside the Lead timeout budget rather than waiting for the long Delegate budget.

