## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 13: Revision Lineage

## Problem

Review and discussion are not enough unless the product records how changes were made.

If a revision overwrites the original Artifact, users lose the ability to answer:

- What changed?
- Why did it change?
- Which review finding caused it?
- Which version entered the final Product?

## Decision

Revision MUST create a new immutable Artifact.

Original Artifacts, Review Artifacts, Discussion Artifacts, Revision Artifacts, and Final Artifacts must remain readable.

## Revision Artifact Metadata

Revision Artifacts SHOULD include:

```json
{
  "productId": "string",
  "sourceArtifactIds": ["string"],
  "reviewArtifactIds": ["string"],
  "discussionArtifactIds": ["string"],
  "changeSummary": "string",
  "resolvedFindingIds": ["string"],
  "revisionOf": "string"
}
```

## Product Reader Behavior

Default reader:

- Shows current recommended content.
- Does not hide prior versions.

History:

- Groups related Artifacts by source/chapter/section when possible.
- Shows original draft, review, discussion, revision, and final references.
- V1 can skip text diff; lineage is mandatory.

## Progress Behavior

Revision Progress rows show:

- source Artifact.
- Review/Discussion inputs.
- change summary.
- new Revision Artifact.

They MUST NOT display unbounded revised content inline.

## Acceptance

- Revision smoke creates original, review, optional discussion, and revision Artifacts.
- Original Artifact content remains unchanged.
- Product reader can access original and revised content.
- Final Product references the selected revision or final assembly explicitly.

## Follow-Up

Add visual diff only after lineage is reliable. Diff is useful but not required for first product-quality revision flow.
