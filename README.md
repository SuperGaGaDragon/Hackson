## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Lst Modified by: Codex

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
| Backend venv | `~/hackson_backend_test/backend/.venv` |
| Backend env file | `~/hackson_backend_test/backend/.env` |
| Raw API verification port | `127.0.0.1:8100`, verified, not kept running |
| Interaction/model verification port | `127.0.0.1:8101`, verified, not kept running |
| Frontend local dev port | `127.0.0.1:5173` |
| Production MongoDB database | `hackson` |
| Smoke MongoDB databases | `hackson_test`, `hackson_target_smoke` |

## must-read documents
| Path | Purpose |
| --- | --- |
| `agents/restrictions` | Repository operating rules |
| `agents/frontend_restrictions.md` | Frontend implementation rules |
| `api.md` | Verified API, port map, request/response shapes |
| `docs/backend-architecture.md` | Backend module boundaries |
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
