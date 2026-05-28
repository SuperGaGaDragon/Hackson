## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Evaluator Runtime UI Contract

## 1. Purpose

The UI must make reliability problems obvious without turning the Work Console into a noisy diagnostics dump.

Evaluator Runtime renders as a report surface inside Work Mode. It should feel like a quality report, not a chat message.

## 2. Placement

Work Console order for Research Missions:

```text
Activity
Reliability
Windows
Product
Progress
Diagnostics
```

Alternative acceptable order:

```text
Activity
Windows
Product
Reliability
Progress
Diagnostics
```

Recommendation for demo:

- Put Reliability directly below Activity when a report exists.
- Keep Product visible nearby so users can compare report issues against final content.

## 3. Reliability Panel

Panel content:

- Score card.
- Status label.
- Current report time and report id.
- Issue badges.
- Top issues.
- Requirement coverage table.
- Claim support table.
- Suggested fixes.
- Report limitations.
- Collapsed report history when more than one report exists.

Compact header:

```text
Reliability
68 / 100
Needs Human Review
3 unsupported claims · 1 missing source · 1 ignored tool failure
```

The panel MUST NOT hide high-severity issues behind Diagnostics.

The primary card MUST render the latest `RELIABILITY_REPORTED` event by event sequence. If that event references a `reportArtifactId`, the UI MUST use the matching Reliability Report Artifact payload. Older reports MUST remain available in collapsed history and MUST NOT replace the primary card.

## 4. Score Rendering

Status labels:

| Status | Label |
| --- | --- |
| `ship_ready` | Ship-ready |
| `minor_review` | Minor review |
| `needs_human_review` | Needs human review |
| `unsafe_to_ship` | Unsafe to ship |

Color rules:

- Ship-ready: quiet success.
- Minor review: neutral warning.
- Needs human review: strong warning.
- Unsafe to ship: danger.

Do not render the score as a game-like achievement. It is a quality gate.

## 5. Issue List

Issue row fields:

- Severity.
- Type.
- Title.
- Description.
- Linked claim or requirement.
- Evidence status.
- Suggested fix.

Rows should be expandable. Collapsed row should still reveal what failed.

Issue types should be human-readable:

- Missing requirement.
- Unsupported claim.
- Weakly supported claim.
- Hallucinated entity.
- Missing source.
- Tool failure ignored.
- Unsafe action.
- Evaluation limitation.
- Mission incomplete.

## 6. Requirement Coverage

Coverage table columns:

- Requirement.
- Status.
- Evidence.

Status labels:

- Met.
- Partial.
- Missing.
- Not evaluable.

For the canonical demo, this table should make the "3 companies, summary, source, outreach email" checklist visible.

## 7. Claim Support

Claim support table columns:

- Claim.
- Support level.
- Best source.
- Reason.

Support labels:

- Supported.
- Weak.
- Unsupported.
- Contradicted.
- Not evaluable.

Long claim text should wrap. Source links should use the source host as visible label when possible.

## 8. Trace References

Issue rows MAY link to:

- event sequence.
- Artifact id.
- Product id.
- source URL.

The first implementation can show references as compact text. Later UI can scroll to the referenced Progress row or Product Artifact.

## 9. Inspector Integration

Inspector should show:

- Latest reliability score.
- Latest report status.
- Open high/critical issue count.
- Evaluation profile.

Inspector MUST NOT duplicate the full issue list.

## 10. Progress Integration

Progress should include:

- `EVALUATION_STARTED`
- `RELIABILITY_REPORTED`
- `EVALUATION_FAILED`

Expanded `RELIABILITY_REPORTED` details should show:

- Score.
- Status.
- Issue counts.
- Report Artifact id.

Expanded `EVALUATION_STARTED` details should show:

- Profile.
- Mode.
- Evaluator version.

Expanded `EVALUATION_FAILED` details should show:

- Stable error code.
- Message.
- Evaluator version.

## 11. Diagnostics

Diagnostics may show raw report payload.

Diagnostics MUST be collapsed by default.

Diagnostics is not the primary report surface.

## 12. Empty States

No report:

```text
No reliability report
```

Evaluation unsupported:

```text
This Mission does not match the research reliability profile.
```

Evaluation failed:

```text
Evaluation failed
```

Include stable error code in expanded details.

## 13. Demo Requirements

Browser smoke should verify:

- Score is visible.
- Status is visible.
- Latest report is selected after repeated evaluation.
- Older report history is collapsed but expandable.
- At least one issue badge is visible.
- Requirement coverage renders.
- Claim support renders.
- Progress contains `RELIABILITY_REPORTED`.
- Diagnostics remains collapsed.
- Mobile has no horizontal overflow.
