# Issue 41: Long-Form Compose Flow For Research Deliverables

Created at: 2026-05-29
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex

## Problem

A production Mission for `French Revolution literature review 8000 words English` reached the Reliability gate, but did not complete. The best deliverable was an expanded revision of about 4,907 words. The Reliability report correctly evaluated the current deliverable Artifact and returned `repair_required`, after which the Lead searched for more evidence instead of using a stale report. The Mission then paused as `paused_retryable` with `model_timeout` during the next long revision turn.

This is product-bad even though the safety gate worked. The user asked for one high-level task, but the system exposed a retryable pause before producing the requested length.

## Root Cause

The current `work_product` tool forces the Lead Agent to put all visible prose in one JSON tool action. That is acceptable for outlines and medium drafts, but it couples two different jobs:

- choosing the next tool/action, which should be a small reliable JSON decision;
- producing thousands of words of polished body prose.

When Reliability finds a word-count gap, the repair contract currently points back to `work_product`. For an 8,000-word research draft, the Lead tends to produce one huge revision action. That single model turn is vulnerable to provider timeout and creates a bad resume experience.

## Product Standard

Long-form research work should feel like a composed writing pipeline:

1. Search and capture source notes.
2. Create an outline or section plan.
3. Write bounded section Artifacts.
4. Compose those section Artifacts into a single final Artifact.
5. Evaluate the final Artifact by exact id/hash.
6. Finish only when the current report passes.

The user should see progress as sections and final assembly, not a silent long turn that ends in `model_timeout`.

## Decision

Add a model-visible `compose_artifacts` tool.

The tool is backend-owned and deterministic. It concatenates already-persisted source Artifacts into a new Product Artifact, with optional heading/intro/conclusion text supplied by the Lead. It does not call the model, search the web, or judge quality.

`compose_artifacts` lets the Lead write long deliverables in smaller `work_product` or Delegate turns, then assemble them without re-generating the whole document inside a Lead action.

## Tool Contract

Input:

```json
{
  "reason": "string <=240",
  "productId": "existing product id",
  "sourceArtifactIds": ["artifact ids in desired order"],
  "productTitle": "string",
  "artifactTitle": "string",
  "artifactKind": "draft|revision|final",
  "intro": "string optional",
  "conclusion": "string optional",
  "summary": "string <=1000"
}
```

Rules:

- `productId` must belong to the current Mission.
- `sourceArtifactIds` must be non-empty and belong to the same Mission.
- Source Artifacts with `artifactRole` in `reliability_report`, `review`, `discussion`, or `search_summary` must not be composed into the final deliverable body.
- Search Summary Artifacts remain evidence inputs; the Lead should write source-aware prose into section Artifacts before composing.
- The composed Artifact is immutable and uses `sourceArtifactIds` lineage.
- `artifactKind=final` updates the Product `deliverableArtifactId` through the existing Product path.
- The observation must include word count, source count, and the new Artifact id.

## Reliability Interaction

For research/paper-like Missions:

- Reliability continues to evaluate the final candidate Artifact exactly by id/hash.
- If word count is missing or partial, `nextActionContract` should mention that the Lead can either write additional section Artifacts or use `compose_artifacts` after section work is complete.
- `finish_mission` requirements are unchanged.

## Acceptance Criteria

- Lead context exposes `compose_artifacts` schema and guidance.
- Parser accepts valid `compose_artifacts` actions and rejects invalid ones.
- Executor creates a composed Artifact with source lineage and a visible `PRODUCT_COMPOSED` event.
- The composed final Artifact becomes the Product deliverable candidate when `artifactKind=final`.
- A later deliverable revision must not replace an existing Product deliverable candidate if it regresses a detected hard
  count requirement by more than 10%. The revision remains visible as Product history, but the prior candidate stays
  authoritative until a revision preserves or improves the hard requirement.
- `finish_mission` can complete using a passing Reliability report for the composed Artifact.
- Unit tests cover composing sections, rejecting non-deliverable source roles, and context guidance.
- Target-machine test can run the French Revolution 8,000-word Mission without requiring one giant Lead revision turn. If the model still chooses poorly, logs should show the gap is model planning rather than missing backend capability.

## Non-Goals

- Do not remove timeouts.
- Do not bypass Reliability.
- Do not auto-pad text to satisfy word count.
- Do not compose raw search snippets as final prose.
