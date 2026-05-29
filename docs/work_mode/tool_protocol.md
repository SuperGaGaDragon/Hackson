## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
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

## 13. V1.0.x Quality Tools

These tools are planned for the V1.0.x quality track after the base V1.0 loop is stable.

They MUST follow the same one-tool-per-turn rule. They MUST be visible to the model only after implementation and smoke coverage exist.

Read-only cognition tools:

- `review_product`
- `discuss_with_delegate`
- `web_search`
- `evaluate_product`

These tools help the Lead think with better evidence. They MUST NOT directly mutate Product content, finish a Mission, or bypass `work_product`.

### 13.1 Tool: review_product

Purpose:

- Let the Lead create a structured review of existing Product or Artifact content.

Schema:

```json
{
  "reason": "string",
  "productIds": ["string"],
  "artifactIds": ["string"],
  "reviewTitle": "string",
  "reviewProfile": "long_form_novel_v1|general_text_v1",
  "verdict": "pass|needs_revision|blocked",
  "score": 0,
  "summary": "string",
  "findings": [
    {
      "severity": "critical|major|minor",
      "area": "requirement|structure|length|consistency|style|readability|other",
      "claim": "string",
      "evidence": "string",
      "requiredChange": "string"
    }
  ],
  "passedChecks": ["string"],
  "recommendedNextTool": "work_product|discuss_with_delegate|finish_mission|ask_user|block_mission"
}
```

Constraints:

- MUST reference current Mission Products or Artifacts.
- MUST persist a Review Artifact.
- MUST emit `PRODUCT_REVIEWED`.
- MUST NOT modify Product content.
- MUST NOT mark Mission completed.
- Findings with `critical` or `major` severity SHOULD include evidence.
- Review content MUST be bounded by context budget; the Lead should call `inspect_product` first when needed.

### 13.2 Tool: discuss_with_delegate

Purpose:

- Let the Lead ask the non-lead Agent a short scoped question about prior work.

Schema:

```json
{
  "reason": "string",
  "agentSlot": "agent_1|agent_2",
  "discussionTitle": "string",
  "windowId": "string|null",
  "productId": "string|null",
  "artifactIds": ["string"],
  "question": "string",
  "expectedOutcome": "string",
  "maxTurns": 1
}
```

Constraints:

- `agentSlot` MUST be the non-lead Agent.
- Discussion MUST be bound to at least one Product, Artifact, or Work Window.
- Default `maxTurns` SHOULD be `1`; hard maximum is `3`.
- Discussion MUST persist a Discussion Artifact.
- Discussion MUST create a visible Discussion Window.
- Discussion MUST NOT modify Product content.
- Discussion MUST NOT finish the Mission.
- Discussion MUST NOT recursively delegate.

### 13.3 Discussion Result Protocol

Discussion delegate model call MUST return structured JSON:

```json
{
  "status": "completed|blocked",
  "title": "string",
  "summary": "string",
  "transcript": [
    {
      "speaker": "lead|delegate",
      "content": "string"
    }
  ],
  "recommendation": "string",
  "reason": "string"
}
```

Backend MUST persist completed discussion output as a Discussion Artifact and return a structured observation to the Lead.

Discussion result ingestion SHOULD be tolerant in the same product spirit as Delegate writing ingestion. If the child Agent returns useful summary, recommendation, transcript text, or plain text but misses the exact wrapper schema, backend MAY canonicalize it into a completed Discussion Artifact. Empty output or unsalvageable broken JSON-like output remains invalid.

### 13.4 Tool: web_search

Purpose:

- Let the Lead retrieve bounded external references when current, niche, or factual information would improve the Mission.

Schema:

```json
{
  "reason": "string",
  "query": "string",
  "searchType": "general|news|technical|reference",
  "maxResults": 5,
  "recencyDays": 30,
  "allowedDomains": ["string"],
  "blockedDomains": ["string"]
}
```

Argument rules:

- `query` MUST be concise and specific.
- `searchType` defaults to `general`.
- `maxResults` defaults to `5`; hard maximum is `10`.
- `recencyDays` MAY be `null` when recency is not relevant.
- `allowedDomains` and `blockedDomains` MAY be empty.

Constraints:

- MUST be read-only.
- MUST emit `WEB_SEARCH_COMPLETED` when search succeeds.
- MUST emit `WEB_SEARCH_FAILED` or return a rejected tool observation when search fails.
- Successful searches MUST create a backend-owned Search Summary Artifact and emit `SEARCH_SUMMARY_CREATED`.
- Search Summary Artifacts MUST use `metadata.artifactRole=search_summary`.
- Search Summary Artifacts MUST be non-deliverable Product History, not authoritative final answers.
- MUST return bounded results; unbounded page content is forbidden.
- MUST expose source URLs to the UI.
- MUST NOT modify Product content.
- MUST NOT finish the Mission.
- MUST NOT run browser automation, shell commands, file access, or computer-control actions.
- MUST NOT expose Codex CLI as the model-visible tool.
- MAY use Codex CLI only as an internal `SearchProvider` if it returns the same structured result schema and passes smoke.

### 13.5 Web Search Result Protocol

`web_search` observation MUST use this structured shape:

```json
{
  "tool": "web_search",
  "status": "ok",
  "query": "string",
  "effectiveQuery": "string",
  "searchType": "general|news|technical|reference",
  "results": [
    {
      "title": "string",
      "url": "string",
      "source": "string",
      "snippet": "string",
      "publishedAt": "string|null"
    }
  ],
  "truncated": false,
  "provider": "string",
  "fallbackApplied": false,
  "fallbackReason": "string|null",
  "attemptCount": 1,
  "summaryProductId": "string",
  "summaryArtifactId": "string"
}
```

Failure observation:

```json
{
  "tool": "web_search",
  "status": "failed",
  "code": "search_provider_unavailable|search_timeout|search_rate_limited|search_no_results",
  "query": "string",
  "effectiveQuery": "string",
  "fallbackApplied": false,
  "fallbackReason": "string|null",
  "attemptCount": 1,
  "retryable": true
}
```

Rules:

- The next Lead turn MAY use `work_product` to turn search results into user-visible writing.
- Search snippets are evidence hints, not final content.
- Providers MAY run bounded internal fallback attempts, but returned results MUST still respect `allowedDomains` and `blockedDomains`.
- `query` is the model-requested query. `effectiveQuery` is the provider query that produced the returned result set.
- If the Mission needs a citation or source trail, the Lead SHOULD preserve the relevant URLs in Product content while the backend preserves the search trail in a Search Summary Artifact.

### 13.6 Tool: evaluate_product

Purpose:

- Let the Lead request a backend-owned Reliability Report for the current Mission and final Product candidate.

Schema:

```json
{
  "reason": "string",
  "profile": "research_reliability_v1",
  "productIds": ["string"],
  "artifactIds": ["string"],
  "focus": "string"
}
```

Constraints:

- MUST be read-only against Product content.
- MUST run Evaluator Runtime against the visible Mission trace.
- MUST evaluate the exact supplied `artifactIds` when they are present.
- If `artifactIds` are absent, MUST evaluate the selected Product `deliverableArtifactId`.
- MUST reject with `evaluation_target_required` when no explicit or Product-level deliverable candidate exists.
- MUST persist a Reliability Report Artifact.
- MUST emit `EVALUATION_STARTED` before report construction unless returning an unchanged current report.
- MUST emit `RELIABILITY_REPORTED`.
- MUST emit `EVALUATION_FAILED` if no report can be produced.
- MUST return evaluated Artifact ids, evaluated content hashes, gate status, score, issue counts, blocking issues, report
  Artifact id, and recommended next action contract.
- MUST NOT modify Product content.
- MUST NOT mark Mission completed.
- For research/paper-like Missions, a current report after the latest Product update is required before `finish_mission`.
- For research/paper-like Missions, the current report must cover the exact `finalArtifactIds` and matching content
  hashes before `finish_mission` can complete.

### 13.7 Evaluate Product Observation

```json
{
  "tool": "evaluate_product",
  "status": "ok",
  "profile": "research_reliability_v1",
  "gateStatus": "repair_required",
  "evaluatedProductIds": ["product_id"],
  "evaluatedArtifactIds": ["artifact_id"],
  "evaluatedArtifactHashes": {
    "artifact_id": "sha256..."
  },
  "score": 80,
  "reliabilityStatus": "needs_human_review",
  "issueCounts": {
    "high": 1,
    "medium": 1
  },
  "reportArtifactId": "artifact_id",
  "blockingIssues": [
    {
      "id": "I1",
      "type": "missing_requirement",
      "severity": "high",
      "artifactIds": ["artifact_id"],
      "requiredAction": "revise_candidate",
      "suggestedTool": "work_product"
    }
  ],
  "topIssues": [
    {
      "id": "I1",
      "type": "missing_requirement",
      "severity": "high",
      "title": "Missing requirement",
      "suggestedFix": "Revise the final answer."
    }
  ],
  "recommendedNextTool": "work_product",
  "nextActionContract": {
    "ifEditing": {
      "tool": "work_product",
      "operation": "revise_artifact",
      "sourceArtifactIds": ["artifact_id"]
    },
    "afterEditing": {
      "tool": "evaluate_product",
      "artifactIds": ["new_artifact_id"]
    },
    "finishOnlyAfter": "gateStatus pass and report hashes match finalArtifactIds"
  }
}
```

`finish_mission` rejection observations for Reliability failures MUST include structured fields whenever available:

```json
{
  "tool": "finish_mission",
  "status": "rejected",
  "code": "reliability_evaluation_required",
  "requiredTool": "evaluate_product",
  "finalArtifactIds": ["artifact_id"],
  "latestReportArtifactId": "artifact_id|null",
  "latestReportCoversFinalArtifacts": false,
  "latestProductUpdatedAfterReport": true,
  "blockingIssueIds": ["I1"]
}
```

The Lead MUST repair the specific blocking issues or evaluate the current final Artifact before calling
`finish_mission` again. It MUST NOT repeatedly rewrite only to chase a numeric score.

## 14. Invalid Turns

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

## 15. 代办

- Convert schemas into backend Pydantic models before implementation.
