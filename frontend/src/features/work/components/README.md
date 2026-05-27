## header
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-26
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store Work Mode Mission Console presentation components.
- 架构思路
  - Components render fixed event types from `/api/work`.
  - Components do not parse model text or execute commands.
  - Keep copy short per frontend restrictions.

## folder structure
|-README.md work component guide
|-ProjectMissionRail.jsx project and mission list plus creation controls
|-MissionHeader.jsx selected mission title, status, and controls
|-ProgressTimeline.jsx mission event timeline
|-SummaryCard.jsx summary event card
|-WarningCard.jsx warning event card
|-ProductPanel.jsx product event panel
|-RawLogPanel.jsx raw log event panel
|-InspectorPanel.jsx status and lead employee inspector

## 代办
- Add ApprovalCard when backend approvals are implemented.
