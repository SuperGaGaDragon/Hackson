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
  - Selected Project rail is a two-zone command surface: Directory above, Composer below.
  - Mission console cards are vertical siblings; cards must not overlap or nest inside each other.
  - Main order is Activity, Product, Windows, Progress, then Diagnostics.
  - Reliability renders as side Quality status by default; full review details stay collapsed until opened.
  - `MissionHeader` mirrors selected Mission identity/status and lifecycle controls; it must not own textarea forms after the command-rail refactor.
  - `ProjectMissionRail` owns selected Project navigation and will compose the Mission input Composer.
  - `ProductPanel` uses persisted Products and Artifacts as the source of truth and exposes Artifact lineage as readable content, including after Done.
  - `ProductPanel` separates the authoritative Deliverable from Product History; `latestArtifactId` is only lineage recency and must not replace the final user-facing result.
  - `ProductPanel` uses a fixed-rhythm Artifact Navigator plus reader layout so generated title length does not control the page shape.
  - `WorkWindowPanel` renders persisted Delegate windows collapsed by default.
  - `ProgressTimeline` is an audit trail, not the primary product reader.
  - `RawLogPanel` is the collapsed Diagnostics surface, not normal user content.
  - Components do not parse model text or execute commands.
  - Default list rows must not render unbounded model prose; full content belongs in Product reader, expanded details, Work Window details, or Diagnostics.
  - Keep copy short per frontend restrictions.

## folder structure
|-README.md work component guide
|-WorkspaceView.jsx workspace project list and new project form
|-ProjectMissionRail.jsx project detail rail with user Agents and missions
|-MissionComposer.jsx selected Mission command input for waiting answers, follow-up, resume, draft start, and running instructions
|-MissionHeader.jsx selected mission title, status, and controls
|-ActivityStrip.jsx latest compact Mission activity row
|-ReliabilityPanel.jsx side Quality status plus expandable event-backed Evaluator Runtime risk report
|-ProgressTimeline.jsx compact mission progress audit trail with single-select category filters
|-WorkWindowPanel.jsx delegate work window list
|-SummaryCard.jsx summary event card
|-WarningCard.jsx warning event card
|-ProductPanel.jsx product and artifact reader
|-RawLogPanel.jsx collapsed diagnostics event panel
|-InspectorPanel.jsx status and lead Agent inspector
|-eventDisplay.js shared Work event display labels, icons, time formatting, and sorting helpers

## 代办
- Add ApprovalCard when backend approvals are implemented.
