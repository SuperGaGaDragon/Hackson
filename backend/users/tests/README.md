## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Tests for the users module.
- 架构思路
  - Prefer service-level tests with fake repositories for business rules.
  - Add API integration tests once the test database lifecycle is finalized.

## folder structure
|-README.md tests folder guide
|-test_user_service.py service-level user tests

## 代办
- Add MongoDB integration tests against a disposable database.
- Add FastAPI route tests with dependency overrides.
