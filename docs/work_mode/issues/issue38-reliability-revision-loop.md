## header
Created at: 2026-05-29
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex

# Issue 38: Reliability Revision Loop

## Problem

Public Work Missions can enter a loop where the Lead keeps trying to repair a Product after Reliability reports,
but the Mission does not reach a normal completed state. The user-facing symptom is that Reliability scores move up
and down while the actual Product does not feel materially repaired.

The suspected failure modes are:

- The Lead creates a fresh Product or fresh draft repeatedly instead of revising the current deliverable lineage.
- The Lead edits content, but the Reliability evaluator is reading the wrong candidate or an old report.
- The evaluator score is too volatile for small textual changes and blocks completion without a stable exit path.
- The tool feedback after `reliability_evaluation_needs_review` is not concrete enough for the Lead to make the next
  revision decision.

## Diagnosis Plan

1. Inspect the stuck public Mission event chain and Product/Artifact lineage without stopping public services.
2. Count Product updates, final candidates, Reliability reports, and `finish_mission` rejections.
3. Compare each Reliability report's evaluated Artifact id with the latest deliverable candidate at that moment.
4. Determine whether the loop is caused by missing revision lineage, evaluator candidate mismatch, or unstable scoring.
5. Build a deterministic regression test at the Mission loop or tool-executor seam.

## Findings

The stuck public Mission did not prove that Product revision was missing. The event chain shows one Product with a long
Artifact lineage and repeated `revise_artifact` / `append_artifact` actions. The core failure was evaluator-side:

- Reliability applied a high-severity `mission_incomplete` issue whenever the Mission status was not `completed`.
- Work Mode requires a passing Reliability report before `finish_mission`.
- Those two rules created a circular gate: while the Mission was still running, the candidate was penalized for not
  already being completed, so the Lead kept repairing instead of converging.
- EvaluatorRuntime used the public Mission detail endpoint, which is UI-limited, so long Missions could lose older
  search evidence during evaluation.
- Reference and URL lines could be parsed as factual claims or entities, causing noisy unsupported-claim and
  hallucinated-entity issues unrelated to the actual deliverable quality.

## Implemented Fix

- Running Missions are evaluated as active candidates. `mission_incomplete` is still emitted for paused, failed,
  blocked, stopped, or unknown statuses.
- EvaluatorRuntime reads a backend-only complete Mission trace for evaluation instead of the UI-limited detail payload.
- Candidate selection prefers the Product `deliverableArtifactId` before older completion/final fallbacks.
- Claim extraction ignores References/Bibliography/Sources blocks, standalone URL/source lines, and APA-style reference
  entries.
- Entity and token extraction strips URLs before factual support checks, preventing URL slugs from becoming
  hallucinated entities.
- Requirements are extracted from Mission title plus goal so user constraints such as `3000 words` in the title are not
  lost.
- Reliability now checks obvious deliverable constraints for long research writing: body word count, requested English
  language, and APA-style citation shape.
- `ship_ready` is blocked by any remaining high-severity issue, even if the numeric score is near the threshold.
- Regression tests cover running-candidate scoring, current deliverable targeting, reference URL lines, and title-level
  word-count gates.

## Product Standard

Reliability must be a convergence mechanism, not a slot machine:

- A Reliability report must be tied to one explicit evaluated Artifact.
- A repair turn must know exactly which Artifact/report it is repairing.
- Completion gating must reject stale or unresolved Reliability reports, but it must not trap the Lead in an
  unbounded rewrite cycle.
- If multiple repair attempts fail to resolve the same blocking issue, the Mission should pause retryably with a
  precise reason instead of continuing indefinitely.

## Self-Grill

### Are we solving score volatility or a broken product loop?

We are solving a broken product loop. Score volatility is a symptom. The deeper bug is that Work Mode cannot currently
prove that a Reliability report evaluated the exact final Artifact that `finish_mission` is trying to ship. A numeric
score should never be the only gate because small extractor changes can move it. The gate must be anchored to explicit
candidate identity, candidate content hash, report freshness, and unresolved blocking issues.

Decision: make Reliability candidate-bound first, then make score presentation secondary.

### Is the model actually failing to revise?

Not primarily. Public traces show one Product with a long Artifact lineage. The Lead is creating revised Artifacts.
The bad loop happens because the runtime feedback is not concrete enough:

- `evaluate_product` validates requested ids but the Evaluator still chooses its own target from Mission state.
- The report does not persist `evaluatedArtifactIds` or `evaluatedArtifactHashes`.
- `finish_mission` can only ask "is there a recent report after the last Product update?", not "does this report cover
  the exact final Artifact ids being shipped?"
- A rejected `finish_mission` tells the Lead to repair quality in general terms, not which report/candidate/issue is
  blocking completion.

Decision: the repair loop must be driven by report target metadata and issue ids, not by vague natural-language
feedback.

### Should a low Reliability score block forever?

No. A low score may indicate high risk, but the runtime must still converge to one of four states:

- `pass`: no blocking issue remains for the selected final candidate.
- `repair_required`: there are concrete model-fixable issues and the Lead gets a repair contract.
- `human_review`: the same blocking issue survived repeated repair attempts or the evidence boundary is insufficient.
- `blocked`: unsafe or structurally impossible without changed requirements.

Decision: introduce a gate status for execution control. Keep `score` as risk triage for humans and UI.

### Should the evaluator mutate Product content?

No. Evaluator Runtime remains read-only. It can produce a Reliability Report and a repair contract. Work Mode tools
still own all Product mutation through immutable Artifact creation.

Decision: no hidden auto-rewrite inside evaluator.

### What would make this feel product-grade to a user?

The user should see and the Lead should receive:

- what was evaluated,
- why it cannot finish,
- what needs to change,
- whether the latest draft is newer than the latest report,
- when the system stops retrying and asks for review.

Decision: the UI and model observation should treat Reliability as a clear checklist, not a fluctuating scoreboard.

## Final Repair Design

### Canonical Terms

- **Candidate Artifact**: the exact deliverable Artifact being evaluated or shipped.
- **Candidate Hash**: a normalized SHA-256 hash of the Candidate Artifact content at evaluation time.
- **Reliability Report**: an immutable report bound to one or more Candidate Artifacts and a Mission trace snapshot.
- **Reliability Gate**: deterministic execution status derived from report issues and freshness.
- **Repair Contract**: model-visible structured instructions for the next repair action.
- **Repair Attempt**: a Product update made after a blocking Reliability Report.

### Report Target Binding

`evaluate_product` MUST pass requested `productIds` and `artifactIds` into Evaluator Runtime. The Evaluator MUST choose
targets in this order:

1. Explicit `artifactIds` from the tool call.
2. The selected Product `deliverableArtifactId`.
3. The current final Product Artifact if the Product has been finalized.
4. A rejected `evaluation_target_required` result when no deliverable candidate exists.

The report payload MUST persist:

```json
{
  "evaluatedProductIds": ["product_id"],
  "evaluatedArtifactIds": ["artifact_id"],
  "evaluatedArtifactHashes": {
    "artifact_id": "sha256..."
  },
  "targetSelectionReason": "explicit_tool_args|product_deliverable|product_final",
  "traceSnapshot": {
    "latestProductEventSequence": 117,
    "latestSearchEventSequence": 42,
    "evaluatorVersion": "string"
  }
}
```

### Gate Status

Every report MUST include `gateStatus`:

| gateStatus | Meaning | Runtime action |
| --- | --- | --- |
| `pass` | No actionable critical/high/medium issue remains for the evaluated candidate. | `finish_mission` may proceed if hashes match final ids. |
| `repair_required` | Concrete issues remain and can be repaired with search/revision/discussion. | Lead receives a repair contract. |
| `human_review` | Evidence boundary is insufficient or repeated repair attempts did not converge. | Pause retryably or ask user, not endless rewriting. |
| `blocked` | Unsafe or structurally impossible state. | Block or stop with precise reason. |

`score` remains visible, but the Lead loop should optimize for resolving blocking issues, not for chasing a numeric
threshold.

### Finish Gate

`finish_mission` MUST reject completion unless the latest Reliability Report:

1. exists,
2. is newer than the latest Product update,
3. covers the exact `finalArtifactIds`,
4. stores hashes matching the current final Artifact content,
5. has `gateStatus="pass"` or an explicitly allowed non-blocking status,
6. has no actionable critical/high/medium issue except obsolete `mission_incomplete`.

If any condition fails, the rejection observation MUST include:

```json
{
  "code": "reliability_evaluation_required",
  "requiredTool": "evaluate_product",
  "finalArtifactIds": ["artifact_id"],
  "latestReportArtifactId": "artifact_id|null",
  "latestReportCoversFinalArtifacts": false,
  "latestProductUpdatedAfterReport": true,
  "blockingIssueIds": ["I1", "I2"]
}
```

### Repair Contract

`evaluate_product` observation MUST return enough information for the Lead to take the next valid action:

```json
{
  "tool": "evaluate_product",
  "status": "ok",
  "gateStatus": "repair_required",
  "evaluatedArtifactIds": ["artifact_id"],
  "evaluatedArtifactHashes": {"artifact_id": "sha256..."},
  "blockingIssues": [
    {
      "id": "I1",
      "type": "unsupported_claim",
      "severity": "high",
      "artifactIds": ["artifact_id"],
      "requiredAction": "remove_or_source",
      "suggestedTool": "web_search|work_product"
    }
  ],
  "nextActionContract": {
    "ifEditing": {
      "tool": "work_product",
      "operation": "revise_artifact",
      "sourceArtifactIds": ["artifact_id"]
    },
    "afterEditing": {
      "tool": "evaluate_product",
      "artifactIds": ["new_artifact_id"]
    },
    "finishOnlyAfter": "gateStatus pass and report hashes match finalArtifactIds"
  }
}
```

### Convergence Control

The runtime MUST detect repeated non-convergence:

- Build an issue signature from `type`, normalized claim/requirement text, and evaluated Artifact target.
- If the same blocking signature appears after two repair attempts, set `gateStatus="human_review"` and recommend
  `ask_user` or `block_mission`, not another blind rewrite.
- If the Lead calls `finish_mission` repeatedly without a fresh passing report, pause retryably with
  `reliability_repair_not_converging`.
- The Mission should stop cleanly with a readable reason instead of exhausting turn budget after another vague retry.

### UI Standard

The Work UI MUST show Reliability as a gate card:

- `Evaluated`: Product title, Artifact title, revision time, and current/stale status.
- `Gate`: Pass, Needs repair, Human review, or Blocked.
- `Blocking issues`: issue ids, severity, direct fix instruction, source/Artifact references.
- `Freshness`: "A newer draft exists; run Check again" when the latest Product update is newer than the report.
- `History`: older reports remain readable but cannot be confused with the current gate.

Do not make users infer state from a raw score that moves up and down.

## Implementation Slices

### Slice 1: Backend Target Binding

- Extend `EvaluatorRuntime.evaluate` to accept `product_ids`, `artifact_ids`, and `focus`.
- Add target selection helper that rejects missing candidates instead of silently falling back to an unrelated Artifact.
- Persist evaluated Product ids, Artifact ids, content hashes, and trace snapshot in report payload and
  `RELIABILITY_REPORTED` event payload.
- Update `evaluate_product` to pass validated ids into Evaluator Runtime.

### Slice 2: Completion Gate

- Add `report_covers_final_artifacts(report, detail, finalArtifactIds)`.
- Require matching ids and hashes before `finish_mission` can complete.
- Return structured rejection details for stale report, wrong target, hash mismatch, and unresolved blocking issues.

### Slice 3: Gate Status And Repair Contract

- Add `gateStatus` and `blockingIssues` to Reliability Report schema.
- Add `nextActionContract` to the model-visible `evaluate_product` observation.
- Stop using score thresholds as the model's primary repair instruction.

### Slice 4: Convergence Guard

- Store or derive repair attempt count from events after each report.
- Detect repeated blocking issue signatures.
- Pause retryably with `reliability_repair_not_converging` after bounded attempts.

### Slice 5: UI Clarity

- Show evaluated candidate and freshness in the Reliability panel.
- Add stale-report copy and Check Again action.
- Keep numeric score but visually subordinate it to gate status and blocking issue list.

## Implemented Closure 2026-05-29

Backend closure now implements the critical reliability loop fix:

- `EvaluatorRuntime.evaluate` accepts `product_ids`, `artifact_ids`, and `focus`.
- `evaluate_product` passes the validated ids through instead of letting Evaluator Runtime silently choose another
  candidate.
- Reliability Reports persist `gateStatus`, `evaluatedProductIds`, `evaluatedArtifactIds`,
  `evaluatedArtifactHashes`, `targetSelectionReason`, and `traceSnapshot`.
- `RELIABILITY_REPORTED` events expose the same target metadata so UI and logs can identify what was evaluated.
- Idempotent report reuse now requires the same evaluator version and the same evaluated Artifact id/hash.
- `finish_mission` for research/paper-like Missions rejects reports that do not cover the exact final Artifact ids and
  current content hashes.
- `evaluate_product` observations now include `blockingIssues` and `nextActionContract` so the Lead receives a concrete
  repair target.
- Repeated blocking issue signatures across historical reports move the gate to `human_review`, preventing endless
  blind rewrite/evaluate loops.

Verified regression tests:

- Explicit `artifactIds` are honored even when a newer deliverable exists.
- Report payload and report event include evaluated Artifact ids and hashes.
- A report for an old Artifact cannot satisfy `finish_mission` for a newer final Artifact.
- Repeated blocking issues escalate the gate to `human_review`.
- Work Mode backend suite passes after the fix.

## Acceptance

- The stuck public Mission has a concrete root-cause analysis recorded from logs/database state.
- A regression test reproduces the observed loop pattern.
- The fix forces Reliability repair to converge on the current deliverable lineage or pause with a clear actionable
  reason.
- Target-machine isolated tests pass without stopping existing public services.
- `evaluate_product(productIds, artifactIds)` evaluates exactly those Artifact ids.
- `finish_mission(finalArtifactIds)` rejects a report bound to any older or different Artifact.
- A Product update after a report makes that report stale until a new report evaluates the new Candidate Artifact hash.
- The same unresolved blocking issue cannot trigger unbounded rewrite/evaluate cycles; it must become `human_review` or
  `paused_retryable`.
