## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store Hackson context-system research, requirements, architecture, and product development plans.
- 架构思路
  - Keep mainstream research separate from Hackson-specific requirements.
  - Keep long-term innovation proposals separate from V1 engineering plans.
  - Use `plan.md` as the implementation-facing context roadmap.

## folder structure
|-README.md context folder guide
|-context-mainstream-research.md mainstream context handling and paper summary
|-context-requirements-for-hackson.md Hackson-specific context requirements
|-context-innovation-proposal.md Context OS innovation proposal
|-plan.md product-level context system implementation plan
|-persona-topic-compact.md implementation blueprint for user profile, idle topic direction, speaker boundary, and compact
|-idle-auto-flow.md product-level Idle Auto state machine and test plan

## related documents
- ../backend-architecture.md explains where backend modules such as `context/`, `model_runtime/`, `conversations/`, and `workers/` should live.
- `plan.md` explains what the context system should do by product version.

## 代办
- Keep `persona-topic-compact.md` synchronized while the V1 compact and profile path stabilizes.
- Keep `idle-auto-flow.md` synchronized while Idle Auto moves from frontend cadence to backend-owned turn policy.
