## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex

# Work Mode V0.5 Single Model Run

## product goal
- Start must produce a real visible Mission artifact.
- `completed` must mean the configured runner produced and persisted output, not that a stub event sequence ended.
- The first product slice supports text artifact generation from the selected Lead Agent and Mission goal.

## non goals
- No shell command execution.
- No Git mutation.
- No Codex CLI process.
- No deploy.
- No multi-iteration supervisor.
- No supporting-Agent brainstorm.
- No approval workflow beyond showing policy state.

## public interface
- Keep existing public flow:
  - `POST /api/work/projects`
  - `POST /api/work/missions`
  - `POST /api/work/missions/{missionId}/start`
  - `GET /api/work/missions/{missionId}`
  - `GET /api/work/missions/{missionId}/events`
- Extend `MissionDetailResponse` with `artifacts`.
- Add artifact public shape:
  - `id`
  - `missionId`
  - `runId`
  - `kind`
  - `title`
  - `content`
  - `createdByEmployee`
  - `metadata`
  - `createdAt`
- Keep Product UI driven by fixed events. `PRODUCT_UPDATED` includes the latest artifact id and short preview.

## runner design
- Introduce a small runner boundary inside `backend/work_mode`.
- The runner receives Project, Mission, Run, and Lead Agent fields.
- The runner returns text content plus metadata.
- The default product runner uses `model_runtime` with a constrained prompt.
- Tests use a fake runner through service/route dependency injection.
- If model runtime is unavailable or rate-limited, mark the Mission `failed` and emit `MISSION_FAILED`; do not emit fake completion.

## event sequence
1. `MISSION_STARTED`
2. `STEP_STARTED` with title `Generate`
3. `RAW_LOG` with runner and lead Agent metadata
4. `PRODUCT_UPDATED` with artifact id, kind, title, preview, model metadata
5. `STEP_COMPLETED`
6. `MISSION_COMPLETED`

## first TDD slice
- Public behavior: after a Mission is started with a fake runner, Mission detail returns one artifact and a `PRODUCT_UPDATED` event referencing it.
- Product UI behavior: Product panel displays artifact title/content preview instead of the old V0 stub text.
- Safety behavior: no shell, Git, or command APIs are introduced.

## target verification
- Use a new target-machine smoke port, not the existing public service, until local tests pass.
- Verify health, auth, Project create, Mission create, Start, Mission detail artifacts, Product event, and frontend render.
- Update `api.md` only after the target smoke result is real.
