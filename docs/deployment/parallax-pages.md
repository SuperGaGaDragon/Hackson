## header
Created at: 2026-10-19
Created by: Codex
Last Modified at: 2026-10-20
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

## production deployment record — 2026-10-19
- Cloudflare account ownership verified through Wrangler OAuth.
- Pages project: `parallax`.
- Production deployment: `2894ac0e-1f1d-43ac-ab90-833752c34aa5`.
- Deployment URL: `https://2894ac0e.parallax-epv.pages.dev/`.
- Production alias: `https://parallax-epv.pages.dev/`.
- Source commit: `f2d8723` on `startup`.
- Previous production rollback deployment: `9b91d1df-6047-4469-8759-a6d96f77f8b2`.
- Production verification passed for root, hashed assets, health, public API, protected API boundary, deep links, packaged Desktop Companion download, desktop/mobile landing, and real Quick Try handoff.
- `hackson.catachess.com` remained live and was not restarted or modified.

## 2026-10-20 light-product release contract
- Extend the public home's warm light visual language into authenticated Auth, Idle, Chat, Work, Me, modal, and Desktop Companion surfaces.
- Preserve all Pages proxy, authentication, SSE, Product/Artifact, download, and rollback behavior.
- Keep `hackson.catachess.com` independent and unchanged.
- Validate the complete local test and browser matrix before a new production Pages deployment.

## production light-theme deployment record — 2026-10-20
- Pages production deployment: `4e7b8d2b-f563-476b-a379-1371af705ef8`.
- Immutable deployment URL: `https://4e7b8d2b.parallax-epv.pages.dev/`.
- Production alias: `https://parallax-epv.pages.dev/`.
- Source commit: `f5da8f0` on `startup`.
- Immediate rollback deployment: `2894ac0e-1f1d-43ac-ab90-833752c34aa5`.
- Production assets: `/assets/index-D0F-n9xA.js` and `/assets/index-sbIvP9B0.css`.
- Real Quick Try and mocked route matrix verified Auth, Work, Idle, Chat, Me, desktop/mobile layout, backend auth, API, and return-to-intro behavior.
- Production color audit found no unintended large dark surfaces, no horizontal overflow, no failed requests, and no browser console errors.
- `hackson.catachess.com` remained independent, live, and unchanged.

## production Pet-label deployment record — 2026-10-20
- Pages production deployment: `e59e367f-b465-417d-9b82-17887805ba08`.
- Immutable deployment URL: `https://e59e367f.parallax-epv.pages.dev/`.
- Source commit: `8dd583d` on `startup`.
- Immediate rollback deployment: `4e7b8d2b-f563-476b-a379-1371af705ef8`.
- Sidebar navigation now says `Pet`; Desktop Companion platform copy remains `Mac alpha` and Apple Silicon.
- Production desktop/mobile route smoke, Pages health, and Hackson health passed.

## Cloudflare project identity
- Pages project name: `parallax`.
- Production Pages domain: `https://parallax-epv.pages.dev/`.
- Deploy only to the existing `parallax` project; do not create a replacement project or change the requested hostname.

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
- Correct project ownership was verified through Wrangler OAuth before production deployment.

## 代办
- Keep the prior deployment id available for rollback until the new Pages release has completed its observation window.
