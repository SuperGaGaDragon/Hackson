## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 7: Research Paper Evidence Gate

## Problem

The initial Reliability Report can show `80 / 100` and `minor_review` when the Evidence Ledger is empty.

That score is misleading for research/paper-like work. A paper may have a final-looking draft, but if the trace contains no evidence, the report cannot validate factual claims.

## Decision

For `research_reliability_v1`, an empty Evidence Ledger MUST cap status at `needs_human_review`.

This cap applies even when the numeric score remains in the 70-84 band.

The report MUST make the reason visible:

- Requirement coverage should include `Use trace-backed evidence for research claims`.
- Issues should include `No evidence ledger`.
- Limitations should say that no trace evidence was available.
- Suggested actions should tell the Lead to run `web_search` or attach source-backed Research Artifacts.

## Paper-Like Requirements

When the Mission goal is paper-like, the evaluator MUST also check:

- A final paper/report draft exists.
- The final draft is not only an outline or plan.
- Thesis/body/conclusion shape is present when detectable.
- Research claims have trace-backed evidence.

The evaluator should support Chinese prompts and Chinese final drafts in this first pass. It does not need a universal academic-writing judge.

## Acceptance

- A completed research Mission with no search evidence is `needs_human_review`, not `minor_review`.
- A Chinese paper Mission that only has an outline reports a missing final-draft requirement.
- A plausible Chinese final paper draft satisfies the final-draft requirement.
- The UI can explain why the report is blocked without opening raw Diagnostics.
