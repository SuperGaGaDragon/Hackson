## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 27: Completed Mission Follow-Up

## Problem

After a Mission reaches `completed`, the user may still want to keep working with the same Lead Agent.

Examples:

- "Make the final answer more aggressive."
- "Add an English version."
- "Use this Product but change the tone."
- "Continue from here with a second pass."

Using the existing Start button is not product-grade because it does not persist the user's new request as the reason for the new Run. Creating a new Mission every time loses Product, Artifact, Review, Discussion, and Evaluation lineage.

## Decision

V1.0.x MUST support a completed Mission follow-up run.

Default behavior:

- Follow-up stays in the same Mission.
- Backend writes a `USER_FOLLOWUP_REQUESTED` event containing the user's request.
- Backend creates a new Run with `metadata.resumeReason = user_followup`.
- Mission status returns from `completed` to `running`.
- Existing Products and Artifacts remain immutable.
- The Lead Agent sees the follow-up request as a high-priority observation and decides the next tool.

The Lead may:

- revise or append a Product Artifact;
- review current Product state;
- discuss with the Delegate;
- ask the user a clarifying question;
- block or recommend a new Mission when the request is materially a different objective.

## Self-Grilled Decisions

### Same Mission or child Mission?

Default same Mission.

The follow-up is usually a revision or continuation of the existing work. Same-Mission follow-up preserves context, lineage, and user ergonomics. A child Mission can come later when the scope clearly becomes a different project.

### Should follow-up mutate the original goal?

No.

The original goal is historical context. The follow-up request is new trace evidence and should be persisted as a user event plus Run metadata.

### Should completed Missions show Start again?

No.

The normal Start button should stay disabled for completed Missions. Completed Missions should expose a separate Continue action so users understand they are adding a new request, not replaying the original Run.

### Should the stream close on completed?

Yes for the completed Run. A follow-up creates a new running state and the frontend can open a new stream.

## Acceptance

- Completed Mission UI shows a concise follow-up input.
- Submitting follow-up creates `USER_FOLLOWUP_REQUESTED`.
- Mission status becomes `running` and a new Run starts.
- Lead context includes the follow-up request prominently.
- Existing Products and Artifacts are preserved.
- Tests cover follow-up API, route launcher, context visibility, and frontend build.
