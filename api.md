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
- Verified backend command:

```bash
HACKSON_MONGO_DATABASE=hackson_test \
HACKSON_JWT_SECRET=target-test-secret-with-more-than-32-bytes \
PYTHONPATH=. \
uvicorn main:app --host 127.0.0.1 --port 8100
```

- Verified port: `127.0.0.1:8100`
- Port status after verification: stopped/free
- Database used in verification: MongoDB database `hackson_test`
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
| 8100 | FastAPI backend temporary test server | `127.0.0.1` | Verified, not kept running | Local target-machine API verification without touching existing services |
| 5173 | Vite frontend temporary dev server | `127.0.0.1` | Running locally | Hackson React frontend prototype |

## verified frontend

### React + Vite prototype
Purpose: local product-level frontend prototype for Idle, Chat, Agents, and future Work surfaces.

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

Notes:
- Frontend does not expose model endpoint, provider, API key, Claude/OpenAI key, or local model path settings.
- V1 product copy is intentionally short per `agents/frontend_restrictions.md`.

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
Purpose: page messages in sequence order.

Headers:

```text
Authorization: Bearer <accessToken>
```

Query parameters:
- `afterSequence`: optional integer cursor.
- `limit`: optional integer, 1 to 100.

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

## developer notes
- All protected user APIs require `Authorization: Bearer <accessToken>`.
- The user module is under `backend/users/`.
- The conversation and raw message module is under `backend/conversations/`.
- Shared backend config, database, and security utilities are under `backend/core/`.
- MongoDB is required for full API verification.
- Do not stop existing target-machine services. Use a new free port for tests.
