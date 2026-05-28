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
|-work_mode_v1_browser_smoke.mjs Playwright smoke for Work Mode V1 UI contract

## 代办
- Add mobile viewport smoke after the desktop V1 release gate is stable.
