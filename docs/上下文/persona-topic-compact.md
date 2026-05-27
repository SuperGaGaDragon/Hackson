# Agent Profiles, Idle Topics, Speaker Boundary, and Compact Plan

Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex

## 1. Product Goal

This slice turns the current demo into a controlled product loop:

- The user can tell the system what kind of person they are and add a bounded story.
- Each user owns two editable Agents, seeded as Nora and Vale.
- Idle has explicit history selection and a New topic modal.
- Idle can be steered by a user topic without pretending that the topic is a chat message.
- Every model call can distinguish User, Nora, and Vale.
- Long histories keep recent turns raw and older turns compacted.

No placeholder product surface is allowed in this slice. The frontend may only expose fields and controls that the backend stores or consumes in the same verified code path.

## 2. User Profile and Two Agents

The user profile is not an Agent persona. It is the human user's preference and background record.

Fields:

- `display_name`: existing public display name.
- `idle_on`: existing idle preference.
- `language_preference`: existing reply language preference.
- `personality`: short user personality note, max 1200 characters.
- `story`: bounded user background story, max 4000 characters.

Rules:

- Store profile fields on the existing user document.
- Return profile fields from register, login, `GET /api/users/me`, and `PATCH /api/users/me`.
- Context may read these fields, but model output must never claim to rewrite them.
- Empty fields are valid and mean "no user profile constraint".

Every user also owns exactly two editable Agent profiles. They are not global catalog records.

Fields per Agent:

- `slot`: fixed `agent_1` or `agent_2`.
- `name`: visible name, max 32 characters.
- `short`: backend-controlled display short label.
- `color`: backend-controlled display color.
- `voice`: visible voice label, max 80 characters.
- `personality`: Agent core persona, max 1200 characters.
- `story`: Agent background or episode state, max 4000 characters.

Rules:

- Registration seeds two profiles from the backend catalog: Nora and Vale.
- `PATCH /api/users/me` can update both Agent profiles in one request.
- Context receives these profiles as `AgentPersonaSnapshot`.
- If a stored profile is missing or malformed, backend normalization falls back to the default catalog for that slot.
- The frontend must show both Agent editors, not one shared profile editor.

## 3. Idle Topic Direction and History

Idle topic direction is an instruction for the next idle generation. It is not a transcript message.

API shape:

```json
{
  "targetAgentId": "agent_1",
  "discussionDirection": "希望从产品演示怎么讲清楚这个方向展开",
  "idleSeed": "继续 idle 对话，保持自然、简短、有生活感。"
}
```

Behavior:

- `discussionDirection` is optional.
- The backend includes it in context under `User direction`.
- The backend must not save it as a user message.
- The frontend stores topic direction on the selected idle conversation metadata and sends it with `Tick` and `Auto`.
- If the user leaves it empty, Idle continues from the latest transcript.

Idle history uses the existing conversation APIs:

- `GET /api/conversations?mode=idle` lists idle topics.
- `POST /api/conversations` with `mode=idle`, `title`, and `metadata.topicDirection` creates a clean idle topic.
- Selecting a history item loads that conversation's messages.
- `GET /api/idle/conversation` remains as a backward-compatible fallback, but the product UI should prefer explicit history.

New topic UI:

- User clicks `New`.
- A modal opens.
- User must enter topic direction.
- Frontend creates the idle conversation, selects it, clears messages, and keeps Auto off.

## 4. Speaker Boundary

The prompt must use explicit speaker names:

- Agent slot `agent_1` is Nora.
- Agent slot `agent_2` is Vale.
- User messages are `User` or the user's display name when available.
- Topic direction is `User direction`, not `User: ...`.

Idle recipe rules:

- Recent transcript contains only visible conversation events.
- The current speaking Agent answers as themselves.
- The model continues from the latest visible message.
- The model treats user direction as steering, not as something Nora or Vale already said.

Companion recipe rules:

- The current user message is the center of the turn.
- Recent companion transcript can contain both user and Agent messages.
- User profile can be included as a constraint, but it is separate from Agent persona.

## 5. Compact

V1 compact uses a simple product-safe policy:

- Keep the newest 20 messages available to interaction orchestration.
- Context recipes still apply their own smaller visible limit.
- When a conversation has more than 20 messages, build a deterministic compact summary from older messages.
- Include that compact summary through the existing `summary` field in `ContextBuildInput`.

This is not a replacement for persisted summaries. Raw messages remain the source of truth. Derived summary workers can later replace the deterministic compact block, but the product must already behave correctly when workers are absent.

Compact text requirements:

- Say how many older turns were compacted.
- Preserve speaker labels.
- Keep a small number of representative older lines.
- Never drop the latest raw turns.

## 6. Frontend Surfaces

### Me

Expose:

- `Name`
- `Lang`
- `Idle`
- `Personality`
- `Story`
- `Nora`
- `Vale`
- `Save`
- `Logout`

Copy must stay terse. Character counts are allowed because the backend enforces hard limits.

### Idle

Expose:

- `History`
- `New`
- `Topic`
- `Target`
- `Auto`
- `Tick`
- `Join`

Behavior:

- Topic comes from the selected idle conversation metadata.
- New opens a modal and creates a clean idle conversation.
- Auto uses the same topic as Tick.
- Join still creates a `companion_1` child and does not write Topic as a message.

## 7. Test Plan

Backend tests:

- User update stores and returns personality/story.
- User update stores and returns both Agent profiles.
- Idle context includes user profile and topic direction separately.
- Idle context uses user-specific Agent profiles.
- Interaction service passes real user profile into context.
- Long idle history includes compact summary and newest raw messages.
- Idle topic direction is not saved as a user message.

Frontend verification:

- Save profile fields in `Me`.
- Edit both Agent profiles in `Me`.
- Create a new Idle topic from the modal.
- Select an older Idle topic from history.
- Run Idle `Tick` with `Topic`.
- Toggle `Auto` with the same `Topic`.
- Confirm timeline shows Nora/Vale speaker identity and the page still scrolls.

## 8. Deployment Rule

The target machine remains authoritative for backend verification. This slice must use a new target-machine port for smoke testing and must not stop any existing target service.
