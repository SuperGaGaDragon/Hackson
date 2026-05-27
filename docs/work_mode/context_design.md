## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

# Work Mode Context Design

## 1. Purpose

This document defines what the Lead Agent and Delegate Agent should see in V1.0.

Context design is a product requirement. The model decides tools, but the backend decides what state is visible and how much content fits in budget.

## 2. Lead Context Package

Every Lead model turn MUST include:

- Mission id.
- Mission title and goal.
- Current Mission status.
- Lead Agent profile.
- Delegate Agent profile.
- Available tools and schemas.
- Hard constraints.
- Product manifest.
- Work Window manifest.
- Recent events.
- Last tool observation.
- Bounded recent Artifact content.
- Current budget counters.

## 3. Product Manifest

The Product manifest MUST list each Product without dumping all content:

```json
{
  "productId": "product_1",
  "title": "8000字小说",
  "status": "active",
  "latestSummary": "已完成大纲和第一章。",
  "artifactIds": ["artifact_1", "artifact_2"],
  "latestArtifactId": "artifact_2",
  "sourceAgentIds": ["agent_1", "agent_2"],
  "estimatedCjkChars": 1400
}
```

Rules:

- Manifest MUST be included every turn.
- Manifest MUST be compact.
- Manifest MUST include Product ids so the model can call `work_product`, `inspect_product`, and `finish_mission`.

## 4. Work Window Manifest

The Work Window manifest MUST list delegate calls:

```json
{
  "windowId": "window_1",
  "agentSlot": "agent_2",
  "title": "第一章草稿",
  "status": "completed",
  "resultArtifactId": "artifact_3",
  "summary": "完成第一章雨夜车站。"
}
```

Rules:

- Completed windows MUST remain visible to the Lead by id and summary.
- Failed or blocked windows MUST include error or blocked reason.

## 5. Recent Events

Recent events SHOULD include:

- Last 10 to 30 events, depending on token budget.
- Event type.
- Title.
- Short message.
- Relevant ids.
- No unbounded large content.

Large event content MUST be referenced by Product, Artifact, or Work Window id.

## 6. Artifact Content Budget

V1.0 default:

- Include full content for the most recent 2 Artifacts if under budget.
- Include summaries for older Artifacts.
- Do not blindly include all Artifact full text.

If the Lead needs older content, it MUST call `inspect_product`.

## 7. inspect_product Context

`inspect_product` returns bounded content to the next Lead model turn.

Constraints:

- Only current Mission Products and Artifacts.
- Max artifacts per inspect call.
- Max returned characters per inspect call.
- Returned content should include title, summary, and excerpt/full content up to limit.

The inspect observation MUST identify truncation if content was clipped.

## 8. Delegate Context Package

Delegate Agent calls are scoped and simple in V1.0.

Delegate context MUST include:

- Mission title and goal.
- Delegate Agent profile.
- Lead Agent brief.
- Expected output type.
- Target Product id when provided.
- Source Artifact summaries or bounded excerpts.
- Hard instruction to return structured delegate result JSON.

Delegate context MUST NOT include:

- Full Mission history by default.
- Backend-internal tool list.
- Ability to call tools.
- Ability to finish Mission.
- Ability to delegate recursively.

## 9. Writing Mission Guidance

For the full 8000 CJK character novel smoke:

- The model MAY decide to create an outline.
- The model MAY decide to delegate chapters to the non-lead Agent.
- The model MAY inspect prior chapters before final assembly.
- The model SHOULD NOT ask the user for topic if the goal says `题材自定`.
- The model MUST create a final Product that passes CJK character count.

The backend MUST NOT hard-code these steps. They belong in model guidance and acceptance criteria, not runtime order.

## 10. Budget Counters

Lead context MUST include budget counters:

```json
{
  "modelTurnsUsed": 4,
  "modelTurnsMax": 20,
  "delegateWindowsUsed": 3,
  "delegateWindowsMax": 12,
  "productsUsed": 2,
  "productsMax": 12,
  "artifactsUsed": 5,
  "artifactsMax": 40
}
```

The model should see budgets so it can decide whether to finish, consolidate, or block.

## 11. Target Context Architecture

V1.0:

- Manifest + recent content + inspect tool.

V1.1:

- Better product summaries.
- Native tool call observations.
- Optional delegate mini-loop context.

V1.5+:

- Read-only file/repo context under permissions.

## 12. 代办

- Choose concrete budget defaults during implementation and record them in `api.md` only after target verification.
