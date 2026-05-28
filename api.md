## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

## brief intro
- This document is the current verified API and port map for Hackson.
- Public product traffic now uses `https://hackson.catachess.com/`.
- Public-domain rows describe the currently promoted product service, including Desktop Pet browser handoff login.
- The `8147` rows describe the isolated Idle Auto smoke service used for its fix.
- The `8148` rows describe the isolated Work V0.5 artifact smoke service. It is not the public product service.
- The `8150` rows describe the isolated Work V1 model-driven loop smoke service. It is not the public product service.
- The `8160` rows describe the isolated Work V1 hardening smoke service with HTTP and browser release gates. It is not the public product service.
- The `8161` rows describe the isolated Work V1 progress hardening smoke service with lifecycle events and bounded retry. It is not the public product service.
- The `8162` rows describe the isolated Work V1 Delegate tolerance smoke service. It is not the public product service.
- The `8163` rows describe the isolated Work V1 UI architecture smoke service. It is not the public product service.
- The `8164` rows describe the isolated Work V1 Product reader regression service. It is not the public product service.
- The `8165` rows describe the isolated Work V1.0.1-6 quality smoke service. It is not the public product service.
- The `8166` rows describe the isolated Context Runtime V1.0-V1.6 smoke service. It is not the public product service.

## current environment
| Item | Value |
| --- | --- |
| Target machine | `catadragon@100.70.248.39` |
| Target access note | Ignored local file `docs/数据库/machine.md`; never push it |
| Public URL | `https://hackson.catachess.com/` |
| Public source path | `~/hackson_domain_8145` |
| Public backend path | `~/hackson_domain_8145/backend` |
| Public frontend build path | `~/hackson_domain_8145/frontend/dist` |
| Public app service | `hackson-domain-8145.service`, user-level systemd, enabled and active |
| Public tunnel service | `hackson-cloudflared.service`, user-level systemd, enabled and active |
| Public backend bind | `127.0.0.1:8145` |
| Public MongoDB database | `hackson_domain_8145` |
| Public Work Mode runtime | V1 model-driven loop with Product/Artifact lineage, visible Work Windows, lifecycle progress events, bounded retry, retryable pause/resume, retryable empty-output handling, JSON-safe model-call context serialization, role-specific Lead/Delegate timeouts, waiting-input answer/resume, completed-Mission follow-up runs, bounded Requirement Grill through `ask_user`, daemon worker launch, startup restart recovery for interrupted Missions, failed-window cleanup, Delegate result tolerance, review/discussion tools, controlled `web_search`, model-visible `evaluate_product`, research/paper final-draft gates, no-evidence Reliability human-review cap, soft tool-use guidance, SSE event streaming with polling fallback, AgentLens Reliability evaluator, Activity -> Reliability -> Windows -> Product -> Progress -> Diagnostics UI, final lineage validation, and final Product all-Artifact reader with fixed-rhythm Artifact Navigator |
| Public Context Runtime | V1.6+ with context package persistence, prompt-log controls, memory controls, Background Idle permission, idle turn idempotency locks, Idle Working input queue, relationship-aware idle dialogue prompt contract, product-grade Me information architecture, account-level Agent continuity across Idle/Companion/Work, evidence-backed relationship memory, and derived-worker freshness lane |
| Public model provider | `codex_cli` through target-machine Codex CLI |
| Public model | `gpt-5.4` |
| Public model command | `/home/catadragon/.nvm/versions/node/v20.19.6/bin/codex exec` |
| Public model auth/config | `/home/catadragon/.codex` |
| Public model timeout | `HACKSON_MODEL_TIMEOUT_SECONDS=900` |
| Public cloudflared config | `~/.cloudflared/hackson.yml` |
| Idle Auto smoke source path | `~/hackson_idle_auto_8146` |
| Idle Auto smoke backend path | `~/hackson_idle_auto_8146/backend` |
| Idle Auto smoke frontend build path | `~/hackson_idle_auto_8146/frontend/dist` |
| Idle Auto smoke service | `hackson-idle-auto-8147.service`, user-level systemd, active |
| Idle Auto smoke backend bind | `127.0.0.1:8147` |
| Idle Auto smoke local check | `127.0.0.1:5187 -> 18147 -> 8147` |
| Idle Auto smoke MongoDB database | `hackson_idle_auto_8147` |
| Work V0.5 smoke source path | `~/hackson_work_v05_8148` |
| Work V0.5 smoke backend path | `~/hackson_work_v05_8148/backend` |
| Work V0.5 smoke frontend build path | `~/hackson_work_v05_8148/frontend/dist` |
| Work V0.5 smoke service | `hackson-work-v05-8148.service`, user-level systemd, active |
| Work V0.5 fake model relay | `hackson-work-v05-fake-model-18148.service`, user-level systemd, active |
| Work V0.5 smoke backend bind | `127.0.0.1:8148` |
| Work V0.5 fake model bind | `127.0.0.1:18148` |
| Work V0.5 smoke database | `hackson_work_v05_8148` |
| Work V1 smoke source path | `~/hackson_work_v1_8150` |
| Work V1 smoke backend path | `~/hackson_work_v1_8150/backend` |
| Work V1 smoke frontend build path | `~/hackson_work_v1_8150/frontend/dist` |
| Work V1 smoke service | `hackson-work-v1-8150.service`, user-level systemd, active |
| Work V1 smoke backend bind | `127.0.0.1:8150` |
| Work V1 smoke database | `hackson_work_v1_8150` |
| Work V1 smoke model provider | `codex_cli` through target-machine Codex CLI |
| Work V1 hardening smoke source path | `~/hackson_work_v1_8160` |
| Work V1 hardening smoke backend path | `~/hackson_work_v1_8160/backend` |
| Work V1 hardening smoke frontend build path | `~/hackson_work_v1_8160/frontend/dist` |
| Work V1 hardening smoke service | `hackson-work-v1-8160.service`, user-level systemd, active |
| Work V1 hardening smoke backend bind | `127.0.0.1:8160` |
| Work V1 hardening smoke database | `hackson_work_v1_8160` |
| Work V1 hardening smoke model provider | `codex_cli` through target-machine Codex CLI |
| Work V1 progress hardening source path | `~/hackson_work_v1_progress_8161` |
| Work V1 progress hardening backend path | `~/hackson_work_v1_progress_8161/backend` |
| Work V1 progress hardening frontend build path | `~/hackson_work_v1_progress_8161/frontend/dist` |
| Work V1 progress hardening service | `hackson-work-v1-progress-8161.service`, user-level systemd, active |
| Work V1 progress hardening backend bind | `127.0.0.1:8161` |
| Work V1 progress hardening database | `hackson_work_v1_progress_8161` |
| Work V1 progress hardening model provider | `codex_cli` through target-machine Codex CLI |
| Work V1 Delegate tolerance source path | `~/hackson_work_v1_delegate_8162` |
| Work V1 Delegate tolerance backend path | `~/hackson_work_v1_delegate_8162/backend` |
| Work V1 Delegate tolerance frontend build path | `~/hackson_work_v1_delegate_8162/frontend/dist` |
| Work V1 Delegate tolerance service | `hackson-work-v1-delegate-8162.service`, user-level systemd, active |
| Work V1 Delegate tolerance backend bind | `127.0.0.1:8162` |
| Work V1 Delegate tolerance database | `hackson_work_v1_delegate_8162` |
| Work V1 Delegate tolerance model provider | `codex_cli` through target-machine Codex CLI |
| Work V1 UI architecture source path | `~/hackson_work_ui_8163` |
| Work V1 UI architecture backend path | `~/hackson_work_ui_8163/backend` |
| Work V1 UI architecture frontend build path | `~/hackson_work_ui_8163/frontend/dist` |
| Work V1 UI architecture service | `hackson-work-ui-8163.service`, user-level systemd, active |
| Work V1 UI architecture backend bind | `127.0.0.1:8163` |
| Work V1 UI architecture database | `hackson_work_ui_8163` |
| Work V1 UI architecture model provider | `codex_cli` through target-machine Codex CLI |
| Work V1 Product reader source path | `~/hackson_work_product_reader_8164` |
| Work V1 Product reader backend path | `~/hackson_work_product_reader_8164/backend` |
| Work V1 Product reader frontend build path | `~/hackson_work_product_reader_8164/frontend/dist` |
| Work V1 Product reader service | `hackson-work-product-reader-8164.service`, user-level systemd, active |
| Work V1 Product reader backend bind | `127.0.0.1:8164` |
| Work V1 Product reader database | `hackson_work_product_reader_8164` |
| Work V1 Product reader model provider | `codex_cli` through target-machine Codex CLI |
| Work V1.0.1-6 quality source path | `~/hackson_work_quality_8165` |
| Work V1.0.1-6 quality backend path | `~/hackson_work_quality_8165/backend` |
| Work V1.0.1-6 quality frontend build path | `~/hackson_work_quality_8165/frontend/dist` |
| Work V1.0.1-6 quality service | `hackson-work-quality-8165.service`, user-level systemd, active |
| Work V1.0.1-6 quality backend bind | `127.0.0.1:8165` |
| Work V1.0.1-6 quality database | `hackson_work_quality_8165` |
| Work V1.0.1-6 quality model provider | `codex_cli` through target-machine Codex CLI |
| Work V1.0.1-6 quality model timeout | `HACKSON_MODEL_TIMEOUT_SECONDS=900` |
| Public frontend assets after Work V1.0.5 promotion | `/assets/index-D-yFdK1R.js`, `/assets/index-CwEAac1R.css` |
| Context Runtime V1.0-V1.6 smoke source path | `~/hackson_context_runtime_8166` |
| Context Runtime V1.0-V1.6 smoke backend path | `~/hackson_context_runtime_8166/backend` |
| Context Runtime V1.0-V1.6 smoke frontend build path | `~/hackson_context_runtime_8166/frontend/dist` |
| Context Runtime V1.0-V1.6 smoke frontend assets | `/assets/index-DNrmBHyi.js`, `/assets/index-DTBHuMeq.css` |
| Public frontend assets after Context Runtime V1.6 promotion | `/assets/index-n_-ZPKaU.js`, `/assets/index-CHTMdui3.css` |
| Public frontend assets after AgentLens promotion | `/assets/index-n_-ZPKaU.js`, `/assets/index-CHTMdui3.css` |
| Public frontend assets after Desktop Pet handoff promotion | `/assets/index-CTj8ztQu.js`, `/assets/index-DTBHuMeq.css` |
| Public frontend assets after Work SSE streaming promotion | `/assets/index-CG4wOHJC.js`, `/assets/index-DTBHuMeq.css` |
| Public frontend assets after Product reader polish promotion | `/assets/index-ESYnQodx.js`, `/assets/index-ByttZ1zW.css` |
| Public frontend assets after Work follow-up promotion | `/assets/index-OVTNRPWP.js`, `/assets/index-QOvacDKh.css` |
| Public frontend assets after Agent stories/account memory promotion | `/assets/index-OVTNRPWP.js`, `/assets/index-QOvacDKh.css` |
| Public frontend assets after Work evaluator tool promotion | `/assets/index-Cy-unphL.js`, `/assets/index-Dx_ve1gX.css` |
| Public frontend assets after Evaluator V1 contract closure | `/assets/index-CHVyLRVQ.js`, `/assets/index-Cg9l671U.css` |
| Local frontend assets after Evaluator V1 contract closure | `/assets/index-CHVyLRVQ.js`, `/assets/index-Cg9l671U.css` |
| Context Runtime 8166 frontend assets after Agent origin story check | `/assets/index-Bb_Fx5DE.js`, `/assets/index-DTBHuMeq.css` |
| Context Runtime V1.0-V1.6 smoke service | `hackson-context-runtime-8166.service`, user-level systemd, active |
| Context Runtime fake model service | `hackson-context-runtime-fake-model-18166.service`, user-level systemd, active |
| Context Runtime V1.0-V1.6 smoke backend bind | `127.0.0.1:8166` |
| Context Runtime fake model bind | `127.0.0.1:18166` |
| Context Runtime V1.0-V1.6 smoke database | `hackson_context_runtime_8166` |
| Context Runtime V1.0-V1.6 smoke model provider | OpenAI-compatible fake relay on `127.0.0.1:18166` |
| Legacy Tailscale URL | `http://100.70.248.39:8130/` |
| Legacy production service | `hackson-production.service`, user-level systemd, enabled and active |
| Legacy production path | `~/hackson_production` |
| Legacy production bind | `0.0.0.0:8130` |
| Legacy production database | `hackson` |

## active Hackson port map
| Port | Service | Bind | Status | Purpose |
| --- | --- | --- | --- | --- |
| 8145 | Hackson public domain FastAPI + React app | `127.0.0.1` | Active as `hackson-domain-8145.service` | Serves `https://hackson.catachess.com/` through `hackson-cloudflared.service`; promoted to AgentLens Reliability evaluator, Work restart-recovery, and Desktop Pet browser handoff login on 2026-05-28 |
| 8147 | Hackson Idle Auto smoke FastAPI + React app | `127.0.0.1` | Active as `hackson-idle-auto-8147.service` | Isolated verification for Idle Auto topic, interjection, speaker, and rate-limit behavior |
| 8148 | Hackson Work V0.5 smoke FastAPI + React app | `127.0.0.1` | Active as `hackson-work-v05-8148.service` | Isolated verification for Work Mission artifact persistence and Product UI render |
| 18148 | Work V0.5 fake OpenAI-compatible model relay | `127.0.0.1` | Active as `hackson-work-v05-fake-model-18148.service` | Test-only model relay for deterministic Work V0.5 success smoke; not a product API |
| 8150 | Hackson Work V1 smoke FastAPI + React app | `127.0.0.1` | Active as `hackson-work-v1-8150.service` | Isolated verification for Work V1 model-selected tool loop, Product/Artifact lineage, retryable pause, and resume |
| 8160 | Hackson Work V1 hardening smoke FastAPI + React app | `127.0.0.1` | Active as `hackson-work-v1-8160.service` | Isolated verification for Work V1 HTTP full smoke, browser UI smoke, and final Product/Artifact lineage |
| 8161 | Hackson Work V1 progress hardening FastAPI + React app | `127.0.0.1` | Active as `hackson-work-v1-progress-8161.service` | Isolated verification for Work V1 lifecycle events, bounded retry, Activity UI, and failed-window cleanup |
| 8162 | Hackson Work V1 Delegate tolerance FastAPI + React app | `127.0.0.1` | Active as `hackson-work-v1-delegate-8162.service` | Isolated verification for tolerant Delegate result ingestion, unstructured prose Artifact persistence, full smoke, HTTP smoke, and browser smoke |
| 8163 | Hackson Work V1 UI architecture FastAPI + React app | `127.0.0.1` | Active as `hackson-work-ui-8163.service` | Isolated verification for Activity, Windows, Product lineage, Progress, Diagnostics, desktop/mobile browser smoke, and no mobile horizontal overflow |
| 8164 | Hackson Work V1 Product reader FastAPI + React app | `127.0.0.1` | Active as `hackson-work-product-reader-8164.service` | Isolated regression verification that final Products keep outline, chapter drafts, and final draft readable after Done |
| 8165 | Hackson Work V1.0.1-6 quality FastAPI + React app | `127.0.0.1` | Active as `hackson-work-quality-8165.service` | Isolated verification for expandable Progress details, New Mission modal, deterministic long-novel quality gates, Review/Discussion tool schema, controlled `web_search`, model-visible `evaluate_product`, research/paper final-draft gates, revision lineage, final Product reader, fixed-rhythm Product Artifact Navigator, `MODEL_TURN_INVALID` event polling, and real Codex 8000字 browser smoke |
| 8166 | Hackson Context Runtime V1.0-V1.6 smoke FastAPI + React app | `127.0.0.1` | Active as `hackson-context-runtime-8166.service` | Isolated verification for context package persistence, Full Prompt Logging, Background Idle setting, prompt-log delete, Me controls, idle tick/idlesay idempotency, worker-derived summaries/account memory, persisted summary selection, memory controls, Idle Working input queue, relationship-aware idle prompt contract, account-level Agent continuity, and deterministic context eval gate |
| 18166 | Context Runtime fake OpenAI-compatible model relay | `127.0.0.1` | Active as `hackson-context-runtime-fake-model-18166.service` | Test-only model relay for deterministic Context Runtime success smoke; not a product API |
| 8130 | Legacy Hackson production FastAPI + React app | `0.0.0.0` | Active as `hackson-production.service` | Retained legacy Tailscale production URL until explicitly retired |

## cleanup record
- On 2026-05-27, old Hackson smoke uvicorn ports were stopped after the current code was promoted to the public domain.
- Stopped Hackson smoke ports: `8101`, `8122`, `8123`, `8124`, `8125`, `8126`, `8131`, `8132`, `8133`, `8141`, `8142`, `8143`, `8144`, `8146`.
- On 2026-05-27, `8147` was reintroduced as `hackson-idle-auto-8147.service` for isolated Idle Auto verification without touching public `8145`.
- On 2026-05-27, temporary Orchestrator V1 smoke ports `8148` and `18148` were used for isolated target-machine verification, then stopped.
- On 2026-05-27, `8148` and `18148` were reintroduced as Work V0.5 isolated smoke services. They are active and intentionally separate from public `8145`.
- On 2026-05-27, `8150` was introduced as the isolated Work V1 model-driven loop smoke service. It is active and intentionally separate from public `8145`, Idle Auto `8147`, Work V0.5 `8148`, and legacy `8130`.
- On 2026-05-27, `8160` was introduced as the isolated Work V1 hardening smoke service. It verified backend tests, frontend build, deterministic full smoke, authenticated HTTP full smoke, browser UI smoke, static frontend serving, and health check without stopping existing services.
- On 2026-05-27, the Work V1 hardening build was promoted to public `8145` after target public-directory tests passed. Public health and static frontend checks passed, deterministic Work V1 full smoke and authenticated HTTP full smoke passed, and a real public browser-triggered Codex Mission entered `paused_retryable model_timeout` with persisted plan/product events and no orphan `codex exec` process.
- On 2026-05-27, `8161` was introduced as the isolated Work V1 progress hardening service. It added safe lifecycle events, bounded automatic retry before `paused_retryable`, failed-window cleanup for delegate provider errors, and a compact Work UI activity strip. Target tests, frontend build, full smoke, HTTP smoke, browser smoke, health, and static React checks passed.
- On 2026-05-27, the Work V1 progress hardening build was promoted to public `8145`. Public-directory Work Mode `52`, model_runtime `24`, interactions `21`, frontend build, deterministic full smoke, and HTTP smoke passed before restart. After restart, `https://hackson.catachess.com/health` and `/` returned `200`, assets `index-HYSRYan8.js` and `index-cInveBCH.css` were served, and real Codex Mission `6a17a145f01aad81f13bca71` completed with lifecycle events around each tool call.
- On 2026-05-28, `8162` was introduced as the isolated Work V1 Delegate tolerance service. It fixes the public Mission `6a17a659f01aad81f13bca8a` failure mode where a Delegate window returned useful writing but missed the strict JSON wrapper. Target Work Mode `55`, model_runtime `24`, interactions `21`, frontend build, full smoke, HTTP smoke, Delegate unstructured-prose HTTP regression, browser smoke, health, and static React checks passed.
- On 2026-05-28, the Work V1 Delegate tolerance build was promoted to public `8145`. Public-directory Work Mode `55`, model_runtime `24`, interactions `21`, frontend build, deterministic full smoke, HTTP smoke, and Delegate unstructured-prose regression passed before restart. After restart, `https://hackson.catachess.com/health` and `/` returned `200`, assets `index-HYSRYan8.js` and `index-cInveBCH.css` were served, public runtime Delegate parse returned `completed` with `delegateStructured=false`, and no orphan `codex exec` process was present.
- On 2026-05-28, `8163` was introduced as the isolated Work V1 UI architecture service. It verifies the Work Console order `Activity -> Windows -> Product -> Progress -> Diagnostics`, Product Artifact lineage, default-collapsed Diagnostics, desktop and mobile browser smoke, and mobile no-horizontal-overflow without touching public `8145`.
- On 2026-05-28, the Work V1 UI architecture frontend build was promoted to public `8145` by replacing only `frontend/dist`; `hackson-domain-8145.service` was not restarted. Public health, root HTML, assets `/assets/index-qPU-cMH4.js` and `/assets/index-BbzX_UAM.css`, and a public browser static Work Console order check passed.
- On 2026-05-28, `8164` was introduced as the isolated Work V1 Product reader regression service. It verifies that a completed final Product defaults to an all-Artifact reader stack and can switch between `All`, outline, chapter drafts, and final draft.
- On 2026-05-28, the Work V1 Product reader frontend build was promoted to public `8145` by replacing only `frontend/dist`; `hackson-domain-8145.service` was not restarted. Public health, root HTML, assets `/assets/index-3udE6cD6.js` and `/assets/index-BcI42SsQ.css`, and a public browser asset-load check passed.
- On 2026-05-28, `8166` and fake model relay `18166` were introduced as isolated Context Runtime V1.0 smoke services. They verified context package persistence, prompt hash/source-id metadata, Full Prompt Logging default-on behavior, disabled prompt text omission, prompt-log deletion, static React serving, and Me prompt-log controls without touching public `8145` or existing smoke services.
- On 2026-05-28, `8166` was updated with Loop 3 idle tick lock verification. The first target attempt exposed a Mongo ObjectId completion bug and failed-lock retry bug; both were fixed with mongomock regression tests. Target HTTP smoke then passed with `idempotent_retry=ok`, and Mongo `idle_turn_locks` showed completed response snapshots for both idempotency keys.
- On 2026-05-28, `8166` was updated with the Loop 4 Background Idle user setting. New users return `backgroundIdleOn=false`; Me shows a `Background` toggle; saving `backgroundIdleOn=true` is verified. No background runner is enabled by this smoke.
- On 2026-05-28, `8166` was updated with the Loop 4 server-side cadence gate. The gate blocks when Background Idle is disabled, allows when enabled and within budget, records successful background turns in `idle_runner_state`, and returns `idle_budget_exhausted` after the configured smoke budget. No daemonized background runner is enabled by this smoke.
- On 2026-05-28, `8166` was updated with the Loop 5 derived worker runner. The HTTP smoke now runs pending jobs through `DerivedWorkerRunner` and verifies persisted summaries, companion preference memory, idle relationship memory, and diary entries. Earlier smoke processed `22` jobs with `0` failed jobs.
- On 2026-05-28, `8166` was updated with Loops 6-8. Persisted session summaries are preferred over synchronous compact summaries for long histories, scoped memory is injected into idle/companion/work context without work-to-companion leakage, Me exposes memory list/disable/enable/delete controls, and `scripts/context_runtime_eval.py` gates mode fit, speaker boundary, topic adherence, repetition, transition quality, memory use, and latency notes. Latest target smoke passed with `idempotent_retry=ok background_gate=ok memory_controls=ok worker_processed=14 persisted_summary=6a17d1f9acac0d98f3d0a95c`; target Mongo counts after smoke were context packages `38`, memory cards `17`, summaries `37`, failed jobs `0`. Target Me browser smoke passed with screenshot `scripts/artifacts/context_runtime_me_memory_smoke.png`.
- On 2026-05-28, `8165` was updated as the isolated Work V1.0.1-4 quality service. Target Work Mode `66`, model_runtime `24`, deterministic full smoke, authenticated HTTP full smoke, frontend build, health, static assets, and real Codex browser smoke passed. The real smoke created Mission `6a17ca6696b9294a46f1f476`, used 4 Delegate windows, persisted 8 Artifacts, recovered from `final_artifact_not_final_content` and `final_artifact_cjk_too_short`, and completed with final Artifact `6a17ccc796b9294a46f1f4c9` at `8827` CJK. The Playwright UI smoke measured full Product text at `23615` CJK and saved target screenshots under `scripts/artifacts/work_mode_v1_quality_target*.png`.
- On 2026-05-28, the Work V1.0.1-4 quality build was promoted to public `8145` from the verified `8165` release source. Public-directory Work Mode `66`, model_runtime `24`, deterministic full smoke, authenticated HTTP full smoke, and frontend build passed before restart. After restart, `127.0.0.1:8145/health`, `https://hackson.catachess.com/health`, and `/` returned `200`; assets `index-3zN414a_.js` and `index-B9725wXu.css` were served. Public `HACKSON_MODEL_TIMEOUT_SECONDS` is `900`. Real public browser smoke passed with Mission `6a17cfa6f1c229f07da02229`, 2 Work Windows, 5 Artifacts, recovery from `final_artifact_not_final_content`, final Product `《潮汐备忘录》最终成稿`, browser-read Product text `22819` CJK, screenshots `scripts/artifacts/work_mode_v1_quality_public*.png`, and no orphan `codex exec` process.
- On 2026-05-28, Context Runtime V1.0-V1.3 was promoted from verified `8166` to public `8145`. Public source was backed up to `~/hackson_backups/context_runtime_public_20260528015746` before the whitelist sync. Public-directory Context Runtime scoped tests passed with `66` tests; `scripts/context_runtime_eval.py` passed with `context_runtime_eval=ok cases=4`; frontend build passed with assets `/assets/index-O58mTWZQ.js` and `/assets/index-dKibUoIc.css`. After restarting `hackson-domain-8145.service`, `127.0.0.1:8145/health`, `https://hackson.catachess.com/health`, root HTML, and both assets returned `200`. Public API smoke verified new-user defaults `fullPromptLoggingOn=true` and `backgroundIdleOn=false`, prompt-log list, memory list, and settings patch. Public Me browser smoke passed with screenshot `scripts/artifacts/context_runtime_me_public_smoke.png`. Public model-backed idle tick succeeded with context package `6a17d9d5a0f8dcab0cfc07dc`; production Mongo `hackson_domain_8145` then showed `context_packages=1`, `prompt_text_stored=1`, `memory_cards=0`, `summaries=0`, `jobs_failed=0`. Post-promotion Work regression also passed in the public directory: Work Mode + model_runtime `91` tests, `work_mode_v1_full_smoke`, `work_mode_v1_http_smoke`, and `work_mode_waiting_input_http_smoke`.
- On 2026-05-28, public `8145` was patched for the Work Mode `waiting_input` answer entry. `ask_user` now has a complete product loop: `USER_INPUT_REQUESTED` displays an answer form, `POST /api/work/missions/{missionId}/answer` records `USER_INPUT_RECEIVED`, closes the waiting run, creates a resumed run, and continues the Mission. Local, `8165`, and public-directory Work Mode `67`, model_runtime `24`, waiting-input HTTP smoke, deterministic full smoke, authenticated HTTP full smoke, and frontend build passed. After restart, `https://hackson.catachess.com/health` returned `200`, public assets `index-CfNoUhgE.js` and `index-Y-VWNAFW.css` were served, public `/answer` returned `409 mission_not_waiting_input` for a non-waiting Mission, and the public JS bundle contains the visible `Input Requested` answer form.
- On 2026-05-28, `8165` and public `8145` were updated with Work V1.0.5 controlled `web_search`. The tool is read-only, backend-owned, and visible through `WEB_SEARCH_COMPLETED` / `WEB_SEARCH_FAILED` events plus source-link Progress details. Local Work Mode discovery passed with `77` tests; `8165` and public-directory Work Mode passed with `73` tests. Deterministic full smoke, `work_mode_v1_search_smoke`, authenticated HTTP full smoke, and frontend build passed on the public release path. The target-machine real provider probe returned `ok 1 duckduckgo_lite`. After restarting `hackson-domain-8145.service`, `127.0.0.1:8145/health` and `https://hackson.catachess.com/health` returned `{"status":"ok"}`, and public assets `index-D-yFdK1R.js` / `index-CwEAac1R.css` were served.
- On 2026-05-28, `8166` and public `8145` were updated with Context Runtime V1.6 idle interruption and human dialogue behavior. Idle Working no longer blocks user input: the UI accepts one queued user line, pauses Auto, renders it as pending, and sends it as soon as the active turn finishes. `POST /api/idle/{conversationId}/messages` now accepts `idempotencyKey` and uses the same idle turn lock as tick so concurrent transcript writes return `423 idle_turn_locked` instead of reordering messages. Idle prompts now include `Relationship stance`, `Turn intent`, previous-Agent response requirements, one-move conversational guidance, and anti-checklist rules. Public source was backed up to `~/hackson_backups/idle_human_public_20260528022746` before the whitelist sync. Public-directory Context Runtime tests passed with `69` tests; Work Mode/model_runtime regression passed with `97` tests; `scripts/context_runtime_eval.py`, `work_mode_v1_full_smoke`, `work_mode_v1_http_smoke`, `work_mode_waiting_input_http_smoke`, and frontend build passed before restart. After restarting `hackson-domain-8145.service`, local and public `/health` returned `{"status":"ok"}`, root HTML served `/assets/index-n_-ZPKaU.js` and `/assets/index-CHTMdui3.css`, public API smoke passed with `context_runtime_http_smoke=ok ... worker_processed=26` on final recheck, public Idle interruption browser smoke passed with screenshot `scripts/artifacts/idle_interruption_public_recheck.png`, public Me smoke passed with screenshot `scripts/artifacts/context_runtime_me_public_recheck.png`, and production logs showed the expected `idle/tick`, `idle/messages`, prompt-log, memory, and Work polling requests without service errors.
- On 2026-05-28, public `8145` was updated with AgentLens Reliability evaluator for Work Missions. Public source files were backed up to `~/hackson_backups/agentlens_public_20260528023904` before the targeted sync. Target Work Mode tests passed with `77` tests; targeted evaluator/route tests passed with `12` tests; target frontend build passed with assets `/assets/index-n_-ZPKaU.js` and `/assets/index-CHTMdui3.css`; target `work_mode_v1_http_smoke.py` passed with `reliability_score=80` and `reliability_status=minor_review`. After restarting only `hackson-domain-8145.service`, local and public `/health` returned `{"status":"ok"}`, public root served the new assets, `scripts/work_mode_agentlens_public_smoke.py` passed against `https://hackson.catachess.com` with Mission `6a17e448abb7d1b24cd60d53`, score `26`, status `unsafe_to_ship`, and issues `hallucinated_entity, missing_source, tool_failure_ignored, unsupported_claim, weakly_supported_claim`; public UI smoke passed with screenshot `scripts/artifacts/work_mode_agentlens_public_ui_smoke.png`.
- On 2026-05-28, public `8145` was patched for Work restart recovery after user testing exposed a `deactivating (stop-sigterm)` hang while a long Codex-backed Delegate turn was active. Work Mission launch no longer uses request-owned FastAPI `BackgroundTasks`; startup recovery now marks interrupted `running` Missions as `paused_retryable`, marks running Work Windows as `failed`, and emits `WORK_WINDOW_FAILED` plus `MISSION_PAUSED_RETRYABLE` without deleting Products, Artifacts, or Events. The affected public Mission `6a17e0d8a86e4f0e354d1974` recovered to `paused_retryable interrupted_restart`; its open window `6a17e141a86e4f0e354d198f` recovered to `failed`. Local Work Mode tests passed with `80` tests and frontend build passed. Isolated `8165` passed Work Mode `80`, `work_mode_v1_search_smoke.py`, `work_mode_v1_full_smoke.py`, and restart-recovery smoke. Public-directory Work Mode `80`, search smoke, full smoke, HTTP smoke, and frontend build passed before restart. Restarting `hackson-domain-8145.service` completed immediately at `02:46:06 EDT`; local and public `/health` returned `{"status":"ok"}`, and no orphan `codex exec` process remained.
- On 2026-05-28, public `8145` was patched for Desktop Pet V0.8.2 browser handoff login. Public source files were backed up to `~/hackson_backups/desktop_handoff_public_20260528084126` before the targeted sync. Public-directory user service/route tests passed with `9` tests; target frontend build passed with assets `/assets/index-CTj8ztQu.js` and `/assets/index-DTBHuMeq.css`. After restarting only `hackson-domain-8145.service`, local and public `/health` returned `{"status":"ok"}`, `POST /api/users/desktop-handoff/claim` returned `200` instead of the previous `405`, public API smoke verified `pending -> linked -> authorized -> pending`, and browser smoke verified both already-logged-in and login-then-bind `?desktopAuth=` flows with screenshot `scripts/artifacts/desktop_pet_browser_handoff_public.png`.
- On 2026-05-28, public `8145` was patched for Work Mode timeout hardening, soft tool-use guidance, and V1.2 event-log streaming. Lead tool-selection calls now use a short default budget (`180s`) while Delegate writing calls keep the long default budget (`900s`); Codex CLI process groups are cleaned after success, timeout, and failure. Lead context now includes soft guidance to use `web_search`, `review_product`, and `discuss_with_delegate` more actively when the task warrants it, without backend hard-coding the workflow. `GET /api/work/missions/{missionId}/events/stream` now streams persisted public Mission events over SSE; frontend Work uses `fetch` + `ReadableStream` so Bearer auth works and falls back to polling if streaming fails. Local, `8165`, and public-directory Work Mode `85` tests, model_runtime `28` tests, deterministic full smoke, search smoke, waiting-input smoke, and frontend build passed. After restart, public `/health` returned `200`, root HTML served `/assets/index-CG4wOHJC.js` and `/assets/index-DTBHuMeq.css`, public SSE probes returned `text/event-stream` with `MISSION_CREATED`, and no orphan `codex exec` process remained.
- On 2026-05-28, `8166` and public `8145` were updated with Me Page product IA and derived worker freshness. Public source was backed up to `~/hackson_backups/me_worker_public_20260528091359` before the targeted sync. Me now prioritizes Account and editable Nora/Vale Agent profiles in the first viewport, moves Prompt Logs into collapsed Debug, keeps each prompt log expandable, labels user context as `Style` and `Background`, and keeps `Away idle` separate from user Background. Memory reads now hide legacy generic relationship cards exactly matching `Nora and Vale shared another idle interaction.` Relationship memory now requires two Agent source messages and summarizes the actual source text. Derived job processing supports scoped smoke runs and a background freshness lane that processes latest pending jobs in addition to FIFO backlog. Local backend tests passed with `218` tests and frontend build passed. Isolated `8166` backend tests passed with `195` tests; target build with Node `20.19.6` served `/assets/index-DNrmBHyi.js` and `/assets/index-DTBHuMeq.css`; target API smoke passed with `context_runtime_http_smoke=ok ... worker_processed=11 persisted_summary=6a1841095ddfc615b4d0da52`; target Me browser smoke passed with screenshot `scripts/artifacts/context_runtime_me_ia_8166_v2.png`. Public-directory backend tests passed with `216` tests; public build served `/assets/index-CG4wOHJC.js` and `/assets/index-DTBHuMeq.css`; after restart `hackson-domain-8145.service`, `hackson-cloudflared.service`, `hackson-context-runtime-8166.service`, and `hackson-context-runtime-fake-model-18166.service` were all active. Final public API smoke passed with `context_runtime_http_smoke=ok user=6a184109a816f35aa141e653 conversation=6a184109a816f35aa141e654 packages=5 first=6a184109a816f35aa141e657 second=6a18410fa816f35aa141e665 idempotent_retry=ok background_gate=ok memory_controls=ok worker_processed=2 persisted_summary=6a184117a816f35aa141e679`; Mongo for that user had `pending=0`, `summaries=5`, `diaries=4`, and content-derived idle relationship memories. Public Me browser smoke passed with screenshot `scripts/artifacts/context_runtime_me_ia_public_v3.png`.
- On 2026-05-28, `8166` and public `8145` were updated with Account Agent Continuity. Account-scoped memory now enters Idle, Companion 1, Companion 2, and Work prompts; explicit user preferences from Companion and Work write to `scope=account`; legacy Companion user memories and Idle relationship memories remain readable as account-continuity input; raw Work trace and task-private memory still stay out of Idle/Companion unless promoted. Public source was backed up to `~/hackson_backups/account_memory_public_20260528102451` before targeted sync. Local scoped backend tests passed with `75 passed`; local `context_runtime_eval.py` passed with `context_runtime_eval=ok cases=4` and account memory assertions. Isolated target `8166` directory tests passed with `75 passed`; target eval passed; temporary non-public `8177` HTTP/Mongo smoke passed against `hackson_context_account_8177` with `account_continuity=ok` and account prompt packages `6a185000a302f7624a00439e,6a185000a302f7624a0043a3,6a185000a302f7624a0043a9`; temporary `8177` was stopped after verification and existing services remained active. Public-directory tests passed with `75 passed`; public eval passed; after restarting only `hackson-domain-8145.service`, local and public `/health` returned `{"status":"ok"}`. Final public HTTP/Mongo smoke passed with `context_runtime_http_smoke=ok user=6a185100677ce09b41002387 conversation=6a185100677ce09b41002388 packages=6 first=6a185100677ce09b4100238b second=6a185106677ce09b41002394 idempotent_retry=ok background_gate=ok memory_controls=ok account_continuity=ok worker_processed=2 persisted_summary=6a185120677ce09b410023c4 account_prompt_packages=6a185117677ce09b410023b7,6a18511b677ce09b410023bc,6a18511f677ce09b410023c3`. Final service check showed `hackson-domain-8145.service`, `hackson-cloudflared.service`, `hackson-context-runtime-8166.service`, and `hackson-context-runtime-fake-model-18166.service` active.
- On 2026-05-28, public `8145` was updated with the detailed default Nora/Vale Agent Origin Stories together with the Account Agent Continuity release. Public source and frontend `dist` were backed up to `~/hackson_backups/story_account_public_20260528103242` before targeted sync. Local verification passed with `89 passed` across Agent/User/Context/Memory/Interactions/Workers tests, `context_runtime_eval=ok cases=4`, and frontend build assets `/assets/index-OVTNRPWP.js` and `/assets/index-QOvacDKh.css`. Public-directory verification passed with `89 passed`; public eval passed; deployed frontend bundle contains `Nora was seven...` and `Vale was six...`. After restarting only `hackson-domain-8145.service`, local and public `/health` returned `{"status":"ok"}`, root HTML served `/assets/index-OVTNRPWP.js` and `/assets/index-QOvacDKh.css`, public registration returned Nora story length `2913` and Vale story length `3070`, and final public Account Continuity smoke passed with `context_runtime_http_smoke=ok user=6a185297fd7d65a5d7a50e09 conversation=6a185297fd7d65a5d7a50e0a packages=6 first=6a185297fd7d65a5d7a50e0d second=6a1852a1fd7d65a5d7a50e14 idempotent_retry=ok background_gate=ok memory_controls=ok account_continuity=ok worker_processed=2 persisted_summary=6a1852c4fd7d65a5d7a50e46 account_prompt_packages=6a1852b5fd7d65a5d7a50e39,6a1852bdfd7d65a5d7a50e3e,6a1852c3fd7d65a5d7a50e45`.
- On 2026-05-28, `8166` and public `8145` were updated with Idle Collaborative Convergence Protocol. Idle prompts now require user-interjection priority, agreement acknowledgment, decision-relevant disagreement, non-repetition, shared-conclusion checks, the settlement phrase `No new disagreement. I accept the current direction.`, and an emphasis-only stop condition while keeping the protocol hidden from visible replies. Public source was backed up to `~/hackson_backups/idle_convergence_public_20260528105756` before targeted sync. Local verification passed with Context Builder `11 passed`, scoped backend `89 passed`, and `context_runtime_eval=ok cases=4` including convergence assertions. Isolated `8178` HTTP/Mongo smoke passed against `hackson_context_convergence_8178` with `context_runtime_http_smoke=ok user=6a1857d9ee9efb87bb0caa4f conversation=6a1857d9ee9efb87bb0caa50 ... account_continuity=ok`; temporary `8178` was stopped and existing services stayed active. Public-directory verification passed with Context Builder `11 passed`, scoped backend `89 passed`, and public eval. After restarting only `hackson-domain-8145.service`, local and public `/health` returned `{"status":"ok"}`, public root served `/assets/index-OVTNRPWP.js` and `/assets/index-QOvacDKh.css`, public HTTP/Mongo smoke passed with `context_runtime_http_smoke=ok user=6a185870a9fabea4f1eaf0de conversation=6a185871a9fabea4f1eaf0df ... account_continuity=ok`, and a user-perspective API smoke confirmed prompt logs contain the convergence protocol while visible Agent replies are non-empty, bounded, and do not expose hidden prompt rules.
- On 2026-05-28, public `8145` static frontend hosting was patched to accept `HEAD /` and `HEAD /{path}` for product-grade uptime probes while preserving the existing React fallback. Local app-level tests verified `GET` and `HEAD` for root and route fallback. Public-directory app tests passed, `hackson-domain-8145.service` was restarted, both local and public `HEAD /` returned `200`, public root served `/assets/index-Cy-unphL.js` and `/assets/index-Dx_ve1gX.css`, and both assets returned `200`.
- On 2026-05-28, public `8145` was patched for user-comfort memory recall. Public audit found that `请记住：我做产品时喜欢你直接指出不舒服的点，不要先安慰我。` produced succeeded `memory_candidate` jobs but no memory card because MemoryWorker only recognized narrow markers such as `我喜欢` and `我偏好`. Issue `docs/上下文/issues/issue13-memory-preference-recall-comfort.md` records the product gap. MemoryWorker now recognizes explicit remember commands, negative preferences, and feedback-style response preferences while still rejecting ordinary chat. Local MemoryWorker tests passed with `4 passed`; local worker/memory/interactions regression passed with `63 passed`; isolated `8166` tests passed with the same counts; temporary `8179` HTTP/Mongo smoke passed with `memory_preference_http_smoke=ok ... cards=1`; temporary `8179` was stopped. Public source was backed up to `~/hackson_backups/memory_comfort_public_20260528112634`, public-directory tests passed with `4 passed` and `63 passed`, and after restarting only `hackson-domain-8145.service`, public `/health` and `HEAD /` returned `200`. A real public user-perspective API audit passed: the new memory card summary was `User explicitly said: 请记住：我做产品时喜欢你直接指出不舒服的点，不要先安慰我。`, and a fresh Companion conversation recalled, `说过，你做产品时希望我直接指出不舒服的点，不要先安慰你。`
- On 2026-05-28, `8165` and public `8145` were updated with Product reader polish and Work Mode model-call resilience. The Product Panel now uses a split `Artifact Navigator + Reader` layout on desktop, clamps generated Artifact titles to a fixed navigation rhythm, keeps `All artifacts` as a normal navigation row, stacks on mobile, and preserves single-Artifact selection. Work Mode now treats `model_response_missing_text` as retryable so a long Delegate/Lead model call pauses retryably instead of hard-failing the Mission, and model-call contexts are normalized through JSON-safe serialization for `datetime`, `date`, set/tuple, and ObjectId-like runtime values. Local verification passed: frontend build, `work_mode_v1_browser_smoke.py` through `scripts/work_mode_v1_run_browser_smoke.py`, Product reader mock UI smoke, and Work Mode action/loop tests with `20` tests. Isolated `8165` verification passed: frontend build, health, Product reader public-bundle UI smoke against `http://127.0.0.1:8165`, and restart cleanup with no orphan `codex exec` process. Public-directory verification passed before restart with Work Mode action/context/loop `22` tests and frontend build. After restarting `hackson-domain-8145.service`, local `/health` returned `{"status":"ok"}`, cloudflared stayed active, root HTML served `/assets/index-ESYnQodx.js` and `/assets/index-ByttZ1zW.css`, and public Product reader UI smoke passed against `https://hackson.catachess.com/` with desktop/mobile screenshots in `/tmp/hackson_public_product_reader*.png`. The Product reader smoke uses API mocks and does not trigger real model execution; concurrent public Work Missions may still show active `codex exec` children while they are running.
- On 2026-05-28, local and isolated `8166` were updated with detailed editable default Agent Origin Stories for Nora and Vale. New users seed non-empty English Nora/Vale stories; empty Agent stories and the old demo placeholders normalize to the new defaults; user-authored Agent stories are preserved. This was not promoted to public `8145` in this pass. Local verification passed with Agent/User tests (`9` tests), User route/Agent tests (`10` tests), and frontend build. Isolated `8166` verification passed with Agent catalog tests (`5` tests), direct default/legacy/custom story checks (`agent_origin_story_target_check=ok`), and frontend build serving `/assets/index-Bb_Fx5DE.js` and `/assets/index-DTBHuMeq.css`.
- On 2026-05-28, `8165` and public `8145` were updated with Work Mode completed-Mission follow-up and bounded Requirement Grill guidance. Completed Missions now expose a separate Continue path instead of replaying the original Start action. `POST /api/work/missions/{missionId}/follow-up` records `USER_FOLLOWUP_REQUESTED`, creates a new `running` Run with `metadata.resumeReason=user_followup`, preserves existing Product/Artifact lineage, and launches the same daemon worker. Lead context now includes `latestUserFollowUp` and `requirementGrill` guidance so the model can ask focused `ask_user` questions when missing requirements materially change the deliverable, while respecting autonomy language such as `随你` and `题材自定`. Local Work Mode tests passed with `98` tests and frontend build passed. Isolated `8165` verification passed with Work Mode `98` tests through `unittest` and frontend build. Public source was backed up to `~/hackson_backups/work_followup_public_20260528101743`; public-directory Work Mode `98` tests and frontend build passed before restart. After restarting `hackson-domain-8145.service`, local and public `/health` returned `{"status":"ok"}`, root served `/assets/index-OVTNRPWP.js` and `/assets/index-QOvacDKh.css`, public API smoke verified completed Start returns `409 mission_followup_required`, `/follow-up` returns `200 running user_followup`, lineage remains `1 Product / 1 Artifact`, and the worker launcher fires exactly once. Public UI smoke with mocked APIs verified completed `Start` is disabled, the Continue form accepts input, submits `/follow-up` once, and updates the Mission to `running`; screenshot `/tmp/work_followup_public_ui_smoke.png`.
- On 2026-05-28, `8165` and public `8145` were updated with Work Mode V1.0.6 evaluator tool and research/paper gates. The Lead toolbox now includes backend-owned `evaluate_product`; it persists a Reliability Report Artifact, emits `RELIABILITY_REPORTED`, returns score/status/top issues/recommended next tool, and never edits Product content. Research/paper-like Missions now reject outline-only completion with `final_paper_draft_required`, require a current Reliability Report after the latest Product update with `reliability_evaluation_required`, and block finish on actionable Reliability issues with `reliability_evaluation_needs_review`. Evaluator `research_reliability_v1` now caps no-evidence reports at `needs_human_review` and checks Chinese paper final-draft shape. Reliability UI now shows Evidence Ledger status, suggested fixes, sources, and limitations instead of only score/issues. Local verification passed with Work Mode `105` tests and frontend build. Isolated `8165` verification passed with `45` targeted Work Mode unittest tests, frontend build, and in-process paper gate smoke. Public source was backed up to `~/hackson_domain_8145_backups/evaluator_tool_20260528_110453`; public-directory `45` targeted Work Mode unittest tests and frontend build passed before restart. After restarting `hackson-domain-8145.service`, local and public `/health` returned `{"status":"ok"}`, public root served `/assets/index-Cy-unphL.js` and `/assets/index-Dx_ve1gX.css`, public in-process paper gate smoke passed with `needs_human_review web_search`, logs showed no traceback/500 after deployment, and active-like public Work Missions were `0`.
- On 2026-05-28, `8165` and public `8145` were updated with Evaluator V1 contract closure. Evaluator now supports `mode=live|replay`, emits `EVALUATION_STARTED`, `RELIABILITY_REPORTED`, and `EVALUATION_FAILED`, includes report `mode`, severity and type `issueCounts`, first-class `toolFailures`, source-backed Research Artifact evidence, and richer Reliability UI fields for requirement evidence, claim reason, best source, tool failures, and Progress details. Local verification passed with Work Mode `110` tests, Work Mode + static frontend `114` tests, and frontend build assets `/assets/index-CHVyLRVQ.js` and `/assets/index-Cg9l671U.css`. Isolated `8165` verification passed with `45` targeted Work Mode unittest tests, frontend build, and database smoke for live report, replay fixture evidence, and paper outline gate. Public source was backed up to `~/hackson_domain_8145_backups/evaluator_contract_20260528_113131`; public-directory `45` targeted Work Mode unittest tests and frontend build passed before restart. After restarting `hackson-domain-8145.service`, local and public `/health` and `/` returned `200`, public root served `/assets/index-CHVyLRVQ.js` and `/assets/index-Cg9l671U.css`, public database smoke passed for live evaluator contract, replay evaluator contract, and `final_paper_draft_required`; smoke-created running Mission was stopped, active-like public Work Missions returned to `0`, and logs showed no traceback/500/error after deployment.
- On 2026-05-28, `8165` and public `8145` were updated with Reliability latest-report history, root-cause-aware no-evidence scoring, tolerant Discussion ingestion, and actionable Lead schema feedback. Public log/database audit identified Mission `6a1873a07930f43553a9031a`: repeated Reliability reports needed current-report selection by latest `RELIABILITY_REPORTED.reportArtifactId`; `discussion_result_invalid` and later `tool_action_schema_invalid` lacked enough feedback for model self-repair. Local verification passed with Work Mode + static frontend `117` tests and frontend build assets `/assets/index-DbtH62Wt.js` and `/assets/index-BcipKgl8.css`. Isolated `8165` verification passed with Work Mode `113` unittest tests and frontend build assets `/assets/index-BeGxqY3P.js` and `/assets/index-BcipKgl8.css`. Public source was backed up to `~/hackson_domain_8145_backups/reliability_discussion_20260528_141150`; public-directory Work Mode `113` unittest tests and frontend build passed before restart. After waiting for blocking running Missions and running Windows to reach `0`, `hackson-domain-8145.service` was restarted. Local and public `/health` plus public `/` returned `200`, public root served `/assets/index-2mQJ4BnJ.js` and `/assets/index-CFlhTWvI.css`, services `hackson-domain-8145.service` and `hackson-cloudflared.service` were active, and post-restart logs showed no traceback, 500, `discussion_result_invalid`, or `tool_action_schema_invalid` errors.
- Non-Hackson services on the target machine were not touched.
- Do not restart old smoke ports for normal product use. Use the public domain service for verification unless a new isolated smoke port is explicitly needed.

## verified API shapes
Public Work, AgentLens, Context Runtime, and Desktop Pet handoff rows below were verified against `https://hackson.catachess.com/` on 2026-05-28. Context Runtime was first verified on isolated `127.0.0.1:8166`, then promoted to public `8145`.

Model-backed public rows were additionally verified on the target machine against `http://127.0.0.1:8145` on 2026-05-27 after configuring `HACKSON_MODEL_PROVIDER=codex_cli`; the smoke confirmed assistant metadata `provider=codex_cli`, `modelName=gpt-5.4`, `idle_quality_v1`, and `companion_join_quality_v1`.

| Method | API | Auth | Module | Purpose |
| --- | --- | --- | --- | --- |
| GET | `/health` | No | `backend/main.py` | Backend health check |
| GET | `/` | No | `backend/main.py` | React frontend HTML |
| GET | `/assets/{asset}` | No | `backend/main.py` | Built frontend assets |
| POST | `/api/users/register` | No | `backend/users/` | Register user and return JWT |
| POST | `/api/users/login` | No | `backend/users/` | Login by email or username |
| GET | `/api/users/me` | Bearer JWT | `backend/users/` | Read current user and the two editable Agent profiles |
| PATCH | `/api/users/me` | Bearer JWT | `backend/users/` | Update current user settings and Agent profiles |
| POST | `/api/users/desktop-handoff` | Bearer JWT | `backend/users/` | Public Desktop Pet V0.8.2 handoff bind; browser login binds a short-lived desktop code to the current user. Verified on public `8145` on 2026-05-28. |
| POST | `/api/users/desktop-handoff/claim` | No | `backend/users/` | Public Desktop Pet V0.8.2 handoff claim; desktop polls with a one-time code and receives a JWT after browser bind. Verified on public `8145` on 2026-05-28. |
| GET | `/api/users/me/prompt-logs` | Bearer JWT | `backend/users/`, `backend/context/` | List the current user's retained full prompt logs for Context Runtime debugging |
| DELETE | `/api/users/me/prompt-logs` | Bearer JWT | `backend/users/`, `backend/context/` | Delete retained full prompt text while keeping context package metadata |
| GET | `/api/memory/me` | Bearer JWT | `backend/memory/` | List current-user non-deleted memory cards for Me controls |
| PATCH | `/api/memory/me/{memoryId}` | Bearer JWT | `backend/memory/` | Set a memory card `status` to `active`, `disabled`, or `archived` |
| DELETE | `/api/memory/me/{memoryId}` | Bearer JWT | `backend/memory/` | Soft-delete a memory card so it leaves UI and context reads |
| GET | `/api/agents` | No | `backend/agents/` | Return baseline Agent display profiles; authenticated UI prefers the current user's editable profiles from `/api/users/me` |
| POST | `/api/conversations` | Bearer JWT | `backend/conversations/` | Create an idle, companion, or work conversation container |
| GET | `/api/conversations` | Bearer JWT | `backend/conversations/` | List current-user conversations by mode/status |
| GET | `/api/conversations/{conversationId}/messages` | Bearer JWT | `backend/conversations/` | Page messages in one owned conversation |
| GET | `/api/idle/conversation` | Bearer JWT | `backend/conversations/` | Get or create the active idle conversation |
| POST | `/api/idle/{conversationId}/tick` | Bearer JWT | `backend/interactions/` | Generate one idle Agent reply |
| POST | `/api/idle/{conversationId}/messages` | Bearer JWT | `backend/interactions/` | Add a visible user line to idle and generate the next Agent reply; accepts optional `idempotencyKey` for queued/interrupted turns |
| POST | `/api/idle/{conversationId}/join` | Bearer JWT | `backend/interactions/` | Create a `companion_1` child from idle and reply |
| POST | `/api/companion/{conversationId}/messages` | Bearer JWT | `backend/interactions/` | Continue a companion conversation |
| POST | `/api/tasks` | Bearer JWT | `backend/tasks/` | Create the legacy minimal Work task and its conversation |
| GET | `/api/tasks` | Bearer JWT | `backend/tasks/` | List current-user legacy Work tasks |
| POST | `/api/tasks/{taskId}/messages` | Bearer JWT | `backend/tasks/`, `backend/interactions/` | Send a legacy task message and get an Agent reply |
| POST | `/api/work/projects` | Bearer JWT | `backend/work_mode/` | Create a Work project by name |
| GET | `/api/work/projects` | Bearer JWT | `backend/work_mode/` | List current-user Work projects |
| POST | `/api/work/missions` | Bearer JWT | `backend/work_mode/` | Create a Mission with `agent_1` or `agent_2` as lead |
| GET | `/api/work/projects/{projectId}/missions` | Bearer JWT | `backend/work_mode/` | List Missions in one Project |
| GET | `/api/work/missions/{missionId}` | Bearer JWT | `backend/work_mode/` | Read Mission detail, current event timeline, persisted Products, Work Windows, and Artifacts |
| POST | `/api/work/missions/{missionId}/start` | Bearer JWT | `backend/work_mode/` | Start or resume the public V1.0.5 model-driven tool loop through the daemon launcher, with visible progress, Product/Artifact lineage, review/discussion tools, controlled `web_search`, deterministic long-novel final quality gates, and restart recovery for interrupted runs |
| POST | `/api/work/missions/{missionId}/answer` | Bearer JWT | `backend/work_mode/` | Submit the user's answer while a Mission is `waiting_input`; records `USER_INPUT_RECEIVED`, resumes the Mission, and launches the model loop |
| POST | `/api/work/missions/{missionId}/follow-up` | Bearer JWT | `backend/work_mode/` | Continue a `completed` Mission with a new user request; records `USER_FOLLOWUP_REQUESTED`, creates a new `running` Run with `resumeReason=user_followup`, preserves prior Products/Artifacts, and launches the model loop |
| POST | `/api/work/missions/{missionId}/evaluate` | Bearer JWT | `backend/work_mode/` | Public AgentLens evaluator; request accepts `{"profile":"research_reliability_v1","mode":"live|replay"}`; reads Mission trace, persists a Reliability Report artifact with `mode`, `issueCounts`, `toolFailures`, evidence, requirements, claims, and limitations, and records `EVALUATION_STARTED` plus `RELIABILITY_REPORTED` or `EVALUATION_FAILED` |
| GET | `/api/work/missions/{missionId}/events` | Bearer JWT | `backend/work_mode/` | Poll Mission events after `afterSequence` |
| GET | `/api/work/missions/{missionId}/events/stream` | Bearer JWT | `backend/work_mode/` | SSE stream for persisted public Mission events after `afterSequence`; emits `work_event` and `ping`, preserves `/events` polling fallback, and does not stream model tokens or hidden reasoning |

## request notes

### Auth headers
Authenticated requests require:

```http
Authorization: Bearer <jwt>
Content-Type: application/json
```

### User registration
```http
POST /api/users/register
```

```json
{
  "username": "demo",
  "email": "demo@example.com",
  "password": "password-with-length"
}
```

Returns a JWT plus the current user object.

New users default `fullPromptLoggingOn` to `true`.

New users default `backgroundIdleOn` to `false`.

### Full Prompt Logging
```http
PATCH /api/users/me
```

```json
{
  "fullPromptLoggingOn": false
}
```

When enabled, future model-backed turns persist full model-visible prompt text for 30 days in `context_packages`. Context package metadata, source ids, prompt hash, and token estimate persist even when this setting is off.

```http
GET /api/users/me/prompt-logs
```

Returns retained prompt logs for the current user:

```json
{
  "promptLogs": [
    {
      "id": "<context-package-id>",
      "conversationId": "<conversation-id>",
      "mode": "idle",
      "targetAgentId": "agent_1",
      "promptHash": "<sha256>",
      "tokenEstimate": 1234,
      "fullPromptText": "system:\\n...",
      "fullPromptTextExpiresAt": "2026-06-27T00:00:00Z",
      "createdAt": "2026-05-28T00:00:00Z"
    }
  ]
}
```

```http
DELETE /api/users/me/prompt-logs
```

```json
{
  "deletedPromptLogs": 1
}
```

This clears retained full prompt text only. Historical prompt text is not editable.

### Desktop Pet handoff
```http
POST /api/users/desktop-handoff
Authorization: Bearer <jwt>
```

```json
{
  "code": "desktop-code-from-pet"
}
```

Returns:

```json
{
  "status": "linked"
}
```

```http
POST /api/users/desktop-handoff/claim
```

```json
{
  "code": "desktop-code-from-pet"
}
```

Pending response:

```json
{
  "status": "pending",
  "accessToken": null,
  "tokenType": null,
  "user": null
}
```

Authorized response returns `status="authorized"`, `accessToken`, `tokenType`, and `user`. Codes are short-lived and one-time.


### Memory controls
```http
GET /api/memory/me
```

Returns non-deleted memory cards owned by the current user:

```json
{
  "memoryCards": [
    {
      "id": "<memory-id>",
      "scope": "companion",
      "ownerType": "user",
      "ownerId": "<user-id>",
      "memoryType": "preference",
      "summary": "User prefers concise Chinese replies.",
      "sourceMessageIds": ["<message-id>"],
      "importanceScore": 0.8,
      "confidence": 0.9,
      "status": "active",
      "metadata": {},
      "createdAt": "2026-05-28T00:00:00Z",
      "updatedAt": "2026-05-28T00:00:00Z"
    }
  ]
}
```

```http
PATCH /api/memory/me/{memoryId}
```

```json
{
  "status": "disabled"
}
```

Allowed status updates are `active`, `disabled`, and `archived`. Disabled or deleted memory cards are excluded from context package memory reads.

```http
DELETE /api/memory/me/{memoryId}
```

```json
{
  "deletedMemoryCard": true
}
```

### Background Idle Setting
```http
PATCH /api/users/me
```

```json
{
  "backgroundIdleOn": true
}
```

This setting is the user permission for future server-owned idle cadence. It defaults to `false`. Current isolated `8166` smoke verifies storage, cadence gating, and Me UI; it does not run a browser-closed background worker.

### Agent profile update
```http
PATCH /api/users/me
```

```json
{
  "agentProfiles": [
    {
      "slot": "agent_1",
      "name": "Plotter",
      "role": "outline lead",
      "personality": "Structured and concise.",
      "story": "Experienced in planning long-form fiction."
    },
    {
      "slot": "agent_2",
      "name": "Drafter",
      "role": "scene writer",
      "personality": "Concrete and image-driven.",
      "story": "Experienced in drafting readable scenes."
    }
  ]
}
```

### Idle topic
```http
POST /api/conversations
```

```json
{
  "mode": "idle",
  "title": "Novel outline",
  "metadata": {
    "topicDirection": "Plan the story before drafting."
  }
}
```

### Idle tick
```http
POST /api/idle/{conversationId}/tick
```

```json
{
  "targetAgentId": "agent_1",
  "discussionDirection": "Stay focused on chapter planning.",
  "idleSeed": "Continue naturally.",
  "idempotencyKey": "client-turn-uuid"
}
```

`idempotencyKey` protects retries for the same transcript. A completed retry returns the same Agent message/context response; a concurrent different key returns `423 idle_turn_locked`.

### Idle user line
```http
POST /api/idle/{conversationId}/messages
```

```json
{
  "content": "Make the protagonist older and more tired.",
  "discussionDirection": "Respond to the user's latest line.",
  "idempotencyKey": "idle-say-client-turn-uuid"
}
```

Returns both the saved user message and the generated Agent message. The frontend may call this after a currently running idle tick finishes when the user typed during `Working`.

`idempotencyKey` protects retries for queued user lines. A completed retry returns the same saved user message, Agent message, and context response; a concurrent different key on the same transcript returns `423 idle_turn_locked`.

### Work project
```http
POST /api/work/projects
```

```json
{
  "name": "Novel"
}
```

`repoPath` is optional internal compatibility metadata. The current UI does not ask the user for it.

### Work mission
```http
POST /api/work/missions
```

```json
{
  "projectId": "<project-id>",
  "title": "Draft chapter plan",
  "goal": "Create a practical outline before writing.",
  "leadEmployeeId": "agent_1"
}
```

Current product flow uses the user's two Agent profiles as Mission leads. Legacy Employee and Project Team endpoints still exist in code for backward compatibility but are not part of the current verified public UI.

### Start mission
```http
POST /api/work/missions/{missionId}/start
```

```json
{}
```

The current V1.0.5 worker emits a model-selected tool timeline. Common events include:

```text
MISSION_CREATED
MISSION_STARTED
MODEL_TURN_STARTED
MODEL_TURN_COMPLETED
MODEL_TURN_INVALID
TOOL_CALLED
MISSION_PLAN_UPDATED
PRODUCT_UPDATED
WORK_WINDOW_OPENED
WORK_WINDOW_COMPLETED
REVIEW_COMPLETED
DISCUSSION_COMPLETED
WEB_SEARCH_COMPLETED
WEB_SEARCH_FAILED
USER_INPUT_REQUESTED
USER_INPUT_RECEIVED
MISSION_COMPLETED
```

Poll with:

```http
GET /api/work/missions/{missionId}/events?afterSequence=<last-sequence>
```

Read persisted output from:

```http
GET /api/work/missions/{missionId}
```

Mission detail returns the current timeline, products, work windows, and artifacts. `artifacts` is sorted newest first:

```json
{
  "artifacts": [
    {
      "id": "<artifact-id>",
      "missionId": "<mission-id>",
      "runId": "<run-id>",
      "kind": "text",
      "title": "Draft chapter plan",
      "content": "Full artifact text",
      "createdByEmployee": {
        "id": "agent_1",
        "name": "Nora",
        "role": "precise"
      },
      "metadata": {
        "runner": "model_runtime",
        "modelName": "gpt-5.4",
        "provider": "codex_cli"
      },
      "createdAt": "2026-05-27T18:00:00Z"
    }
  ]
}
```

`PRODUCT_UPDATED` carries bounded metadata and references the persisted Artifact. Full Artifact content is read from Mission detail, not duplicated into every event payload.

`web_search` is not an HTTP endpoint. It is a controlled internal Work tool selected by the Lead model through the V1 tool protocol. The backend executes the provider call, persists `WEB_SEARCH_COMPLETED` or `WEB_SEARCH_FAILED`, and returns bounded source observations to the next model turn. Search results are informational only; visible deliverables must still be written through `work_product`.

### Evaluate mission
```http
POST /api/work/missions/{missionId}/evaluate
```

```json
{
  "profile": "research_reliability_v1",
  "mode": "live"
}
```

Returns Mission detail after writing a `report` Artifact with `metadata.artifactRole="reliability_report"` and `metadata.reportPayload`. The evaluator only treats trace evidence, especially `WEB_SEARCH_COMPLETED` snippets, as evidence; final answer text cannot support itself.

## latest verification
- AgentLens evaluator local verification on 2026-05-28:
  - Work Mode evaluator and route tests passed with `PYTHONPATH=backend .venv/bin/python -m pytest backend/work_mode/tests/test_work_mode_evaluator.py backend/work_mode/tests/test_work_mode_routes.py -q`.
  - Full local Work Mode suite passed with `77` tests.
  - Frontend `npm run build` passed after adding the Reliability panel.
  - Local HTTP smoke passed with `/api/work/missions/{missionId}/evaluate`, a Reliability Report artifact, `RELIABILITY_REPORTED`, `reliability_score=80`, and `reliability_status=minor_review`.
  - Local browser smoke passed on isolated ports `9127` and `5127`, including the `Check` action, Reliability panel, desktop screenshot, mobile screenshot, and no mobile horizontal overflow.
- AgentLens public verification on 2026-05-28:
  - Target public Work Mode tests passed with `77` tests; targeted evaluator/route tests passed with `12` tests.
  - Target frontend build passed with `/assets/index-n_-ZPKaU.js` and `/assets/index-CHTMdui3.css`.
  - Target HTTP smoke passed with `reliability_score=80` and `reliability_status=minor_review`.
  - Public `/health`, root HTML, and assets passed after restarting only `hackson-domain-8145.service`.
  - Public AgentLens API smoke passed against `https://hackson.catachess.com` with seeded trace Mission `6a17e448abb7d1b24cd60d53`, score `26`, status `unsafe_to_ship`, and expected issue taxonomy.
  - Public AgentLens UI smoke passed and saved `scripts/artifacts/work_mode_agentlens_public_ui_smoke.png`.
- Local backend tests passed before deployment:
  - `backend/interactions/tests`: 18 tests.
  - `backend/work_mode/tests`: 14 tests.
- Local frontend build passed before deployment.
- Context Runtime V1.0 local verification on 2026-05-28:
  - `backend/agents/tests`, `context`, `conversations`, `diary`, `interactions`, `memory`, `model_runtime`, `orchestration`, `summaries`, `tasks`, `backend/tests`, `users`, `workers`, and `work_mode` all passed through per-directory unittest discovery.
  - Context Runtime scoped checks passed after Loops 6-8: context/users/memory/interactions/workers `66` tests.
  - Deterministic eval gate passed: `context_runtime_eval=ok cases=4`.
  - Frontend `npm run build` passed with assets `/assets/index-D8Rq9q5i.js` and `/assets/index-dKibUoIc.css`.
  - Verified `GET /api/users/me/prompt-logs` and `DELETE /api/users/me/prompt-logs` with FastAPI route tests; verified context package persistence and `context_package_id` message linkage through service tests.
- Context Runtime V1.0 isolated target verification on active `8166`:
  - Target source: `~/hackson_context_runtime_8166`.
  - Target services: `hackson-context-runtime-8166.service` on `127.0.0.1:8166` and `hackson-context-runtime-fake-model-18166.service` on `127.0.0.1:18166`.
  - Target database: `hackson_context_runtime_8166`.
  - Target scoped tests passed after Loops 6-8: context/users/memory/interactions/workers `66` tests.
  - Target deterministic eval gate passed: `context_runtime_eval=ok cases=4`.
  - Target frontend build passed with Node `20.19.6`, assets `/assets/index-D8Rq9q5i.js` and `/assets/index-dKibUoIc.css`.
  - Target HTTP smoke passed with `idempotent_retry=ok background_gate=ok memory_controls=ok worker_processed=14 persisted_summary=6a17d1f9acac0d98f3d0a95c`: register returned `fullPromptLoggingOn=true` and `backgroundIdleOn=false`; first idle tick created a context package with full prompt text; retrying the same `idempotencyKey` returned the same Agent message and context package; `GET /api/users/me/prompt-logs` returned the retained prompt text; `PATCH /api/users/me` disabled Full Prompt Logging and separately saved `backgroundIdleOn=true`; second idle tick created metadata without full prompt text; `DELETE /api/users/me/prompt-logs` cleared retained text while keeping all package records; Background Idle gate blocked disabled state, allowed enabled state, then recorded one turn and exhausted the smoke budget; worker runner persisted summaries, memory, and diary entries; memory controls listed, disabled, re-enabled, and soft-deleted one memory; a later long-history idle tick used a persisted session summary instead of a compact summary.
  - Target Mongo worker smoke after latest run: context packages `38`, summaries `37`, memory cards `17`, failed jobs `0`.
  - Target Mongo smoke verified `idle_runner_state` persisted `budget_day='2026-05-28'` and `daily_turns=1`.
  - Target Mongo smoke verified `idle_turn_locks` completed rows include response snapshots and that failed lock rows do not prevent later retry after the fix.
  - Target static React check passed through the active service build with JS `/assets/index-D8Rq9q5i.js` and CSS `/assets/index-dKibUoIc.css`.
  - Browser smoke through local SSH tunnel verified Me `Prompt log` default-on control, `Background` default-off control, `Logs/Delete` controls, `Memory` panel rendering, zero API failures, and no horizontal overflow. Screenshots: `scripts/artifacts/context_runtime_me_smoke.png`, `scripts/artifacts/context_runtime_me_background_smoke.png`, `scripts/artifacts/context_runtime_me_memory_smoke.png`.
  - Existing public `8145`, Idle Auto `8147`, Work services `8148/8150/8160/8161/8162/8163/8164/8165`, fake relay `18148`, and legacy `8130` were not stopped.
- Context Runtime V1.6 idle interruption and human-dialogue verification on 2026-05-28:
  - Local scoped backend tests passed: `69 passed` across context, users, memory, interactions, and workers.
  - Local deterministic eval passed: `context_runtime_eval=ok cases=4`, including `Relationship stance`, `Turn intent`, previous-line response, one-move guidance, and anti-checklist assertions.
  - Local frontend build passed with `/assets/index-n_-ZPKaU.js` and `/assets/index-CHTMdui3.css`; isolated target `8166` build served `/assets/index-ZUSjv_K4.js` and `/assets/index-CwEAac1R.css`.
  - Local browser smoke passed on isolated ports `18266` and `5273`: Idle `Say` remained enabled during `Working`, queued user text rendered immediately, and the queued line was sent after the active turn finished.
  - Isolated target `8166` verification passed with `69` backend tests, `context_runtime_eval=ok cases=4`, frontend build, HTTP/Mongo smoke, Me browser smoke, and Idle interruption browser smoke through an SSH tunnel.
  - Public-directory verification passed before restart: Context Runtime `69` tests; Work Mode/model_runtime `97` tests; deterministic context eval; `work_mode_v1_full_smoke`; `work_mode_v1_http_smoke`; `work_mode_waiting_input_http_smoke`; frontend build.
  - Public post-restart verification passed: `hackson-domain-8145.service` and `hackson-cloudflared.service` active; local and public `/health` returned `{"status":"ok"}`; root HTML referenced `/assets/index-n_-ZPKaU.js` and `/assets/index-CHTMdui3.css`; both assets returned `200`.
  - Public model-backed Context Runtime smoke passed with `context_runtime_http_smoke=ok user=6a17e449abb7d1b24cd60d58 conversation=6a17e44aabb7d1b24cd60d59 packages=5 first=6a17e44aabb7d1b24cd60d5c second=6a17e44fabb7d1b24cd60d6b idempotent_retry=ok background_gate=ok memory_controls=ok worker_processed=26 persisted_summary=6a17e45e7740f84d83d99a5a`.
- Public browser smokes passed: Idle interruption screenshot `scripts/artifacts/idle_interruption_public_recheck.png`; Me prompt-log/background defaults screenshot `scripts/artifacts/context_runtime_me_public_recheck.png`.
- Context Runtime Me IA and derived freshness verification on 2026-05-28:
  - Local backend tests passed with `218 passed`; local frontend build passed with `/assets/index-575GUaz8.js` and `/assets/index-DTBHuMeq.css`.
  - Local Me browser smoke passed with screenshot `scripts/artifacts/context_runtime_me_ia_local_v5.png`, verifying Account + Agent editors in the first viewport and Debug collapsed by default.
  - Isolated `8166` backend tests passed with `195 passed`; `8166` frontend build passed with `/assets/index-DNrmBHyi.js` and `/assets/index-DTBHuMeq.css`.
  - `8166` HTTP smoke passed with `context_runtime_http_smoke=ok user=6a184109f8a8fcf2755c4d7c conversation=6a184109f8a8fcf2755c4d7d packages=5 first=6a184109f8a8fcf2755c4d80 second=6a184109f8a8fcf2755c4d87 idempotent_retry=ok background_gate=ok memory_controls=ok worker_processed=11 persisted_summary=6a1841095ddfc615b4d0da52`.
  - `8166` Me browser smoke passed with screenshot `scripts/artifacts/context_runtime_me_ia_8166_v2.png`.
  - Public-directory backend tests passed with `216 passed`; public build passed with `/assets/index-CG4wOHJC.js` and `/assets/index-DTBHuMeq.css`.
  - Final public HTTP smoke passed with `context_runtime_http_smoke=ok user=6a184109a816f35aa141e653 conversation=6a184109a816f35aa141e654 packages=5 first=6a184109a816f35aa141e657 second=6a18410fa816f35aa141e665 idempotent_retry=ok background_gate=ok memory_controls=ok worker_processed=2 persisted_summary=6a184117a816f35aa141e679`.
  - Final public Mongo check for that smoke user showed `pending=0`, `summaries=5`, `diaries=4`, and content-derived idle relationship memories rather than the old generic sentence.
  - Final public Me browser smoke passed with screenshot `scripts/artifacts/context_runtime_me_ia_public_v3.png`.
- Target backend tests passed under `~/hackson_domain_8145/backend`.
- Target frontend build passed with Node `20.19.6`; the public asset at that deployment was `/assets/index-DGOMmalo.js`.
- `hackson-domain-8145.service` was restarted and returned `{"status":"ok"}` on `127.0.0.1:8145/health`.
- Public API smoke verified auth, Agent profile update, Project creation, Mission creation, Mission start, and Mission events.
- Public Work Console static-only update on 2026-05-27:
  - Public `frontend/dist` was backed up on the target, then replaced without restarting `hackson-domain-8145.service`.
  - Latest public assets verified as `/assets/index-O85af_uy.js` and `/assets/index-BNnrJWzs.css`.
  - Browser smoke verified a completed Work Mission renders Progress, Summary, and Product as separate vertical cards; Summary overlaps `0` Progress rows; completed `Start` is disabled; failed resource count is `0`.
  - Screenshot: `/tmp/hackson_work_public_final.png`.
- Model-backed Idle/Companion routes can currently return `429 {"detail":"model_rate_limited"}` when the upstream model provider is rate-limited; this is a stable API response, not a backend crash.
- Idle Auto smoke verification on `8147`:
  - Target scoped tests passed: `40 passed, 4 warnings`.
  - API smoke confirmed provider `429` returns `{"detail":"model_rate_limited"}` and a failed idle tick leaves `0` messages.
  - Local UI path `5187 -> 18147 -> 8147` verified topic creation during rate limit shows `Model busy`, keeps `Auto` off, and makes no extra tick requests after failure.
  - Screenshot: `/tmp/hackson_idle_auto_model_busy_ui.png`.
- Orchestrator V1 target smoke verification on temporary `8148`:
  - Target scoped tests passed under `~/hackson_orchestrator_v1_8148/backend`: orchestration `5`, model_runtime `17`, interactions `21`.
  - Real provider smoke confirmed model-backed idle routes can still return stable `429 {"detail":"model_rate_limited"}`.
  - Fake OpenAI-compatible relay on temporary `18148` verified Responses-mode success path for register, idle tick, idle say, idle join, companion_1 follow-up, and companion_2 message.
  - Verified assistant message metadata contains `orchestration_policy`, `reasoning_effort`, `tool_policy`, `provider`, `provider_response_id`, and `reasoning_summary`.
- Work V0.5 isolated smoke verification on active `8148`:
  - Local Work tests passed: `16` tests.
  - Local model_runtime/interactions regression passed: `38` tests.
  - Local frontend build passed with assets `/assets/index-BQ4JHagk.js` and `/assets/index-C-nEjYQU.css`.
  - Target Work tests passed under `~/hackson_work_v05_8148/backend`: `16` tests.
  - Target frontend build passed with Node `20.19.6`.
  - Target success smoke on `127.0.0.1:8148` verified register, Project create, Mission create, Start, `MISSION_COMPLETED`, one persisted text Artifact, and `PRODUCT_UPDATED` without full `content` payload.
  - Target failure smoke on temporary `8149` verified model network failure produces `MISSION_FAILED`, `artifactCount: 0`, and no fake Product result; `8149` was stopped and removed after verification.
  - Local UI path `5192 -> 18148 -> 8148` verified Work page creates Project/Mission and renders the persisted Artifact in Product with failed resource count `0`.
  - Screenshot: `/tmp/hackson_work_v05_ui.png`.
  - `8148` and `18148` remain active as isolated Work V0.5 smoke services; public `8145`, Idle Auto `8147`, and legacy `8130` were not touched.
- Orchestrator V1 public deployment on `8145`:
  - Local backend full module unittest passed and local frontend build passed before deployment.
  - Target public directory tests passed: orchestration `5`, model_runtime `17`, interactions `21`.
  - Target frontend build passed with Node `20.19.6`; public assets remain `/assets/index-O85af_uy.js` and `/assets/index-BNnrJWzs.css`.
  - `hackson-domain-8145.service` was restarted and returned `{"status":"ok"}` on `127.0.0.1:8145/health`.
  - Public domain `https://hackson.catachess.com/health` returned `{"status":"ok"}` and `GET /` returned the React HTML.
  - Public API smoke verified register and conversation creation. Model-backed idle and companion routes returned stable `429 {"detail":"model_rate_limited"}` from the current upstream provider limit, not a backend crash.
  - Public backend code now routes model-backed idle and companion generation through `backend/orchestration/` and stores orchestration metadata when the provider succeeds.
- Work Mode Codex public fix on `8145`:
  - Root cause confirmed: idle and companion already injected `CodexCliClient`; Work Mode runner only built `ModelRuntime` with the OpenAI-compatible client, so `HACKSON_MODEL_PROVIDER=codex_cli` produced `model_codex_cli_unavailable`.
  - Public backend now injects `CodexCliClient` in Work Mode and bounds V0.5 generation to a single first-pass artifact with low reasoning effort.
  - Local tests passed: all backend `*/tests` directories, including Work Mode `18`, model_runtime `23`, and interactions `21`.
  - Target public tests passed under `~/hackson_domain_8145/backend`: Work Mode `18`, model_runtime `23`, interactions `21`.
  - `hackson-domain-8145.service` was restarted and returned `active` plus `{"status":"ok"}` on `127.0.0.1:8145/health`.
  - Target public API smoke on `127.0.0.1:8145` completed Mission `6a17428e1c922129e72e8968` titled `撰写一个8000字小说`; events reached `MISSION_COMPLETED`, one text Artifact was persisted, artifact length was `1055`, and metadata was `{"runner":"model_runtime","modelName":"gpt-5.4","provider":"codex_cli"}`.
- Public browser smoke verified Register/Login, Agent editing, Workspace Project creation, Project detail, Mission creation, Start, completion timeline, desktop screenshot, and mobile screenshot with `0` failed API responses.
- Screenshots:
  - `/tmp/hackson_public_work_agents_desktop.png`
  - `/tmp/hackson_public_work_done_desktop.png`
  - `/tmp/hackson_public_work_mobile.png`
- Work V1 isolated smoke verification on active `8150`:
  - Target source: `~/hackson_work_v1_8150`.
  - Target service: `hackson-work-v1-8150.service`, active on `127.0.0.1:8150`.
  - Target database: `hackson_work_v1_8150`.
  - Target tests passed: Work Mode `46`, model_runtime `24`.
  - Target frontend build passed with Node `20.19.6`, assets `/assets/index-B-RFrSxG.js` and `/assets/index-hERmjtRu.css`.
  - Deterministic full smoke passed on target: `work_mode_v1_full_smoke=ok`, `events=12`, `windows=2`, `products=1`, `artifacts=4`, `final_cjk=9936`.
  - Real Codex-backed HTTP smoke verified `mission_plan` and `work_product` persisted on a real Mission, then a provider timeout produced `paused_retryable` instead of `failed`.
  - Resume smoke verified the same paused Mission can be started again through `POST /api/work/missions/{missionId}/start` and complete; final event sequence included `MISSION_PAUSED_RETRYABLE`, second `MISSION_STARTED`, `MISSION_PLAN_UPDATED`, two `PRODUCT_UPDATED`, `PRODUCT_INSPECTED`, and `MISSION_COMPLETED`.
  - Codex CLI timeout cleanup verified no orphan `codex exec` process remained after timeout.
  - Existing public `8145`, Idle Auto `8147`, Work V0.5 `8148`, fake relay `18148`, and legacy `8130` services were not stopped.
- Work V1 long-turn progress local verification:
  - Added safe non-streaming lifecycle events: `MODEL_TURN_STARTED`, `MODEL_TURN_HEARTBEAT`, `MODEL_TURN_COMPLETED`, `MODEL_TURN_RETRYING`, `MODEL_TURN_INVALID`, `TOOL_CALLED`, and `WORK_WINDOW_FAILED`.
  - Added bounded automatic retry for retryable Lead model errors before `paused_retryable`.
  - Delegate model failures after `WORK_WINDOW_OPENED` now mark the Work Window `failed` and emit `WORK_WINDOW_FAILED` instead of leaving the window running.
  - React Work UI now includes a compact latest-activity strip so long model turns do not look frozen while event polling continues.
  - Local verification passed: all backend test directories, Work Mode `51`, model_runtime `24`, interactions `21`, frontend build, in-process full smoke `final_cjk=9936`, HTTP full smoke `final_cjk=9936`, and browser smoke `windows=2/final_cjk=9936`.
  - After adding env-tunable progress settings, local Work Mode tests passed with `52` tests and all backend test directories passed.
  - Target isolated `8161` verification passed: Work Mode `52`, model_runtime `24`, interactions `21`, frontend build, in-process full smoke `events=30/windows=2/products=1/artifacts=4/final_cjk=9936`, HTTP full smoke `events=30/windows=2/products=1/artifacts=4/final_cjk=9936`, browser smoke `windows=2/final_cjk=9936`, service `active`, `/health` ok, and static React root/assets present.
- Work V1 UI architecture isolated verification on active `8163`:
  - Target source: `~/hackson_work_ui_8163`.
  - Target service: `hackson-work-ui-8163.service`, active on `127.0.0.1:8163`.
  - Target database: `hackson_work_ui_8163`.
  - Target Work Mode tests passed: `55`.
  - Target frontend build passed with Node `20.19.6`, assets `/assets/index-qPU-cMH4.js` and `/assets/index-BbzX_UAM.css`.
  - Target in-process full smoke passed: `events=30/windows=2/products=1/artifacts=4/final_cjk=9936`.
  - Target HTTP full smoke passed: `events=30/windows=2/products=1/artifacts=4/final_cjk=9936`.
  - Target browser smoke passed with desktop and mobile screenshots, verified Work Console order, Artifact lineage, default-collapsed Diagnostics, final CJK count `9936`, and no mobile horizontal overflow.
  - Target `8163` live service health returned `{"status":"ok"}` and static root/assets returned `200`.
- Work V1 UI architecture public static verification on active `8145`:
  - Public `frontend/dist` was backed up to `~/hackson_domain_8145/frontend/dist.backup_work_ui_20260527230937`, then replaced from `~/hackson_work_ui_8163/frontend/dist` without restarting `hackson-domain-8145.service`.
  - Public domain `https://hackson.catachess.com/health` returned `{"status":"ok"}`.
  - Public root and assets verified with browser UA: `/assets/index-qPU-cMH4.js` and `/assets/index-BbzX_UAM.css` returned `200`.
  - Public Playwright static check registered a test user, created a Project and draft Mission without starting the model, and verified Work Console order `activity>windows>product>progress>diagnostics` with Diagnostics collapsed.
  - Screenshot: `scripts/artifacts/work_mode_public_ui_static_check.png`.
- Work V1 Product reader isolated verification on active `8164`:
  - Target source: `~/hackson_work_product_reader_8164`.
  - Target service: `hackson-work-product-reader-8164.service`, active on `127.0.0.1:8164`.
  - Target database: `hackson_work_product_reader_8164`.
  - Target Work Mode tests passed: `55`.
  - Target frontend build passed with Node `20.19.6`, assets `/assets/index-3udE6cD6.js` and `/assets/index-BcI42SsQ.css`.
  - Target in-process full smoke passed: `events=30/windows=2/products=1/artifacts=4/final_cjk=9936`.
  - Target HTTP full smoke passed: `events=30/windows=2/products=1/artifacts=4/final_cjk=9936`.
  - Target browser smoke passed with final Product reader assertions: `All` contains `故事大纲`, `第一章草稿`, `第二章草稿`, and `最终成稿`; single Artifact selection works; returning to `All` works; final Artifact alone remains at least `8000` CJK.
  - Target `8164` live service health returned `{"status":"ok"}` and static root/assets returned `200`.
- Work V1 Product reader public static verification on active `8145`:
  - Public `frontend/dist` was backed up to `~/hackson_domain_8145/frontend/dist.backup_product_reader_20260527233038`, then replaced from `~/hackson_work_product_reader_8164/frontend/dist` without restarting `hackson-domain-8145.service`.
  - Public domain `https://hackson.catachess.com/health` returned `{"status":"ok"}`.
  - Public root and assets verified with browser UA: `/assets/index-3udE6cD6.js` and `/assets/index-BcI42SsQ.css` returned `200`.
  - Public Playwright asset-load check verified the deployed React bundle is `index-3udE6cD6.js`.
