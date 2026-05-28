## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 8: Delegate Result Tolerance

## Problem

Public Codex-backed Work Mode Mission `6a17a659f01aad81f13bca8a` proved the Lead loop can plan, create a Product, and open sequential Delegate windows. The first two windows completed. The third window failed with `delegate_result_invalid`, which marked the Mission `failed`.

This is not product-level behavior for long writing Missions. A Delegate window is a scoped writing call. If it returns useful prose but misses the strict JSON wrapper, the system should persist that prose as the window Artifact instead of discarding the work.

## Decision

V1.0 keeps the Lead Agent strict:

- Lead turns MUST return one JSON tool action.
- Plain Lead text is still invalid.
- The backend still owns tool schemas and validation.

V1.0 makes Delegate result ingestion tolerant:

- Valid structured Delegate JSON remains the preferred result.
- JSON inside a markdown fence may be parsed.
- JSON embedded in surrounding text may be parsed.
- A non-empty unstructured prose result MAY be canonicalized into a completed Delegate Artifact.
- Empty results or broken JSON-like results remain invalid.
- Invalid Delegate structured results are retryable and should pause as `paused_retryable` after the failed Work Window is visible.

## Product Rule

Do not throw away user-visible long-form writing just because the child writer missed a wrapper format.

The user should see one of:

- a completed Work Window with the returned content saved as an Artifact, or
- a failed Work Window followed by `paused_retryable`, preserving prior Products and windows.

The Mission should not jump straight to unrecoverable `failed` for a recoverable Delegate wrapper failure.

## Acceptance

- Delegate plain prose completes the Work Window and creates a Product Artifact.
- Delegate fenced JSON completes the Work Window and creates a Product Artifact.
- Broken JSON-like Delegate output marks the window failed and pauses retryably.
- Existing full V1 deterministic smoke still passes.
- Public real-model smoke no longer fails solely because a Delegate writes prose instead of exact JSON.

## Follow-Up

V1.1 native tool calling should reduce wrapper misses, but tolerant ingestion must remain as a fallback because provider adapters and long-form generation can still return text under stress.
