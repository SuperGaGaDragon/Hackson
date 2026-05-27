## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex

## brief intro
- goal for this folder.
  - Root of the Hackson repository.
- 架构思路
  - Product and research documents live under `docs/`.
  - Backend code lives under `backend/` and is split by domain module.
  - Frontend code lives under `frontend/`.
  - Agent operating rules live under `agents/`.
  - Verified API and port information lives in `api.md`.

## target machine quick reference
| Item | Value |
| --- | --- |
| Target machine | `catadragon@100.70.248.39` |
| Secret connection note | See ignored local file `docs/数据库/machine.md`; never push it |
| Backend test path | `~/hackson_backend_test/backend` |
| Backend test venv | `~/hackson_backend_test/.venv` |
| Backend env file | `~/hackson_backend_test/backend/.env` |
| Production app URL | `http://100.70.248.39:8130/`, verified and running |
| Production service | `hackson-production.service`, user-level systemd, enabled |
| Production path | `~/hackson_production` |
| Production backend bind | `0.0.0.0:8130` |
| Production frontend assets | served by FastAPI from `~/hackson_production/frontend/dist` |
| Current product smoke backend path | `~/hackson_backend_current_8125/backend` |
| Current product smoke venv | `~/hackson_backend_review_smoke/backend/.venv` |
| Raw API verification port | `127.0.0.1:8100`, verified, not kept running |
| Interaction/model verification port | `127.0.0.1:8101`, verified, not kept running |
| Latest target smoke backend | `127.0.0.1:8125`, verified and running |
| Latest local backend tunnel | `127.0.0.1:18125 -> 127.0.0.1:8125`, verified but not kept running |
| Latest verified frontend dev port | `127.0.0.1:5177`, verified but not kept running |
| Product database smoke backend | `127.0.0.1:8126`, verified and running |
| Product database local tunnel | `127.0.0.1:18126 -> 127.0.0.1:8126`, verified and running |
| Product database frontend dev port | `127.0.0.1:5178`, verified and running |
| Work Mode V0 stable backend | `127.0.0.1:8142`, verified and running on target machine |
| Work Mode V0 stable local frontend check | `127.0.0.1:5182 -> 18142 -> 8142`, verified but not kept running |
| Work Mode V0.1 Employee backend | `127.0.0.1:8143`, verified and running on target machine |
| Work Mode V0.1 Employee local frontend check | `127.0.0.1:5184 -> 18143 -> 8143`, verified but not kept running |
| Local context-fix backend | `127.0.0.1:8130`, verified and running with in-memory `mongomock` |
| Local context-fix frontend dev port | `127.0.0.1:5179`, verified and running |
| Default frontend local dev port | `127.0.0.1:5173` |
| Production MongoDB database | `hackson` |
| Latest smoke MongoDB database | `hackson_current_8125` |
| Work Mode V0 stable MongoDB database | `hackson_work_mode_v0_stable` |
| Work Mode V0.1 Employee MongoDB database | `hackson_work_mode_v01_employees` |
| Older smoke MongoDB databases | `hackson_test`, `hackson_target_smoke`, `hackson_review_smoke_latest` |

## must-read documents
| Path | Purpose |
| --- | --- |
| `agents/restrictions` | Repository operating rules |
| `agents/frontend_restrictions.md` | Frontend implementation rules |
| `api.md` | Verified API, port map, request/response shapes |
| `docs/backend-architecture.md` | Backend module boundaries |
| `docs/deployment/production.md` | Production deployment topology and verification record |
| `docs/上下文/plan.md` | Context system product plan |
| `docs/数据库/machine.md` | Target machine access note; ignored locally |

## folder structure
|-README.md root repository guide
|-api.md verified API and port map
|-agents/ agent operating restrictions
|-backend/ FastAPI backend
|-docs/ product, context, and database documents
|-frontend/ React + Vite frontend
|-skills-lock.json skill lock metadata

## 代办
- Keep `api.md` updated only with APIs that were actually verified.
- Keep this root README synchronized when verified ports change.
