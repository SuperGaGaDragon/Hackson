## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

## brief intro
- This document is the current verified API and port map for Hackson.
- Public product traffic now uses `https://hackson.catachess.com/`.
- Public-domain rows describe the currently promoted product service.
- The `8147` rows describe the isolated Idle Auto smoke service used for its fix.
- The `8148` rows describe the isolated Work V0.5 artifact smoke service. It is not the public product service.
- The `8150` rows describe the isolated Work V1 model-driven loop smoke service. It is not the public product service.
- The `8160` rows describe the isolated Work V1 hardening smoke service with HTTP and browser release gates. It is not the public product service.
- The `8161` rows describe the isolated Work V1 progress hardening smoke service with lifecycle events and bounded retry. It is not the public product service.
- The `8162` rows describe the isolated Work V1 Delegate tolerance smoke service. It is not the public product service.
- The `8163` rows describe the isolated Work V1 UI architecture smoke service. It is not the public product service.

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
| Public Work Mode runtime | V1 model-driven loop with Product/Artifact lineage, visible Work Windows, lifecycle progress events, bounded retry, retryable pause/resume, failed-window cleanup, Delegate result tolerance, Activity -> Windows -> Product -> Progress -> Diagnostics UI, and final lineage validation |
| Public model provider | `codex_cli` through target-machine Codex CLI |
| Public model | `gpt-5.4` |
| Public model command | `/home/catadragon/.nvm/versions/node/v20.19.6/bin/codex exec` |
| Public model auth/config | `/home/catadragon/.codex` |
| Public cloudflared config | `~/.cloudflared/hackson.yml` |
| Idle Auto smoke source path | `~/hackson_idle_auto_8146` |
| Idle Auto smoke backend path | `~/hackson_idle_auto_8146/backend` |
| Idle Auto smoke frontend build path | `~/hackson_idle_auto_8146/frontend/dist` |
| Idle Auto smoke service | `hackson-idle-auto-8147.service`, user-level systemd, active |
| Idle Auto smoke backend bind | `127.0.0.1:8147` |
| Idle Auto smoke local check | `127.0.0.1:5187 -> 18147 -> 8147` |
| Idle Auto smoke MongoDB database | `hackson_idle_auto_8147` |
| Work V0.5 smoke source path | `~/hackson_work_v05_8148` |
| Work V0.5 smoke backend path | `~/hackson_work_v05_8148/backend` |
| Work V0.5 smoke frontend build path | `~/hackson_work_v05_8148/frontend/dist` |
| Work V0.5 smoke service | `hackson-work-v05-8148.service`, user-level systemd, active |
| Work V0.5 fake model relay | `hackson-work-v05-fake-model-18148.service`, user-level systemd, active |
| Work V0.5 smoke backend bind | `127.0.0.1:8148` |
| Work V0.5 fake model bind | `127.0.0.1:18148` |
| Work V0.5 smoke database | `hackson_work_v05_8148` |
| Work V1 smoke source path | `~/hackson_work_v1_8150` |
| Work V1 smoke backend path | `~/hackson_work_v1_8150/backend` |
| Work V1 smoke frontend build path | `~/hackson_work_v1_8150/frontend/dist` |
| Work V1 smoke service | `hackson-work-v1-8150.service`, user-level systemd, active |
| Work V1 smoke backend bind | `127.0.0.1:8150` |
| Work V1 smoke database | `hackson_work_v1_8150` |
| Work V1 smoke model provider | `codex_cli` through target-machine Codex CLI |
| Work V1 hardening smoke source path | `~/hackson_work_v1_8160` |
| Work V1 hardening smoke backend path | `~/hackson_work_v1_8160/backend` |
| Work V1 hardening smoke frontend build path | `~/hackson_work_v1_8160/frontend/dist` |
| Work V1 hardening smoke service | `hackson-work-v1-8160.service`, user-level systemd, active |
| Work V1 hardening smoke backend bind | `127.0.0.1:8160` |
| Work V1 hardening smoke database | `hackson_work_v1_8160` |
| Work V1 hardening smoke model provider | `codex_cli` through target-machine Codex CLI |
| Work V1 progress hardening source path | `~/hackson_work_v1_progress_8161` |
| Work V1 progress hardening backend path | `~/hackson_work_v1_progress_8161/backend` |
| Work V1 progress hardening frontend build path | `~/hackson_work_v1_progress_8161/frontend/dist` |
| Work V1 progress hardening service | `hackson-work-v1-progress-8161.service`, user-level systemd, active |
| Work V1 progress hardening backend bind | `127.0.0.1:8161` |
| Work V1 progress hardening database | `hackson_work_v1_progress_8161` |
| Work V1 progress hardening model provider | `codex_cli` through target-machine Codex CLI |
| Work V1 Delegate tolerance source path | `~/hackson_work_v1_delegate_8162` |
| Work V1 Delegate tolerance backend path | `~/hackson_work_v1_delegate_8162/backend` |
| Work V1 Delegate tolerance frontend build path | `~/hackson_work_v1_delegate_8162/frontend/dist` |
| Work V1 Delegate tolerance service | `hackson-work-v1-delegate-8162.service`, user-level systemd, active |
| Work V1 Delegate tolerance backend bind | `127.0.0.1:8162` |
| Work V1 Delegate tolerance database | `hackson_work_v1_delegate_8162` |
| Work V1 Delegate tolerance model provider | `codex_cli` through target-machine Codex CLI |
| Work V1 UI architecture source path | `~/hackson_work_ui_8163` |
| Work V1 UI architecture backend path | `~/hackson_work_ui_8163/backend` |
| Work V1 UI architecture frontend build path | `~/hackson_work_ui_8163/frontend/dist` |
| Work V1 UI architecture service | `hackson-work-ui-8163.service`, user-level systemd, active |
| Work V1 UI architecture backend bind | `127.0.0.1:8163` |
| Work V1 UI architecture database | `hackson_work_ui_8163` |
| Work V1 UI architecture model provider | `codex_cli` through target-machine Codex CLI |
| Legacy Tailscale URL | `http://100.70.248.39:8130/` |
| Legacy production service | `hackson-production.service`, user-level systemd, enabled and active |
| Legacy production path | `~/hackson_production` |
| Legacy production bind | `0.0.0.0:8130` |
| Legacy production database | `hackson` |

## active Hackson port map
| Port | Service | Bind | Status | Purpose |
| --- | --- | --- | --- | --- |
| 8145 | Hackson public domain FastAPI + React app | `127.0.0.1` | Active as `hackson-domain-8145.service` | Serves `https://hackson.catachess.com/` through `hackson-cloudflared.service`; promoted to Work V1 Delegate tolerance build on 2026-05-28 |
| 8147 | Hackson Idle Auto smoke FastAPI + React app | `127.0.0.1` | Active as `hackson-idle-auto-8147.service` | Isolated verification for Idle Auto topic, interjection, speaker, and rate-limit behavior |
| 8148 | Hackson Work V0.5 smoke FastAPI + React app | `127.0.0.1` | Active as `hackson-work-v05-8148.service` | Isolated verification for Work Mission artifact persistence and Product UI render |
| 18148 | Work V0.5 fake OpenAI-compatible model relay | `127.0.0.1` | Active as `hackson-work-v05-fake-model-18148.service` | Test-only model relay for deterministic Work V0.5 success smoke; not a product API |
| 8150 | Hackson Work V1 smoke FastAPI + React app | `127.0.0.1` | Active as `hackson-work-v1-8150.service` | Isolated verification for Work V1 model-selected tool loop, Product/Artifact lineage, retryable pause, and resume |
| 8160 | Hackson Work V1 hardening smoke FastAPI + React app | `127.0.0.1` | Active as `hackson-work-v1-8160.service` | Isolated verification for Work V1 HTTP full smoke, browser UI smoke, and final Product/Artifact lineage |
| 8161 | Hackson Work V1 progress hardening FastAPI + React app | `127.0.0.1` | Active as `hackson-work-v1-progress-8161.service` | Isolated verification for Work V1 lifecycle events, bounded retry, Activity UI, and failed-window cleanup |
| 8162 | Hackson Work V1 Delegate tolerance FastAPI + React app | `127.0.0.1` | Active as `hackson-work-v1-delegate-8162.service` | Isolated verification for tolerant Delegate result ingestion, unstructured prose Artifact persistence, full smoke, HTTP smoke, and browser smoke |
| 8163 | Hackson Work V1 UI architecture FastAPI + React app | `127.0.0.1` | Active as `hackson-work-ui-8163.service` | Isolated verification for Activity, Windows, Product lineage, Progress, Diagnostics, desktop/mobile browser smoke, and no mobile horizontal overflow |
| 8130 | Legacy Hackson production FastAPI + React app | `0.0.0.0` | Active as `hackson-production.service` | Retained legacy Tailscale production URL until explicitly retired |

## cleanup record
- On 2026-05-27, old Hackson smoke uvicorn ports were stopped after the current code was promoted to the public domain.
- Stopped Hackson smoke ports: `8101`, `8122`, `8123`, `8124`, `8125`, `8126`, `8131`, `8132`, `8133`, `8141`, `8142`, `8143`, `8144`, `8146`.
- On 2026-05-27, `8147` was reintroduced as `hackson-idle-auto-8147.service` for isolated Idle Auto verification without touching public `8145`.
- On 2026-05-27, temporary Orchestrator V1 smoke ports `8148` and `18148` were used for isolated target-machine verification, then stopped.
- On 2026-05-27, `8148` and `18148` were reintroduced as Work V0.5 isolated smoke services. They are active and intentionally separate from public `8145`.
- On 2026-05-27, `8150` was introduced as the isolated Work V1 model-driven loop smoke service. It is active and intentionally separate from public `8145`, Idle Auto `8147`, Work V0.5 `8148`, and legacy `8130`.
- On 2026-05-27, `8160` was introduced as the isolated Work V1 hardening smoke service. It verified backend tests, frontend build, deterministic full smoke, authenticated HTTP full smoke, browser UI smoke, static frontend serving, and health check without stopping existing services.
- On 2026-05-27, the Work V1 hardening build was promoted to public `8145` after target public-directory tests passed. Public health and static frontend checks passed, deterministic Work V1 full smoke and authenticated HTTP full smoke passed, and a real public browser-triggered Codex Mission entered `paused_retryable model_timeout` with persisted plan/product events and no orphan `codex exec` process.
- On 2026-05-27, `8161` was introduced as the isolated Work V1 progress hardening service. It added safe lifecycle events, bounded automatic retry before `paused_retryable`, failed-window cleanup for delegate provider errors, and a compact Work UI activity strip. Target tests, frontend build, full smoke, HTTP smoke, browser smoke, health, and static React checks passed.
- On 2026-05-27, the Work V1 progress hardening build was promoted to public `8145`. Public-directory Work Mode `52`, model_runtime `24`, interactions `21`, frontend build, deterministic full smoke, and HTTP smoke passed before restart. After restart, `https://hackson.catachess.com/health` and `/` returned `200`, assets `index-HYSRYan8.js` and `index-cInveBCH.css` were served, and real Codex Mission `6a17a145f01aad81f13bca71` completed with lifecycle events around each tool call.
- On 2026-05-28, `8162` was introduced as the isolated Work V1 Delegate tolerance service. It fixes the public Mission `6a17a659f01aad81f13bca8a` failure mode where a Delegate window returned useful writing but missed the strict JSON wrapper. Target Work Mode `55`, model_runtime `24`, interactions `21`, frontend build, full smoke, HTTP smoke, Delegate unstructured-prose HTTP regression, browser smoke, health, and static React checks passed.
- On 2026-05-28, the Work V1 Delegate tolerance build was promoted to public `8145`. Public-directory Work Mode `55`, model_runtime `24`, interactions `21`, frontend build, deterministic full smoke, HTTP smoke, and Delegate unstructured-prose regression passed before restart. After restart, `https://hackson.catachess.com/health` and `/` returned `200`, assets `index-HYSRYan8.js` and `index-cInveBCH.css` were served, public runtime Delegate parse returned `completed` with `delegateStructured=false`, and no orphan `codex exec` process was present.
- On 2026-05-28, `8163` was introduced as the isolated Work V1 UI architecture service. It verifies the Work Console order `Activity -> Windows -> Product -> Progress -> Diagnostics`, Product Artifact lineage, default-collapsed Diagnostics, desktop and mobile browser smoke, and mobile no-horizontal-overflow without touching public `8145`.
- On 2026-05-28, the Work V1 UI architecture frontend build was promoted to public `8145` by replacing only `frontend/dist`; `hackson-domain-8145.service` was not restarted. Public health, root HTML, assets `/assets/index-qPU-cMH4.js` and `/assets/index-BbzX_UAM.css`, and a public browser static Work Console order check passed.
- Non-Hackson services on the target machine were not touched.
- Do not restart old smoke ports for normal product use. Use the public domain service for verification unless a new isolated smoke port is explicitly needed.

## verified public APIs
All rows below were verified against `https://hackson.catachess.com/` on 2026-05-27.

Model-backed rows were additionally verified on the target machine against `http://127.0.0.1:8145` on 2026-05-27 after configuring `HACKSON_MODEL_PROVIDER=codex_cli`; the smoke confirmed assistant metadata `provider=codex_cli`, `modelName=gpt-5.4`, `idle_quality_v1`, and `companion_join_quality_v1`.

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
| GET | `/api/work/missions/{missionId}` | Bearer JWT | `backend/work_mode/` | Read Mission detail, current event timeline, persisted Products, Work Windows, and Artifacts |
| POST | `/api/work/missions/{missionId}/start` | Bearer JWT | `backend/work_mode/` | Start or resume the V1 model-driven tool loop in current HEAD; public `8145` still runs its deployed version until promoted |
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

The V0.5 worker emits model-backed artifact events:

```text
MISSION_STARTED
STEP_STARTED
RAW_LOG
PRODUCT_UPDATED
STEP_COMPLETED
MISSION_COMPLETED
```

Poll with:

```http
GET /api/work/missions/{missionId}/events?afterSequence=<last-sequence>
```

Read persisted output from:

```http
GET /api/work/missions/{missionId}
```

`artifacts` is sorted newest first:

```json
{
  "artifacts": [
    {
      "id": "<artifact-id>",
      "missionId": "<mission-id>",
      "runId": "<run-id>",
      "kind": "text",
      "title": "Draft chapter plan",
      "content": "Full artifact text",
      "createdByEmployee": {
        "id": "agent_1",
        "name": "Nora",
        "role": "precise"
      },
      "metadata": {
        "runner": "model_runtime",
        "modelName": "gpt-5.4",
        "provider": "codex_cli"
      },
      "createdAt": "2026-05-27T18:00:00Z"
    }
  ]
}
```

`PRODUCT_UPDATED` carries `artifactId`, `kind`, `summary`, `changedFiles`, and `tests`. The full Artifact content is not duplicated into event payloads.

V0.5 Work Mission generation is intentionally bounded to one model pass. Long requests such as an 8000-character story return a usable first draft, sample, or outline artifact; a later supervisor loop should expand it across multiple runs.

## latest verification
- Local backend tests passed before deployment:
  - `backend/interactions/tests`: 18 tests.
  - `backend/work_mode/tests`: 14 tests.
- Local frontend build passed before deployment.
- Target backend tests passed under `~/hackson_domain_8145/backend`.
- Target frontend build passed with Node `20.19.6`; the public asset at that deployment was `/assets/index-DGOMmalo.js`.
- `hackson-domain-8145.service` was restarted and returned `{"status":"ok"}` on `127.0.0.1:8145/health`.
- Public API smoke verified auth, Agent profile update, Project creation, Mission creation, Mission start, and Mission events.
- Public Work Console static-only update on 2026-05-27:
  - Public `frontend/dist` was backed up on the target, then replaced without restarting `hackson-domain-8145.service`.
  - Latest public assets verified as `/assets/index-O85af_uy.js` and `/assets/index-BNnrJWzs.css`.
  - Browser smoke verified a completed Work Mission renders Progress, Summary, and Product as separate vertical cards; Summary overlaps `0` Progress rows; completed `Start` is disabled; failed resource count is `0`.
  - Screenshot: `/tmp/hackson_work_public_final.png`.
- Model-backed Idle/Companion routes can currently return `429 {"detail":"model_rate_limited"}` when the upstream model provider is rate-limited; this is a stable API response, not a backend crash.
- Idle Auto smoke verification on `8147`:
  - Target scoped tests passed: `40 passed, 4 warnings`.
  - API smoke confirmed provider `429` returns `{"detail":"model_rate_limited"}` and a failed idle tick leaves `0` messages.
  - Local UI path `5187 -> 18147 -> 8147` verified topic creation during rate limit shows `Model busy`, keeps `Auto` off, and makes no extra tick requests after failure.
  - Screenshot: `/tmp/hackson_idle_auto_model_busy_ui.png`.
- Orchestrator V1 target smoke verification on temporary `8148`:
  - Target scoped tests passed under `~/hackson_orchestrator_v1_8148/backend`: orchestration `5`, model_runtime `17`, interactions `21`.
  - Real provider smoke confirmed model-backed idle routes can still return stable `429 {"detail":"model_rate_limited"}`.
  - Fake OpenAI-compatible relay on temporary `18148` verified Responses-mode success path for register, idle tick, idle say, idle join, companion_1 follow-up, and companion_2 message.
  - Verified assistant message metadata contains `orchestration_policy`, `reasoning_effort`, `tool_policy`, `provider`, `provider_response_id`, and `reasoning_summary`.
- Work V0.5 isolated smoke verification on active `8148`:
  - Local Work tests passed: `16` tests.
  - Local model_runtime/interactions regression passed: `38` tests.
  - Local frontend build passed with assets `/assets/index-BQ4JHagk.js` and `/assets/index-C-nEjYQU.css`.
  - Target Work tests passed under `~/hackson_work_v05_8148/backend`: `16` tests.
  - Target frontend build passed with Node `20.19.6`.
  - Target success smoke on `127.0.0.1:8148` verified register, Project create, Mission create, Start, `MISSION_COMPLETED`, one persisted text Artifact, and `PRODUCT_UPDATED` without full `content` payload.
  - Target failure smoke on temporary `8149` verified model network failure produces `MISSION_FAILED`, `artifactCount: 0`, and no fake Product result; `8149` was stopped and removed after verification.
  - Local UI path `5192 -> 18148 -> 8148` verified Work page creates Project/Mission and renders the persisted Artifact in Product with failed resource count `0`.
  - Screenshot: `/tmp/hackson_work_v05_ui.png`.
  - `8148` and `18148` remain active as isolated Work V0.5 smoke services; public `8145`, Idle Auto `8147`, and legacy `8130` were not touched.
- Orchestrator V1 public deployment on `8145`:
  - Local backend full module unittest passed and local frontend build passed before deployment.
  - Target public directory tests passed: orchestration `5`, model_runtime `17`, interactions `21`.
  - Target frontend build passed with Node `20.19.6`; public assets remain `/assets/index-O85af_uy.js` and `/assets/index-BNnrJWzs.css`.
  - `hackson-domain-8145.service` was restarted and returned `{"status":"ok"}` on `127.0.0.1:8145/health`.
  - Public domain `https://hackson.catachess.com/health` returned `{"status":"ok"}` and `GET /` returned the React HTML.
  - Public API smoke verified register and conversation creation. Model-backed idle and companion routes returned stable `429 {"detail":"model_rate_limited"}` from the current upstream provider limit, not a backend crash.
  - Public backend code now routes model-backed idle and companion generation through `backend/orchestration/` and stores orchestration metadata when the provider succeeds.
- Work Mode Codex public fix on `8145`:
  - Root cause confirmed: idle and companion already injected `CodexCliClient`; Work Mode runner only built `ModelRuntime` with the OpenAI-compatible client, so `HACKSON_MODEL_PROVIDER=codex_cli` produced `model_codex_cli_unavailable`.
  - Public backend now injects `CodexCliClient` in Work Mode and bounds V0.5 generation to a single first-pass artifact with low reasoning effort.
  - Local tests passed: all backend `*/tests` directories, including Work Mode `18`, model_runtime `23`, and interactions `21`.
  - Target public tests passed under `~/hackson_domain_8145/backend`: Work Mode `18`, model_runtime `23`, interactions `21`.
  - `hackson-domain-8145.service` was restarted and returned `active` plus `{"status":"ok"}` on `127.0.0.1:8145/health`.
  - Target public API smoke on `127.0.0.1:8145` completed Mission `6a17428e1c922129e72e8968` titled `撰写一个8000字小说`; events reached `MISSION_COMPLETED`, one text Artifact was persisted, artifact length was `1055`, and metadata was `{"runner":"model_runtime","modelName":"gpt-5.4","provider":"codex_cli"}`.
- Public browser smoke verified Register/Login, Agent editing, Workspace Project creation, Project detail, Mission creation, Start, completion timeline, desktop screenshot, and mobile screenshot with `0` failed API responses.
- Screenshots:
  - `/tmp/hackson_public_work_agents_desktop.png`
  - `/tmp/hackson_public_work_done_desktop.png`
  - `/tmp/hackson_public_work_mobile.png`
- Work V1 isolated smoke verification on active `8150`:
  - Target source: `~/hackson_work_v1_8150`.
  - Target service: `hackson-work-v1-8150.service`, active on `127.0.0.1:8150`.
  - Target database: `hackson_work_v1_8150`.
  - Target tests passed: Work Mode `46`, model_runtime `24`.
  - Target frontend build passed with Node `20.19.6`, assets `/assets/index-B-RFrSxG.js` and `/assets/index-hERmjtRu.css`.
  - Deterministic full smoke passed on target: `work_mode_v1_full_smoke=ok`, `events=12`, `windows=2`, `products=1`, `artifacts=4`, `final_cjk=9936`.
  - Real Codex-backed HTTP smoke verified `mission_plan` and `work_product` persisted on a real Mission, then a provider timeout produced `paused_retryable` instead of `failed`.
  - Resume smoke verified the same paused Mission can be started again through `POST /api/work/missions/{missionId}/start` and complete; final event sequence included `MISSION_PAUSED_RETRYABLE`, second `MISSION_STARTED`, `MISSION_PLAN_UPDATED`, two `PRODUCT_UPDATED`, `PRODUCT_INSPECTED`, and `MISSION_COMPLETED`.
  - Codex CLI timeout cleanup verified no orphan `codex exec` process remained after timeout.
  - Existing public `8145`, Idle Auto `8147`, Work V0.5 `8148`, fake relay `18148`, and legacy `8130` services were not stopped.
- Work V1 long-turn progress local verification:
  - Added safe non-streaming lifecycle events: `MODEL_TURN_STARTED`, `MODEL_TURN_HEARTBEAT`, `MODEL_TURN_COMPLETED`, `MODEL_TURN_RETRYING`, `MODEL_TURN_INVALID`, `TOOL_CALLED`, and `WORK_WINDOW_FAILED`.
  - Added bounded automatic retry for retryable Lead model errors before `paused_retryable`.
  - Delegate model failures after `WORK_WINDOW_OPENED` now mark the Work Window `failed` and emit `WORK_WINDOW_FAILED` instead of leaving the window running.
  - React Work UI now includes a compact latest-activity strip so long model turns do not look frozen while event polling continues.
  - Local verification passed: all backend test directories, Work Mode `51`, model_runtime `24`, interactions `21`, frontend build, in-process full smoke `final_cjk=9936`, HTTP full smoke `final_cjk=9936`, and browser smoke `windows=2/final_cjk=9936`.
  - After adding env-tunable progress settings, local Work Mode tests passed with `52` tests and all backend test directories passed.
  - Target isolated `8161` verification passed: Work Mode `52`, model_runtime `24`, interactions `21`, frontend build, in-process full smoke `events=30/windows=2/products=1/artifacts=4/final_cjk=9936`, HTTP full smoke `events=30/windows=2/products=1/artifacts=4/final_cjk=9936`, browser smoke `windows=2/final_cjk=9936`, service `active`, `/health` ok, and static React root/assets present.
- Work V1 UI architecture isolated verification on active `8163`:
  - Target source: `~/hackson_work_ui_8163`.
  - Target service: `hackson-work-ui-8163.service`, active on `127.0.0.1:8163`.
  - Target database: `hackson_work_ui_8163`.
  - Target Work Mode tests passed: `55`.
  - Target frontend build passed with Node `20.19.6`, assets `/assets/index-qPU-cMH4.js` and `/assets/index-BbzX_UAM.css`.
  - Target in-process full smoke passed: `events=30/windows=2/products=1/artifacts=4/final_cjk=9936`.
  - Target HTTP full smoke passed: `events=30/windows=2/products=1/artifacts=4/final_cjk=9936`.
  - Target browser smoke passed with desktop and mobile screenshots, verified Work Console order, Artifact lineage, default-collapsed Diagnostics, final CJK count `9936`, and no mobile horizontal overflow.
  - Target `8163` live service health returned `{"status":"ok"}` and static root/assets returned `200`.
- Work V1 UI architecture public static verification on active `8145`:
  - Public `frontend/dist` was backed up to `~/hackson_domain_8145/frontend/dist.backup_work_ui_20260527230937`, then replaced from `~/hackson_work_ui_8163/frontend/dist` without restarting `hackson-domain-8145.service`.
  - Public domain `https://hackson.catachess.com/health` returned `{"status":"ok"}`.
  - Public root and assets verified with browser UA: `/assets/index-qPU-cMH4.js` and `/assets/index-BbzX_UAM.css` returned `200`.
  - Public Playwright static check registered a test user, created a Project and draft Mission without starting the model, and verified Work Console order `activity>windows>product>progress>diagnostics` with Diagnostics collapsed.
  - Screenshot: `scripts/artifacts/work_mode_public_ui_static_check.png`.
