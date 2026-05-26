## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-26
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - React + Vite frontend for Hackson verified backend flows.
- 架构思路
  - Build only the surfaces backed by verified APIs in root `api.md`.
  - Current product surfaces are Auth, Idle, Chat, Work, and Me.
  - Local dev calls `/api` through the Vite proxy to avoid browser CORS.
  - Current verified local proxy target is `127.0.0.1:18125`, which tunnels to target backend `127.0.0.1:8125`.
  - `src/api/` owns HTTP calls.
  - `src/domain/` owns fixed MVP Agent slot and message mapping.
  - `src/features/` owns product flows.
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

## 代办
- Add Agent editing only after verified Agent APIs exist.
- Add tool trace views only after verified Work trace read APIs exist.
- Replace the temporary `18125 -> 8125` dev proxy after a stable backend process is finalized.
