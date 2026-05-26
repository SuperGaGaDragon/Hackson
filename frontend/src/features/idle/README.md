## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-26
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Own Idle product flow using verified idle APIs.
- 架构思路
  - Load active idle conversation, page message history, tick one Agent reply, join into companion_1, then continue the child conversation.
  - Keep parent idle context above child companion turns instead of globally sorting their independent sequence values together.
  - Pin the transcript to the latest child turn without waiting for smooth-scroll timing.

## folder structure
|-README.md idle feature guide
|-IdlePage.jsx idle timeline, tick, join, and status UI

## 代办
- Add polling only after interaction cadence is decided.
