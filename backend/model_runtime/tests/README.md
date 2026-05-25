## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Tests for platform-managed model runtime configuration, request shaping, and response normalization.
- 架构思路
  - Test model runtime without making network calls.
  - Keep provider-specific request formatting behind the client interface.

## folder structure
|-README.md tests folder guide
|-test_model_runtime.py model runtime unit tests

## 代办
- Add live relay smoke tests only after a safe local environment is configured.
