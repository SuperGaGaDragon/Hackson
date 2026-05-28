## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 25: Model Context Must Be JSON-Safe

## Problem

Public logs showed a Work worker thread crashing inside `json.dumps(context)`:

```text
TypeError: Object of type datetime is not JSON serializable
```

The failing path was `discuss_with_delegate`. Its context included public Mission/Product/Artifact data that still contained Mongo/Python runtime objects such as `datetime`.

This is a model-adapter boundary bug. Tool executors should not have to know every persistence type that might appear in context.

## Decision

All Work Mode model-call adapters MUST serialize context through one JSON-safe helper before constructing `ModelGenerateRequest`.

Required conversions:

- `datetime` and `date` -> ISO 8601 string.
- Mongo/ObjectId-like values -> string.
- Nested dict/list/tuple/set values -> recursively normalized through `json.dumps`.

If serialization still fails, the adapter MUST raise `ToolActionClientError("model_context_serialization_error")` instead of letting the worker thread crash.

## Acceptance

- Lead and Delegate request builders accept contexts containing `datetime`.
- Delegate/discussion model calls no longer crash the worker on JSON serialization.
- Existing Action/Delegate tests pass.
- Target-machine Work Mode tests pass before deployment.
