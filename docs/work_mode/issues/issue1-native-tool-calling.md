## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

# Issue 1: Native Tool Calling Migration

## Problem

The final Work Mode direction requires provider-native tool calling. V1.0 should not block on a specific provider format, because the product loop must be proven first.

## Decision

V1.0 MUST use provider-agnostic JSON Action.

V1.1 MUST add provider-native tool calling adapter while preserving:

- Same backend tool schemas.
- Same ToolExecutor.
- Same UI event contract.
- JSON Action fallback.

## Risks

- JSON output can be malformed.
- Native providers expose different tool call formats.
- Streaming native tool calls can arrive partially.
- Provider relay may not support tool calling consistently.

## Constraints

- V1.0 MUST reject plain assistant text.
- V1.0 MUST retry invalid JSON only up to limit.
- V1.1 MUST NOT require UI changes for native tool calling.
- V1.1 MUST NOT remove JSON Action fallback.

## Implementation Notes

Create a `ToolActionClient` boundary:

```text
ToolActionClient.generate_action(context)
  -> ToolActionCandidate | ToolActionParseError
```

V1.0 implementation:

- Calls `model_runtime.generate`.
- Parses JSON.

V1.1 implementation:

- Calls native tool calling provider when configured.
- Normalizes provider tool calls to the same internal action.

## Acceptance

- Same fake tool sequence passes through JSON Action and native adapter tests.
- Full 8000 CJK character smoke passes with native tool calling before JSON fallback is retired from default paths.
