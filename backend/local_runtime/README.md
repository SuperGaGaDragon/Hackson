## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Local-only runners for testing backend modules without FastAPI routes.
- 架构思路
  - Keep smoke scripts outside product modules.
  - Scripts may compose `context/` and `model_runtime/` for local verification.
  - Scripts must not introduce user-facing API contracts.

## folder structure
|-README.md local runtime folder guide
|-__init__.py Python package marker
|-run_context_model_smoke.py local context + model runtime smoke runner
|-run_idle_context_model_smoke.py local idle context + model runtime smoke runner without MongoDB
|-run_idle_full_smoke.py local idle repository + context + model smoke runner
|-run_companion1_full_smoke.py local companion_1 repository + transition context + model smoke runner
|-run_companion2_full_smoke.py local companion_2 repository + context + model smoke runner

## 代办
- Add cleanup helpers for target-machine smoke databases if repeated runs become noisy.
