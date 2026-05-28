## header
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

## brief intro
- goal for this folder.
  - Store Work Mode Mission Console presentation components.
- 架构思路
  - Components render fixed event types from `/api/work`.
  - Project detail renders the two user-owned Agents passed from `App.jsx`; it does not create Work-only Employees.
  - Mission console cards are vertical siblings; cards must not overlap or nest inside each other.
  - Main order is Activity, optional Reliability, Windows, Product, Progress, then Diagnostics.
  - `MissionHeader` mirrors the selected Mission status and disables actions that the user should not take from a terminal state.
  - `MissionHeader` owns waiting-input replies and completed-Mission follow-up input.
  - `ProductPanel` uses persisted Products and Artifacts as the source of truth and exposes Artifact lineage as readable content, including after Done.
  - `ProductPanel` uses a fixed-rhythm Artifact Navigator plus reader layout so generated title length does not control the page shape.
  - `WorkWindowPanel` renders persisted Delegate windows collapsed by default.
  - `ProgressTimeline` is an audit trail, not the primary product reader.
  - `RawLogPanel` is the collapsed Diagnostics surface, not normal user content.
  - Components do not parse model text or execute commands.
  - Keep copy short per frontend restrictions.

## folder structure
|-README.md work component guide
|-WorkspaceView.jsx workspace project list and new project form
|-ProjectMissionRail.jsx project detail rail with user Agents and missions
|-MissionHeader.jsx selected mission title, status, and controls
|-ActivityStrip.jsx latest compact Mission activity row
|-ReliabilityPanel.jsx latest Evaluator Runtime reliability score, issues, and evidence summary
|-ProgressTimeline.jsx compact mission progress audit trail
|-WorkWindowPanel.jsx delegate work window list
|-SummaryCard.jsx summary event card
|-WarningCard.jsx warning event card
|-ProductPanel.jsx product and artifact reader
|-RawLogPanel.jsx collapsed diagnostics event panel
|-InspectorPanel.jsx status and lead Agent inspector
|-eventDisplay.js shared Work event display labels, icons, time formatting, and sorting helpers

## 代办
- Add ApprovalCard when backend approvals are implemented.
