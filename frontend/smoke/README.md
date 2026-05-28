## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store frontend browser smoke scripts that need frontend npm dependencies.
- 架构思路
  - Scripts run from the frontend package root so dependencies resolve through `node_modules`.
  - Product code remains under `src/`; smoke code stays outside the React bundle.

## folder structure
|-README.md smoke folder guide
|-work_mode_v1_browser_smoke.mjs Playwright smoke for Work Mode V1 UI contract and Reliability panel
|-work_mode_agentlens_public_ui_smoke.mjs Playwright smoke for public AgentLens Reliability panel
|-work_mode_product_reader_public_ui_smoke.mjs Playwright smoke for production-bundle Product reader layout using API mocks
|-work_command_rail_public_smoke.mjs Playwright smoke for public Work command rail, Mission Composer, and Progress filters
|-context_runtime_me_smoke.mjs Playwright smoke for Me IA, Agent editor priority, collapsed Debug, prompt-log access, and memory controls
|-idle_interruption_smoke.mjs Playwright smoke for typing during Idle Working state; `HACKSON_SMOKE_TIMEOUT_MS` covers slower public model turns

## 代办
- Add mobile viewport smoke after the desktop V1 release gate is stable.
