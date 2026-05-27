## header
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-26
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store Work Mode Mission Runtime backend tests.
- 架构思路
  - Use in-memory fakes for service and worker unit tests.
  - Use FastAPI dependency overrides for route tests.
  - MongoDB target-machine smoke belongs in `api.md` only after verification.

## folder structure
|-README.md work_mode tests guide
|-test_work_mode_service.py WorkModeService and V0 worker unit tests
|-test_work_mode_routes.py `/api/work` route tests

## 代办
- Add MongoDB repository integration tests after V0 target smoke is stable.
