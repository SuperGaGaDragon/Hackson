## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 29: Research Paper Final Draft Gate

## Problem

Research and paper-like Missions can currently finish with a plan, outline, or chapter map as the final Product.

That is unacceptable when the user asks for a paper, essay, literature review, research report, or other final writing deliverable. A thesis outline can be useful work, but it is not the final Product.

Examples:

- `写一篇海地革命论文`
- `写一个文献综述`
- `draft a research paper`
- `produce a final essay`

## Decision

The backend MUST add a deterministic final-draft gate for research/paper-like Missions.

This is not workflow hard-coding. The model still chooses tools and order. The gate only validates that a `finish_mission` call references a deliverable that matches the requested shape.

For research/paper-like Missions, `finish_mission` MUST require:

- At least one final Artifact id.
- A referenced Artifact inside the referenced Product.
- A final-draft-like Artifact, not only an outline, plan, checklist, or blueprint.
- Enough body prose to be plausibly user-usable.

The gate SHOULD reject:

- `artifactKind="outline"` used as final.
- Titles dominated by `大纲`, `计划`, `蓝图`, `提纲`, `outline`, `plan`, or `blueprint`.
- Short fragments that only describe what the paper will do.

The gate SHOULD allow:

- `artifactKind="final"` or `report` with body sections.
- Chinese or English paper prose.
- Drafts that are imperfect but materially usable as a final manuscript.

## Recovery

When rejected, the Mission loop MUST treat the rejection as model-correctable.

Preferred Lead recovery:

1. Call `work_product`.
2. Reference the existing Product.
3. Create or revise an Artifact with `artifactKind="final"` or `report`.
4. Put the full final paper/report draft in `content`.
5. Call `evaluate_product` when the Mission has research claims.
6. Call `finish_mission` again with the final Artifact id.

## Acceptance

- A paper Mission cannot complete with only a plan or outline.
- A paper Mission with a plausible final draft can pass the deterministic final-draft gate.
- The rejection appears as `MODEL_TURN_INVALID` with a stable code.
- The Lead receives a bounded observation that tells it how to repair Product state.
