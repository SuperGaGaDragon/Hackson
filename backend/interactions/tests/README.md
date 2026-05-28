## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Tests for interaction orchestration and HTTP routes without real model calls.
- 架构思路
  - Use fake conversation repository and fake model runtime.
  - Verify that user messages are saved, idle turn locks prevent duplicates, context is built, context package ids are linked, Agent replies are saved, and FastAPI routes expose the behavior.

## folder structure
|-README.md tests folder guide
|-test_interaction_service.py interaction service unit tests
|-test_interaction_routes.py FastAPI interaction route tests
|-test_idle_turn_lock.py idle turn lock and idempotency tests

## 代办
- Add streaming route tests after streaming support is introduced.
