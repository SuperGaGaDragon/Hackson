## header
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store Work Mode Mission Console presentation components.
- 架构思路
  - Components render fixed event types from `/api/work`.
  - Project detail renders the two user-owned Agents passed from `App.jsx`; it does not create Work-only Employees.
  - Mission console cards are vertical siblings; cards must not overlap or nest inside each other.
  - `MissionHeader` mirrors the selected Mission status and disables actions that the user should not take from a terminal state.
  - `ProductPanel` prefers persisted Mission artifacts over event preview text.
  - Components do not parse model text or execute commands.
  - Keep copy short per frontend restrictions.

## folder structure
|-README.md work component guide
|-WorkspaceView.jsx workspace project list and new project form
|-ProjectMissionRail.jsx project detail rail with user Agents and missions
|-MissionHeader.jsx selected mission title, status, and controls
|-ProgressTimeline.jsx mission event timeline
|-SummaryCard.jsx summary event card
|-WarningCard.jsx warning event card
|-ProductPanel.jsx product event panel
|-RawLogPanel.jsx raw log event panel
|-InspectorPanel.jsx status and lead Agent inspector

## 代办
- Add ApprovalCard when backend approvals are implemented.
