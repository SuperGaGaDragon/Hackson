## header
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex

## brief intro
- goal for this file.
  - Define the production deployment target for Hackson V1 and record what must be verified.
- 架构思路
  - Production is separate from review and smoke servers.
  - Existing target-machine services must not be stopped.
  - The production backend serves both `/api/*` and the built React frontend from one origin.

## production topology
| Item | Value |
| --- | --- |
| Target machine | `catadragon@100.70.248.39` |
| Production source path | `~/hackson_production` |
| Production backend path | `~/hackson_production/backend` |
| Production frontend build path | `~/hackson_production/frontend/dist` |
| Process manager | user-level `systemd` |
| Service name | `hackson-production.service` |
| Backend bind | `0.0.0.0:8130` |
| Public target URL over Tailscale | `http://100.70.248.39:8130/` |
| Production MongoDB database | `hackson` |

## public domain topology
| Item | Value |
| --- | --- |
| Public URL | `https://hackson.catachess.com/` |
| Public source path | `~/hackson_domain_8145` |
| Public backend path | `~/hackson_domain_8145/backend` |
| Public frontend build path | `~/hackson_domain_8145/frontend/dist` |
| Process manager | user-level `systemd` |
| App service name | `hackson-domain-8145.service` |
| Tunnel service name | `hackson-cloudflared.service` |
| Backend bind | `127.0.0.1:8145` |
| Public MongoDB database | `hackson_domain_8145` |

## port cleanup policy
- Keep Hackson public domain services: `hackson-domain-8145.service` and `hackson-cloudflared.service`.
- Keep legacy Hackson production service `hackson-production.service` on `8130` until the user explicitly retires it.
- Do not touch non-Hackson services such as catachess database/game ports.
- Stop ad hoc Hackson smoke uvicorn processes after their verification value is folded into `api.md`.
- After public domain promotion, do not keep old smoke ports such as `8101`, `8122-8126`, `8131-8133`, `8141-8144`, `8146`, or `8147` running.

## runtime configuration
- Production secrets live only on the target machine in `~/hackson_production/backend/.env`.
- Required backend env keys:
  - `HACKSON_APP_ENV=production`
  - `HACKSON_MONGO_URI=mongodb://127.0.0.1:27017`
  - `HACKSON_MONGO_DATABASE=hackson`
  - `HACKSON_JWT_SECRET=<target-only strong value>`
  - `HACKSON_STATIC_FRONTEND_DIR=/home/catadragon/hackson_production/frontend/dist`
- Model runtime secrets remain platform-side only. They must be available through the production service environment or target-machine `.env` files read by `backend/model_runtime/`.

## deployment steps
1. Confirm local worktree is clean and `startup` is pushed to origin.
2. On the target machine, create or update `~/hackson_production` from the verified `startup` source. The target machine currently cannot clone the private GitHub repo directly, so deployment uses local `rsync` from a clean pushed checkout.
3. Build backend virtualenv under `~/hackson_production/backend/.venv`.
4. Build frontend before importing the production backend app because `HACKSON_STATIC_FRONTEND_DIR` requires `frontend/dist/index.html`.
5. Build frontend with Node `20.19.6` from target-machine `nvm`, `npm ci`, and `npm run build`.
6. Run backend unit tests on the target machine before starting production.
7. Write target-only backend `.env`.
8. Install or update `~/.config/systemd/user/hackson-production.service`.
9. Run `systemctl --user daemon-reload`, enable, restart, and verify the service.

## public domain deployment steps
1. Confirm local tests and frontend build pass.
2. Sync the current working tree to `~/hackson_domain_8145` with `rsync`, excluding `.git`, local dependency caches, and backend `.venv`.
3. Reuse or create `~/hackson_domain_8145/backend/.venv`.
4. Build frontend `dist` locally or on target, then ensure `HACKSON_STATIC_FRONTEND_DIR=/home/catadragon/hackson_domain_8145/frontend/dist`.
5. Run target backend tests in `~/hackson_domain_8145/backend`.
6. Restart only `hackson-domain-8145.service`.
7. Verify `https://hackson.catachess.com/` through API and browser checks.

## verification checklist
- `GET /health` returns `200`.
- `GET /` returns the React frontend HTML from `frontend/dist`.
- `GET /assets/*` returns built frontend assets.
- `POST /api/users/register` writes into MongoDB database `hackson_domain_8145` for public domain verification.
- `GET /api/users/me` works with the returned JWT.
- `PATCH /api/users/me` saves the user's two editable Agent profiles.
- `GET /api/agents` returns baseline Agent display profiles.
- `GET /api/idle/conversation` creates or returns an idle conversation.
- `POST /api/idle/{conversationId}/tick` returns one Agent reply.
- `POST /api/idle/{conversationId}/messages` records a visible Idle user line and returns one Agent reply.
- `POST /api/idle/{conversationId}/join` returns a `companion_1` conversation and Agent response.
- `POST /api/companion/{conversationId}/messages` continues the companion conversation.
- `POST /api/tasks` creates a legacy minimal Work Mode task.
- `POST /api/tasks/{taskId}/messages` returns a Work Mode Agent response.
- `POST /api/work/projects` creates a Project by name.
- `POST /api/work/missions` creates a Mission with `agent_1` or `agent_2` as lead.
- `POST /api/work/missions/{missionId}/start` starts the deterministic V0 worker.
- `GET /api/work/missions/{missionId}/events` returns Mission timeline events.

## current status
- Public domain `https://hackson.catachess.com/` is live and verified.
- `hackson-domain-8145.service` is enabled and active under user-level `systemd`.
- `hackson-cloudflared.service` is enabled and active under user-level `systemd`.
- Public domain serves FastAPI APIs and React `frontend/dist` from one origin.
- Public backend binds to `127.0.0.1:8145`.
- Public MongoDB database is `hackson_domain_8145`.
- Latest verified public frontend asset:
  - `/assets/index-DGOMmalo.js`
- Latest public API smoke verified:
  - `GET /health`
  - `GET /`
  - `GET /assets/index-DGOMmalo.js`
  - `POST /api/users/register`
  - `POST /api/users/login`
  - `GET /api/users/me`
  - `PATCH /api/users/me`
  - `GET /api/agents`
  - `GET /api/idle/conversation`
  - `POST /api/idle/{conversationId}/tick`
  - `POST /api/idle/{conversationId}/messages`
  - `POST /api/idle/{conversationId}/join`
  - `POST /api/companion/{conversationId}/messages`
  - `POST /api/tasks`
  - `GET /api/tasks`
  - `POST /api/tasks/{taskId}/messages`
  - `POST /api/work/projects`
  - `GET /api/work/projects`
  - `POST /api/work/missions`
  - `GET /api/work/projects/{projectId}/missions`
  - `GET /api/work/missions/{missionId}`
  - `POST /api/work/missions/{missionId}/start`
  - `GET /api/work/missions/{missionId}/events`
- Latest public UI E2E verified on `https://hackson.catachess.com/`:
  - Register/Login succeeded.
  - The two Agent profiles were saved and used as Work Mission leads.
  - Workspace showed Projects and New Project only.
  - Project detail showed Agents and Missions without Employee or Team setup.
  - Mission creation, Start, polling, and completion timeline succeeded.
  - Desktop and mobile screenshots passed with `0` failed API responses.
- Model-backed Idle/Companion smoke can return upstream `429` during provider throttling; the public API now exposes this as `{"detail":"model_rate_limited"}` instead of an unhandled `500`.
- Latest public screenshots:
  - `/tmp/hackson_public_work_agents_desktop.png`
  - `/tmp/hackson_public_work_done_desktop.png`
  - `/tmp/hackson_public_work_mobile.png`
- Legacy production port `8130` remains live as `hackson-production.service` until explicitly retired.
- Old Hackson smoke uvicorn ports were stopped after public-domain promotion: `8101`, `8122-8126`, `8131-8133`, `8141-8144`, `8146`, `8147`.
- Non-Hackson target services were not touched.

## resolved production issue
- The first production UI E2E showed the Idle composer entering `Working` without sending `/api/idle/{conversationId}/join`.
- Root cause: frontend optimistic IDs used `crypto.randomUUID()`, which is not reliable on the target-machine HTTP production origin.
- Fix: `frontend/src/domain/messages.js` now uses `makeClientId()` with a safe fallback, and Work pending messages reuse the same helper.
