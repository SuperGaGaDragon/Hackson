# Hackson Frontend Integration Blueprint

Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex

## 1. Scope

This frontend pass connects only the backend functions currently verified in `api.md`.

Supported:

- Register.
- Login.
- Current user.
- User settings.
- Idle conversation.
- Idle message history.
- Idle tick.
- Idle join.
- Companion chat.
- Companion message history.
- Work tasks.
- Work task messages.

Not supported in this pass:

- Agent editing.
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
- `POST /api/idle/{conversationId}/join`
- `POST /api/companion/{conversationId}/messages`

UI:

- `Idle`
- `Tick`
- `Auto`
- `Join`
- timeline sorted by `sequence`

Behavior:

- Load or create active idle conversation.
- Load message history.
- `Tick` creates one Agent message.
- `Auto` drives repeated `Tick` calls while the page is open.
- Auto mode alternates `agent_1` and `agent_2` so idle looks like two Agents taking turns.
- `Join` creates a `companion_1` child and freezes the parent idle transcript as transition context.
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

Purpose: show and edit only verified user settings.

Uses:

- `GET /api/users/me`
- `PATCH /api/users/me`
- `POST /api/users/logout`

UI:

- `Me`
- `Name`
- `Idle`
- `Lang`
- `Save`
- `Logout`

### Work

Purpose: create a task and send Work Mode messages.

Uses:

- `GET /api/agents`
- `POST /api/tasks`
- `GET /api/tasks`
- `GET /api/conversations/{conversationId}/messages`
- `POST /api/tasks/{taskId}/messages`

UI:

- `Work`
- `Tasks`
- `Objective`
- `Send`

Behavior:

- List existing tasks.
- Create a new task from an objective.
- Load selected task transcript.
- Send work messages through the task interaction endpoint.
- Show the user message immediately while the model reply is pending.
- New work messages auto-scroll to the bottom.

## 3. API Base

The frontend uses same-origin `/api` calls in local dev.

Default:

```text
/api
```

Local dev proxy:

```text
VITE_API_PROXY_TARGET=http://127.0.0.1:18126
```

Reason:

- `api.md` says target port `8126` is the latest product-level backend smoke for the production MongoDB database `hackson`.
- Local port `18126` is the SSH tunnel to target `127.0.0.1:8126`.
- User registration must land in `hackson.users`, not a temporary review database.
- The same FastAPI app mounts the API paths.
- Browser requests from Vite to a different backend origin can hit CORS.
- Vite proxy keeps browser requests same-origin while forwarding to the active backend.
- `VITE_API_BASE_URL` is reserved for environments where the backend explicitly allows cross-origin requests.
- If `/api/agents` returns 404 through Vite, the dev server is pointed at an older backend process.

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
- Agent display names come from backend `/api/agents`; prompt persona also comes from the same backend catalog.

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
- local render on `127.0.0.1:5173`
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
- Create a task.
- Send a work message.
- Verify `companion_1` follow-up after `Join`.
- Save user settings.
