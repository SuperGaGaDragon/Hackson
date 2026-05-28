## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store Desktop Pet API client modules for verified Hackson APIs.
- 架构思路
  - Use a Tauri native command for HTTP to avoid desktop WebView CORS issues.
  - Resolve the active Hackson source in one shared client so auth and Work Mode watch the same environment.
  - Keep token handling local to the desktop app.
  - Do not add speculative API paths before they are verified in root `api.md`.

## folder structure
|-README.md desktop API folder guide
|-client.js shared native HTTP wrapper and token helpers
|-users.js login and current-user APIs
|-work.js Work Mode Project, Mission, detail, and event APIs

## 代办
- Replace localStorage token storage with OS secure storage before public distribution.
