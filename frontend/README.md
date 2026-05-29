## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

## brief intro
- goal for this folder.
  - React + Vite frontend for Parallex verified backend flows.
- 架构思路
  - Build only the surfaces backed by verified APIs in root `api.md`.
  - Current product surfaces are Auth, Idle, Chat, Work, and Me.
  - Local dev calls `/api` through the Vite proxy to avoid browser CORS.
  - Production serves the built `dist/` bundle from FastAPI at `http://100.70.248.39:8130/`.
  - Current product-level local proxy target is `127.0.0.1:18126`, which tunnels to target backend `127.0.0.1:8126` using MongoDB database `hackson`.
  - Current verified local product dev port is `127.0.0.1:5178`.
  - `src/api/` owns HTTP calls.
  - `src/domain/` owns fixed MVP Agent slot and message mapping.
  - `src/features/` owns product flows.
  - Public browser title and visible brand labels say Parallex; legacy Hackson names may remain in backend deployment details until a separate migration.
  - Follow `docs/frontend/intro.md` for the current integration blueprint.
  - Do not expose model endpoint, provider, API key, or local model path settings in user UI.

## folder structure
|-README.md frontend folder guide
|-package.json npm scripts and frontend dependencies
|-package-lock.json locked npm dependency graph
|-index.html Vite HTML entry
|-vite.config.js Vite React configuration
|-src/ React source folder
|-public/ static public assets folder
|-smoke/ frontend browser smoke scripts

## 代办
- Add Agent editing only after verified Agent APIs exist.
- Add tool trace views only after verified Work trace read APIs exist.
- Keep the default dev proxy pointed at the production-database smoke backend, not review smoke databases.
