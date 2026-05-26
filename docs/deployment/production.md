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
2. On the target machine, create or update `~/hackson_production` from `origin/startup`.
3. Build backend virtualenv under `~/hackson_production/backend/.venv`.
4. Run backend unit tests on the target machine before starting production.
5. Build frontend with `npm ci` and `npm run build`.
6. Write target-only backend `.env`.
7. Install or update `~/.config/systemd/user/hackson-production.service`.
8. Run `systemctl --user daemon-reload`, enable, restart, and verify the service.

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
- Planned production port: `8130`.
- Verification is pending until the production service is started and smoke-tested.
