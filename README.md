## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

## intro
- **Product:** Hackson is an AI work operating system built around two persistent, user-editable Agents, not a one-off chatbot thread.
- **Public demo:** The current public build runs at `https://hackson.catachess.com/` on the target server, backed by FastAPI, React + Vite, MongoDB, systemd services, and a Cloudflare tunnel.
- **Agent profiles:** Each user owns two editable Agent profiles with names, personalities, voices, stories, and account-level continuity. The same Agents appear across Idle, Companion, Work, memory, and Desktop Pet flows.
- **Idle Mode:** Two Agents can hold an ongoing topic-driven conversation. Users can start topics, let the Agents continue, interrupt while a turn is generating, and join the discussion without corrupting transcript order.
- **Companion Mode:** Users can either branch from Idle into a context-aware companion conversation or start a direct companion chat for a focused user-Agent exchange.
- **Context Runtime:** Every model-backed turn is built from an auditable context package with source ids, prompt hash, token budget notes, Agent identity, recent messages, summaries, governed memory, and optional full prompt logging controlled by the user.
- **Memory and continuity:** Hackson stores evidence-backed memory cards for explicit user preferences and facts. Users can view, disable, or delete memory, while raw messages remain the source of truth.
- **Derived workers:** Background workers generate summaries, memory candidates, diary entries, and relationship summaries without blocking the main user interaction path.
- **Work Mode:** Users create Projects and Missions. A selected Lead Agent drives each Mission through validated tools, visible events, Work Windows, Product/Artifact lineage, user questions, follow-up runs, and restart-safe execution.
- **Product lineage:** Work deliverables are stored as Products with immutable Artifacts such as outlines, drafts, chapters, revisions, reviews, reports, and final outputs. The UI provides a reader-oriented Artifact Navigator instead of burying final work in logs.
- **Agent collaboration:** The Lead Agent can delegate scoped work to the other Agent, discuss/review deliverables, inspect prior Artifacts, ask the user for missing requirements, and continue completed Missions without overwriting history.
- **Research support:** Work Mode includes a controlled backend `web_search` tool with visible source links. It is read-only and bounded; it is not browser automation or arbitrary computer control.
- **AgentLens Evaluator:** Hackson can evaluate research Missions with a Reliability Report that checks requirement coverage, evidence support, missing sources, hallucinated entities, ignored tool failures, and incomplete deliverables. Reports include score, status, issue taxonomy, tool failures, evidence, limitations, and suggested fixes.
- **Desktop Pet:** A Tauri + React Desktop Pet connects to the same account and reflects Work Mode status as a lightweight desktop presence. It is a read-only progress companion, not an independent executor.
- **Verified engineering surface:** The project includes documented API contracts, target-server deployment records, route-level tests, unit tests, smoke scripts, browser checks, public health checks, and explicit production service mapping.
- **Documented roadmap:** Planned directions include native tool-calling adapters, parallel Work Windows, controlled Codex/code execution with diff/test/approval gates, richer evaluator profiles, citation alignment, repair loops, desktop tray/notifications, and project-level reliability operations.

## advantage
- **Clear differentiation from chatbots:** Hackson models AI work as persistent Projects, Missions, Products, Artifacts, memory, and reliability reports rather than as disposable chat transcripts.
- **Trust is a first-class product surface:** The Evaluator Runtime does not claim to prove truth. It objectively flags reliability risk from visible trace, sources, tool failures, and requirement coverage, which makes failures inspectable instead of hidden.
- **Auditable context, not prompt magic:** Context packages make model inputs reproducible and debuggable through prompt hashes, source ids, budget decisions, retained prompt logs, and user-controlled deletion.
- **Long-task supervision:** Work Mode supports progress visibility, retryable pauses, waiting-input flows, follow-up runs, restart recovery, SSE event streaming, and durable Product/Artifact lineage for tasks that cannot fit in one model turn.
- **Human-centered control:** Users can edit Agent identities, inspect memory, delete retained prompt text, answer blocking questions, stop Missions, continue completed work, and review final Artifacts.
- **Persistent two-Agent world:** Nora/Vale-style account Agents carry continuity across Idle, Companion, Work, and Desktop Pet. This creates a coherent product experience instead of isolated AI screens.
- **Product-grade safety boundaries:** V1 Work tools are backend-validated and database-scoped. Shell, file, browser, Codex CLI computer-control, and destructive actions are intentionally excluded from the current public V1 loop until approval gates exist.
- **Evidence-backed memory:** Long-term memory requires user-authored evidence. Work-private trace does not leak into Idle or Companion by default unless promoted through governed memory.
- **Judge-friendly demonstration loop:** A live demo can show a Mission from creation to planning, delegation, search, Product creation, reliability evaluation, and follow-up, with every step visible in the UI.
- **Real deployed system:** The project is running on a real target server with MongoDB persistence, systemd services, Cloudflare tunnel, public domain, smoke tests, browser screenshots, and production health checks.
- **Modular architecture:** FastAPI modules separate users, Agents, conversations, interactions, context, model runtime, memory, workers, Work Mode, and evaluation. This makes the system easier to extend beyond the hackathon.
- **Path to coding workflows without overclaiming:** The roadmap already separates current text/research Mission Runtime from future controlled Codex execution, diff capture, test capture, approval, and apply flows.
- **Polished multi-surface experience:** Web app, Work Console, Me settings, Product reader, Reliability panel, and Desktop Pet all use the same backend truth instead of fragmented demos.
- **Pragmatic AI stack:** Hackson uses React + Vite, FastAPI, MongoDB, Tauri, Codex CLI as the current model provider, OpenAI-compatible runtime support, controlled search, and standard Python/JS test tooling.

## brief intro
- goal for this folder.
  - Root of the Hackson repository.
- 架构思路
  - Product and research documents live under `docs/`.
  - Backend code lives under `backend/` and is split by domain module.
  - Frontend code lives under `frontend/`.
  - Desktop Pet code lives under `desktop/`.
  - Agent operating rules live under `agents/`.
  - Evaluator Runtime reliability-report documents live under `docs/evaluator/`.
  - Verified API and port information lives in `api.md`.

## target machine quick reference
| Item | Value |
| --- | --- |
| Target machine | `catadragon@100.70.248.39` |
| Secret connection note | See ignored local file `docs/数据库/machine.md`; never push it |
| Hackson public domain URL | `https://hackson.catachess.com/`, verified and running |
| Hackson public domain service | `hackson-domain-8145.service`, user-level systemd, enabled |
| Hackson public tunnel service | `hackson-cloudflared.service`, user-level systemd, enabled |
| Hackson public domain path | `~/hackson_domain_8145` |
| Hackson public domain backend bind | `127.0.0.1:8145` |
| Hackson public domain cloudflared config | `~/.cloudflared/hackson.yml` |
| Hackson public domain frontend assets | served by FastAPI from `~/hackson_domain_8145/frontend/dist` |
| Idle Auto smoke service | `hackson-idle-auto-8147.service`, user-level systemd, active for current verification |
| Idle Auto smoke backend bind | `127.0.0.1:8147` |
| Idle Auto local frontend check | `127.0.0.1:5187 -> 18147 -> 8147` |
| Legacy production URL | `http://100.70.248.39:8130/`, retained and running until explicitly retired |
| Legacy production service | `hackson-production.service`, user-level systemd, enabled |
| Legacy production path | `~/hackson_production` |
| Legacy production backend bind | `0.0.0.0:8130` |
| Default frontend local dev port | `127.0.0.1:5173` |
| Hackson public domain MongoDB database | `hackson_domain_8145` |
| Idle Auto smoke MongoDB database | `hackson_idle_auto_8147` |
| Legacy production MongoDB database | `hackson` |
| Stopped old Hackson smoke ports | `8101`, `8122-8126`, `8131-8133`, `8141-8144`, `8146` |

## must-read documents
| Path | Purpose |
| --- | --- |
| `agents/restrictions` | Repository operating rules |
| `agents/frontend_restrictions.md` | Frontend implementation rules |
| `api.md` | Verified API, port map, request/response shapes |
| `docs/backend-architecture.md` | Backend module boundaries |
| `docs/deployment/production.md` | Production deployment topology and verification record |
| `docs/上下文/final_version.md` | Context Runtime product roadmap and version contract |
| `docs/evaluator/final_version.md` | Evaluator Runtime product roadmap and version contract |
| `docs/数据库/machine.md` | Target machine access note; ignored locally |

## folder structure
|-README.md root repository guide
|-api.md verified API and port map
|-agents/ agent operating restrictions
|-backend/ FastAPI backend
|-desktop/ Tauri + React Desktop Pet app
|-docs/ product, context, and database documents
|-docs/evaluator/ Evaluator Runtime reliability-report documents
|-frontend/ React + Vite frontend
|-skills-lock.json skill lock metadata

## 代办
- Keep `api.md` updated only with APIs that were actually verified.
- Keep this root README synchronized when verified ports change.
