## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-26
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store the Work Mode task page backed by verified `/api/tasks` APIs.
- 架构思路
  - Keep the first Work UI small: task list, objective input, selected task transcript, Agent target, and one composer.
  - Use `POST /api/tasks` for task creation and `POST /api/tasks/{taskId}/messages` for model-backed work replies.
  - Do not expose autonomous tool execution because v1.5 backend does not implement it.

## folder structure
|-README.md work feature guide
|-WorkPage.jsx Work Mode task page

## 代办
- Add tool trace display after backend exposes a verified read API.
