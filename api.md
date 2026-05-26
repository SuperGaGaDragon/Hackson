## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex

## brief intro
- This document is the verified API and port map for Hackson.
- Only APIs that have been tested on the target machine are listed here.
- Backend uses FastAPI. Frontend uses React + Vite.
- V1 demo model endpoint is platform-managed and is not exposed through user APIs.

## verified environment
- Target machine: documented locally in `docs/数据库/machine.md`; that file is ignored and must not be pushed.
- Backend test directory on target machine: `~/hackson_backend_test/backend`
- Verified raw user/conversation backend command:

```bash
HACKSON_MONGO_DATABASE=hackson_test \
HACKSON_JWT_SECRET=target-test-secret-with-more-than-32-bytes \
PYTHONPATH=. \
uvicorn main:app --host 127.0.0.1 --port 8100
```

- Verified interaction/model backend command:

```bash
cd ~/hackson_backend_test/backend
.venv/bin/python -m uvicorn main:app --host 127.0.0.1 --port 8101
```

- Verified raw user/conversation port: `127.0.0.1:8100`
- Verified interaction/model port: `127.0.0.1:8101`
- Port status after verification: stopped/free
- Database used in raw user/conversation verification: MongoDB database `hackson_test`
- Database used in interaction/model verification: MongoDB database `hackson_target_smoke`
- Production database initialized: MongoDB database `hackson`
- Production database status:
  - collections: `users`, `conversations`, `messages`, `conversation_counters`
  - `users` indexes: `_id_`, `username_normalized_1` unique, `email_normalized_1` unique
  - `conversations` indexes: `_id_`, `user_id_1_mode_1_status_1_updated_at_-1`, `user_id_1_mode_1_last_message_at_-1`, `parent_conversation_id_1`
  - `messages` indexes: `_id_`, `conversation_id_1_sequence_1` unique, `conversation_id_1_created_at_-1`, `user_id_1_created_at_-1`, `user_id_1_sender_slot_1_created_at_-1`
  - `conversation_counters` indexes: `_id_`, `conversation_id_1` unique
- Last verified at: 2026-05-25

## port map
| Port | Service | Bind | Status | Purpose |
| --- | --- | --- | --- | --- |
| 8100 | FastAPI backend temporary test server | `127.0.0.1` | Verified, not kept running | Target-machine raw user/conversation API verification without touching existing services |
| 8101 | FastAPI backend temporary test server | `127.0.0.1` | Running on target machine during latest frontend check | Target-machine interaction/context/model API verification without touching existing services |
| 8120 | FastAPI backend temporary test server | `127.0.0.1` | Verified, stopped after check | Target-machine Agent catalog API verification without touching existing services |
| 8122 | FastAPI backend temporary test server | `127.0.0.1` | Verified, running during latest diagnosis | Target-machine latest backend verification for Agent catalog and idle join without touching existing services |
| 5173 | Vite frontend temporary dev server | `127.0.0.1` | Running locally | Hackson React frontend prototype |
| 18101 | SSH local tunnel to target backend | `127.0.0.1` | Running locally during latest frontend check | Local browser access to target-machine `127.0.0.1:8101` |
| 5175 | Vite frontend temporary dev server with API proxy | `127.0.0.1` | Running locally during latest frontend check | Local frontend connected to target backend through Vite proxy |

## api端口集合
| Method | API | Auth | Verified Port | Module | Purpose |
| --- | --- | --- | --- | --- | --- |
| GET | `/health` | No | `8100`, `8101` | `backend/main.py` | Backend health check |
| POST | `/api/users/register` | No | `8100`, `8101` | `backend/users/` | Register user and return JWT |
| POST | `/api/users/login` | No | `8100` | `backend/users/` | Login by email or username |
| GET | `/api/users/me` | Bearer JWT | `8100` | `backend/users/` | Read current user |
| PATCH | `/api/users/me` | Bearer JWT | `8100` | `backend/users/` | Update current user settings |
| POST | `/api/users/logout` | No server state | `8100` | `backend/users/` | Client-side JWT logout placeholder |
| GET | `/api/agents` | No | `8120`, `8122` | `backend/agents/` | List fixed V1 Agent display profiles |
| POST | `/api/conversations` | Bearer JWT | `8100`, `8101` | `backend/conversations/` | Create conversation container |
| GET | `/api/conversations` | Bearer JWT | `8100` | `backend/conversations/` | List current user's conversations |
| GET | `/api/conversations/{conversationId}` | Bearer JWT | `8100` | `backend/conversations/` | Read one owned conversation |
| POST | `/api/conversations/{conversationId}/messages` | Bearer JWT | `8100` | `backend/conversations/` | Append raw historical message |
| GET | `/api/conversations/{conversationId}/messages` | Bearer JWT | `8100`, `8101` | `backend/conversations/` | Page conversation messages |
| GET | `/api/idle/conversation` | Bearer JWT | `8100`, `8101` | `backend/conversations/` | Get or create active idle conversation |
| POST | `/api/idle/{conversationId}/tick` | Bearer JWT | `8101` | `backend/interactions/` | Generate one idle Agent reply |
| POST | `/api/idle/{conversationId}/join` | Bearer JWT | `8101`, `8122` | `backend/interactions/` | Create companion_1 from idle and reply |
| POST | `/api/companion/{conversationId}/messages` | Bearer JWT | `8101` | `backend/interactions/` | Save companion_2 user message and reply |

Notes:
- Ports `8100` and `8101` were temporary target-machine verification ports and are not kept running.
- The API paths are mounted by the same FastAPI app; use the active backend deployment base URL in production.
- Detailed request and response shapes are listed below.

## verified frontend

### React + Vite frontend
Purpose: local frontend for verified Auth, Idle, Chat, and Me backend flows.

Directory:

```text
frontend/
```

Run:

```bash
cd frontend
npm install
npm run dev -- --port 5173
```

Verified URL:

```text
http://127.0.0.1:5173/
```

Verified checks:

- `npm run build`
- desktop screenshot at `1440x960`
- mobile screenshot at `390x844`
- target-machine API smoke through `8101`
- local browser E2E through SSH tunnel `18101` and Vite port `5175`

Notes:
- Frontend does not expose model endpoint, provider, API key, Claude/OpenAI key, or local model path settings.
- V1 product copy is intentionally short per `agents/frontend_restrictions.md`.
- Current frontend only renders backend-backed surfaces: Auth, Idle, Chat, and Me.
- Idle uses `/api/idle/conversation`, message history, `/api/idle/{conversationId}/tick`, and `/api/idle/{conversationId}/join`.
- Chat uses `companion_2` conversation creation/history and `/api/companion/{conversationId}/messages`.
- Local browser checks should use Vite proxy to avoid CORS:

```bash
ssh -N -L 127.0.0.1:18101:127.0.0.1:8101 catadragon@100.70.248.39
VITE_API_PROXY_TARGET=http://127.0.0.1:18101 npm run dev -- --port 5175
```

Latest frontend E2E result:
- Register succeeded.
- Idle loaded.
- Tick created one Agent message.
- Join created a `companion_1` child with user and Agent messages.
- Chat created/sent a `companion_2` message pair.
- Me loaded current user settings.

Latest frontend issue check:
- Idle / `companion_1` link is backend-healthy. Frontend now keeps parent idle history visible, inserts a `Joined` event, then shows returned `companion_1` user and Agent messages.
- `companion_2` history selection uses existing `GET /api/conversations?mode=companion_2` plus message history. No new backend endpoint is required for selection.
- Local auto title is derived from the first user message. Persistent server-side renaming would require a future verified conversation update endpoint.
- Browser E2E verified: two idle ticks, join continuity from 2 to 4 visible messages, two chat conversations, history switch back to the first conversation.
- Idle auto mode is frontend-driven by repeated `tick` calls. There is no verified backend scheduler or 24x7 idle loop yet.
- Browser E2E verified auto idle produced both fixed MVP Agent slots: Nora then Vale.
- Timeline has `overflow: auto` and auto-scrolls to the latest message. If content is shorter than the panel, there is no scroll range.

## verified APIs

### GET /health
Purpose: backend health check.

Request:

```bash
curl http://127.0.0.1:8100/health
```

Verified response:

```json
{"status":"ok"}
```

### POST /api/users/register
Purpose: create a V1 demo user and return an access token.

Request body:

```json
{
  "username": "api_doc_1779741798",
  "email": "api_doc_1779741798@example.com",
  "password": "password123"
}
```

Verified response shape:

```json
{
  "accessToken": "<jwt>",
  "tokenType": "bearer",
  "user": {
    "id": "<mongo_object_id>",
    "username": "api_doc_1779741798",
    "displayName": "api_doc_1779741798",
    "email": "api_doc_1779741798@example.com",
    "idleOn": true,
    "languagePreference": "zh",
    "createdAt": "<iso_datetime>",
    "updatedAt": "<iso_datetime>"
  }
}
```

Notes:
- User records do not include model endpoint, API key, provider, Claude/OpenAI key, or local model path.
- `username` supports letters, numbers, and `_`.
- `password` minimum length is 8.

### POST /api/users/login
Purpose: authenticate an existing user by email or username.

Request body:

```json
{
  "identifier": "api_doc_1779741798@example.com",
  "password": "password123"
}
```

Verified response shape:

```json
{
  "accessToken": "<jwt>",
  "tokenType": "bearer",
  "user": {
    "id": "<mongo_object_id>",
    "username": "api_doc_1779741798",
    "displayName": "api_doc_1779741798",
    "email": "api_doc_1779741798@example.com",
    "idleOn": true,
    "languagePreference": "zh",
    "createdAt": "<iso_datetime>",
    "updatedAt": "<iso_datetime>"
  }
}
```

### GET /api/users/me
Purpose: read the current authenticated user.

Headers:

```text
Authorization: Bearer <accessToken>
```

Verified response shape:

```json
{
  "id": "<mongo_object_id>",
  "username": "api_doc_1779741798",
  "displayName": "api_doc_1779741798",
  "email": "api_doc_1779741798@example.com",
  "idleOn": true,
  "languagePreference": "zh",
  "createdAt": "<iso_datetime>",
  "updatedAt": "<iso_datetime>"
}
```

### PATCH /api/users/me
Purpose: update current user's demo-visible settings.

Headers:

```text
Authorization: Bearer <accessToken>
Content-Type: application/json
```

Request body:

```json
{
  "display_name": "API Doc User",
  "idle_on": false,
  "language_preference": "en"
}
```

Verified response shape:

```json
{
  "id": "<mongo_object_id>",
  "username": "api_doc_1779741798",
  "displayName": "API Doc User",
  "email": "api_doc_1779741798@example.com",
  "idleOn": false,
  "languagePreference": "en",
  "createdAt": "<iso_datetime>",
  "updatedAt": "<iso_datetime>"
}
```

### POST /api/users/logout
Purpose: V1 client-side JWT logout placeholder.

Verified status:

```text
204 No Content
```

Notes:
- V1 does not maintain server-side token revocation.
- Frontend should discard the access token.

### GET /api/agents
Purpose: list backend-owned fixed V1 Agent display profiles.

Request:

```bash
curl http://127.0.0.1:8120/api/agents
```

Verified response:

```json
[
  {
    "slot": "agent_1",
    "name": "Nora",
    "short": "A1",
    "color": "teal",
    "voice": "precise"
  },
  {
    "slot": "agent_2",
    "name": "Vale",
    "short": "A2",
    "color": "amber",
    "voice": "sharp"
  }
]
```

Notes:
- Prompt persona and frontend display profiles come from the same backend `agents` catalog.
- This API does not expose core persona, speaking style, model endpoint, provider, or API keys.
- If a frontend proxy returns 404 for this path, it is pointed at an older backend process that has not loaded `backend/agents/routes.py`.

### POST /api/conversations
Purpose: create a conversation container for `idle`, `companion_1`, `companion_2`, or future `work`.

Headers:

```text
Authorization: Bearer <accessToken>
Content-Type: application/json
```

Verified request body:

```json
{
  "mode": "companion_2",
  "title": "Demo Chat"
}
```

Verified response shape:

```json
{
  "id": "<conversation_id>",
  "userId": "<user_id>",
  "mode": "companion_2",
  "status": "active",
  "title": "Demo Chat",
  "participantSlots": ["agent_1", "agent_2"],
  "parentConversationId": null,
  "messageCount": 0,
  "lastMessageAt": null,
  "metadata": {},
  "createdAt": "<iso_datetime>",
  "updatedAt": "<iso_datetime>"
}
```

Notes:
- `companion_1` and `companion_2` use the same `conversations` collection.
- `mode` controls context behavior; storage remains unified.
- `agent_1` and `agent_2` are fixed Agent identity slots, not user model endpoints.

### GET /api/conversations
Purpose: list the current user's conversations.

Headers:

```text
Authorization: Bearer <accessToken>
```

Verified query:

```bash
curl "http://127.0.0.1:8100/api/conversations?mode=companion_2" \
  -H "Authorization: Bearer <accessToken>"
```

Verified response shape:

```json
[
  {
    "id": "<conversation_id>",
    "userId": "<user_id>",
    "mode": "companion_2",
    "status": "active",
    "title": "Demo Chat",
    "participantSlots": ["agent_1", "agent_2"],
    "parentConversationId": null,
    "messageCount": 2,
    "lastMessageAt": "<iso_datetime>",
    "metadata": {},
    "createdAt": "<iso_datetime>",
    "updatedAt": "<iso_datetime>"
  }
]
```

### GET /api/conversations/{conversationId}
Purpose: read one current-user-owned conversation.

Headers:

```text
Authorization: Bearer <accessToken>
```

Status:
- Implemented with the same response shape as `POST /api/conversations`.
- Ownership is enforced by `userId`.

### POST /api/conversations/{conversationId}/messages
Purpose: append a raw message to a conversation.

Headers:

```text
Authorization: Bearer <accessToken>
Content-Type: application/json
```

Verified user message body:

```json
{
  "sender_type": "user",
  "sender_id": "me",
  "role": "user",
  "content": "hello"
}
```

Verified Agent message body:

```json
{
  "sender_type": "agent",
  "sender_slot": "agent_1",
  "role": "assistant",
  "content": "hi from agent 1"
}
```

Verified response shape:

```json
{
  "id": "<message_id>",
  "conversationId": "<conversation_id>",
  "userId": "<user_id>",
  "mode": "companion_2",
  "sequence": 1,
  "senderType": "user",
  "senderId": "me",
  "senderSlot": null,
  "role": "user",
  "content": "hello",
  "contentType": "text",
  "metadata": {},
  "createdAt": "<iso_datetime>"
}
```

Notes:
- Agent messages require `sender_slot`.
- Valid V1 Agent slots are `agent_1` and `agent_2`.
- Message order inside a conversation is determined by `sequence`.

### GET /api/conversations/{conversationId}/messages
Purpose: page messages in sequence order or query messages by created time.

Headers:

```text
Authorization: Bearer <accessToken>
```

Query parameters:
- `afterSequence`: optional integer cursor.
- `createdAfter`: optional ISO datetime lower bound, inclusive.
- `createdBefore`: optional ISO datetime upper bound, exclusive.
- `limit`: optional integer, 1 to 100.

Rules:
- Use `afterSequence` for stable transcript pagination.
- Use `createdAfter` / `createdBefore` for time-window lookup.
- Do not combine `afterSequence` with time filters.
- Time-filtered responses are sorted by `createdAt` descending.
- Sequence pagination responses are sorted by `sequence` ascending.

Verified response shape:

```json
{
  "messages": [
    {
      "id": "<message_id>",
      "conversationId": "<conversation_id>",
      "userId": "<user_id>",
      "mode": "companion_2",
      "sequence": 1,
      "senderType": "user",
      "senderId": "me",
      "senderSlot": null,
      "role": "user",
      "content": "hello",
      "contentType": "text",
      "metadata": {},
      "createdAt": "<iso_datetime>"
    }
  ],
  "nextAfterSequence": null
}
```

Verified time query:

```bash
curl "http://127.0.0.1:8100/api/conversations/<conversationId>/messages?createdAfter=2026-05-25T21%3A41%3A59.248000&limit=10" \
  -H "Authorization: Bearer <accessToken>"
```

Verified time-query response shape:

```json
{
  "messages": [
    {
      "sequence": 2,
      "senderType": "agent",
      "senderSlot": "agent_1",
      "content": "time indexed reply",
      "createdAt": "2026-05-25T21:42:00.258000"
    },
    {
      "sequence": 1,
      "senderType": "user",
      "senderSlot": null,
      "content": "time indexed hello",
      "createdAt": "2026-05-25T21:41:59.248000"
    }
  ],
  "nextAfterSequence": null
}
```

MongoDB index verification:
- Query by current user and time uses `user_id_1_created_at_-1`.
- Query by conversation and time uses `conversation_id_1_created_at_-1`.

### GET /api/idle/conversation
Purpose: get or create the current user's active idle conversation.

Headers:

```text
Authorization: Bearer <accessToken>
```

Verified response shape:

```json
{
  "id": "<conversation_id>",
  "userId": "<user_id>",
  "mode": "idle",
  "status": "active",
  "title": "Idle",
  "participantSlots": ["agent_1", "agent_2"],
  "parentConversationId": null,
  "messageCount": 0,
  "lastMessageAt": null,
  "metadata": {
    "created_by": "get_or_create_active_idle"
  },
  "createdAt": "<iso_datetime>",
  "updatedAt": "<iso_datetime>"
}
```

### POST /api/idle/{conversationId}/tick
Purpose: generate one idle Agent reply through the full interaction chain.

Chain:

```text
interactions -> conversations -> context -> model_runtime -> conversations
```

Headers:

```text
Authorization: Bearer <accessToken>
Content-Type: application/json
```

Verified request body:

```json
{
  "targetAgentId": "agent_1",
  "idleSeed": "继续 idle 对话，保持自然、简短、有生活感。",
  "metadata": {}
}
```

Verified status:

```text
201 Created
```

Verified response shape:

```json
{
  "conversation": {
    "id": "<idle_conversation_id>",
    "mode": "idle",
    "messageCount": 1
  },
  "userMessage": null,
  "agentMessage": {
    "id": "<message_id>",
    "conversationId": "<idle_conversation_id>",
    "sequence": 1,
    "senderType": "agent",
    "senderSlot": "agent_1",
    "role": "assistant",
    "content": "<model_text>",
    "metadata": {
      "prompt_hash": "<sha256>",
      "token_estimate": "<integer>",
      "model_name": "<platform_model_name>"
    }
  },
  "context": {
    "promptHash": "<sha256>",
    "tokenEstimate": "<integer>",
    "modelName": "<platform_model_name>"
  }
}
```

Verified target-machine smoke values:
- `agentMessage.sequence`: `1`
- `context.promptHash`: non-empty SHA-256 string

Notes:
- This API does not create a user message.
- `targetAgentId` defaults to `agent_1`.
- `agent_1` and `agent_2` map to the fixed backend Agent catalog until `backend/agents/` persistence exists.

### POST /api/idle/{conversationId}/join
Purpose: let the user join an idle conversation and create a `companion_1` child conversation.

Chain:

```text
interactions -> conversations create child -> conversations save user message -> context transition -> model_runtime -> conversations save Agent reply
```

Headers:

```text
Authorization: Bearer <accessToken>
Content-Type: application/json
```

Verified request body:

```json
{
  "content": "我可以加入刚才的话题吗？",
  "targetAgentId": "agent_1",
  "metadata": {}
}
```

Verified status:

```text
201 Created
```

Verified response shape:

```json
{
  "conversation": {
    "id": "<companion_1_conversation_id>",
    "mode": "companion_1",
    "parentConversationId": "<idle_conversation_id>",
    "messageCount": 2
  },
  "userMessage": {
    "conversationId": "<companion_1_conversation_id>",
    "sequence": 1,
    "senderType": "user",
    "role": "user",
    "content": "我可以加入刚才的话题吗？"
  },
  "agentMessage": {
    "conversationId": "<companion_1_conversation_id>",
    "sequence": 2,
    "senderType": "agent",
    "senderSlot": "agent_1",
    "role": "assistant",
    "content": "<model_text>"
  },
  "context": {
    "promptHash": "<sha256>",
    "tokenEstimate": "<integer>",
    "modelName": "<platform_model_name>"
  }
}
```

Verified target-machine smoke values:
- `userMessage.sequence`: `1`
- `agentMessage.sequence`: `2`
- `context.promptHash`: non-empty SHA-256 string
- Latest diagnosis on port `8122`: HTTP curl returned `201 Created` with `conversation.mode=companion_1`, `agentMessage.senderSlot=agent_1`, and `context.modelName=gpt-5.1`.

Notes:
- The path parameter is the source idle conversation id.
- The returned conversation is the newly created `companion_1` child.
- Use `conversation.parentConversationId` to link back to idle history.
- If this route returns `500 model_api_key_missing`, the backend process did not load platform model secrets. Model runtime now reads process env, `.env`, `../.env`, and `~/.env`.

### POST /api/companion/{conversationId}/messages
Purpose: append a `companion_2` user message and generate one Agent reply.

Chain:

```text
interactions -> conversations save user message -> context -> model_runtime -> conversations save Agent reply
```

Headers:

```text
Authorization: Bearer <accessToken>
Content-Type: application/json
```

Verified request body:

```json
{
  "content": "一句话说明 Hackson V1 目标。",
  "targetAgentId": "agent_2",
  "metadata": {}
}
```

Verified status:

```text
201 Created
```

Verified response shape:

```json
{
  "conversation": {
    "id": "<companion_2_conversation_id>",
    "mode": "companion_2",
    "messageCount": 2
  },
  "userMessage": {
    "conversationId": "<companion_2_conversation_id>",
    "sequence": 1,
    "senderType": "user",
    "role": "user",
    "content": "一句话说明 Hackson V1 目标。"
  },
  "agentMessage": {
    "conversationId": "<companion_2_conversation_id>",
    "sequence": 2,
    "senderType": "agent",
    "senderSlot": "agent_2",
    "role": "assistant",
    "content": "<model_text>"
  },
  "context": {
    "promptHash": "<sha256>",
    "tokenEstimate": "<integer>",
    "modelName": "<platform_model_name>"
  }
}
```

Verified target-machine smoke values:
- `userMessage.sequence`: `1`
- `agentMessage.sequence`: `2`
- `context.promptHash`: non-empty SHA-256 string
- Follow-up `GET /api/conversations/{conversationId}/messages?limit=10` returned two messages with sequences `1,2`.

Notes:
- This is the product interaction endpoint for `companion_2`.
- `POST /api/conversations/{conversationId}/messages` remains the raw historical append endpoint and should not be used by the frontend for model replies.

## developer notes
- All protected user APIs require `Authorization: Bearer <accessToken>`.
- The user module is under `backend/users/`.
- The conversation and raw message history module is under `backend/conversations/`.
- The product interaction orchestration module is under `backend/interactions/`.
- The context builder module is under `backend/context/`.
- The model runtime module is under `backend/model_runtime/`.
- Shared backend config, database, and security utilities are under `backend/core/`.
- MongoDB is required for full API verification.
- Do not stop existing target-machine services. Use a new free port for tests.
