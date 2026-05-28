## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 5: Demo Replay And Live Mode

## Problem

Live search and model calls can fail during a hackathon demo.

But a fully mocked demo can feel fake if it does not share the real product path.

Evaluator Runtime needs deterministic replay for reliability and a live path for credibility.

## Decision

V1.0 supports both replay and live modes using the same report schema.

Replay mode seeds a Work Mission trace with realistic events, search observations, Products, and failures. Evaluator Runtime runs normally over that trace.

Live mode runs a Research Mission with controlled `web_search`, then evaluates the resulting trace.

## Self-Grilled Decisions

### Is replay dishonest?

No, if it is clearly a deterministic demo case and uses the same evaluator pipeline.

Replay is a resilience tool, not a fake evaluator.

### Should replay skip Work Mode?

No.

Replay should create or load Work Mode-shaped Mission detail so the evaluator exercises the same TraceReader, EvidenceLedgerBuilder, and ReportWriter.

### Should live mode be mandatory for the demo?

Preferred but not mandatory.

The final presentation should be able to fall back to replay if search or provider APIs fail.

## Consequences

- Demo is robust.
- Tests can use replay fixtures.
- The team must clearly label replay cases.

## Acceptance

- Successful replay case and failure replay case exist.
- Live and replay reports share the same JSON schema.
- UI does not need special replay-only components.
