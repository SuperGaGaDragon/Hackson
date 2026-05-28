## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
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

- Current Activity.
- Work Windows.
- Product Panel.
- Mission Progress.
- Diagnostics.
- Control Panel.

Required tests/build:

```bash
npm --prefix frontend run build
```

Browser checks:

- Current Activity renders.
- Work Windows render above Mission Progress.
- Product Panel renders before Mission Progress.
- Product Panel exposes readable Artifact lineage and does not hide earlier partial Artifacts after Done.
- Product Panel can switch between all Artifacts and one selected Artifact.
- Product Panel uses a fixed-rhythm Artifact Navigator instead of a wrapping title-card grid.
- Mission Progress renders clock time and compact sequence metadata.
- Diagnostics renders collapsed raw event detail.
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

## 14. Loop 12: V1.0.1 Progress Details And Create Modal

Implement the lowest-risk quality-track UI improvements first.

Required behavior:

- Progress rows expand inline with bounded structured details.
- Only one Progress row is expanded at a time unless a later UX decision changes this.
- Product event details link to Product Panel for full content.
- Plan event details show steps.
- Selected Project rail no longer shows permanent Mission title/goal creation fields.
- `New Mission` opens a modal or drawer and closes after successful creation.

Required tests/build:

```bash
npm --prefix frontend run build
```

Browser checks:

- Expand a plan row and see plan steps.
- Expand a Product row and see Product/Artifact metadata plus bounded excerpt.
- Confirm full long-form content remains in Product Panel.
- Confirm completed Mission rail does not show permanent create inputs.
- Create a Mission through `New Mission`.

Exit criteria:

- UI is quieter during completed Mission reading.
- Progress is still useful as an audit trail with accessible detail.

## 15. Loop 13: V1.0.2 Deterministic Product Checks

Add product-quality checks before model review tools.

Required checks:

- Final Artifact CJK character count meets the configured full-smoke minimum.
- Final Product ids exist and belong to the Mission.
- Final Artifact ids exist and belong to the Mission.
- At least one outline Artifact exists for long-form writing smoke.
- At least one chapter/draft Artifact exists.
- Final Artifact is not outline-only.
- Product API exposes lineage needed by the UI.

Required tests:

- Passing full smoke Product passes all checks.
- Too-short final Artifact fails.
- Missing final Product reference fails.
- Missing final Artifact reference fails.
- Outline-only final fails.
- Product lineage response includes all relevant Artifacts.

Exit criteria:

- Full smoke has deterministic failure reasons before any model-visible review tool is added.

## 16. Loop 14: V1.0.3 Review And Discussion Tools

Add model-visible quality workflow tools after deterministic checks are stable.

Required backend behavior:

- `review_product` validates Product/Artifact refs.
- `review_product` persists a Review Artifact.
- `review_product` emits `PRODUCT_REVIEWED`.
- `discuss_with_delegate` validates non-lead Agent and source binding.
- `discuss_with_delegate` creates a Discussion Window.
- `discuss_with_delegate` persists a Discussion Artifact.
- Review and Discussion tools do not modify Product content and do not finish Mission.

Required UI behavior:

- Review rows appear in Progress and Product lineage.
- Discussion Windows appear in the Windows surface with distinct type/copy.
- Discussion transcript summary and recommendation are expandable.

Required tests:

- Review Artifact creation.
- Discussion Artifact creation.
- Invalid cross-Mission Artifact refs rejected.
- Discussion max turn bound enforced.
- Neither tool mutates source Artifact content.

Exit criteria:

- A smoke Mission can review a Product, discuss a prior Artifact with the Delegate, then let the Lead choose the next tool.

## 17. Loop 15: V1.0.4 Revision Lineage

Add revision history after review/discussion Artifacts are stable.

Required behavior:

- `work_product.operation=revise_artifact` creates a new immutable Revision Artifact.
- Revision metadata links source Artifact ids.
- Revision metadata links Review and Discussion Artifact ids when provided.
- Product reader keeps original, review, discussion, revision, and final Artifacts accessible.
- Progress rows show change summary and linked source/review/discussion Artifacts.

Required tests:

- Original Artifact content remains unchanged after revision.
- Revision Artifact references original source.
- Final Product can reference revised/final Artifact explicitly.
- Product reader API returns enough lineage for UI grouping.

Exit criteria:

- Users can understand what changed, why it changed, and which version entered the final Product.

## 18. Loop 16: V1.0.5 Controlled Web Search

Add the read-only external research tool after revision lineage is stable.

Required backend behavior:

- `web_search` validates query, search type, result limit, recency, and domain filters.
- `web_search` calls a backend `SearchProvider`.
- The provider returns normalized result objects with title, URL, source, snippet, and optional published date.
- Executor emits `WEB_SEARCH_COMPLETED` on success.
- Executor emits `WEB_SEARCH_FAILED` or returns a stable failed observation on provider failure.
- Search output does not mutate Product content and does not finish Mission.
- Codex CLI, if used, is only an internal provider adapter and never a model-visible tool.

Required UI behavior:

- Search rows appear in Progress with query and result count.
- Expanded search row shows bounded source links and snippets.
- Diagnostics exposes raw structured payload.

Required tests:

- Tool protocol accepts valid `web_search`.
- Tool protocol rejects invalid `maxResults`, empty query, and invalid search type.
- Fake Search provider proves result normalization and event persistence.
- Mission loop smoke proves Lead can search, observe, and then call `work_product`.
- Browser smoke shows Search rows and source links.

Exit criteria:

- Local tests pass.
- Local browser build passes.
- Target-machine quality smoke passes on a non-public port.
- Public deployment happens only after target smoke passes.

## 19. Loop 17: Restart Recovery

Protect public Work Missions from process restarts while long Codex-backed work is running.

Required backend behavior:

- Start Work Mission execution with a process-local daemon launcher, not FastAPI `BackgroundTasks`.
- Startup recovery finds stale `running` and `stopping` Missions.
- `running` Work Windows become failed with an interruption summary.
- `running` Runs and Missions become `paused_retryable`.
- `stopping` Runs and Missions become `stopped`.
- Recovery emits visible events and preserves all prior Products, Artifacts, Work Windows, and Events.

Required tests:

- Service test proves interrupted running Mission recovers to `paused_retryable`.
- Service test proves running Work Window becomes failed.
- Route test proves `/start` launches through the launcher without request-owned background tasks.
- Public smoke verifies restart health and recoverable Mission state.

## 20. Recommended Test Commands

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

## 21. Rollback

Rollback should preserve:

- Existing Project/Mission data.
- Existing Events.
- Existing Artifacts.

If V1.0 loop is unstable:

- Keep new documents.
- Feature-flag the V1.0 runner.
- Fall back to V0.5 single-call worker only as emergency compatibility.
- Do not delete Products, Windows, or Artifacts created during testing.

## 22. 代办

- Add concrete issue tracker tickets after this document is accepted.
