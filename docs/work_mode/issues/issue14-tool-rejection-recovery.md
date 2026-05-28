## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 14: Tool Rejection Recovery

## Problem

Target-machine real-model smoke exposed a recovery gap.

The Lead can call a syntactically valid tool with semantically invalid references or quality state. Example:

- `finish_mission` references existing outline/chapter/review Artifacts.
- Deterministic long-novel gate rejects the call because no `final` Artifact exists.
- The rejection is a correct backend decision, but the Mission loop must not crash or stay `running` without progress.

## Decision

Tool execution rejections caused by public tool contract validation are model-correctable invalid turns.

The Mission loop MUST:

- Catch FastAPI `HTTPException` raised by tool execution.
- Emit `MODEL_TURN_INVALID` with `phase=tool_execution`, `tool`, `statusCode`, and stable error code.
- Return a bounded `lastObservation` to the Lead.
- Continue the loop until the invalid-turn budget is exhausted.
- Mark the Mission `paused_retryable` after repeated invalid tool turns exceed the configured budget, because a
  resumed Run may recover with a fresh model turn and the persisted checkpoint.

The Mission loop MUST NOT:

- Mark `failed` for deterministic contract rejections unless an actual system invariant is broken.
- Leave a Mission stuck in `running` after the background runner exits.
- Treat a quality gate rejection as a provider failure.

## Long-Novel Recovery Instruction

For these deterministic quality errors:

- `final_artifact_required`
- `final_artifact_not_in_final_product`
- `final_artifact_not_final_content`
- `final_artifact_cjk_too_short`
- `missing_outline_artifact`
- `missing_chapter_artifact`

The Lead observation MUST tell the model to repair Product state before finishing.

Preferred recovery:

1. Use `work_product`.
2. Reference the same Product.
3. Create or revise an Artifact with `artifactKind="final"`.
4. Include the complete final manuscript content, not only an outline or chapter.
5. Call `finish_mission` again with that final Artifact id.

## Acceptance

- A scripted long-novel Mission that first calls invalid `finish_mission` can recover by creating a valid final Artifact and then finish.
- The Progress timeline includes the rejected tool as a visible invalid turn.
- `MODEL_TURN_INVALID` is part of the public API event response schema, so polling events never returns 500 for a visible recovery event.
- The Mission never remains `running` after a deterministic tool rejection if the runner exits.
- Target-machine full browser smoke can wait for real long generation without masking deterministic rejections.
