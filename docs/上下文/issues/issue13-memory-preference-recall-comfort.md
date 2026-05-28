## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 13: Memory Preference Recall Comfort

## Problem

A user can explicitly ask an Agent to remember an interaction preference, receive a natural confirmation, then open a fresh Companion conversation and get a cold-start answer. In the public product audit, the phrase `请记住：我做产品时喜欢你直接指出不舒服的点，不要先安慰我。` produced a succeeded `memory_candidate` job but no memory card, because the extractor only recognized a narrow set of markers such as `我喜欢`, `我偏好`, and `I prefer`.

This breaks the product promise that Nora and Vale become more familiar with the user over time.

## Self Grill

Question: Is the backend worker down?

Recommended answer: No. Public Mongo showed the memory candidate jobs as `succeeded`; the failure is semantic extraction, not job execution.

Question: Should every user sentence become memory?

Recommended answer: No. Memory must remain evidence-backed and conservative. The fix should only widen explicit preference forms, especially `请记住`, `记住`, `我不喜欢`, `不要`, and product-feedback preference sentences that users clearly author.

Question: Should recall wait for a long asynchronous worker window?

Recommended answer: Not for core product comfort. The background worker can stay async, but the extractor must at least persist obvious preferences when its job runs. A later improvement can add synchronous fast-lane memory for explicit `remember this` commands.

## Decision

Expand MemoryWorker's explicit preference detector to recognize:

- positive preferences: `我喜欢`, `我偏好`, `我更喜欢`, `I like`, `I prefer`.
- negative preferences: `我不喜欢`, `别`, `不要`, `don't`, `do not`.
- explicit memory commands: `请记住`, `记住`, `remember`, `please remember`.
- feedback-style preference lines where the user asks the Agent to respond in a particular way.

The resulting memory remains `scope=account`, `owner_type=user`, and `memory_type=preference`, with the original user message as source evidence.

## Required Tests

- MemoryWorker accepts `请记住：我做产品时喜欢你直接指出不舒服的点，不要先安慰我。`
- MemoryWorker accepts negative preference wording such as `我不喜欢空泛安慰。`
- MemoryWorker does not accept ordinary non-preference user chat.
- Public user-perspective API smoke must verify a fresh Companion conversation recalls the preference.

## Exit Criteria

When a user explicitly tells an Agent how they prefer feedback, a later conversation can recall that preference without sounding like a cold start.
