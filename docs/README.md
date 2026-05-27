## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store product, architecture, deployment, frontend, database, context, and Work Mode planning documents.
- 架构思路
  - Keep verified runtime facts in `api.md` at the repository root.
  - Keep product-level plans in this folder.
  - Keep current Work Mode Mission Runtime documents under `work_mode/`.
  - Keep context research and implementation plans under `上下文/`.

## folder structure
|-README.md docs folder guide
|-需求文档v1.md Brainstorm of ideas and functions
|-需求文档final.md final version of functions
|-plan.md overall product roadmap
|-backend-architecture.md backend product-level module architecture plan
|-deployment/ production deployment topology and verification records
|-frontend/ frontend product design direction
|-work_mode/ current Work Mode Agent Mission Runtime documents; old V0/V0.5 plans are archived under `work_mode/legacy/`
|-上下文/ context system research, requirements, and plans
|-数据库/ database design and local target-machine notes
|-model升级/ model and orchestration upgrade plans

## recommended reading order for new backend developers
1. `docs/需求文档final.md`
2. `docs/上下文/plan.md`
3. `docs/backend-architecture.md`
4. `docs/frontend/design.md`
5. `docs/deployment/production.md`
6. `docs/work_mode/final_version.md`
7. `docs/work_mode/implementation_plan.md`
8. `backend/README.md`
9. `docs/plan.md`

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
- `docs/上下文/context-mainstream-research.md`: 主流上下文处理方案与论文综述.
- `docs/上下文/context-requirements-for-hackson.md`: 结合 Hackson 产品模式的上下文系统需求文档.
- `docs/上下文/context-innovation-proposal.md`: Hackson Context OS 创新架构提案.
- `docs/model升级/version.md`: ChatGPT-like unified orchestration rollout plan.
- `docs/model升级/plan.md`: Hackson Orchestrator V1 implementation plan.
- `docs/model升级/diary.md`: concise Chinese engineering log for the model upgrade.
- `docs/数据库/designation.md`: V1 用户和数据库公开设计说明.

## 代办
- Keep this README synchronized when new planning folders are added.
