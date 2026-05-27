## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store the Work Mode Workspace and Project Mission pages backed by verified `/api/work` APIs.
- 架构思路
  - Work opens to a Workspace project list and New Project form.
  - Project detail owns the two user-edited Agents from `Me`, Missions, console, and Inspector.
  - Use `/api/work` Project, Mission, and Event APIs verified on the target machine.
  - Do not expose Work-only Employee or Team creation in the current product UI.
  - Do not expose autonomous tool execution before backend safety gates exist.

## folder structure
|-README.md work feature guide
|-WorkPage.jsx Work Mode Workspace and Project detail page

## 代办
- Add tool trace display after backend exposes a verified read API.
