## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store Hackson model and orchestration upgrade goals, version boundaries, and implementation planning notes.
- 架构思路
  - Treat the upgrade as a product orchestration effort, not a simple model-name replacement.
  - Keep long-term ambition in `goal.md`.
  - Keep release scope and gates in `version.md`.
  - Keep implementation order, tests, and rollback strategy in `plan.md`.
  - Keep concise Chinese engineering progress notes in `diary.md`.
  - Implementation must preserve the existing backend boundaries: `context/` decides what the model sees, `model_runtime/` decides how to call providers, and `interactions/` owns mode-specific product flow.

## folder structure
|-README.md model upgrade documentation guide
|-goal.md product goal and ChatGPT-like orchestration rationale
|-version.md versioned rollout plan for unified orchestration
|-plan.md V1 Hackson Orchestrator implementation manual
|-eval.md fixed qualitative evaluation set for V1
|-diary.md concise Chinese engineering log

## 代办
- Keep `eval.md` updated only when the quality gate changes.
