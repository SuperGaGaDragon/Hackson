## header
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store product and engineering plans for Work Mode as an Agent Mission Runtime.
- 架构思路
  - Keep brainstorm notes separate from executable plans.
  - Use `versions.md` to define product release boundaries.
  - Use `plan.md` as the implementation manual for the first production slice.
  - Use `v0_5_single_model_run.md` for the current single-run product slice that turns Mission goals into persisted artifacts.
  - Work Mode must evolve from the existing minimal `/api/tasks` chat flow into a supervised mission runtime with fixed UI events, worker execution, and human approval.

## folder structure
|-README.md work_mode documentation guide
|-brainstorm.md raw product and architecture brainstorm
|-versions.md product-level version roadmap and release gates
|-plan.md detailed implementation plan for the first Work Mode runtime slices
|-v0_5_single_model_run.md current V0.5 single model-run implementation blueprint

## 代办
- Add `event_protocol.md` after V0 event schemas stabilize in code.
- Add `runtime_state_machine.md` after the first worker loop is implemented and verified.
