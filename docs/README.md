## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store product, architecture, deployment, frontend, database, context, Work Mode, Evaluator Runtime, and Desktop Pet planning documents.
- 架构思路
  - Keep verified runtime facts in `api.md` at the repository root.
  - Keep product-level plans in this folder.
  - Keep current Work Mode Mission Runtime documents under `work_mode/`.
  - Keep current Evaluator Runtime documents under `evaluator/`.
  - Keep current Desktop Pet documents under `桌宠/`.
  - Keep current Context Runtime documents under `上下文/`; old context research and V1 notes are archived under `上下文/legacy/`.

## folder structure
|-README.md docs folder guide
|-需求文档v1.md Brainstorm of ideas and functions
|-需求文档final.md final version of functions
|-plan.md overall product roadmap
|-backend-architecture.md backend product-level module architecture plan
|-deployment/ production deployment topology and verification records
|-frontend/ frontend product design direction
|-work_mode/ current Work Mode Agent Mission Runtime documents; old V0/V0.5 plans are archived under `work_mode/legacy/`
|-evaluator/ current Evaluator Runtime reliability-report documents
|-桌宠/ current Desktop Pet Work Mode presence documents
|-上下文/ current Context Runtime documents; old research and V1 notes are archived under `上下文/legacy/`
|-数据库/ database design and local target-machine notes
|-model升级/ model and orchestration upgrade plans

## recommended reading order for new backend developers
1. `docs/需求文档final.md`
2. `docs/上下文/final_version.md`
3. `docs/backend-architecture.md`
4. `docs/frontend/design.md`
5. `docs/deployment/production.md`
6. `docs/work_mode/final_version.md`
7. `docs/work_mode/implementation_plan.md`
8. `docs/evaluator/final_version.md`
9. `docs/evaluator/implementation_plan.md`
10. `backend/README.md`
11. `docs/plan.md`

## important files
- `docs/work_mode/final_version.md`: authoritative Work Mode roadmap and version contract.
- `docs/work_mode/architecture.md`: Work Mode Mission Runtime architecture.
- `docs/work_mode/tool_protocol.md`: model-visible tool protocol and hard constraints.
- `docs/work_mode/state_machine.md`: Mission, Run, Work Window, Product, and Artifact state machine.
- `docs/work_mode/context_design.md`: Lead and Delegate Agent context design.
- `docs/work_mode/ui_contract.md`: React Work UI rendering contract.
- `docs/work_mode/implementation_plan.md`: detailed Work Mode V1.0 implementation sequence.
- `docs/work_mode/issues/`: technical risk notes linked from the final roadmap.
- `docs/work_mode/legacy/`: archived V0/V0.5 plans, not an execution source.
- `docs/evaluator/final_version.md`: authoritative Evaluator Runtime roadmap and version contract.
- `docs/evaluator/architecture.md`: Evaluator Runtime architecture and ownership boundaries.
- `docs/evaluator/evaluation_model.md`: Research reliability checks, scoring, issue taxonomy, and report schema.
- `docs/evaluator/state_machine.md`: Evaluation Run, Reliability Report, Reliability Issue, and Evidence Item state transitions.
- `docs/evaluator/ui_contract.md`: Work Console Reliability Report rendering contract.
- `docs/evaluator/implementation_plan.md`: detailed Evaluator Runtime V1.0 implementation sequence.
- `docs/evaluator/issues/`: technical risk notes linked from the Evaluator Runtime roadmap.
- `docs/桌宠/final_version.md`: authoritative Desktop Pet roadmap and product contract.
- `docs/桌宠/architecture.md`: Desktop Pet architecture and ownership boundaries.
- `docs/桌宠/state_mapping.md`: Work Mode event to pet state mapping.
- `docs/桌宠/ui_contract.md`: desktop window, tray, interaction, and notification contract.
- `docs/桌宠/implementation_plan.md`: detailed Desktop Pet V1.0 implementation sequence.
- `docs/桌宠/versions.md`: Desktop Pet versioned rollout plan.
- `docs/桌宠/issues/`: technical risk notes linked from the Desktop Pet roadmap.
- `docs/上下文/final_version.md`: authoritative Context Runtime roadmap and version contract.
- `docs/上下文/architecture.md`: Context Runtime architecture and ownership boundaries.
- `docs/上下文/context_package.md`: model-visible context package design and budget rules.
- `docs/上下文/implementation_plan.md`: detailed Context Runtime implementation sequence.
- `docs/上下文/legacy/`: archived context research and old V1 plans, not an execution source.
- `docs/model升级/version.md`: ChatGPT-like unified orchestration rollout plan.
- `docs/model升级/plan.md`: Hackson Orchestrator V1 implementation plan.
- `docs/model升级/diary.md`: concise Chinese engineering log for the model upgrade.
- `docs/数据库/designation.md`: V1 用户和数据库公开设计说明.

## 代办
- Keep this README synchronized when new planning folders are added.
