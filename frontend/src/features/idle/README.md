## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Own Idle product flow using verified idle APIs.
- 架构思路
  - Load active idle conversation, page message history, tick one Agent reply, and join into companion_1.
  - Sort transcript by backend `sequence`.

## folder structure
|-README.md idle feature guide
|-IdlePage.jsx idle timeline, tick, join, and status UI

## 代办
- Add polling only after interaction cadence is decided.
