## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex

## brief intro
- goal for this folder.
  - Own platform-managed model configuration and model-call orchestration.
- 架构思路
  - `model_runtime/` answers how the backend calls the model.
  - It should not know idle, companion, diary, or relationship business rules.
  - V1 model endpoints are configured by the platform, not by users.

## responsibilities
- Read enabled platform model runtime config.
- Call the configured model endpoint.
- Handle timeout, retry, and concurrency limits.
- Normalize model responses for callers.
- Support streaming later if the frontend needs it.

## not responsible for
- User-owned model settings.
- API key storage in user data.
- Prompt recipe construction.
- Conversation persistence.
- Memory or summary generation.

## planned files
|-README.md module guide
|-__init__.py Python package marker
|-client.py low-level provider HTTP or SDK calls
|-orchestrator.py timeout, retry, streaming, and concurrency orchestration
|-config_repository.py model_runtime_configs persistence
|-schemas.py model request and response schemas
|-tests/ model runtime tests

## model config rule
- Users do not configure endpoint, provider, API key, Claude/OpenAI key, or local model path in V1.
- Platform API keys should live in secret refs or environment variables.
- `model_runtime_configs` may store `api_key_secret_ref`, never raw user-facing secrets.

## version plan
- v1.0: Basic generate call through one platform-managed endpoint.
- v1.1: Support companion_1 calls through the same interface.
- v1.2: Add token budget awareness and better timeout handling.
- v1.5: Support work-mode tool-call-oriented prompts if needed.
