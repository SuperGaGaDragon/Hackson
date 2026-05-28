## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

## brief intro
- goal for this folder.
  - Store the current execution source for Hackson Evaluator Runtime.
- 架构思路
  - Treat Evaluator Runtime as the reliability layer for Work Mode, not as a separate general-purpose platform.
  - Make `final_version.md` the product roadmap and decision source.
  - Keep implementation details split by architecture, evaluation model, state machine, UI contract, and execution plan.
  - Keep known technical risks in `issues/`, linked from the roadmap.

## folder structure
|-README.md current Evaluator Runtime documentation guide
|-final_version.md authoritative Evaluator Runtime roadmap and version contract
|-architecture.md Evaluator Runtime architecture and ownership boundaries
|-evaluation_model.md checks, scoring, issue taxonomy, and report schema
|-state_machine.md Evaluation run, report, issue, and evidence state transitions
|-ui_contract.md React reliability report rendering contract
|-implementation_plan.md engineer-facing implementation sequence and acceptance tests
|-issues/ technical risk notes linked from final_version.md
|-legacy/ archived evaluator brainstorms; not execution source

## related documents
- `../work_mode/` is the runtime that Evaluator Runtime inspects first.
- `../work_mode/issues/issue16-web-search-tool.md` defines the controlled search tool that creates the first Evidence Ledger.
- `../上下文/` defines auditable context language that Evaluator Runtime must not confuse with trace or full prompt logging.
- `../backend-architecture.md` explains backend module boundaries.

## 代办
- Keep V1.0 scoped to Research Missions.
- Do not claim universal hallucination detection.
- Add issue notes only when a risk changes the Evaluator Runtime architecture.
