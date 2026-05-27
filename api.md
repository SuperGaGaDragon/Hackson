## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex

## brief intro
- This document is the verified API and port map for Hackson.
- Only APIs that have been tested on the target machine are listed here.
- Backend uses FastAPI. Frontend uses React + Vite.
- V1 demo model endpoint is platform-managed and is not exposed through user APIs.

## verified environment
- Target machine: documented locally in `docs/数据库/machine.md`; that file is ignored and must not be pushed.
- Backend test directory on target machine: `~/hackson_backend_test/backend`
- Latest current backend directory on target machine: `~/hackson_backend_current_8125/backend`
- Latest smoke venv used by current backend ports: `~/hackson_backend_review_smoke/backend/.venv`
- Persona/topic/compact smoke directory on target machine: `~/hackson_persona_topic_8131/backend`
- Agent/Idle history smoke directory on target machine: `~/hackson_agent_idle_8132/backend`
- Idle Say/topic/speaker smoke directory on target machine: `~/hackson_idle_say_8133/backend`
- Work Mode Mission Runtime smoke directory on target machine: `~/hackson_work_mode_smoke/backend`
- Work Mode Mission Runtime smoke venv: `~/hackson_work_mode_smoke/backend/.venv`
- Work Mode V0 stable smoke directory on target machine: `~/hackson_work_mode_v0_stable/backend`
- Work Mode V0 stable smoke venv: `~/hackson_work_mode_v0_stable/backend/.venv`
- Work Mode V0.1 Employee smoke directory on target machine: `~/hackson_work_mode_v01_employees/backend`
- Work Mode V0.1 Employee smoke venv: `~/hackson_work_mode_v01_employees/backend/.venv`
- Work Mode Workspace name-only smoke directory on target machine: `~/hackson_work_mode_workspace_nameonly_8144/backend`
- Work Mode Workspace name-only smoke venv: `~/hackson_work_mode_workspace_nameonly_8144/backend/.venv`
- Work Mode Two Agent smoke directory on target machine: `~/hackson_work_mode_two_agents_8146/backend`
- Work Mode Two Agent smoke venv: `~/hackson_work_mode_two_agents_8146/backend/.venv`
- Public domain deployment directory on target machine: `~/hackson_domain_8145`
- Public domain deployment backend venv: `~/hackson_domain_8145/backend/.venv`
- Public domain deployment URL: `https://hackson.catachess.com/`
- Public domain deployment backend bind: `127.0.0.1:8145`
- Public domain deployment service: `hackson-domain-8145.service`, user-level systemd, enabled and active.
- Public domain cloudflared service: `hackson-cloudflared.service`, user-level systemd, enabled and active.
- Public domain cloudflared config: `~/.cloudflared/hackson.yml`
- Public domain note: target-machine cloudflared currently manages the `catachess.com` zone; `hackson.catiechess.com` did not resolve from this target configuration.
- Production directory on target machine: `~/hackson_production`
- Production user-level systemd service: `hackson-production.service`
- Production app URL: `http://100.70.248.39:8130/`
- Production backend bind: `0.0.0.0:8130`
- Production frontend assets are served by FastAPI from `~/hackson_production/frontend/dist`.
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
- Verified review smoke port: `127.0.0.1:8125`
- Verified product database smoke port: `127.0.0.1:8126`
- Verified persona/topic/compact smoke port: `127.0.0.1:8131`
- Verified Agent/Idle history smoke port: `127.0.0.1:8132`
- Verified Idle Say/topic/speaker smoke port: `127.0.0.1:8133`
- Verified Work Mode Mission Runtime smoke port: `127.0.0.1:8141`
- Verified Work Mode V0 stable smoke port: `127.0.0.1:8142`
- Verified Work Mode V0.1 Employee smoke port: `127.0.0.1:8143`
- Verified Work Mode Workspace name-only smoke port: `127.0.0.1:8144`
- Verified Work Mode Two Agent smoke port: `127.0.0.1:8146`
- Verified public domain deployment port: `127.0.0.1:8145`
- Verified production port: `100.70.248.39:8130`
- Port status after verification: target smoke ports are running; local tunnels/dev servers are temporary unless listed as running.
- Database used in raw user/conversation verification: MongoDB database `hackson_test`
- Database used in interaction/model verification: MongoDB database `hackson_target_smoke`
- Database used in review smoke verification: MongoDB database `hackson_current_8125`
- Database used in product database smoke verification: MongoDB database `hackson`
- Database used in persona/topic/compact smoke verification: MongoDB database `hackson_persona_topic_8131`
- Database used in Agent/Idle history smoke verification: MongoDB database `hackson_agent_idle_8132`
- Database used in Idle Say/topic/speaker smoke verification: MongoDB database `hackson_idle_say_8133`
- Database used in Work Mode Mission Runtime smoke verification: MongoDB database `hackson_work_mode_smoke`
- Database used in Work Mode V0 stable smoke verification: MongoDB database `hackson_work_mode_v0_stable`
- Database used in Work Mode V0.1 Employee smoke verification: MongoDB database `hackson_work_mode_v01_employees`
- Database used in Work Mode Workspace name-only smoke verification: MongoDB database `hackson_work_mode_workspace_nameonly_8144`
- Database used in Work Mode Two Agent smoke verification: MongoDB database `hackson_work_mode_two_agents_8146`
- Database used in public domain deployment verification: MongoDB database `hackson_domain_8145`
- Production database initialized: MongoDB database `hackson`
- Production database status:
  - collections: `users`, `conversations`, `messages`, `conversation_counters`, `derived_jobs`, `tasks`, `tool_traces`
  - `users` indexes: `_id_`, `username_normalized_1` unique, `email_normalized_1` unique
  - `conversations` indexes: `_id_`, `user_id_1_mode_1_status_1_updated_at_-1`, `user_id_1_mode_1_last_message_at_-1`, `parent_conversation_id_1`
  - `messages` indexes: `_id_`, `conversation_id_1_sequence_1` unique, `conversation_id_1_created_at_-1`, `user_id_1_created_at_-1`, `user_id_1_sender_slot_1_created_at_-1`
  - `conversation_counters` indexes: `_id_`, `conversation_id_1` unique
  - `tasks` indexes: `_id_`, `user_id_1_status_1_updated_at_-1`, `conversation_id_1`
- Production service verification:
  - `hackson-production.service` is enabled and active under user-level `systemd`.
  - Process listens on `0.0.0.0:8130`.
  - Frontend build used target-machine `nvm` Node `20.19.6`.
  - Latest production assets: `/assets/index-CSg3RgOA.js`, `/assets/index-DOSivJMg.css`.
- Production user write verification:
  - Vite proxy path `5178 -> 18126 -> 8126` registered `viteprod_1779763130`.
  - MongoDB query found `viteprod_1779763130@example.com` in `hackson.users`.
  - The same email was absent from `hackson_current_8125.users`.
- Local context-fix verification:
  - Local frontend path `5179 -> 127.0.0.1:8130` registered `ui_ctx_1779852614`.
  - The local `8130` process uses in-memory `mongomock`; it is separate from target production `100.70.248.39:8130`.
  - After 46 idle messages, Nora `#47` responded to the latest "红色按钮" marker instead of the older "工具还是同事" marker.
- Persona/topic/compact verification:
  - Target backend path `~/hackson_persona_topic_8131/backend` served FastAPI on `127.0.0.1:8131` without touching production `8130`.
  - Target backend tests passed: `58 passed, 4 warnings`.
  - API smoke user `persona_1779855711` saved `personality` and `story`, created a long idle history, sent `discussionDirection`, received an Agent reply from `agent_1`, and persisted `0` user messages for the topic direction.
  - API smoke model: `gpt-5.1`.
  - Frontend target-backed path `5180 -> 18131 -> 8131` completed Register, Me profile save, Idle Topic entry, and Tick with `31` API responses and `0` API errors.
  - Screenshot: `/tmp/hackson_persona_topic_ui.png`.
- Agent/Idle history verification:
  - Target backend path `~/hackson_agent_idle_8132/backend` served FastAPI on `127.0.0.1:8132` without touching production `8130`.
  - Local full backend tests passed: `62 passed, 4 warnings`.
  - Target scoped backend tests passed for `agents`, `users`, `context`, `interactions`, and `conversations`: `31 passed`.
  - Target full backend test collection is blocked by unrelated in-progress `work_mode` employee test/schema drift, not by Agent/Idle history modules.
  - API smoke user `agentidle_57756400` saved two user-owned Agent profiles `Mira` and `Rook`, created two idle conversations with topic metadata, ticked the selected idle topic, and persisted `0` user messages for topic direction.
  - API smoke model: `gpt-5.1`.
  - Frontend target-backed path `5183 -> 18132 -> 8132` verified Me renders two Agent editors, Idle renders History/New, New opens a topic modal, Tick produces a visible `Mira` Agent message, and no UI status errors were present.
  - Screenshot: `/tmp/hackson_agent_idle_ui.png`.
- Idle Say/topic/speaker verification:
  - Target backend path `~/hackson_idle_say_8133/backend` served FastAPI on `127.0.0.1:8133` without touching production `8130`.
  - Local full backend tests passed: `67 passed, 4 warnings`.
  - Target full backend tests passed: `67 passed, 4 warnings`.
  - API smoke user `idlesay_1779859412` saved two user-owned Agent profiles `Mira` and `Rook`, created one idle conversation with `metadata.topicDirection`, appended a visible idle user interjection through `POST /api/conversations/{conversationId}/messages`, then ticked the same idle conversation with `discussionDirection`.
  - API smoke confirmed message types stayed in one idle conversation as `["user", "agent"]`; no companion conversation was created for Say.
  - API smoke model: `gpt-5.1`.
  - Frontend target-backed path `5185 -> 18133 -> 8133` verified New topic, Say, Auto, and speaker labels. After Say, the page stayed in `IDLE`, `Auto` remained enabled, clicking Auto generated visible `Mira #2`, and the Topic panel retained `只讨论 30 秒产品演示开场，不要回到技术实现`.
  - Screenshot: `/tmp/hackson_idle_say_ui.png`.
- Work Mode Mission Runtime verification:
  - Target backend path `~/hackson_work_mode_smoke/backend` served FastAPI on `127.0.0.1:8141` without touching production `8130`.
  - Target MongoDB database `hackson_work_mode_smoke` stored `work_projects`, `work_missions`, `work_runs`, `work_steps`, `work_events`, and `work_event_counters`.
  - Verified event sequence: `MISSION_CREATED`, `MISSION_STARTED`, `STEP_STARTED`, `SUMMARY`, `RAW_LOG`, `PRODUCT_UPDATED`, `STEP_COMPLETED`, `MISSION_COMPLETED`.
  - Verified Lead Employee fields: `leadEmployeeId=employee_default_lead`, `leadEmployeeName=Lead`.
  - Frontend target-backed path `5181 -> 18141 -> 8141` completed Register, Login, Project create, Mission create, Mission start, event polling, and responsive screenshots.
  - Screenshots: `/tmp/hackson_work_mode_target_desktop.png`, `/tmp/hackson_work_mode_target_mobile.png`.
- Work Mode V0 stable verification:
  - Target backend path `~/hackson_work_mode_v0_stable/backend` served FastAPI on `127.0.0.1:8142` without touching production `8130`.
  - Target backend module tests passed, including `work_mode/tests` with `9` tests.
  - Target API smoke verified Start, Stop, `MISSION_STOP_REQUESTED`, `MISSION_STOPPED`, `afterSequence`, Lead Employee fields, and MongoDB indexes.
  - Target event sequence for stop path: `MISSION_CREATED`, `MISSION_STARTED`, `STEP_STARTED`, `MISSION_STOP_REQUESTED`, `MISSION_STOPPED`.
  - Frontend target-backed path `5182 -> 18142 -> 8142` completed Register, Login, Project create, Mission create, completed path, stopped path, event polling, and mobile check.
  - Screenshots: `/tmp/hackson_work_mode_v0_complete_desktop.png`, `/tmp/hackson_work_mode_v0_stop_desktop.png`, `/tmp/hackson_work_mode_v0_mobile.png`.
- Work Mode V0.1 Employee verification:
  - Target backend path `~/hackson_work_mode_v01_employees/backend` served FastAPI on `127.0.0.1:8143` without touching production `8130`.
  - Target `work_mode/tests` passed with `12` tests.
  - API smoke verified Employee create/list, Project Team add/list, Mission create with selected Lead Employee, selected Employee role in event payloads, and final completed Mission.
  - Target MongoDB database `hackson_work_mode_v01_employees` stored `work_employees`, `work_project_employees`, `work_projects`, `work_missions`, and `work_events` with indexes.
  - Frontend target-backed path `5184 -> 18143 -> 8143` completed Register, Login, Employee create, Project create, Team add, Lead select, Mission start, event polling, and mobile check.
  - Screenshots: `/tmp/hackson_work_mode_v01_employee_desktop.png`, `/tmp/hackson_work_mode_v01_employee_mobile.png`.
- Work Mode Workspace name-only verification:
  - Target backend path `~/hackson_work_mode_workspace_nameonly_8144/backend` served FastAPI on `127.0.0.1:8144` without touching production `8130` or existing Work smoke `8143`.
  - Local and target `work_mode/tests` passed with `12` tests.
  - API smoke registered `nameonly_1779860201`, created `Name Only Project` through `POST /api/work/projects` with body `{"name":"Name Only Project"}`, listed it through `GET /api/work/projects`, and confirmed MongoDB stored `repo_path` as an empty internal value.
  - Frontend target-backed path `5186 -> 18144 -> 8144` registered a new user, verified the Workspace New Project form has no repo/path input, created `Name UI 1779860276330` with name only, opened Project detail, returned to Workspace on mobile, and had `0` failed API responses.
  - Screenshots: `/tmp/hackson_work_nameonly_workspace_desktop.png`, `/tmp/hackson_work_nameonly_project_desktop.png`, `/tmp/hackson_work_nameonly_workspace_mobile.png`.
- Work Mode Two Agent verification:
  - Target backend path `~/hackson_work_mode_two_agents_8146/backend` served FastAPI on `127.0.0.1:8146` without touching production `8130`, public domain `8145`, or existing Work smoke ports.
  - Local and target `work_mode/tests` passed with `14` tests.
  - API smoke registered `twoagent_1779861983`, updated the user's two `agentProfiles`, created a Project by name only, created a Mission with `leadEmployeeId: "agent_1"` without calling Employee or Team APIs, and started the Mission.
  - Verified Mission and MongoDB values: `leadEmployeeId=agent_1`, `leadEmployeeName=Plotter`, `leadEmployeeRole=outline lead`, `payload.employee.id=agent_1`.
  - Frontend target-backed path `5189 -> 18146 -> 8146` registered a new user, updated the two Agents to `Plotter` and `Drafter`, created a Project, verified no Employee or Team controls were visible, created a Mission, clicked Start, reached completion, and had `0` failed API responses.
  - Screenshots: `/tmp/hackson_work_agents_project_desktop.png`, `/tmp/hackson_work_agents_started_desktop.png`, `/tmp/hackson_work_agents_mobile.png`.
- Public domain deployment verification:
  - Target backend path `~/hackson_domain_8145/backend` serves FastAPI on `127.0.0.1:8145` with React assets from `~/hackson_domain_8145/frontend/dist`.
  - Services are enabled and active: `hackson-domain-8145.service` and `hackson-cloudflared.service`.
  - Public URL is `https://hackson.catachess.com/`.
  - Target deployment tests passed: `tests/test_main_static_frontend.py` and `work_mode/tests`, `13 passed`.
  - Public smoke verified `GET /health`, `GET /`, `GET /assets/index-CheJ5rE_.js`, `POST /api/users/register`, `POST /api/work/projects`, and `POST /api/idle/{conversationId}/tick`.
  - Public model smoke returned `gpt-5.1`.
  - Browser screenshot: `/tmp/hackson_domain_home.png`.
- Last verified at: 2026-05-27

## port map
| Port | Service | Bind | Status | Purpose |
| --- | --- | --- | --- | --- |
| 8100 | FastAPI backend temporary test server | `127.0.0.1` | Verified, not kept running | Target-machine raw user/conversation API verification without touching existing services |
| 8101 | FastAPI backend temporary test server | `127.0.0.1` | Running on target machine during latest frontend check | Target-machine interaction/context/model API verification without touching existing services |
| 8120 | FastAPI backend temporary test server | `127.0.0.1` | Verified, stopped after check | Target-machine Agent catalog API verification without touching existing services |
| 8122 | FastAPI backend temporary test server | `127.0.0.1` | Verified, running during latest diagnosis | Target-machine latest backend verification for Agent catalog and idle join without touching existing services |
| 8123 | FastAPI backend temporary test server | `127.0.0.1` | Older review smoke, superseded by `8124` | Target-machine review smoke for task API and new backend modules without touching existing services |
| 8124 | FastAPI backend temporary test server | `127.0.0.1` | Older review smoke, superseded by `8125` | Target-machine review smoke for task API and new backend modules without touching existing services |
| 8125 | FastAPI backend temporary test server | `127.0.0.1` | Verified, running during latest backend review smoke | Latest target-machine smoke for companion_1 continuation and Work Mode without touching existing services |
| 8126 | FastAPI backend temporary product database smoke server | `127.0.0.1` | Verified and running | Product database auth smoke using MongoDB database `hackson` without touching existing services |
| 8131 | FastAPI backend temporary persona/topic/compact smoke server | `127.0.0.1` | Verified and running | Target-machine persona, idle topic direction, and compact smoke using MongoDB database `hackson_persona_topic_8131` without touching production |
| 8132 | FastAPI backend temporary Agent/Idle history smoke server | `127.0.0.1` | Verified and running | Target-machine user-owned Agent profiles, idle history, and new topic modal smoke using MongoDB database `hackson_agent_idle_8132` |
| 8133 | FastAPI backend temporary Idle Say/topic/speaker smoke server | `127.0.0.1` | Verified and running | Target-machine Idle Say, topic steering, and speaker boundary smoke using MongoDB database `hackson_idle_say_8133` |
| 8141 | FastAPI backend temporary Work Mode Mission Runtime smoke server | `127.0.0.1` | Verified and running | Target-machine Work Mode V0 Mission Runtime smoke using MongoDB database `hackson_work_mode_smoke` without touching production |
| 8142 | FastAPI backend temporary Work Mode V0 stable smoke server | `127.0.0.1` | Verified and running | Target-machine Work Mode V0 completed and stopped path smoke using MongoDB database `hackson_work_mode_v0_stable` |
| 8143 | FastAPI backend temporary Work Mode V0.1 Employee smoke server | `127.0.0.1` | Verified and running | Target-machine Employee Library and Project Team smoke using MongoDB database `hackson_work_mode_v01_employees` |
| 8144 | FastAPI backend temporary Work Mode Workspace name-only smoke server | `127.0.0.1` | Verified and running | Target-machine name-only Project creation smoke using MongoDB database `hackson_work_mode_workspace_nameonly_8144` |
| 8145 | Hackson public domain FastAPI backend and frontend | `127.0.0.1` | Verified, enabled, and running as `hackson-domain-8145.service` | Public domain deployment for `https://hackson.catachess.com/`, serving `/api/*` and React `dist/` from one origin |
| 8146 | FastAPI backend temporary Work Mode Two Agent smoke server | `127.0.0.1` | Verified and running | Target-machine two user Agent Mission lead smoke using MongoDB database `hackson_work_mode_two_agents_8146` |
| 8130 | Hackson production FastAPI backend and frontend | `0.0.0.0` | Verified, enabled, and running as `hackson-production.service` | Production app serving `/api/*` and React `dist/` from one origin |
| 8130 | FastAPI backend temporary local context-fix server | `127.0.0.1` on local Mac | Verified and running in `screen` session `hackson_backend_8130` | Local-only latest idle context verification with in-memory `mongomock`; not production |
| 5173 | Vite frontend temporary dev server | `127.0.0.1` | Running locally | Hackson React frontend prototype |
| 18101 | SSH local tunnel to target backend | `127.0.0.1` | Running locally during latest frontend check | Local browser access to target-machine `127.0.0.1:8101` |
| 18122 | SSH local tunnel to target backend | `127.0.0.1` | Verified, running during latest diagnosis | Local browser access to latest target backend `127.0.0.1:8122` |
| 18124 | SSH local tunnel to target backend | `127.0.0.1` | Historical Work frontend integration | Local browser access to target backend `127.0.0.1:8124` |
| 18125 | SSH local tunnel to target backend | `127.0.0.1` | Verified during latest frontend integration, not kept running locally | Local browser access to latest target backend `127.0.0.1:8125` |
| 18126 | SSH local tunnel to target backend | `127.0.0.1` | Verified and running | Local browser access to product database backend `127.0.0.1:8126` |
| 18131 | SSH local tunnel to target backend | `127.0.0.1` | Verified and running | Local browser access to target persona/topic/compact backend `127.0.0.1:8131` |
| 18132 | SSH local tunnel to target backend | `127.0.0.1` | Verified and running | Local browser access to target Agent/Idle history backend `127.0.0.1:8132` |
| 18133 | SSH local tunnel to target backend | `127.0.0.1` | Verified and running | Local browser access to target Idle Say/topic/speaker backend `127.0.0.1:8133` |
| 18141 | SSH local tunnel to target backend | `127.0.0.1` | Verified during Work Mode frontend integration, not kept running locally | Local browser access to target Work Mode backend `127.0.0.1:8141` |
| 18142 | SSH local tunnel to target backend | `127.0.0.1` | Verified during Work Mode V0 stable frontend integration, not kept running locally | Local browser access to target Work Mode V0 backend `127.0.0.1:8142` |
| 18143 | SSH local tunnel to target backend | `127.0.0.1` | Verified during Work Mode V0.1 Employee frontend integration, not kept running locally | Local browser access to target Work Mode Employee backend `127.0.0.1:8143` |
| 18144 | SSH local tunnel to target backend | `127.0.0.1` | Verified during Work Mode Workspace name-only frontend integration, not kept running locally | Local browser access to target Work Mode name-only backend `127.0.0.1:8144` |
| 18146 | SSH local tunnel to target backend | `127.0.0.1` | Verified during Work Mode Two Agent frontend integration, not kept running locally | Local browser access to target Work Mode two Agent backend `127.0.0.1:8146` |
| 5175 | Vite frontend temporary dev server with API proxy | `127.0.0.1` | Verified after restart against `18122`; running as PID recorded in `/tmp/hackson_frontend_5175.pid` | Local frontend connected to latest target backend through Vite proxy |
| 5177 | Vite frontend temporary dev server with API proxy | `127.0.0.1` | Verified against `18125 -> 8125`, not kept running locally | Local frontend E2E for companion_1 continuation and Work Mode |
| 5178 | Vite frontend temporary dev server with API proxy | `127.0.0.1` | Verified and running | Local frontend product database auth smoke through default proxy `18126 -> 8126` |
| 5179 | Vite frontend temporary dev server with API proxy | `127.0.0.1` | Verified and running in `screen` session `hackson_frontend_5179` | Local UI verification for latest idle context fix through `127.0.0.1:8130` |
| 5180 | Vite frontend temporary dev server with API proxy | `127.0.0.1` | Verified and running in `screen` session `hackson_frontend_5180` | Local persona/topic UI verification through `18131 -> 8131` |
| 5183 | Vite frontend temporary dev server with API proxy | `127.0.0.1` | Verified and running in `screen` session `hackson_frontend_5183` | Local Agent/Idle history UI verification through `18132 -> 8132` |
| 5185 | Vite frontend temporary dev server with API proxy | `127.0.0.1` | Verified and running | Local Idle Say/topic/speaker UI verification through `18133 -> 8133` |
| 5181 | Vite frontend temporary dev server with API proxy | `127.0.0.1` | Verified during Work Mode frontend integration, not kept running locally | Local Work Mode UI verification through `18141 -> 8141` |
| 5182 | Vite frontend temporary dev server with API proxy | `127.0.0.1` | Verified during Work Mode V0 stable frontend integration, not kept running locally | Local Work Mode V0 completed/stopped UI verification through `18142 -> 8142` |
| 5184 | Vite frontend temporary dev server with API proxy | `127.0.0.1` | Verified during Work Mode V0.1 Employee frontend integration, not kept running locally | Local Work Mode Employee UI verification through `18143 -> 8143` |
| 5186 | Vite frontend temporary dev server with API proxy | `127.0.0.1` | Verified during Work Mode Workspace name-only frontend integration, not kept running locally | Local Work Mode Workspace name-only UI verification through `18144 -> 8144` |
| 5189 | Vite frontend temporary dev server with API proxy | `127.0.0.1` | Verified during Work Mode Two Agent frontend integration, not kept running locally | Local Work Mode two Agent UI verification through `18146 -> 8146` |

## api端口集合
| Method | API | Auth | Verified Port | Module | Purpose |
| --- | --- | --- | --- | --- | --- |
| GET | `/health` | No | `8100`, `8101`, `8126`, `8130`, `8131`, `8132`, `8133`, `8141`, `8142`, `8143`, `8144`, `8145`, `8146`, `https://hackson.catachess.com` | `backend/main.py` | Backend health check |
| GET | `/` | No | `8130`, `8145`, `https://hackson.catachess.com` | `backend/main.py` | React frontend HTML |
| GET | `/assets/{asset}` | No | `8130`, `8145`, `https://hackson.catachess.com` | `backend/main.py` | React frontend assets |
| POST | `/api/users/register` | No | `8100`, `8101`, `8126`, `8130`, `8131`, `8132`, `8133`, `8141`, `8142`, `8143`, `8144`, `8145`, `8146`, `https://hackson.catachess.com` | `backend/users/` | Register user and return JWT |
| POST | `/api/users/login` | No | `8100`, `8141`, `8142`, `8143` | `backend/users/` | Login by email or username |
| GET | `/api/users/me` | Bearer JWT | `8100`, `8126`, `8130`, `8131`, `8132`, `8133`, `8146` | `backend/users/` | Read current user, including human profile and two Agent profiles |
| PATCH | `/api/users/me` | Bearer JWT | `8100`, `8131`, `8132`, `8133`, `8146` | `backend/users/` | Update current user settings, including human profile and two Agent profiles |
| POST | `/api/users/logout` | No server state | `8100` | `backend/users/` | Client-side JWT logout placeholder |
| GET | `/api/agents` | No | `8120`, `8122`, `8130`, `8131` | `backend/agents/` | List fixed V1 Agent display profiles |
| POST | `/api/conversations` | Bearer JWT | `8100`, `8101`, `8132`, `8133` | `backend/conversations/` | Create conversation container, including clean idle topics |
| GET | `/api/conversations` | Bearer JWT | `8100`, `8132`, `8133` | `backend/conversations/` | List current user's conversations, including idle history |
| GET | `/api/conversations/{conversationId}` | Bearer JWT | `8100` | `backend/conversations/` | Read one owned conversation |
| POST | `/api/conversations/{conversationId}/messages` | Bearer JWT | `8100`, `8131`, `8133` | `backend/conversations/` | Append raw historical message; product-approved for Idle Say interjection |
| GET | `/api/conversations/{conversationId}/messages` | Bearer JWT | `8100`, `8101`, `8131`, `8132`, `8133` | `backend/conversations/` | Page conversation messages |
| GET | `/api/idle/conversation` | Bearer JWT | `8100`, `8101`, `8130`, `8131`, `8133` | `backend/conversations/` | Get or create active idle conversation |
| POST | `/api/idle/{conversationId}/tick` | Bearer JWT | `8101`, `8131`, `8132`, `8133`, `8145`, `https://hackson.catachess.com` | `backend/interactions/` | Generate one idle Agent reply; accepts optional `discussionDirection` |
| POST | `/api/idle/{conversationId}/join` | Bearer JWT | `8101`, `8122`, `8125`, `8130` | `backend/interactions/` | Create companion_1 from idle and reply |
| POST | `/api/companion/{conversationId}/messages` | Bearer JWT | `8101`, `8125`, `8130` | `backend/interactions/` | Save companion_1 or companion_2 user message and reply |
| POST | `/api/tasks` | Bearer JWT | `8124`, `8125`, `8130` | `backend/tasks/` | Create Work Mode task and its `work` conversation |
| GET | `/api/tasks` | Bearer JWT | `8124`, `8125`, `8130` | `backend/tasks/` | List current user's Work Mode tasks |
| GET | `/api/tasks/{taskId}` | Bearer JWT | Local tests | `backend/tasks/` | Read one current-user-owned Work Mode task |
| POST | `/api/tasks/{taskId}/messages` | Bearer JWT | `8124`, `8125`, `8130` | `backend/tasks/`, `backend/interactions/` | Send a minimal Work Mode message using task state |
| POST | `/api/work/projects` | Bearer JWT | `8141`, `8142`, `8143`, `8144`, `8145`, `8146`, `https://hackson.catachess.com` | `backend/work_mode/` | Create a Work Mode Project by name; `repoPath` is optional internal metadata |
| GET | `/api/work/projects` | Bearer JWT | `8141`, `8142`, `8143`, `8144`, `8146` | `backend/work_mode/` | List current user's Work Mode Projects |
| POST | `/api/work/employees` | Bearer JWT | `8143` | `backend/work_mode/` | Create a Work Mode Employee profile |
| GET | `/api/work/employees` | Bearer JWT | `8143` | `backend/work_mode/` | List current user's Work Mode Employees |
| POST | `/api/work/projects/{projectId}/employees` | Bearer JWT | `8143` | `backend/work_mode/` | Add an Employee to a Project team |
| GET | `/api/work/projects/{projectId}/employees` | Bearer JWT | `8143` | `backend/work_mode/` | List Project team Employees |
| POST | `/api/work/missions` | Bearer JWT | `8141`, `8142`, `8143`, `8146` | `backend/work_mode/` | Create a Mission with a default Lead, legacy Employee, or current user Agent slot `agent_1` / `agent_2` |
| GET | `/api/work/projects/{projectId}/missions` | Bearer JWT | `8141`, `8142`, `8143`, `8146` | `backend/work_mode/` | List Missions in one Project |
| GET | `/api/work/missions/{missionId}` | Bearer JWT | `8141`, `8142`, `8143`, `8146` | `backend/work_mode/` | Read Mission detail and recent events |
| POST | `/api/work/missions/{missionId}/start` | Bearer JWT | `8141`, `8142`, `8143`, `8146` | `backend/work_mode/` | Start the V0 deterministic Mission worker |
| POST | `/api/work/missions/{missionId}/stop` | Bearer JWT | `8142` | `backend/work_mode/` | Request stop for a running Mission and emit stop events |
| GET | `/api/work/missions/{missionId}/events` | Bearer JWT | `8141`, `8142`, `8146` | `backend/work_mode/` | Poll Mission events after a sequence number |

Notes:
- Ports `8100` and `8101` were temporary target-machine verification ports and are not kept running.
- The API paths are mounted by the same FastAPI app; use the active backend deployment base URL in production.
- Production base URL is `http://100.70.248.39:8130/`.
- Detailed request and response shapes are listed below.
- New derived modules are verified by local and target-machine backend tests: `summaries/`, `memory/`, `diary/`, `workers/`, `tasks/`, and `work_mode/`.

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
- latest diagnosis uses SSH tunnel `18122` to target backend `8122`, then Vite port `5175`
- Work frontend integration used SSH tunnel `18124` to target backend `8124`
- Latest frontend integration uses SSH tunnel `18125` to target backend `8125`, then Vite port `5177`
- Product database auth smoke uses SSH tunnel `18126` to target backend `8126`, then Vite port `5178`
- Local context-fix UI verification uses Vite port `5179` to local backend `127.0.0.1:8130`
- Persona/topic UI verification uses SSH tunnel `18131` to target backend `8131`, then Vite port `5180`
- Agent/Idle history UI verification uses SSH tunnel `18132` to target backend `8132`, then Vite port `5183`
- Idle Say/topic/speaker UI verification uses SSH tunnel `18133` to target backend `8133`, then Vite port `5185`
- Work Mode Two Agent UI verification uses SSH tunnel `18146` to target backend `8146`, then Vite port `5189`
- Production UI E2E uses `http://100.70.248.39:8130/` directly with no Vite proxy.
- latest `5175` API smoke: `/api/agents` returned `200 OK`; `/api/idle/{conversationId}/join` returned `201 Created`

Notes:
- Frontend does not expose model endpoint, provider, API key, Claude/OpenAI key, or local model path settings.
- V1 product copy is intentionally short per `agents/frontend_restrictions.md`.
- Current frontend only renders backend-backed surfaces: Auth, Idle, Chat, Work, and Me.
- Idle uses `/api/conversations?mode=idle`, `/api/conversations` for New topic, message history, `/api/idle/{conversationId}/tick`, and `/api/idle/{conversationId}/join`.
- Idle Say uses `POST /api/conversations/{conversationId}/messages` to append a visible user interjection while staying in idle; the next Tick or Auto call uses `/api/idle/{conversationId}/tick`.
- Companion follow-up uses `/api/companion/{conversationId}/messages` for `companion_1` and `companion_2`.
- Chat uses `companion_2` conversation creation/history and `/api/companion/{conversationId}/messages`.
- Work uses `/api/tasks`, task history, and `/api/tasks/{taskId}/messages`.
- Local browser checks should use Vite proxy to avoid CORS:

```bash
ssh -N -L 127.0.0.1:18122:127.0.0.1:8122 catadragon@100.70.248.39
VITE_API_PROXY_TARGET=http://127.0.0.1:18122 npm run dev -- --port 5175
```

For current frontend integration against the latest review backend:

```bash
ssh -N -L 127.0.0.1:18125:127.0.0.1:8125 catadragon@100.70.248.39
VITE_API_PROXY_TARGET=http://127.0.0.1:18125 npm run dev -- --port 5177
```

For product database auth verification:

```bash
ssh -fN -L 127.0.0.1:18126:127.0.0.1:8126 catadragon@100.70.248.39
npm run dev -- --host 127.0.0.1 --port 5178
```

Latest frontend E2E result:
- Register succeeded.
- Idle loaded.
- Tick created one Agent message.
- Join created a `companion_1` child with user and Agent messages.
- Companion_1 child follow-up sent through `/api/companion/{conversationId}/messages` and returned user `#3` plus Agent `#4`.
- Chat created/sent a `companion_2` message pair.
- Chat send now shows the outgoing user message immediately, replaces it with the persisted user message after the API returns, then appends the Agent reply.
- Work created a task, sent a Work message, and returned user `#1` plus Agent `#2`.
- Me loaded current user settings.

Latest frontend issue check:
- Idle / `companion_1` link is backend-healthy. Frontend now keeps parent idle history visible, inserts a `Joined` event, shows returned `companion_1` user and Agent messages, then keeps the composer enabled for child follow-up turns.
- `companion_2` history selection uses existing `GET /api/conversations?mode=companion_2` plus message history. No new backend endpoint is required for selection.
- Local auto title is derived from the first user message. Persistent server-side renaming would require a future verified conversation update endpoint.
- Browser E2E verified: two idle ticks, join continuity from 2 to 4 visible messages, two chat conversations, history switch back to the first conversation.
- Idle auto mode is frontend-driven by repeated `tick` calls. There is no verified backend scheduler or 24x7 idle loop yet.
- Browser E2E verified auto idle produced both fixed MVP Agent slots: Nora then Vale.
- Timeline has `overflow: auto` and auto-scrolls to the latest message. If content is shorter than the panel, there is no scroll range.
- Latest diagnosis: `5175` was returning `/api/agents` 404 because it was still proxying to older `8101`. Restarting `5175` against `18122 -> 8122` makes `/api/agents` return 200 and idle join return 201.
- Latest `companion_2` diagnosis: local browser E2E verified pending order `You #0.5`, final order `You #1` then `Vale #2`, timeline pinned to bottom, no browser console errors, and no failed requests.
- Latest target backend smoke on `8125`: register, idle join, companion_1 follow-up, task create, and Work message all returned 2xx; companion follow-up ended at `You #3` and Agent `#4`; Work ended at `You #1` and Agent `#2`; both model calls used `gpt-5.1`.
- Latest UI E2E on `5177 -> 18125 -> 8125`: Join entered `Companion`, composer stayed enabled, follow-up returned visible `You #3` then `Vale #4`, Work create/send returned visible `You #1` then `Vale #2`, with no browser console errors and no failed requests.
- Product database auth smoke on `5178 -> 18126 -> 8126`: `POST /api/users/register` and `GET /api/users/me` returned 2xx for `viteprod_1779763130`; MongoDB confirmed the user exists in `hackson.users` and not in `hackson_current_8125.users`.
- Production API smoke on `8130`: health, frontend HTML, frontend asset, register, current user, Agents, idle conversation, idle join, companion follow-up, task create, and Work message all returned 2xx; model calls used `gpt-5.1`; MongoDB confirmed the smoke user, 6 messages, and 1 task in `hackson`.
- Production UI E2E on `http://100.70.248.39:8130/`: Register, Idle join, companion follow-up, Work task create, and Work message all completed through production APIs with no browser console errors and no failed requests. Screenshot: `/tmp/hackson_production_ui.png`.
- Production UI fix: optimistic message IDs no longer require `crypto.randomUUID()` because target-machine production currently uses an HTTP origin.
- Local context-fix UI E2E on `5179 -> 127.0.0.1:8130`: after 45 old idle messages plus one latest "红色按钮" marker, Nora `#47` answered the latest marker; browser console errors and failed requests were empty. Screenshot: `/tmp/hackson-context-fix-user-test.png`.
- Persona/topic UI E2E on `5180 -> 18131 -> 8131`: Register, Me profile save, Idle Topic entry, and Tick completed with no failed API responses. Screenshot: `/tmp/hackson_persona_topic_ui.png`.
- Agent/Idle history UI E2E on `5183 -> 18132 -> 8132`: Me rendered two user-owned Agent editors `Mira` and `Rook`; Idle rendered History/New; New opened a topic modal; Tick produced one visible `Mira #1` Agent message; no UI status errors were present. Screenshot: `/tmp/hackson_agent_idle_ui.png`.
- Idle Say/topic/speaker UI E2E on `5185 -> 18133 -> 8133`: New created a clean idle topic; Say appended `You #1` in the same idle conversation; the page stayed in `IDLE`; Auto remained enabled and active; Auto generated `Mira #2`; the Topic panel retained `只讨论 30 秒产品演示开场，不要回到技术实现`; no UI status errors were present. Screenshot: `/tmp/hackson_idle_say_ui.png`.
- Work Mode Workspace name-only UI E2E on `5186 -> 18144 -> 8144`: Register, Workspace, name-only Project create, Project detail, Back to Workspace, and mobile Workspace passed with `0` failed API responses. Screenshots: `/tmp/hackson_work_nameonly_workspace_desktop.png`, `/tmp/hackson_work_nameonly_project_desktop.png`, `/tmp/hackson_work_nameonly_workspace_mobile.png`.
- Work Mode Two Agent UI E2E on `5189 -> 18146 -> 8146`: Register, user Agent profile update to `Plotter` and `Drafter`, Project create, two Agent lead selection, Mission create, Start, completion, and mobile screenshot passed with `0` failed API responses. Screenshots: `/tmp/hackson_work_agents_project_desktop.png`, `/tmp/hackson_work_agents_started_desktop.png`, `/tmp/hackson_work_agents_mobile.png`.

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
    "personality": "",
    "story": "",
    "agentProfiles": [
      {
        "slot": "agent_1",
        "name": "Nora",
        "short": "A1",
        "color": "teal",
        "voice": "precise",
        "personality": "冷静、会追问概念的哲学型 Agent。",
        "story": "正在帮助 Hackson 跑通 V1 demo。"
      },
      {
        "slot": "agent_2",
        "name": "Vale",
        "short": "A2",
        "color": "amber",
        "voice": "sharp",
        "personality": "务实、直接、擅长把想法变成计划的 Agent。",
        "story": "正在把产品计划落成可运行链路。"
      }
    ],
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
    "personality": "",
    "story": "",
    "agentProfiles": [
      {
        "slot": "agent_1",
        "name": "Nora",
        "short": "A1",
        "color": "teal",
        "voice": "precise",
        "personality": "冷静、会追问概念的哲学型 Agent。",
        "story": "正在帮助 Hackson 跑通 V1 demo。"
      },
      {
        "slot": "agent_2",
        "name": "Vale",
        "short": "A2",
        "color": "amber",
        "voice": "sharp",
        "personality": "务实、直接、擅长把想法变成计划的 Agent。",
        "story": "正在把产品计划落成可运行链路。"
      }
    ],
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
  "personality": "说话直接，先给结论，再给理由。",
  "story": "我是一个正在打磨 Hackson demo 的用户。",
  "agentProfiles": [
    {
      "slot": "agent_1",
      "name": "Mira",
      "short": "A1",
      "color": "teal",
      "voice": "careful skeptic",
      "personality": "A careful skeptic who spots product risk.",
      "story": "Mira remembers failed demos."
    },
    {
      "slot": "agent_2",
      "name": "Rook",
      "short": "A2",
      "color": "amber",
      "voice": "direct builder",
      "personality": "A direct builder who turns ambiguity into next steps.",
      "story": "Rook ships small slices."
    }
  ],
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
  "language_preference": "en",
  "personality": "说话直接，先给结论，再给理由。",
  "story": "我是一个正在打磨 Hackson demo 的用户。",
  "agentProfiles": [
    {
      "slot": "agent_1",
      "name": "Mira",
      "voice": "careful skeptic",
      "personality": "A careful skeptic who spots product risk.",
      "story": "Mira remembers failed demos."
    },
    {
      "slot": "agent_2",
      "name": "Rook",
      "voice": "direct builder",
      "personality": "A direct builder who turns ambiguity into next steps.",
      "story": "Rook ships small slices."
    }
  ]
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
  "personality": "说话直接，先给结论，再给理由。",
  "story": "我是一个正在打磨 Hackson demo 的用户。",
  "agentProfiles": [
    {
      "slot": "agent_1",
      "name": "Mira",
      "short": "A1",
      "color": "teal",
      "voice": "careful skeptic",
      "personality": "A careful skeptic who spots product risk.",
      "story": "Mira remembers failed demos."
    },
    {
      "slot": "agent_2",
      "name": "Rook",
      "short": "A2",
      "color": "amber",
      "voice": "direct builder",
      "personality": "A direct builder who turns ambiguity into next steps.",
      "story": "Rook ships small slices."
    }
  ],
  "createdAt": "<iso_datetime>",
  "updatedAt": "<iso_datetime>"
}
```

Notes:
- `personality` maximum length is 1200 characters.
- `story` maximum length is 4000 characters.
- `agentProfiles` must contain the two fixed slots `agent_1` and `agent_2`.
- Agent `name` max is 32 characters, `voice` max is 80, Agent `personality` max is 1200, and Agent `story` max is 4000.

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
Purpose: append a raw message to a conversation. The product frontend may use this endpoint only for Idle `Say`, where the user adds a visible interjection without requesting an immediate companion reply.

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
  "content": "hello",
  "metadata": {
    "source": "idle_say"
  }
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
  "metadata": {
    "source": "idle_say"
  },
  "createdAt": "<iso_datetime>"
}
```

Verified Idle Say values on port `8133`:
- HTTP status: `201 Created`
- Follow-up `POST /api/idle/{conversationId}/tick` stayed in `conversation.mode = "idle"`
- Follow-up `GET /api/conversations/{conversationId}/messages?limit=20` returned message types `["user", "agent"]`
- No `companion_1` conversation is created by Say.

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
  "discussionDirection": "希望从产品约束和用户预期的角度继续讨论。",
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
- `discussionDirection` is an optional user steering field. It enters the model context as direction, not as a persisted transcript message.
- Long idle histories are compacted into a deterministic context summary before recent messages are sent to the model.
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
Purpose: append a `companion_1` or `companion_2` user message and generate one Agent reply.

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

Verified `companion_1` continuation values on port `8125`:
- HTTP status: `201 Created`
- `conversation.mode`: `companion_1`
- `conversation.parentConversationId`: original idle conversation id
- `conversation.messageCount`: `4`
- `userMessage.sequence`: `3`
- `agentMessage.sequence`: `4`
- `agentMessage.senderSlot`: `agent_2`
- `context.modelName`: `gpt-5.1`

Notes:
- This is the product interaction endpoint for `companion_1` continuation and `companion_2`.
- `POST /api/conversations/{conversationId}/messages` remains the raw historical append endpoint. The frontend may use it for Idle `Say`; it should not be used for model replies.

### POST /api/tasks
Purpose: create a Work Mode task and a linked `work` conversation.

Headers:

```text
Authorization: Bearer <accessToken>
Content-Type: application/json
```

Verified request body:

```json
{
  "objective": "Prepare target smoke checklist"
}
```

Verified response shape:

```json
{
  "id": "<task_id>",
  "userId": "<user_id>",
  "conversationId": "<work_conversation_id>",
  "objective": "Prepare target smoke checklist",
  "status": "active",
  "currentPhase": "intake",
  "planSummary": null,
  "progressSummary": null,
  "openQuestions": [],
  "blockers": [],
  "metadata": {},
  "createdAt": "<iso_datetime>",
  "updatedAt": "<iso_datetime>"
}
```

Verified target-machine smoke values on port `8125`:
- `status`: `active`
- linked `conversationId`: non-empty Mongo id
- `GET /api/tasks` returned the created task.

### POST /api/tasks/{taskId}/messages
Purpose: send one minimal Work Mode message using the task state in `ContextMode.WORK`.

Verified target-machine smoke values on port `8125`:
- HTTP status: `201 Created`
- `conversation.mode`: `work`
- `userMessage.sequence`: `1`
- `agentMessage.sequence`: `2`
- `agentMessage.senderSlot`: `agent_2`
- `context.modelName`: `gpt-5.1`

Notes:
- V1.5 does not run Codex CLI or autonomous tools.
- Work messages stay in `mode=work`; companion and idle recipes do not include Work Mode state by default.

### POST /api/work/missions
Purpose: create a Work Mode Mission. Current Work UI selects one of the two user-owned Agents from `Me` by sending `leadEmployeeId` as `agent_1` or `agent_2`.

Headers:

```text
Authorization: Bearer <accessToken>
Content-Type: application/json
```

Verified request body on port `8146`:

```json
{
  "projectId": "<project_id>",
  "title": "Novel Outline",
  "goal": "Plan an 8000 word novel.",
  "leadEmployeeId": "agent_1"
}
```

Verified response fields on port `8146`:

```json
{
  "leadEmployeeId": "agent_1",
  "leadEmployeeName": "Plotter",
  "leadEmployeeRole": "outline lead",
  "status": "draft"
}
```

Verified event payload:

```json
{
  "employee": {
    "id": "agent_1",
    "name": "Plotter",
    "role": "outline lead"
  }
}
```

Notes:
- The response keeps `leadEmployee*` names for compatibility with existing Work Mode event cards.
- In the current product UI, that value represents a user-owned Agent, not a Work-only Employee.
- Legacy Employee and Project Team APIs remain verified on port `8143`, but the current Work UI does not call them.

## developer notes
- All protected user APIs require `Authorization: Bearer <accessToken>`.
- The user module is under `backend/users/`.
- The conversation and raw message history module is under `backend/conversations/`.
- The product interaction orchestration module is under `backend/interactions/`.
- The context builder module is under `backend/context/`.
- The model runtime module is under `backend/model_runtime/`.
- The summary module is under `backend/summaries/`.
- The long-term memory module is under `backend/memory/`.
- The derived jobs and workers module is under `backend/workers/`.
- The Work Mode task module is under `backend/tasks/`.
- The diary module is under `backend/diary/`.
- Shared backend config, database, and security utilities are under `backend/core/`.
- MongoDB is required for full API verification.
- Do not stop existing target-machine services. Use a new free port for tests.
