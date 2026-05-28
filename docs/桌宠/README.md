## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store the current execution source for Hackson Desktop Pet as a Work Mode desktop presence product.
- 架构思路
  - Treat Desktop Pet as a companion surface for Work Mode, not a separate agent runtime.
  - Make `final_version.md` the product roadmap and decision source.
  - Keep implementation details split by product architecture, state mapping, UI contract, implementation plan, and version roadmap.
  - Keep technical risks in `issues/`, linked from the roadmap.
  - Reuse verified backend APIs from root `api.md`; do not invent unverified API contracts in UI documents.

## folder structure
|-README.md current Desktop Pet documentation guide
|-final_version.md authoritative Desktop Pet roadmap and product contract
|-architecture.md Desktop Pet product architecture and ownership boundaries
|-state_mapping.md Work Mode event to pet state mapping
|-ui_contract.md desktop window, tray, interaction, and notification rendering contract
|-implementation_plan.md engineer-facing implementation sequence and acceptance tests
|-versions.md versioned rollout plan and release gates
|-issues/ technical risk notes linked from final_version.md

## 代办
- Finalize the desktop runtime choice after a Tauri prototype validates transparent always-on-top windows on macOS.
- Add signed distribution notes after V1.0 local build and smoke pass.
