## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 3: Evidence Ledger Boundary

## Problem

If the evaluator treats any text in the Mission as evidence, it will rubber-stamp the Agent's own claims.

Example:

```text
Final Product says: MapleNeural Labs is a Toronto enterprise AI startup.
Evaluator sees that text in the final Product and marks the entity as found.
```

That would destroy the value of trace-based evaluation.

## Decision

Evidence Ledger includes only externally grounded or tool-observed material, not the final answer itself.

Allowed V1.0 evidence:

- `WEB_SEARCH_COMPLETED` source results.
- Research Artifacts created from search observations.
- source metadata attached to Artifacts.
- bounded inspected excerpts when the excerpt comes from a source Artifact.

Not evidence:

- final Product prose.
- Lead Agent explanations.
- hidden prompts.
- full prompt logs.
- unsupported source URLs typed by the model without retrieval.

## Self-Grilled Decisions

### Can a final answer source link count as evidence?

Only if the link appears in the Evidence Ledger or a retrieved source observation.

A URL written in the final answer but never retrieved is a citation candidate, not evidence.

### Can snippets be enough?

For V1.0, yes, because the goal is reliability risk detection.

The report must disclose that snippet support is not full-web proof. V1.1 can add page fetch or richer source alignment.

### Should evaluator search again to verify claims?

Not in V1.0 by default.

V1.0 evaluates the agent's trace. If the trace is insufficient, that is itself a reliability issue. Later versions can support evaluator-owned verification search as a separate mode.

## Consequences

- Agents cannot self-certify by writing confident prose.
- Missing search becomes visible.
- Some true claims may be flagged unsupported if the Agent failed to retrieve evidence.

## Acceptance

- Tests prove final Product text is not used as Evidence Ledger input.
- Unsupported but true-sounding claims are still flagged when no trace evidence exists.
- Report limitations explain trace-bound evidence.
