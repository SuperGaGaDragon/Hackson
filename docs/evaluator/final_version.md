## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Evaluator Runtime Final Version Roadmap

## 1. Purpose

Evaluator Runtime is Hackson's reliability layer for agentic Work.

Most demos show an Agent completing a task. Evaluator Runtime shows whether the Agent's result is trustworthy enough to ship, review, rerun, or block. It inspects the Work Mission trace, Products, Artifacts, tool observations, and evidence sources, then produces a Reliability Report with a score, issue taxonomy, trace references, and suggested fixes.

The first product surface is AgentLens for Research Missions.

Current issue notes:

- `issues/issue1-evaluation-is-not-proof.md`
- `issues/issue2-work-mode-integration.md`
- `issues/issue3-evidence-ledger-boundary.md`
- `issues/issue4-llm-judge-discipline.md`
- `issues/issue5-demo-replay-and-live-mode.md`
- `issues/issue6-incomplete-mission-gate.md`
- `issues/issue7-research-paper-evidence-gate.md`

## 2. Product North Star

Work Mode answers: "What did the Agents produce?"

Evaluator Runtime answers: "Can this output be trusted, and where exactly did it fail?"

Core loop:

```text
Research Mission
  -> Work Mode Lead Agent uses tools and creates Products
  -> Work Mode persists events, Products, Artifacts, windows, and search observations
  -> Evaluator Runtime builds an Evidence Ledger
  -> Evaluator Runtime checks requirements, claims, citations, tool failures, and risk
  -> Reliability Report is persisted as a Product Artifact and report record
  -> UI shows score, issues, trace references, and suggested fixes
```

Evaluator Runtime does not replace the Lead Agent. It is a separate quality gate that evaluates the Mission after or during execution.

## 3. Hard Product Constraints

- V1.0 MUST focus on Research Missions.
- V1.0 MUST evaluate Work Mode state, not hidden chain-of-thought.
- V1.0 MUST use visible Mission events, Products, Artifacts, Work Windows, and search observations as the trace.
- V1.0 MUST NOT claim to prove correctness.
- V1.0 MUST distinguish unsupported, weakly supported, and supported claims.
- V1.0 MUST produce actionable Reliability Issues with severity and suggested fixes.
- V1.0 MUST NOT mark an incomplete Mission as `ship_ready`.
- V1.0 MUST keep search/read evidence bounded.
- V1.0 MUST support deterministic fallback demo data.
- V1.0 MUST render reports in the Work Console without requiring a new app surface.
- V1.0 MUST preserve Work Mode's rule that Product content changes only through Work Mode tools.
- Evaluator Runtime MUST NOT mutate final Product content directly.
- Evaluator Runtime MUST NOT expose provider secrets, raw chain-of-thought, or unbounded page text.

## 4. Version Summary

| Version | Name | Product Result | Runtime Result | Release Gate |
| --- | --- | --- | --- | --- |
| V1.0 | Research Reliability Report | A user can run or replay a research Mission and see score, issues, evidence status, and suggested fixes. | Requirement coverage, claim extraction, evidence matching, tool failure checks, scoring, report persistence, Work UI report panel. | Demo catches a hallucinated entity, missing source, ignored tool failure, and missing requirement from a trace-backed research case. |
| V1.1 | Citation And Source Alignment | Reports can tie specific final-answer citations to source snippets and detect citation mismatch. | Citation parser, source-to-claim matcher, URL normalization, source support verdicts. | Demo flags a claim citing an irrelevant page while preserving supported claims. |
| V1.2 | Repair Loop | The Lead Agent can consume Reliability Issues and choose whether to rerun search, revise Product, ask user, or block. | `check_reliability` observation becomes model-visible; issue ids can be referenced by later Work tools. | A Mission improves from needs-review to ship-ready after a revision that addresses report issues. |
| V1.3 | Evaluation Profiles | Teams can select bounded evaluation profiles for research, writing, code-report, or outreach tasks. | Profile-specific requirements, scoring weights, issue taxonomy subsets, and UI labels. | Research and outreach profiles produce different requirement checks from the same runtime contract. |
| V1.5 | Continuous Reliability Gate | Evaluator Runtime can run during long Missions at checkpoints without waiting for final completion. | Trigger policy, partial reports, issue lifecycle, report versioning. | Long Mission shows checkpoint report, then final report with resolved/open issue status. |
| V2.0 | Multi-Agent Reliability Operations | Evaluator Runtime becomes a project-level quality layer across Work Missions. | Report history, trend metrics, issue recurrence, team review workflow. | Project view shows recurring failure modes across several Research Missions. |

## 5. V1.0 Scope

V1.0 supports the canonical Research Mission:

```text
Find 3 AI startups in Toronto working on enterprise AI.
For each, provide a one-sentence summary, source link, and personalized outreach email.
```

V1.0 checks:

- Mission completion gate.
- Requirement Coverage.
- Evidence support for factual claims.
- Tool Failure Ignored.
- Hallucinated Entity risk.
- Low confidence or over-specific claims.
- Basic risky action detection for external actions such as sending email.

V1.0 does not need full citation mismatch if source links are not claim-level yet. Citation mismatch becomes V1.1.

## 6. Product Positioning

The pitch should be:

```text
Most hackathon projects build agents. Hackson also shows whether an agent can be trusted.
Evaluator Runtime records the Work Mission trace, checks research claims against retrieved evidence, and produces a Reliability Report with actionable failure modes.
```

The mature claim is:

```text
We do not prove correctness. We flag reliability risks based on trace, evidence, and requirement coverage.
```

Avoid:

- "Detects all hallucinations."
- "Works for every agent and every task."
- "Guarantees truth."
- "Fully autonomous safety platform."

## 7. Product Integration

Evaluator Runtime belongs under Work Mode first.

Reason:

- Work Mode already owns Mission, Run, Event, Product, Artifact, Work Window, and tool protocol.
- Research evidence naturally enters through Work Mode `web_search`.
- The Work Console already renders trace, Product, Progress, and Diagnostics.
- A separate Evaluator app would duplicate task, trace, and report concepts.

Public product language:

- Work Mode creates the work.
- Evaluator Runtime checks the work.
- Reliability Report is the user-visible deliverable.

## 8. Report Contract

Every Reliability Report MUST include:

- Evaluation profile.
- Score from 0 to 100.
- Status: `ship_ready`, `minor_review`, `needs_human_review`, or `unsafe_to_ship`.
- Summary.
- Issue counts by type and severity.
- Requirement coverage table.
- Claim support table.
- Tool failure summary.
- Evidence Ledger references.
- Suggested fixes.
- Evaluator limitations.

Scores are decision support, not truth labels.

`ship_ready` also requires `mission.status == completed`. Score bands cannot override this gate.

`research_reliability_v1` with an empty Evidence Ledger MUST cap status at `needs_human_review`. A numeric score in the 70-84 range cannot make no-evidence research work a minor review.

Paper-like research Missions MUST check that the final Artifact is a final draft, not only a plan, outline, or chapter map.

Initial status bands:

| Score | Status |
| --- | --- |
| 85-100 | `ship_ready` |
| 70-84 | `minor_review` |
| 50-69 | `needs_human_review` |
| 0-49 | `unsafe_to_ship` |

## 9. Demo Strategy

V1.0 needs two demo cases.

### Case 1: Mostly Successful Research

Mission:

```text
Find 3 Toronto AI companies and summarize what they do with sources.
```

Expected report:

- Score around 85-92.
- Minor issue for weak support or incomplete personalization.
- Demonstrates that the evaluator can pass good work.

### Case 2: Controlled Failure

Trace includes:

- A search result set with real companies.
- One fake company in the final Product.
- One failed search event.
- One missing source link.
- One over-specific claim not supported by snippets.

Expected report:

- Score around 55-70.
- Issues: hallucinated entity, unsupported claim, missing source, ignored tool failure.
- Suggested fixes: rerun search, remove fake company, add source links, revise final Product.

The failure case MUST be replayable without live external APIs.

## 10. Relationship To Work Mode Roadmap

Evaluator Runtime depends on these Work Mode capabilities:

- V1.0 Mission trace and Product/Artifact lineage.
- V1.0.3 review/discussion artifacts, useful but not required.
- V1.0.5 controlled `web_search`, required for strong Research Mission evidence.

Evaluator Runtime can start with fake or replayed search observations before live `web_search` is fully implemented, but public V1.0 should use the same Evidence Ledger schema as live search.

## 11. Open Risks

Known risks:

- LLM-as-judge can be vague or self-confirming.
- Evidence snippets can be too shallow for strong factual verification.
- Score can feel authoritative beyond what the system can prove.
- UI can become noisy if report issues, raw Progress, and Diagnostics compete.
- The Lead Agent may learn to write around the evaluator instead of doing better research.
- Replay data can make the demo look fake unless clearly separated from live mode.

See linked issue notes under `issues/`.
