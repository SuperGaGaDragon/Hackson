## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

# Work Mode V1.0 Implementation Plan

## 1. Purpose

This document is the engineer-facing build order for V1.0 Pure API Text Mission Loop.

Follow this plan after reading `final_version.md`, `architecture.md`, `tool_protocol.md`, `state_machine.md`, `context_design.md`, and `ui_contract.md`.

## 2. Preflight

Before implementation:

```bash
git status --short
find docs/work_mode -maxdepth 2 -type f | sort
```

Rules:

- Do not edit files under `docs/work_mode/legacy/` except for legacy notices.
- Do not change target-machine services until local tests pass.
- Do not update `api.md` until verified behavior exists.
- Do not implement file/shell/Codex CLI computer tools in V1.0.

## 3. Loop 1: Tool Protocol Models

Implement backend-only schemas.

Likely files:

- `backend/work_mode/tool_protocol.py`
- `backend/work_mode/tests/test_work_mode_tool_protocol.py`
- `backend/work_mode/README.md`
- `backend/work_mode/tests/README.md`

Required tests:

- Valid `mission_plan`.
- Valid `work_product`.
- Valid `inspect_product`.
- Valid `delegate_agent`.
- Valid `ask_user`.
- Valid `finish_mission`.
- Valid `block_mission`.
- Plain text rejected.
- Unknown tool rejected.
- Multiple tools rejected.
- Missing fields rejected.

Exit criteria:

- Tool validation is deterministic.
- No model/network calls.

## 4. Loop 2: Product And Work Window Persistence

Add Product and Work Window concepts.

Implementation can use dedicated collections or existing artifact metadata, but public service methods MUST expose Product and Window concepts.

Required service behavior:

- Create Product.
- Append immutable Artifact.
- Link Artifact to Product.
- Create Work Window.
- Mark Work Window completed/blocked/failed.
- List Product manifest.
- List Work Window manifest.

Required tests:

- Artifacts are immutable.
- Final Product can be referenced.
- Invalid Product id is rejected.
- Window belongs to current Mission.
- Ownership checks pass.

Exit criteria:

- Mission detail can return Products, Artifacts, and Windows.

## 5. Loop 3: Context Builder

Add Lead and Delegate context builders.

Likely files:

- `backend/work_mode/context.py`
- tests in `backend/work_mode/tests/`

Required behavior:

- Lead context includes Mission goal, tool schemas, product manifest, window manifest, recent events, last observation, and budgets.
- Lead context includes only bounded recent Artifact content.
- Delegate context includes brief, Agent profile, expected output, scoped source content, and structured result instruction.

Required tests:

- Product manifest included.
- Old Artifacts summarized or omitted when over budget.
- Recent N Artifact full content included within budget.
- Delegate context excludes tool list.

Exit criteria:

- Context can be built without network/model calls.

## 6. Loop 4: JSON Action Model Client

Add a provider-agnostic model action adapter around `model_runtime`.

Required behavior:

- Calls model runtime.
- Parses one JSON Action.
- Rejects plain assistant text.
- Returns parse/validation errors for retry.

Required tests:

- Valid JSON action parses.
- Surrounding prose fails.
- Invalid JSON fails.
- Multiple actions fail.
- Model runtime errors map to retryable or fatal categories.

Exit criteria:

- The action client can be tested with fake model responses.

## 7. Loop 5: Tool Executor

Implement V1.0 tools.

Required behavior:

- `mission_plan` writes plan event.
- `work_product` creates Product/Artifact and writes Product event.
- `inspect_product` returns bounded content and writes inspect event.
- `delegate_agent` creates Window, calls delegate model once, persists delegate Artifact, completes Window, writes events.
- `ask_user` sets `waiting_input`.
- `finish_mission` validates final Product and completes Mission.
- `block_mission` blocks Mission.

Required tests:

- Every valid tool persists an event.
- `delegate_agent` only targets non-lead Agent.
- `delegate_agent` cannot run concurrently.
- `finish_mission` requires existing Product id.
- `inspect_product` cannot inspect another Mission's Artifact.

Exit criteria:

- Tool execution works with fake model clients.

## 8. Loop 6: Mission Loop Runner

Replace V0.5 single-call worker with the V1.0 loop behind the existing start route.

Required behavior:

- One tool call per Lead turn.
- Retry invalid turns up to limit.
- Pause transient provider failures as `paused_retryable`.
- Stop when user requests stop.
- Stop on `finish_mission`, `block_mission`, budget exhaustion, failed retries, or provider fatal error.

Required tests:

- Lead plans, delegates, writes Product, finishes.
- Invalid turn retries then fails.
- Provider timeout becomes `paused_retryable`.
- User stop becomes `stopped`.
- Full loop does not hard-code tool order.

Exit criteria:

- In-memory service test proves a model-selected action sequence completes.

## 9. Loop 7: API And UI Response Shape

Extend Mission detail response.

Response should include:

- Mission.
- Active/latest Run.
- Events.
- Products.
- Artifacts.
- Work Windows.

Required tests:

- Existing route compatibility for Projects/Missions.
- Mission detail includes Products and Windows.
- Event polling still works.

Exit criteria:

- Backend API is stable before frontend work.

## 10. Loop 8: Frontend V1.0 UI

Implement UI contract.

Required surfaces:

- Mission Timeline.
- Work Windows.
- Product Panel.
- Control Panel.

Required tests/build:

```bash
npm --prefix frontend run build
```

Browser checks:

- Timeline and windows render.
- Large content collapsed by default.
- Product Panel shows final Product.
- Resume/answer controls appear for matching statuses.

Exit criteria:

- Browser screenshot proves the process is visible.

## 11. Loop 9: Local Full Smoke

Full smoke MUST create an 8000 CJK character novel Mission.

Required assertions:

- Mission completed.
- `mission_plan` used.
- `delegate_agent` used at least twice.
- At least one Product.
- At least three Artifacts.
- Final Product referenced by `finish_mission`.
- Final Artifact CJK count >= 8000.
- Final Artifact is not only an outline.

Exit criteria:

- Local backend and frontend pass.

## 12. Loop 10: Target-Machine Verification

Rules:

- Do not stop existing services unless explicitly approved.
- Use a new smoke port and database first.
- After smoke passes, promote only with user approval.
- Update `api.md` only after verified behavior.

Target smoke must run the same full 8000 CJK character acceptance.

Exit criteria:

- Target full smoke passes.
- Browser smoke passes.
- `api.md` records only verified endpoints and port facts.

## 13. Loop 11: Product-Ready Hardening

V1.0 is not product-ready until the release gate is verified through public HTTP and the fixed React UI, not only in-process fake clients.

Required hardening:

- `finish_mission` completion events MUST include final Product and Artifact ids.
- `finish_mission` MUST reject final Artifact ids that do not exist or do not belong to the current Mission.
- The full 8000 CJK smoke MUST be runnable against a live HTTP server with authenticated API calls.
- Browser smoke MUST prove Timeline, Work Windows, Product Panel, and terminal status are visible.
- Browser smoke MUST verify delegate windows are collapsed by default and expandable.

Exit criteria:

- Backend unit tests cover final Product and Artifact lineage.
- HTTP full smoke passes locally.
- Browser UI smoke passes locally.
- Target-machine HTTP and browser smoke pass on a new port before any promotion.

## 14. Recommended Test Commands

Backend scoped:

```bash
PYTHONPATH=backend python -m unittest discover -s backend/work_mode/tests
PYTHONPATH=backend python -m unittest discover -s backend/model_runtime/tests
```

Backend all directories:

```bash
for d in $(find backend -path '*/tests' -type d | sort); do
  PYTHONPATH=backend python -m unittest discover -s "$d"
done
```

Frontend:

```bash
npm --prefix frontend run build
```

## 14. Rollback

Rollback should preserve:

- Existing Project/Mission data.
- Existing Events.
- Existing Artifacts.

If V1.0 loop is unstable:

- Keep new documents.
- Feature-flag the V1.0 runner.
- Fall back to V0.5 single-call worker only as emergency compatibility.
- Do not delete Products, Windows, or Artifacts created during testing.

## 15. 代办

- Add concrete issue tracker tickets after this document is accepted.
