# Hackson Frontend Integration Blueprint

Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex

## 1. Scope

This frontend pass connects only the backend functions currently verified in `api.md`.

Supported:

- Register.
- Login.
- Current user.
- User settings.
- Two editable Agent profiles.
- Idle conversation.
- Idle message history.
- Idle tick.
- Idle user interjection.
- Idle join.
- Companion chat.
- Companion message history.
- Workspace Projects.
- Project Missions.
- Mission lead selection from the user's two Agents.
- Mission start and timeline polling.
- User personality and story settings.
- Idle topic direction.

Not supported in this pass:

- Diary.
- Memory cards.
- Relationship editor.
- Model endpoint settings.
- Provider settings.
- API key settings.
- Local model path settings.

## 2. Product Surfaces

### Auth

Purpose: get a JWT.

Uses:

- `POST /api/users/register`
- `POST /api/users/login`
- `GET /api/users/me`

UI:

- `Login`
- `Register`
- `Enter`

### Idle

Purpose: watch and operate the live idle conversation.

Uses:

- `GET /api/agents`
- `GET /api/idle/conversation`
- `GET /api/conversations/{conversationId}/messages`
- `POST /api/idle/{conversationId}/tick`
- `POST /api/idle/{conversationId}/messages`
- `POST /api/idle/{conversationId}/join`
- `POST /api/companion/{conversationId}/messages`

UI:

- `Idle`
- `Tick`
- `Auto`
- `Topic`
- `Say`
- `Join`
- timeline sorted by `sequence`

Behavior:

- Load or create active idle conversation.
- Load message history.
- `Tick` creates one Agent message.
- `Auto` drives repeated `Tick` calls while the page is open.
- `Topic` sends `discussionDirection` to the backend. It is a steering instruction, not a saved message.
- Auto mode alternates `agent_1` and `agent_2` so idle looks like two Agents taking turns.
- `Say` appends a visible user interjection to the same idle conversation and keeps the UI in Idle.
- After `Say`, `Auto` remains clickable and the next tick sees the user line as a user line.
- `Join` is explicit. It creates a `companion_1` child and freezes the parent idle transcript as transition context.
- After `Join`, the UI enters `Companion` mode and sends later turns to the child conversation through `/api/companion/{conversationId}/messages`.
- Parent idle messages and child companion messages are not globally sequence-sorted together; parent context stays above child turns.
- New messages auto-scroll to the bottom of the visible timeline.

Backend note:

- There is no verified backend scheduler or 24x7 idle loop yet.
- Current frontend idle activity is driven by repeated calls to `/api/idle/{conversationId}/tick`.

### Chat

Purpose: user-led companion chat.

Uses:

- `GET /api/agents`
- `POST /api/conversations`
- `GET /api/conversations?mode=companion_2`
- `GET /api/conversations/{conversationId}/messages`
- `POST /api/companion/{conversationId}/messages`

UI:

- `Chat`
- `New`
- `Send`

Behavior:

- List existing `companion_2` conversations.
- Let the user select a conversation.
- Create a new `companion_2` conversation when needed.
- Send through product interaction endpoint.
- Show the user message immediately while the model reply is pending.
- Append returned user and Agent messages.
- New chat messages auto-scroll to the bottom.
- Derive a short local title from the first user message so the sidebar is scannable.

Backend note:

- Conversation history selection does not need a new backend endpoint.
- Auto naming can start in frontend by reading each conversation's first page of messages.
- Product-grade server-side rename would need a future verified endpoint such as `PATCH /api/conversations/{conversationId}`.

### Me

Purpose: show and edit verified user settings and the human user's bounded profile.

Uses:

- `GET /api/users/me`
- `PATCH /api/users/me`
- `POST /api/users/logout`

UI:

- `Me`
- `Name`
- `Idle`
- `Lang`
- `Personality`
- `Story`
- `Save`
- `Logout`

Behavior:

- Save `personality` and `story` through `PATCH /api/users/me`.
- Enforce frontend character limits that match backend validation.
- Never expose model endpoint or provider settings.

### Work

Purpose: manage Projects, create Missions, and supervise Mission progress.

Uses:

- `GET /api/agents`
- `POST /api/work/projects`
- `GET /api/work/projects`
- `POST /api/work/missions`
- `GET /api/work/projects/{projectId}/missions`
- `GET /api/work/missions/{missionId}`
- `POST /api/work/missions/{missionId}/start`
- `GET /api/work/missions/{missionId}/events`

UI:

- `Workspace`
- `New Project`
- `Project`
- `Agents`
- `Missions`
- `Start`
- `Timeline`

Behavior:

- The Work entry screen shows only existing Projects and New Project.
- A Project is created by name only. The UI does not ask for a repo path.
- After a Project is opened, the user can create Missions.
- A Mission lead is selected from the current user's two Agent profiles.
- `Start` runs the V0 deterministic Mission worker.
- The page polls Mission events and renders progress, summary, product, logs, and warnings.

## 3. API Base

The frontend uses same-origin `/api` calls.

Default:

```text
/api
```

Public product environment:

```text
https://hackson.catachess.com/
```

Reason:

- The public app serves FastAPI APIs and React assets from one origin.
- Target backend binds to `127.0.0.1:8145` behind cloudflared.
- User registration lands in MongoDB database `hackson_domain_8145`.
- `VITE_API_BASE_URL` is reserved for explicitly cross-origin environments.
- Old target smoke ports are not product endpoints.

## 4. Frontend Architecture

```text
src/
  api/
    agents.js
    client.js
    users.js
    conversations.js
    interactions.js
    tasks.js
  domain/
    agents.js
    messages.js
  features/
    auth/
    idle/
    chat/
    work/
    me/
  shared/
    components/
  App.jsx
  main.jsx
  styles.css
```

Rules:

- `api/` owns HTTP only.
- `features/` owns product flows.
- `domain/` owns mapping and fallback display data.
- `shared/` owns reusable UI.
- Components do not know raw endpoint paths.
- Normal product messaging never calls raw append.
- Idle `Say` uses `/api/idle/{conversationId}/messages`; it records a visible user interjection and generates the next Agent reply without leaving Idle.
- Agent display names come from the current user's editable `agentProfiles`; `/api/agents` is only the baseline fallback catalog.

## 5. Data Rules

Messages:

- Sort by `sequence`.
- Show `senderSlot` for Agent identity.
- Show user messages as `You`.
- Show unknown system/tool rows plainly.
- Timeline must scroll independently when messages exceed the visible panel.
- The full page must also scroll when the viewport is too short for all panels.
- New messages should scroll the timeline to the latest item.
- Responsive layouts must not let timeline content expand the page infinitely; the page scroll and timeline scroll are separate.
- Idle topic direction must never render as a transcript message unless the backend returns it as a message.

Auth:

- Store JWT in `localStorage`.
- Send `Authorization: Bearer <token>`.
- Clear JWT on logout or unauthorized response.

Errors:

- Keep copy short.
- Show action-local errors.
- Do not show stack traces.

## 6. Verification

Must pass:

- `npm run build`
- public render on `https://hackson.catachess.com/` after deployment
- desktop screenshot
- mobile screenshot

Manual backend verification:

- Login or register.
- Load Idle.
- Click `Tick`.
- Send `Join`.
- Open Chat.
- Send a message.
- Open Work.
- Create a Project.
- Open Project detail.
- Create a Mission with one of the two Agents as lead.
- Start the Mission.
- Verify Mission completion events render.
- Verify `companion_1` follow-up after `Join`.
- Save user settings.
