## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store local Desktop Pet state definitions and timing rules.
- 架构思路
  - Keep V0.6 behavior deterministic and backend-free.
  - Later Work Mode event mapping can build on this state model.
  - Keep V0.8.3 Progress glance summarization in pure domain code so the tiny pet UI only renders prepared rows.

## folder structure
|-README.md desktop pet domain folder guide
|-missionState.js Work Mode Mission and event to pet state mapping
|-missionState.test.mjs node tests for active Mission selection, pet state copy, and Progress glance summary
|-petStates.js local cat state labels, messages, timing, and movement rules

## 代办
- Add richer Work Mode event mapping after native notifications are introduced.
