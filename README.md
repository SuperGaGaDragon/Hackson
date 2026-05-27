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
| Hackson public domain URL | `https://hackson.catachess.com/`, verified and running |
| Hackson public domain service | `hackson-domain-8145.service`, user-level systemd, enabled |
| Hackson public tunnel service | `hackson-cloudflared.service`, user-level systemd, enabled |
| Hackson public domain path | `~/hackson_domain_8145` |
| Hackson public domain backend bind | `127.0.0.1:8145` |
| Hackson public domain cloudflared config | `~/.cloudflared/hackson.yml` |
| Hackson public domain frontend assets | served by FastAPI from `~/hackson_domain_8145/frontend/dist` |
| Idle Auto smoke service | `hackson-idle-auto-8147.service`, user-level systemd, active for current verification |
| Idle Auto smoke backend bind | `127.0.0.1:8147` |
| Idle Auto local frontend check | `127.0.0.1:5187 -> 18147 -> 8147` |
| Legacy production URL | `http://100.70.248.39:8130/`, retained and running until explicitly retired |
| Legacy production service | `hackson-production.service`, user-level systemd, enabled |
| Legacy production path | `~/hackson_production` |
| Legacy production backend bind | `0.0.0.0:8130` |
| Default frontend local dev port | `127.0.0.1:5173` |
| Hackson public domain MongoDB database | `hackson_domain_8145` |
| Idle Auto smoke MongoDB database | `hackson_idle_auto_8147` |
| Legacy production MongoDB database | `hackson` |
| Stopped old Hackson smoke ports | `8101`, `8122-8126`, `8131-8133`, `8141-8144`, `8146` |

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
