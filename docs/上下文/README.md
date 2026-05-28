## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store the current execution source for Hackson Context Runtime.
- 架构思路
  - Treat old context research and V1 notes as historical documents only.
  - Make `final_version.md` the product roadmap and decision source.
  - Keep implementation details split by runtime architecture, state machine, context package design, UI/debug contract, and execution plan.
  - Keep known technical risks in `issues/`, linked from the roadmap.

## folder structure
|-README.md current Context Runtime documentation guide
|-final_version.md authoritative Context Runtime roadmap and version contract
|-architecture.md Context Runtime architecture and ownership boundaries
|-state_machine.md Conversation, turn, memory, summary, and idle-runner state transitions
|-context_package.md model-visible context package design and budget rules
|-ui_contract.md React context, memory, and debug rendering contract
|-implementation_plan.md engineer-facing implementation sequence and acceptance tests
|-issues/ technical risk notes linked from final_version.md
|-legacy/ archived context research and old V1 plans; not execution source

## related documents
- `../backend-architecture.md` explains backend module boundaries.
- `../model升级/plan.md` explains the current model orchestration path.
- `../work_mode/` is the structural reference for this folder's active/legacy split.

## 代办
- Finish the first grilling pass and promote resolved decisions into `final_version.md`.
- Add issue notes only when a risk changes the Context Runtime architecture.
