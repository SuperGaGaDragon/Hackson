## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 10: Final Product Reader Must Preserve Lineage

## Problem

The Product Panel exposed Artifact lineage as labels, but the reader switched to only `latestArtifact` when a Product reached `final`.

For a long writing Mission this makes earlier work look lost:

- outline exists in persistence, but is not readable in Product.
- chapter drafts exist in persistence, but are not readable in Product.
- final/latest Artifact dominates the reader after `Done`.

This is a Product bug, not a backend persistence bug.

## Decision

Product Panel MUST treat Artifact lineage as readable product content, not just metadata.

Required behavior:

- Final Products default to an all-Artifact reader stack.
- The final Artifact remains visible as one section in that stack.
- Users can switch from the stack to a single Artifact.
- Users can return to the stack.
- Product reader MUST preserve product `artifactIds` order when available.
- Fallback sorting by `createdAt` is allowed only when a Product has no ordered `artifactIds`.

## Acceptance

- A completed 8000 CJK novel Mission shows outline, chapter drafts, and final draft inside Product reader content.
- Clicking an Artifact lineage control shows that Artifact's content.
- Returning to `All` shows every Product Artifact again.
- The full smoke still verifies final Product CJK count is at least 8000.
- Browser smoke fails if final Product only exposes the latest Artifact content.

## Follow-Up

Future UI can add section-level collapse for very large Products, but the default V1 behavior must not make earlier Artifacts look swallowed.
