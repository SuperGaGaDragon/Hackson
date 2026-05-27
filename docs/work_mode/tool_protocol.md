## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

# Work Mode Tool Protocol

## 1. Purpose

This document defines the V1.0 model-visible toolbox and JSON Action protocol.

The protocol is strict. The model MUST call one tool every turn. Plain assistant text is invalid.

## 2. Protocol Direction

Final target:

- V1.1+ MUST support provider-native tool calling.

V1.0 transition:

- V1.0 MUST use provider-agnostic JSON Action.
- V1.0 MUST keep the backend tool schema identical to the future native tool schema.
- V1.0 MUST keep JSON Action fallback after native tool calling is added.

See `issues/issue1-native-tool-calling.md`.

## 3. JSON Action Envelope

Every Lead model turn MUST return exactly this JSON shape:

```json
{
  "tool": "mission_plan",
  "arguments": {
    "reason": "short user-visible reason"
  }
}
```

Rules:

- The response MUST be valid JSON.
- The top-level object MUST contain `tool` and `arguments`.
- `tool` MUST be one of the V1.0 allowed tool names.
- `arguments` MUST validate against the selected tool schema.
- The model MUST NOT include extra prose before or after JSON.
- If invalid, backend MUST return a format error observation and retry up to `max_invalid_turns`.

## 4. Common Argument Rules

All visible tools SHOULD include:

```json
{
  "reason": "why this tool is appropriate now"
}
```

`reason` rules:

- MUST be user-visible.
- MUST NOT contain raw chain-of-thought.
- MUST be concise.
- SHOULD be <= 240 characters.

## 5. Tool: mission_plan

Purpose:

- Create or update the Mission plan.
- Show the Lead Agent's current intended structure.

Schema:

```json
{
  "reason": "string",
  "planTitle": "string",
  "steps": [
    {
      "title": "string",
      "status": "pending|in_progress|completed|changed",
      "notes": "string"
    }
  ]
}
```

Constraints:

- `steps` MUST contain 1 to 20 items.
- This tool MUST NOT finish the Mission.
- This tool MUST create a visible plan event.

## 6. Tool: work_product

Purpose:

- Create user-visible product content.
- Create a new Product or append an immutable Artifact to an existing Product.

Schema:

```json
{
  "reason": "string",
  "operation": "create_product|append_artifact|revise_artifact|finalize_product",
  "productId": "string|null",
  "sourceArtifactIds": ["string"],
  "productTitle": "string",
  "artifactTitle": "string",
  "artifactKind": "outline|chapter|draft|revision|final|report|notes|other",
  "content": "string",
  "summary": "string"
}
```

Constraints:

- `create_product` MUST NOT provide an existing `productId`.
- `append_artifact`, `revise_artifact`, and `finalize_product` MUST reference an existing Product.
- `sourceArtifactIds` MAY be empty.
- Content MUST be persisted as a new immutable Artifact.
- Prior Artifacts MUST NOT be overwritten.
- Large Product events MUST be collapsed by default in timeline.

## 7. Tool: inspect_product

Purpose:

- Let the Lead inspect bounded Product or Artifact content before deciding the next action.

Schema:

```json
{
  "reason": "string",
  "productIds": ["string"],
  "artifactIds": ["string"],
  "focus": "string"
}
```

Constraints:

- MUST be read-only.
- MUST only inspect Products or Artifacts from the current Mission.
- MUST enforce max inspected artifacts and max returned characters.
- MUST create a visible collapsed inspect event.
- Event MAY expose inspected excerpts behind expand.
- Full unbounded content MUST remain in Product/Artifact storage, not event payload.

## 8. Tool: delegate_agent

Purpose:

- Let the Lead open a visible work window and ask the non-lead Agent to complete a scoped writing or review task.

Schema:

```json
{
  "reason": "string",
  "agentSlot": "agent_1|agent_2",
  "windowTitle": "string",
  "brief": "string",
  "expectedOutput": "outline|chapter|review|revision|summary|other",
  "targetProductId": "string|null",
  "sourceArtifactIds": ["string"]
}
```

Constraints:

- `agentSlot` MUST be the non-lead Agent.
- Each call MUST create one new Work Window.
- Work Windows MUST execute sequentially in V1.0.
- Work Window execution MUST be exactly one structured model call in V1.0.
- Delegate output MUST persist as an Artifact with `sourceAgentId` and `workWindowId`.
- Delegate output MUST be visible and expandable in UI.
- Delegate windows MUST NOT call tools in V1.0.
- Delegate windows MUST NOT finish the Mission.
- Delegate windows MUST NOT recursively delegate.

## 9. Tool: ask_user

Purpose:

- Ask the user for missing information.

Schema:

```json
{
  "reason": "string",
  "question": "string",
  "suggestedOptions": ["string"]
}
```

Constraints:

- MUST set Mission status to `waiting_input`.
- MUST create a visible question event.
- V1.0 MAY auto-resume after the user answers.
- Computer/file/shell tool modes MUST NOT auto-resume without explicit approval in future versions.
- Full smoke with `题材自定` SHOULD NOT use `ask_user`.

## 10. Tool: finish_mission

Purpose:

- Mark Mission completed with explicit final deliverables.

Schema:

```json
{
  "reason": "string",
  "summary": "string",
  "finalProductIds": ["string"],
  "finalArtifactIds": ["string"]
}
```

Constraints:

- `finalProductIds` MUST contain at least one existing Product id.
- Referenced Products MUST belong to the current Mission.
- Referenced Artifacts MUST belong to the current Mission.
- Backend MUST reject finish if referenced Products do not exist.
- Backend MUST mark Mission completed only after validation passes.

## 11. Tool: block_mission

Purpose:

- Let the Lead intentionally stop because the goal cannot be completed without a changed condition.

Schema:

```json
{
  "reason": "string",
  "blockedReason": "string",
  "neededFromUser": "string"
}
```

Constraints:

- MUST set Mission status to `blocked`.
- MUST NOT be used for transient provider errors.
- Runtime/system failures MUST use `failed` or `paused_retryable`, not this tool.

## 12. Delegate Result Protocol

V1.0 delegate Agent calls do not use the full toolbox.

Delegate model call MUST return structured JSON:

```json
{
  "status": "completed|blocked",
  "title": "string",
  "summary": "string",
  "content": "string",
  "reason": "string"
}
```

Backend MUST persist completed delegate output as an Artifact and return a structured observation to the Lead.

## 13. Invalid Turns

Invalid model turns include:

- Plain assistant text.
- Invalid JSON.
- Unknown tool.
- Multiple tool calls.
- Missing required argument.
- Invalid Product or Artifact reference.
- Tool not allowed in current Mission state.

Runtime behavior:

- Retry invalid turns up to `max_invalid_turns`.
- Persist invalid turn events for debugging.
- Mark Mission `failed` after invalid retries are exhausted.

## 14. 代办

- Convert schemas into backend Pydantic models before implementation.
