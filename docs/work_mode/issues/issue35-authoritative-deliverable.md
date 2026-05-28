## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 35: Authoritative Deliverable Surface

## Problem

Work Mode currently uses one Product lineage for everything:

- outline
- draft
- revision
- final candidate
- review report
- reliability report
- delegate notes
- revision plan

That is correct for audit history, but it is not enough for users. Users need one clean, authoritative answer to read.

The observed public Mission showed why this matters. A Product's `latestArtifactId` can point to a review, revision
plan, or intermediate artifact because it means "latest written artifact", not "best deliverable". The UI then forces
users to inspect a long Artifact list and guess which item is safe to use.

## Self-Grilled Decisions

Question: Should Product History disappear after a final answer exists?

Decision: No. History is valuable. It explains how the Agent worked and lets users inspect reviews, revisions, and
lineage. Removing it would make Work Mode less transparent.

Question: Should the UI infer the final answer by picking the newest `kind=final` Artifact?

Decision: No. That is only a fallback. The backend must expose an explicit Product-level contract so frontend and
future clients do not duplicate fragile heuristics.

Question: Should blocked Missions have an empty result?

Decision: No. A blocked Mission often has a useful best candidate. The UI must show that candidate as a blocked
deliverable, explain why it is not accepted, and offer recovery actions.

Question: Should review and reliability reports ever become the authoritative deliverable?

Decision: No for normal Work Products. Review and reliability reports belong in Product History and Reliability
surfaces. A report can be an artifact, but it should not replace the user-facing answer.

## Decision

Add an explicit deliverable contract on Product:

```text
product.latestArtifactId      = newest lineage item
product.deliverableArtifactId = current authoritative answer candidate
product.deliveryStatus        = draft_candidate | blocked_candidate | verified_final | user_accepted | none
```

Definitions:

- `draft_candidate`: best current answer while work is active.
- `blocked_candidate`: best current answer when the Mission is blocked or quality gate failed.
- `verified_final`: accepted by the Mission completion path.
- `user_accepted`: future state when a user chooses to accept a blocked candidate.
- `none`: no deliverable-like content exists yet.

Deliverable-like artifact kinds:

- `final`
- `revision`
- `draft`
- `chapter`
- `mission_result`
- `text`

Non-deliverable artifact roles:

- `review`
- `reliability_report`
- `discussion`
- revision plans and reports when marked by metadata.

## Backend Contract

When creating a Product Artifact:

- Always append to `artifactIds`.
- Always update `latestArtifactId`.
- Update `deliverableArtifactId` only if the Artifact is deliverable-like.
- Do not let `review_product`, `evaluate_product`, `discuss_with_delegate`, or delegate summary notes overwrite the
  deliverable pointer unless the created Artifact is explicitly deliverable-like.

When finishing a Mission:

- Mark final Products as `final`.
- Set `deliverableArtifactId` to the final Artifact selected by `finish_mission`.
- Set `deliveryStatus` to `verified_final`.

When blocking a Mission:

- Keep or infer the best deliverable candidate.
- Set `deliveryStatus` to `blocked_candidate` for affected Products.
- Do not erase the candidate.

For existing Products without the new fields:

- Public API may infer a deliverable from the newest deliverable-like Artifact in `artifactIds`.
- This inference is a compatibility fallback, not the canonical write path.

## UI Contract

Product Panel must split into two conceptual surfaces:

1. `Deliverable`
   - Clean current answer.
   - Shows status: verified, blocked, draft, or user accepted.
   - Shows blocker reason when Mission is blocked.
   - Offers visible recovery choices for blocked Missions: resume with instruction, accept current candidate later, or
     inspect Reliability.

2. `Product History`
   - Full artifact lineage.
   - Review/reliability/report artifacts stay visible here.
   - Defaults to compact navigation with full content in reader.

The user should not have to hunt through Product History to find the answer.

## Acceptance

- A Product with artifacts `final -> review -> revision plan` keeps the `final` or latest deliverable candidate in
  `deliverableArtifactId`; the review/plan remains only in history.
- A Product with a later `revision` after a failed review updates the deliverable candidate to that revision.
- A blocked Mission shows a clean `Deliverable` card with `Blocked candidate` and blocker reason.
- Product History still shows every artifact in lineage order.
- Existing Products without deliverable fields still show a best candidate through fallback inference.
- Browser smoke verifies that the Deliverable surface is visible separately from History.

## Future Work

- Add explicit user action `Accept current candidate` to turn `blocked_candidate` into `user_accepted`.
- Add artifact-level `deliverableRole` if future tools need richer states such as appendix, bibliography, or attachment.
