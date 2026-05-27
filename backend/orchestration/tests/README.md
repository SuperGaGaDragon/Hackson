## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store unit tests for Hackson orchestration policy and service behavior.
- 架构思路
  - Tests use fake model runtime objects and do not make network calls.
  - Policy tests verify deterministic mode settings.
  - Service tests verify conversion from context package to model runtime request.

## folder structure
|-README.md orchestration tests guide
|-test_orchestration_policy.py deterministic policy tests
|-test_orchestration_service.py orchestrator service tests with fake runtime

## 代办
- Add streaming event tests when V1.1 begins.
