## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store the current execution source for Work Mode as a model-driven Mission Runtime.
- 架构思路
  - Treat old V0/V0.5 plans as historical documents only.
  - Make `final_version.md` the product roadmap and decision source.
  - Keep implementation details split by runtime architecture, tool protocol, state machine, context design, UI contract, and execution plan.
  - Keep V1.0.x quality improvements in `quality_track.md` so they do not collide with the main V1.1 native-tool and V1.2 streaming roadmap.
  - Keep known technical risks in `issues/`, linked from the roadmap.

## folder structure
|-README.md current Work Mode documentation guide
|-final_version.md authoritative Work Mode roadmap and version contract
|-architecture.md Mission Runtime architecture and ownership boundaries
|-tool_protocol.md model tool protocol, schemas, and hard constraints
|-state_machine.md Mission, run, window, product, and artifact state transitions
|-context_design.md model context package design and budget rules
|-ui_contract.md React event and product rendering contract
|-quality_track.md V1.0.x Progress details, checks, review, discussion, and revision design
|-implementation_plan.md engineer-facing implementation sequence and acceptance tests
|-issues/ technical risk notes linked from final_version.md
|-legacy/ archived Work Mode V0/V0.5 documents; not execution source

## 代办
- Finish public V1.0 acceptance on a normal API runtime or a user-approved equivalent target.
- Add V1.0 non-streaming progress and bounded retry from `issues/issue7-long-turn-progress.md`.
- Implement V1.0.1 Progress details and Mission create modal before V1.0.3 review/discussion tools.
