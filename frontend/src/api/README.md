## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store HTTP client modules for APIs verified in root `api.md`.
- 架构思路
  - `client.js` owns base URL, auth headers, JSON parsing, and API errors.
  - Local dev uses same-origin `/api` paths and Vite proxy to avoid CORS.
  - Feature-specific files expose small functions grouped by backend module.
  - Components should call feature hooks, not raw API paths.
  - Idle `Say` must use the interaction API because it records the user interjection and the immediate Agent reply as one product turn.

## folder structure
|-README.md API folder guide
|-client.js shared fetch wrapper and token helpers
|-agents.js backend-owned Agent display profile APIs
|-users.js user auth and settings APIs
|-conversations.js conversation creation and message history APIs
|-interactions.js idle and companion product interaction APIs
|-tasks.js Work Mode task APIs

## 代办
- Add refresh-token support only if the backend implements it.
