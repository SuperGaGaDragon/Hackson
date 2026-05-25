## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - React + Vite frontend for the Hackson product prototype.
- 架构思路
  - Build the V1 product shell around Idle, Chat, Agents, and future Work surfaces.
  - Keep the frontend model-driven and local-first until backend conversation APIs are ready.
  - Follow `docs/frontend/design.md` for the calm observatory interface direction.
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
- Connect Idle, Chat, and Agents screens to verified backend APIs as they are implemented.
- Add browser screenshot QA loop once Playwright or the in-app browser flow is available.
