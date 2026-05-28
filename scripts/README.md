## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store local engineering scripts for repeatable smoke checks and operational verification.
- 架构思路
  - Scripts should be deterministic by default and avoid external services unless the filename or CLI flags clearly mark them as live checks.
  - Product acceptance scripts assert observable public behavior instead of private implementation details.

## folder structure
|-README.md scripts folder guide
|-work_mode_v1_full_smoke.py deterministic Work Mode V1 full acceptance smoke
|-work_mode_v1_http_smoke.py deterministic Work Mode V1 authenticated HTTP smoke
|-work_mode_v1_run_browser_smoke.py local browser smoke orchestrator
|-work_mode_v1_smoke_helpers.py shared deterministic smoke model clients and assertions
|-work_mode_v1_smoke_server.py isolated FastAPI app for browser smoke
|-artifacts/ generated smoke artifacts folder

## 代办
- Add target-machine smoke wrappers only when they can run without stopping existing services.
