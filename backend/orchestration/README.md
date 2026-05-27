## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Own Hackson product-level orchestration policy for model calls.
- 架构思路
  - `interactions/` owns product flow and message persistence.
  - `context/` owns what the model sees.
  - `orchestration/` owns mode policy, reasoning effort, output budget, and model-call metadata.
  - `model_runtime/` owns provider wire calls and fallback behavior.
  - V1 uses this module for `idle`, `companion_1`, and `companion_2` while keeping responses synchronous.

## folder structure
|-README.md orchestration module guide
|-__init__.py Python package marker
|-schemas.py orchestration request, response, and policy schemas
|-policies.py deterministic V1 mode policy selection
|-service.py Hackson Orchestrator service
|-tests/ orchestration unit tests

## 代办
- Add streaming event policy after V1 quality upgrade is verified.
