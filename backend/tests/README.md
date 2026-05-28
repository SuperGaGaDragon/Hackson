## header
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex

## brief intro
- goal for this folder.
  - Store cross-module backend tests for application-level wiring.
- 架构思路
  - Module-specific tests stay inside each module.
  - Tests here cover `main.py` behavior that spans HTTP routing, static frontend hosting, and app composition.

## folder structure
|-README.md backend app test folder guide
|-test_main_static_frontend.py verifies production static frontend mounting and startup worker wiring

## 代办
- Add app-level health and startup smoke tests if deployment behavior grows beyond static hosting and static `HEAD` checks.
