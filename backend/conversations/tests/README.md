## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Tests for the conversations module.
- 架构思路
  - Prefer service-level tests with fake repositories for conversation business rules.
  - Add MongoDB integration tests after database lifecycle helpers are formalized.

## folder structure
|-README.md tests folder guide
|-test_conversation_service.py service-level conversation tests

## 代办
- Add FastAPI route tests with auth dependency overrides.
- Add MongoDB integration tests for indexes and sequence counters.
