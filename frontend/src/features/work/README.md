## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex

## brief intro
- goal for this folder.
  - Store the Work Mode Workspace and Project Mission pages backed by verified `/api/work` APIs.
- 架构思路
  - Work opens to a Workspace project list and New Project form.
  - Project detail owns the two user-edited Agents from `Me`, Missions, console, Mission Map, and Info/Quality modals.
  - Use `/api/work` Project, Mission, and Event APIs verified on the target machine.
  - Selected Project navigation should use a two-zone rail: Directory above and Mission Composer below.
  - Mission detail renders a single vertical console stream so Activity, Product, Windows, Progress, and Diagnostics never overlap.
  - Mission Map is the right-side table of contents on desktop and moves above the main content on mobile.
  - `ActivityStrip` renders the latest safe runtime lifecycle event so long model turns do not look frozen.
  - `WorkWindowPanel` renders delegated Agent work above Progress because it answers who is working before showing the audit trail.
  - `ProductPanel` renders Product and Artifact lineage from persisted state and never treats only the latest Artifact as the whole deliverable.
  - `RawLogPanel` is the collapsed Diagnostics surface for raw event payloads.
  - Running Missions use the SSE event stream when available and fall back to event polling if streaming fails.
  - Terminal mission actions must be truthful; a completed mission cannot present an enabled `Start` action.
  - Completed missions may continue with Leader through the Mission Composer, preserving prior Products and Artifacts.
  - Waiting-input answers, completed follow-up, and resumable-state instructions should converge into one selected Mission Composer.
  - Default rows must stay compact; long generated text belongs in Product reader or bounded expanded details.
  - Do not expose Work-only Employee or Team creation in the current product UI.
  - Do not expose autonomous tool execution before backend safety gates exist.

## folder structure
|-README.md work feature guide
|-WorkPage.jsx Work Mode Workspace and Project detail page
|-components/ fixed Work UI components for Activity, Mission Map, Windows, Product, Progress, Diagnostics, and Info/Quality modals

## 代办
- Add richer streaming state labels after the backend exposes safe partial-progress events beyond persisted Mission events.
