## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 4: LLM Judge Discipline

## Problem

Evaluator Runtime needs semantic judgement for requirements and evidence support.

But a vague LLM judge can become arbitrary:

- It may reward polished writing.
- It may ignore missing evidence.
- It may invent reasons.
- It may produce unstable scores.

If the evaluator is just "ask another model if this is good", the product is not credible.

## Decision

Use deterministic checks first and model-assisted checks only behind narrow structured schemas.

The evaluator model must not produce the final score directly in V1.0. It produces structured intermediate outputs:

- requirements.
- claims.
- support verdicts.
- short reasons.

ScoreCalculator owns the score.

## Self-Grilled Decisions

### Should the same model evaluate its own answer?

Avoid when possible, but V1.0 may use the platform model for both generation and evaluation because the contract is structured and trace-bound.

The demo should emphasize methodology, not model independence.

### Should we use a stronger judge model?

Eventually yes.

V1.0 can use the configured platform model if latency and cost are acceptable. The architecture should allow a separate evaluator model later.

### Should evaluator prompts be user-editable?

No in V1.0.

Custom prompts would make reports incomparable and harder to trust. Evaluation profiles can become configurable in V1.3.

## Consequences

- More engineering work than a simple judge prompt.
- Better auditability.
- Score changes are traceable to issue weights.

## Acceptance

- Requirement extractor returns JSON only.
- Claim extractor returns JSON only.
- Evidence checker returns JSON only.
- Score calculator is deterministic from issues.
- Invalid evaluator JSON creates an `evaluation_limitation` issue instead of silently passing.
