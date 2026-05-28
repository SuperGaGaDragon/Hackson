## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 1: Evaluation Is Not Proof

## Problem

Agent reliability language can easily overclaim.

If Evaluator Runtime says it "detects hallucinations" or "verifies truth", users and judges may infer stronger guarantees than the system can provide. V1.0 only sees the Mission trace, Products, Artifacts, and bounded evidence snippets. That is enough to flag serious risks, but not enough to prove external truth.

## Decision

Evaluator Runtime MUST be positioned as a reliability risk detector and quality gate.

It produces a Reliability Report, not a certificate of correctness.

Canonical claim:

```text
We do not prove correctness. We flag reliability risks based on trace, evidence, and requirement coverage.
```

## Self-Grilled Decisions

### Should the report use a score?

Yes, because the score is demo-legible and useful for triage.

But the UI and docs must say score is decision support. It is not a truth probability.

### Should high scores imply shipping without review?

Only within the chosen profile and risk band.

`ship_ready` means no major issues were found from the available trace. It does not mean the output is globally true.

### Should the evaluator ever say "hallucinated"?

Use `hallucinated_entity` only for the concrete case where an entity appears in the final Product but not in any retrieved evidence. Avoid broad "the answer is hallucinated" language.

## Consequences

- Reports need visible limitations.
- The pitch becomes more mature and credible.
- Some users may want stronger claims, but the product avoids false safety.

## Acceptance

- Every Reliability Report includes limitations.
- UI labels issue types concretely.
- Docs avoid "guarantee", "certify", and "detect all hallucinations".
