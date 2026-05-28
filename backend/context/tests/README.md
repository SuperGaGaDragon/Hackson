## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Tests for context construction, recipes, transition context, and auditable context packages.
- 架构思路
  - Test context behavior without databases or model providers.
  - Keep context deterministic so prompt package changes are easy to review.
  - Verify package persistence through service-level fake repositories before route smoke.

## folder structure
|-README.md tests folder guide
|-test_context_builder.py context builder behavior tests
|-test_context_package_service.py context package persistence, retention, list, and delete tests

## 代办
- Add database-backed integration tests once the Mongo test lifecycle is finalized.
