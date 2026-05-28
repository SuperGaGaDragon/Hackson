## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 12: Review And Delegate Discussion Tools

## Problem

The current V1.0 toolbox can plan, write, inspect, delegate, ask, finish, and block. It does not yet model a high-quality review loop.

Without review/discussion tools, the Lead can jump from writing to finish with no visible quality checkpoint.

## Decision

Add two model-visible tools after deterministic checks are stable:

- `review_product`
- `discuss_with_delegate`

These tools are quality workflow tools. They do not directly modify Product content and do not finish a Mission.

## Tool: `review_product`

Purpose:

- Let the Lead produce a structured review of existing Product or Artifact content.

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
- Review content MUST be bounded by context budget; use `inspect_product` first when needed.

## Tool: `discuss_with_delegate`

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

Delegate discussion result:

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

Constraints:

- `agentSlot` MUST be the non-lead Agent.
- Discussion MUST be bound to at least one Product, Artifact, or Work Window.
- V1.0.3 default `maxTurns` SHOULD be `1`; hard maximum is `3`.
- Discussion MUST persist a Discussion Artifact.
- Discussion MUST create a visible Discussion Window.
- Discussion MUST NOT modify Product content.
- Discussion MUST NOT finish the Mission.
- Discussion MUST NOT recursively delegate.

## UI Requirements

Review:

- Product Panel shows Review Artifacts in lineage/history.
- Progress row shows verdict, score, and findings summary.
- Critical/major findings are visually distinct.

Discussion:

- Discussion Window appears near Work Windows or in the same Windows surface with `discussion` type.
- It is collapsed by default.
- Expanded view shows transcript and recommendation.
- Product Panel links Discussion Artifact to the relevant source Artifact(s).

## Revision Link

The next revision tool should reference:

- source Artifact id.
- Review Artifact id when present.
- Discussion Artifact id when present.

Original content MUST remain immutable.

## Acceptance

- `review_product` persists a Review Artifact and emits `PRODUCT_REVIEWED`.
- `discuss_with_delegate` persists a Discussion Artifact and emits visible discussion window events.
- Neither tool modifies Product content.
- Lead can observe the review/discussion result and choose the next tool.
- Browser smoke shows Review and Discussion in Progress and Product lineage.

## Follow-Up

Add `revise_product` or extend `work_product.operation=revise_artifact` after Review and Discussion Artifacts are stable.
