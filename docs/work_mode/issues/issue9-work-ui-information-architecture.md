## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 9: Work UI Information Architecture

## Problem

The current Work UI makes every event look equally important. Model state, tool choice, work-window state, product updates, and raw diagnostics all render as similar timeline cards. This is confusing for long Missions because users cannot quickly answer:

- Is the Mission alive?
- Which Agent window is doing work?
- Where is the readable deliverable?
- What is raw diagnostic noise?

The Product Panel also currently favors one latest Artifact. For multi-part writing, that can make the UI appear to lose earlier chapters even when the backend persisted them.

## Self-Grilled Decisions

### 1. What is the main user job?

The user wants confidence and readable output, not raw telemetry.

Decision:

- The main Mission surface MUST prioritize current activity, Work Windows, and Product before the full Progress feed.
- The user should be able to see who is working and what was produced without opening raw logs.

### 2. Should `Progress` own everything?

No.

Decision:

- `Progress` is an audit trail.
- `Work Windows` is the Agent work-unit surface.
- `Product` is the canonical deliverable reader.
- `Diagnostics` is the raw event/debug surface.

### 3. Should timestamps replace sequence numbers?

Yes for primary UI.

Decision:

- Event rows MUST show local clock time when `createdAt` exists.
- Sequence number MAY remain as a muted diagnostic token.
- Large `#sequence` labels MUST NOT be the primary temporal signal.

### 4. How should `Thinking`, `Tool selected`, and `Started` differ?

They are different semantic layers.

Decision:

- Model state events render compactly as activity/state.
- Tool decisions render as decision/action rows.
- Product and Work Window events render as output/state-change rows.
- Failure, pause, and retry events use stronger visual treatment.
- Heartbeats are not allowed to create a wall of identical large cards.

### 5. What is a Work Window?

A Work Window is a delegated work unit, not a file and not a final product.

Decision:

- Work Windows MUST appear above Progress.
- Work Windows MUST be collapsed by default.
- A window summary MUST show title, delegate Agent slot, status, and linked result Artifact when available.

### 6. What is a Product?

A Product is the user-readable deliverable.

Decision:

- Product Panel MUST expose Product list and Artifact lineage.
- Product Panel MUST NOT show only the latest Artifact as if it were the entire deliverable.
- If a final Product exists, default to the final Artifact.
- If no final Product exists, render a draft stack that keeps every Product Artifact visible in order.

### 7. What are Logs?

Logs are diagnostics, not normal user content.

Decision:

- Rename `Logs` to `Diagnostics`.
- Diagnostics MUST be collapsed by default.
- Diagnostics SHOULD show raw event payloads for engineering/debug use.

## Required UI Order

The Mission Console MUST render in this order:

1. Current Activity.
2. Work Windows.
3. Product.
4. Progress.
5. Diagnostics.

The side rail MAY show Inspector and warnings.

## Acceptance

- Work Windows appear above Progress.
- Product Panel shows Artifact lineage and readable content.
- Product Panel does not hide earlier chapter Artifacts when no final Artifact exists.
- Progress rows show local time and compact sequence metadata.
- Model state, tool decisions, products, windows, and failures have distinct visual classes.
- Diagnostics is collapsed by default and contains raw event detail.
- Browser smoke verifies ordering, Product lineage, Diagnostics, and full final Product content.

## Follow-Up

V1.2 streaming can add partial-progress tokens, but it MUST reuse the same information architecture: activity first, windows/product second, audit trail third, diagnostics last.
