## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex

## brief intro
- This document is the verified API and port map for Hackson.
- Only APIs that have been tested on the target machine are listed here.
- Backend uses FastAPI. Frontend will use React + Vite.
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
- Last verified at: 2026-05-25

## port map
| Port | Service | Bind | Status | Purpose |
| --- | --- | --- | --- | --- |
| 8100 | FastAPI backend temporary test server | `127.0.0.1` | Verified, not kept running | Local target-machine API verification without touching existing services |

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

## developer notes
- All protected user APIs require `Authorization: Bearer <accessToken>`.
- The user module is under `backend/users/`.
- Shared backend config, database, and security utilities are under `backend/core/`.
- MongoDB is required for full API verification.
- Do not stop existing target-machine services. Use a new free port for tests.
