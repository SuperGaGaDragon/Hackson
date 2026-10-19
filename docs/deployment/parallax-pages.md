## header
Created at: 2026-10-19
Created by: Codex
Last Modified at: 2026-10-19
Last Modified by: Codex

# Parallax Pages Production Contract

## brief intro
- goal for this file.
  - Define the parallel `https://parallax-epv.pages.dev/` product entry without deleting, renaming, restarting, or replacing `https://hackson.catachess.com/`.
- 架构思路
  - Preserve the existing Parallax landing page as the public home.
  - Let the existing Hackson React product own authenticated Work, Idle, Chat, Me, and Desktop Companion routes.
  - Keep browser traffic same-origin on Pages and proxy only fixed backend paths to the existing Hackson public origin.
  - Treat the Hackson domain as an independent production origin and rollback path.

## non-destructive boundary
- `hackson.catachess.com` remains deployed and independently usable.
- Pages deployment MUST NOT restart, stop, mutate, or replace the Hackson backend service or tunnel.
- Pages deployment MUST NOT change the Hackson MongoDB database or model runtime configuration.
- Existing Parallax landing copy, sections, actions, responsive behavior, and footer MUST remain present.
- Existing Hackson Product/Artifact history, Work events, memory, users, and authentication remain backend-owned.
- A failed Pages release MUST be recoverable by selecting the previous Pages deployment; it must not require a Hackson rollback.

## route ownership
| Path | Owner | Contract |
| --- | --- | --- |
| `/` | Parallax landing | Always renders the preserved public landing, including for authenticated users. |
| `/work` | Hackson React app | Signed-out entry creates a real temporary Hackson user, then opens Work. |
| `/idle` | Hackson React app | Signed-out entry creates a real temporary Hackson user, then opens Idle. |
| `/companion` | Hackson React app | Signed-out entry creates a real temporary Hackson user, then opens Chat. |
| `/me` | Hackson React app | Signed-out entry creates a real temporary Hackson user, then opens Me. |
| `/work_project/:id` | Hackson React app | Preserves authenticated deep-link behavior. |
| `/work_mission/:id` | Hackson React app | Preserves authenticated deep-link behavior. |
| `/download/companion` | Hackson React app | Public download page; no temporary account required. |
| `/api/*` | Pages edge proxy | Proxies to `https://hackson.catachess.com/api/*` with method, query, body, and Authorization preserved. |
| `/health` | Pages edge proxy | Proxies the real Hackson JSON health response. |
| `/assets/downloads/*` | Pages static asset with proxy fallback | Serves packaged Desktop Companion artifacts locally and falls back to the Hackson origin when absent. |
| built assets | Cloudflare Pages | Served directly from the Pages deployment. |

## edge proxy constraints
- Upstream origin is a compile-time constant; visitors cannot choose a proxy target.
- `/api/*` responses MUST use `Cache-Control: no-store` at the edge.
- SSE responses MUST remain streaming and MUST preserve `text/event-stream`.
- Proxy transport failures return bounded `502` responses without exposing upstream internals.
- Unknown browser navigation routes fall back to the built `index.html`.
- Unknown asset and non-navigation requests keep their real `404` instead of receiving SPA HTML.

## release gate
Before production publication:

1. Backend full test suite passes.
2. Context Runtime evaluation passes.
3. Deterministic Work full, HTTP, search, and waiting-input smokes pass.
4. Frontend production build passes.
5. Pages edge proxy smoke passes for API, health, download, static assets, SPA fallback, auth forwarding, and failure response.
6. Browser smoke verifies the preserved landing on desktop and mobile with no horizontal overflow.
7. Browser smoke verifies Create account, Try first, Work, Idle, Chat, Me, and Desktop Companion navigation.
8. Browser Work smoke verifies Product, Work Windows, Progress, Quality, Diagnostics, SSE fallback, and final Artifact lineage.
9. Desktop JavaScript and Rust tests pass.
10. Public Pages smoke verifies `/health`, `/api/agents`, protected API auth behavior, and Desktop Companion download.

## rollout and rollback
- Capture the current Pages root HTML, asset names, checksums, screenshots, and route results before publication.
- Build and test from a clean source commit.
- Publish only to the existing `parallax-epv` project.
- Verify the exact production URL after deployment.
- If any release check fails, restore the prior Pages deployment. Do not change the Hackson domain.

## known access prerequisite
- The current local Wrangler account does not list the `parallax-epv` Pages project.
- Production publication requires the Cloudflare account or deployment credential that owns that exact project.
- Do not create a replacement project or change the requested hostname to work around missing ownership.

## local verification record — 2026-10-19
- Backend: `294 passed`.
- Context Runtime deterministic evaluation: `4` cases passed.
- Work Mode deterministic full smoke: completed with `9936` CJK characters.
- Work Mode HTTP, Search Summary, and waiting-input smokes: passed.
- Work Mode browser smoke: passed with two Work Windows, Product/Artifact lineage, Quality, SSE, desktop, and mobile coverage.
- Pages edge worker smoke: passed for auth forwarding, request bodies, API no-store policy, SSE, health, download, local asset preference, SPA fallback, security headers, and bounded `502` behavior.
- Wrangler local Pages Runtime: compiled successfully; `/health`, `/api/agents`, deep links, and the packaged `5.8 MB` Desktop Companion download returned `200`.
- Preserved landing browser smoke: desktop and mobile passed with Work, Idle, Chat, Me, and Desktop Companion entry coverage.
- Visual regression: current public Pages reference and local landing shared `1440x1052` dimensions with only `71` differing pixels (`0.0047%`).
- Frontend and Desktop dependency audits: `0 vulnerabilities` after compatible lockfile updates.
- Desktop Pet: `10` JavaScript tests, Vite build, and `3` Rust tests passed.
- Production Pages deployment remains pending only on access to the existing `parallax-epv` Cloudflare project.

## 代办
- Record the exact Pages project id and deployment id after authenticated access is available.
- Record the final public verification results in `api.md` only after deployment succeeds.
