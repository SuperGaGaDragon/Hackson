## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store local engineering scripts for repeatable smoke checks and operational verification.
- 架构思路
  - Scripts should be deterministic by default and avoid external services unless the filename or CLI flags clearly mark them as live checks.
  - Product acceptance scripts assert observable public behavior instead of private implementation details.
  - Target-machine smoke scripts must use isolated ports and must not stop existing services.

## folder structure
|-README.md scripts folder guide
|-work_mode_v1_full_smoke.py deterministic Work Mode V1 full acceptance smoke
|-work_mode_v1_http_smoke.py deterministic Work Mode V1 authenticated HTTP smoke with AgentLens evaluation check
|-work_mode_agentlens_public_smoke.py public-domain AgentLens evaluator smoke with seeded trace and live `/evaluate`
|-work_mode_v1_search_smoke.py deterministic Work Mode V1 Web Search tool smoke
|-work_mode_waiting_input_http_smoke.py deterministic Work Mode waiting_input answer/resume smoke
|-work_mode_v1_run_browser_smoke.py local browser smoke orchestrator
|-work_mode_v1_smoke_helpers.py shared deterministic smoke model clients and assertions
|-work_mode_v1_smoke_server.py isolated FastAPI app for browser smoke
|-context_runtime_fake_model.py deterministic OpenAI-compatible fake model relay for Context Runtime smoke
|-context_runtime_http_smoke.py authenticated HTTP and MongoDB smoke for Context Runtime V1.0-V1.6; verifies prompt-log contracts and supports optional fake-model first-content assertion
|-context_runtime_eval.py deterministic context-package eval gate for mode, speaker, topic, transition, convergence, account memory, and latency metadata
|-context_runtime_smoke_server.py in-memory API server for local browser smoke of Idle interruption behavior
|-artifacts/ generated smoke artifacts folder

## 代办
- Add target-machine smoke wrappers only when they can run without stopping existing services.
