## header
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-26
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

## verification checklist
- `GET /health` returns `200`.
- `GET /` returns the React frontend HTML from `frontend/dist`.
- `GET /assets/*` returns built frontend assets.
- `POST /api/users/register` writes into MongoDB database `hackson`.
- `GET /api/users/me` works with the returned JWT.
- `GET /api/agents` returns the two fixed V1 Agent display profiles.
- `GET /api/idle/conversation` creates or returns an idle conversation.
- `POST /api/idle/{conversationId}/join` returns a `companion_1` conversation and Agent response.
- `POST /api/companion/{conversationId}/messages` continues the companion conversation.
- `POST /api/tasks` creates a Work Mode task.
- `POST /api/tasks/{taskId}/messages` returns a Work Mode Agent response.

## current status
- Production port `8130` is live and verified.
- `hackson-production.service` is enabled and active under user-level `systemd`.
- Production serves FastAPI APIs and React `frontend/dist` from the same origin: `http://100.70.248.39:8130/`.
- Latest verified frontend assets:
  - `/assets/index-CSg3RgOA.js`
  - `/assets/index-DOSivJMg.css`
- Latest production API smoke verified:
  - `GET /health`
  - `GET /`
  - `GET /assets/index-CSg3RgOA.js`
  - `POST /api/users/register`
  - `GET /api/users/me`
  - `GET /api/agents`
  - `GET /api/idle/conversation`
  - `POST /api/idle/{conversationId}/join`
  - `POST /api/companion/{conversationId}/messages`
  - `POST /api/tasks`
  - `POST /api/tasks/{taskId}/messages`
- Latest production UI E2E verified on `http://100.70.248.39:8130/`:
  - Register succeeded.
  - Idle join returned `201`.
  - Companion follow-up returned `201`.
  - Work task creation returned `201`.
  - Work message returned `201`.
  - No browser console errors.
  - No failed browser requests.
- Production database verification:
  - MongoDB database `hackson` contains the production smoke users, conversations, messages, and tasks.
  - `messages` indexes include `conversation_id_1_sequence_1`, `conversation_id_1_created_at_-1`, `user_id_1_created_at_-1`, and `user_id_1_sender_slot_1_created_at_-1`.
  - `tasks` indexes include `user_id_1_status_1_updated_at_-1` and `conversation_id_1`.

## resolved production issue
- The first production UI E2E showed the Idle composer entering `Working` without sending `/api/idle/{conversationId}/join`.
- Root cause: frontend optimistic IDs used `crypto.randomUUID()`, which is not reliable on the target-machine HTTP production origin.
- Fix: `frontend/src/domain/messages.js` now uses `makeClientId()` with a safe fallback, and Work pending messages reuse the same helper.
