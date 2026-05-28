## header
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store Work Mode Mission Runtime backend tests.
- 架构思路
  - Use in-memory fakes for service and worker unit tests.
  - Use FastAPI dependency overrides for route tests.
  - V0.5 tests must prove Mission start persists artifacts through public Mission detail, not only internal repositories.
  - V1.0 tests must start at the public tool protocol boundary before adding Product, Window, context, or loop behavior.
  - V1.2 stream tests cover SSE formatting over the persisted event log and must not depend on raw model-token streaming.
  - MongoDB target-machine smoke belongs in `api.md` only after verification.

## folder structure
|-README.md work_mode tests guide
|-test_work_mode_service.py WorkModeService and V0 worker unit tests
|-test_work_mode_routes.py `/api/work` route tests
|-test_work_mode_tool_protocol.py V1.0 tool action parser and validator tests
|-test_work_mode_context.py V1.0 Lead and Delegate Agent context builder tests
|-test_work_mode_action_client.py V1.0 JSON Action model adapter tests
|-test_work_mode_tool_executor.py V1.0 visible tool execution behavior tests
|-test_work_mode_loop.py V1.0 Mission loop tests
|-test_work_mode_search.py V1.0.5 Web Search provider normalization tests
|-test_work_mode_evaluator.py Evaluator Runtime report tests over Work Mode trace and evidence

## 代办
- Add MongoDB repository integration tests after V0 target smoke is stable.
