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
  - Agent operating rules live under `agents/`.
  - Verified API and port information lives in `api.md`.

## folder structure
|-README.md root repository guide
|-api.md verified API and port map
|-agents/ agent operating restrictions
|-backend/ FastAPI backend
|-docs/ product, context, and database documents
|-skills-lock.json skill lock metadata

## 代办
- Add frontend folder when React + Vite work starts.
- Keep `api.md` updated only with APIs that were actually verified.
