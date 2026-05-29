## header
Created at: 2026-05-29
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex

# Issue 14: Idle Brainstorm Card To Work Mission

## Problem

Idle can produce useful raw conversation, but the current product leaves the user to manually copy ideas into Work Mode.

The existing summary runtime is not enough because it is a context-compression layer. It is optimized for prompt budget and auditability, not for a user-facing decision moment. A product-grade Idle-to-Work loop needs an explicit card the user can inspect, edit, and promote into a draft Work Mission.

## Grill

Q: Should Idle automatically create Work Missions when the Agents converge?

A: No. That would pollute Work with model-authored guesses. Idle may suggest a mission, but the user must confirm the title, goal, lead Agent, and target Project.

Q: Should the card be backed by the existing persisted `Summary` worker?

A: Not as the first implementation. Persisted summaries are allowed to be lossy context inputs. The Brainstorm Card is a product surface and must be rebuilt from raw source messages with explicit source message ids. The worker can later improve wording, but the card contract must not depend on background jobs.

Q: Should this expose hidden reasoning?

A: No. The card uses visible transcript messages only. It must not store or display chain-of-thought, hidden prompt text, or internal model notes.

Q: What makes the card trustworthy enough for a demo?

A: The user sees fixed sections, source count, and source message ids. The suggested Mission is editable before creation. Promotion creates a draft Mission through the existing Work API instead of starting execution.

## Decision

Add a backend-owned Idle Brainstorm Card endpoint.

The card shape:

- `topic`
- `keyIdeas`
- `disagreements`
- `decision`
- `openQuestions`
- `suggestedMission.title`
- `suggestedMission.goal`
- `sourceMessageIds`
- `sourceMessageCount`
- `generatedAt`

Rules:

- The card is built from visible raw Idle messages for the authenticated user.
- Source message ids are mandatory.
- The endpoint may return a deterministic card without a model call.
- The frontend must let the user refresh the card.
- The frontend must let the user edit Mission title and goal before creation.
- The frontend must require an existing or newly created Work Project before promotion.
- Promotion uses `POST /api/work/missions` and creates a `draft` Mission.
- Promotion metadata must record `source: idle_brainstorm`, `idleConversationId`, and `sourceMessageIds`.

## Product Contract

Idle owns discovery and conversation.

Work owns execution.

The boundary is the user-confirmed Mission draft:

```text
Idle transcript
  -> Brainstorm Card
  -> user edits Mission draft
  -> Work Project + draft Mission
```

The card should feel like a concise brief, not a debug dump. Source ids belong behind a compact disclosure surface.

## Risks

- A deterministic card can feel less intelligent than a model-written card.
- A model-written card can hallucinate decisions that were not in the transcript.
- A one-click promotion button can create messy Work data if no edit step exists.
- A Project picker can become noisy if the user has many Projects.

The first implementation chooses deterministic extraction plus user editing. A later model-backed version can keep the same API shape and add provenance.

## Acceptance

- Backend route returns a Brainstorm Card for an Idle conversation.
- Backend rejects non-Idle conversations.
- Backend returns source message ids for every card.
- Frontend Idle right rail can build and refresh the card.
- Frontend promotion modal lets the user choose an existing Project or create a new one.
- Frontend lets the user edit title, goal, and lead Agent.
- Created Work Mission includes `idle_brainstorm` metadata and remains draft.
- User can jump to the created Work Mission.
- Local backend tests, frontend build, and target-machine smoke pass before public promotion.
