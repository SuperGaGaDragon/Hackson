## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 31: Discussion Result Tolerance And Schema Feedback

## Problem

Public Work Mode testing showed a long research Mission reaching review, then failing after:

- `DISCUSSION_WINDOW_FAILED` with `discussion_result_invalid`.
- repeated Lead `MODEL_TURN_INVALID` events with `tool_action_schema_invalid`.
- terminal `mission_loop_turn_budget_exceeded`.

This is bad product behavior. A Delegate Discussion is a read-only cognition tool. If the child Agent returns useful advice but misses one JSON wrapper field, the system should preserve that advice as a Discussion Artifact instead of converting the Mission into a dead end.

The second problem is observability. `tool_action_schema_invalid` currently hides the exact schema failure from both the Lead observation and the UI. The Lead only sees a generic invalid code, making repeated invalid turns more likely.

## Production Evidence

Confirmed on public `8145` before rollout:

- Mission `6a1873a07930f43553a9031a` (`写一个关于美国独立的文献综述`) produced `DISCUSSION_WINDOW_FAILED` at event `#143` and paused retryably with `discussion_result_invalid` at event `#144`.
- After restart, the same Mission continued through delegate and review work, but events `#187`, `#189`, `#191`, `#199`, `#201`, and `#203` were only `tool_action_schema_invalid` without bounded field detail.
- The Mission exhausted invalid turns and failed with `tool_action_schema_invalid` at event `#204`.
- The latest Review Artifact explicitly recommended `work_product`; therefore the next correct recovery was not a hard failure but a schema-correct `work_product` call producing a single final draft.

Root cause: the protocol gave the Lead no actionable schema repair information, and the Discussion result parser treated recoverable delegate output shape drift as fatal.

## Decision

Keep Lead tool calls strict:

- Lead turns MUST still return exactly one valid JSON Action.
- Unknown tools, plain text, multiple actions, and invalid tool schemas remain invalid.
- Backend validation remains authoritative.

Make Discussion result ingestion tolerant:

- Valid structured Discussion JSON remains preferred.
- Fenced or embedded JSON remains parseable.
- Dict-shaped Discussion results with useful `summary`, `recommendation`, `content`, `text`, `result`, `output`, or transcript text MAY be coerced into a completed Discussion Result.
- Non-empty unstructured text MAY be canonicalized into a completed Discussion Artifact.
- Empty output remains invalid.
- Broken JSON-like output with no salvageable text remains invalid.

Improve schema feedback:

- `ToolActionValidationError` SHOULD include a bounded detail string.
- `MODEL_TURN_INVALID` payload SHOULD include that detail when available.
- The next Lead observation SHOULD explain the invalid field/category, not only the generic code.

## Constraints

- Do not silently complete when the child Agent returned empty output.
- Do not let Discussion mutate Product content.
- Do not relax Lead JSON Action schema.
- Do not dump full Pydantic internals or long model output into Progress.
- Keep user-facing rows compact; details belong in expanded Progress or Diagnostics.

## Acceptance

- A Discussion result with only `summary` and `recommendation` completes the Discussion Window and creates a Discussion Artifact.
- A plain-text Discussion result completes the Discussion Window and creates a Discussion Artifact.
- Empty Discussion output still fails visibly and pauses retryably.
- Lead schema invalid events include bounded detail.
- Work Mode tests cover tolerant Discussion ingestion and schema feedback.

## Rollout Guard

- Do not restart public `hackson-domain-8145.service` while a Work Mission is `running` or a Work Window is `running`.
- Validate the same code on isolated `8165` first.
- After public restart, check logs for `discussion_result_invalid`, `tool_action_schema_invalid`, traceback, and 500s using only post-restart log windows.
