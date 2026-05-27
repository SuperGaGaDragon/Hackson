## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex

## brief intro
- This document is the current verified API and port map for Hackson.
- Public product traffic now uses `https://hackson.catachess.com/`.
- Only currently retained Hackson services and APIs verified on the public domain are listed as active.
- Historical smoke ports were intentionally removed from the active map after public-domain promotion.

## current environment
| Item | Value |
| --- | --- |
| Target machine | `catadragon@100.70.248.39` |
| Target access note | Ignored local file `docs/数据库/machine.md`; never push it |
| Public URL | `https://hackson.catachess.com/` |
| Public source path | `~/hackson_domain_8145` |
| Public backend path | `~/hackson_domain_8145/backend` |
| Public frontend build path | `~/hackson_domain_8145/frontend/dist` |
| Public app service | `hackson-domain-8145.service`, user-level systemd, enabled and active |
| Public tunnel service | `hackson-cloudflared.service`, user-level systemd, enabled and active |
| Public backend bind | `127.0.0.1:8145` |
| Public MongoDB database | `hackson_domain_8145` |
| Public cloudflared config | `~/.cloudflared/hackson.yml` |
| Legacy Tailscale URL | `http://100.70.248.39:8130/` |
| Legacy production service | `hackson-production.service`, user-level systemd, enabled and active |
| Legacy production path | `~/hackson_production` |
| Legacy production bind | `0.0.0.0:8130` |
| Legacy production database | `hackson` |

## active Hackson port map
| Port | Service | Bind | Status | Purpose |
| --- | --- | --- | --- | --- |
| 8145 | Hackson public domain FastAPI + React app | `127.0.0.1` | Active as `hackson-domain-8145.service` | Serves `https://hackson.catachess.com/` through `hackson-cloudflared.service` |
| 8130 | Legacy Hackson production FastAPI + React app | `0.0.0.0` | Active as `hackson-production.service` | Retained legacy Tailscale production URL until explicitly retired |

## cleanup record
- On 2026-05-27, old Hackson smoke uvicorn ports were stopped after the current code was promoted to the public domain.
- Stopped Hackson smoke ports: `8101`, `8122`, `8123`, `8124`, `8125`, `8126`, `8131`, `8132`, `8133`, `8141`, `8142`, `8143`, `8144`, `8146`, `8147`.
- Non-Hackson services on the target machine were not touched.
- Do not restart old smoke ports for normal product use. Use the public domain service for verification unless a new isolated smoke port is explicitly needed.

## verified public APIs
All rows below were verified against `https://hackson.catachess.com/` on 2026-05-27.

| Method | API | Auth | Module | Purpose |
| --- | --- | --- | --- | --- |
| GET | `/health` | No | `backend/main.py` | Backend health check |
| GET | `/` | No | `backend/main.py` | React frontend HTML |
| GET | `/assets/{asset}` | No | `backend/main.py` | Built frontend assets |
| POST | `/api/users/register` | No | `backend/users/` | Register user and return JWT |
| POST | `/api/users/login` | No | `backend/users/` | Login by email or username |
| GET | `/api/users/me` | Bearer JWT | `backend/users/` | Read current user and the two editable Agent profiles |
| PATCH | `/api/users/me` | Bearer JWT | `backend/users/` | Update current user settings and Agent profiles |
| GET | `/api/agents` | No | `backend/agents/` | Return baseline Agent display profiles; authenticated UI prefers the current user's editable profiles from `/api/users/me` |
| POST | `/api/conversations` | Bearer JWT | `backend/conversations/` | Create an idle, companion, or work conversation container |
| GET | `/api/conversations` | Bearer JWT | `backend/conversations/` | List current-user conversations by mode/status |
| GET | `/api/conversations/{conversationId}/messages` | Bearer JWT | `backend/conversations/` | Page messages in one owned conversation |
| GET | `/api/idle/conversation` | Bearer JWT | `backend/conversations/` | Get or create the active idle conversation |
| POST | `/api/idle/{conversationId}/tick` | Bearer JWT | `backend/interactions/` | Generate one idle Agent reply |
| POST | `/api/idle/{conversationId}/messages` | Bearer JWT | `backend/interactions/` | Add a visible user line to idle and generate the next Agent reply |
| POST | `/api/idle/{conversationId}/join` | Bearer JWT | `backend/interactions/` | Create a `companion_1` child from idle and reply |
| POST | `/api/companion/{conversationId}/messages` | Bearer JWT | `backend/interactions/` | Continue a companion conversation |
| POST | `/api/tasks` | Bearer JWT | `backend/tasks/` | Create the legacy minimal Work task and its conversation |
| GET | `/api/tasks` | Bearer JWT | `backend/tasks/` | List current-user legacy Work tasks |
| POST | `/api/tasks/{taskId}/messages` | Bearer JWT | `backend/tasks/`, `backend/interactions/` | Send a legacy task message and get an Agent reply |
| POST | `/api/work/projects` | Bearer JWT | `backend/work_mode/` | Create a Work project by name |
| GET | `/api/work/projects` | Bearer JWT | `backend/work_mode/` | List current-user Work projects |
| POST | `/api/work/missions` | Bearer JWT | `backend/work_mode/` | Create a Mission with `agent_1` or `agent_2` as lead |
| GET | `/api/work/projects/{projectId}/missions` | Bearer JWT | `backend/work_mode/` | List Missions in one Project |
| GET | `/api/work/missions/{missionId}` | Bearer JWT | `backend/work_mode/` | Read Mission detail and current event timeline |
| POST | `/api/work/missions/{missionId}/start` | Bearer JWT | `backend/work_mode/` | Start the V0 deterministic Mission worker |
| GET | `/api/work/missions/{missionId}/events` | Bearer JWT | `backend/work_mode/` | Poll Mission events after `afterSequence` |

## request notes

### Auth headers
Authenticated requests require:

```http
Authorization: Bearer <jwt>
Content-Type: application/json
```

### User registration
```http
POST /api/users/register
```

```json
{
  "username": "demo",
  "email": "demo@example.com",
  "password": "password-with-length"
}
```

Returns a JWT plus the current user object.

### Agent profile update
```http
PATCH /api/users/me
```

```json
{
  "agentProfiles": [
    {
      "slot": "agent_1",
      "name": "Plotter",
      "role": "outline lead",
      "personality": "Structured and concise.",
      "story": "Experienced in planning long-form fiction."
    },
    {
      "slot": "agent_2",
      "name": "Drafter",
      "role": "scene writer",
      "personality": "Concrete and image-driven.",
      "story": "Experienced in drafting readable scenes."
    }
  ]
}
```

### Idle topic
```http
POST /api/conversations
```

```json
{
  "mode": "idle",
  "title": "Novel outline",
  "metadata": {
    "topicDirection": "Plan the story before drafting."
  }
}
```

### Idle tick
```http
POST /api/idle/{conversationId}/tick
```

```json
{
  "speakerSlot": "agent_1",
  "discussionDirection": "Stay focused on chapter planning."
}
```

### Idle user line
```http
POST /api/idle/{conversationId}/messages
```

```json
{
  "content": "Make the protagonist older and more tired.",
  "speakerSlot": "agent_2",
  "discussionDirection": "Respond to the user's latest line."
}
```

Returns both the saved user message and the generated Agent message.

### Work project
```http
POST /api/work/projects
```

```json
{
  "name": "Novel"
}
```

`repoPath` is optional internal compatibility metadata. The current UI does not ask the user for it.

### Work mission
```http
POST /api/work/missions
```

```json
{
  "projectId": "<project-id>",
  "title": "Draft chapter plan",
  "goal": "Create a practical outline before writing.",
  "leadEmployeeId": "agent_1"
}
```

Current product flow uses the user's two Agent profiles as Mission leads. Legacy Employee and Project Team endpoints still exist in code for backward compatibility but are not part of the current verified public UI.

### Start mission
```http
POST /api/work/missions/{missionId}/start
```

```json
{}
```

The V0 worker emits deterministic events:

```text
MISSION_STARTED
STEP_STARTED
SUMMARY
RAW_LOG
PRODUCT_UPDATED
STEP_COMPLETED
MISSION_COMPLETED
```

Poll with:

```http
GET /api/work/missions/{missionId}/events?afterSequence=<last-sequence>
```

## latest verification
- Local backend tests passed before deployment:
  - `backend/interactions/tests`: 18 tests.
  - `backend/work_mode/tests`: 14 tests.
- Local frontend build passed before deployment.
- Target backend tests passed under `~/hackson_domain_8145/backend`.
- Target frontend build passed with Node `20.19.6`; latest public asset verified as `/assets/index-DGOMmalo.js`.
- `hackson-domain-8145.service` was restarted and returned `{"status":"ok"}` on `127.0.0.1:8145/health`.
- Public API smoke verified auth, Agent profile update, Project creation, Mission creation, Mission start, and Mission events.
- Model-backed Idle/Companion routes can currently return `429 {"detail":"model_rate_limited"}` when the upstream model provider is rate-limited; this is a stable API response, not a backend crash.
- Public browser smoke verified Register/Login, Agent editing, Workspace Project creation, Project detail, Mission creation, Start, completion timeline, desktop screenshot, and mobile screenshot with `0` failed API responses.
- Screenshots:
  - `/tmp/hackson_public_work_agents_desktop.png`
  - `/tmp/hackson_public_work_done_desktop.png`
  - `/tmp/hackson_public_work_mobile.png`
