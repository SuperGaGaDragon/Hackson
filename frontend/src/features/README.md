## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store product feature modules that match currently verified backend behavior.
- 架构思路
  - Each feature owns its page, local state, and API flow.
  - No feature should implement backend functionality that is not verified in `api.md`.

## folder structure
|-README.md features folder guide
|-auth/ login and register feature
|-idle/ idle conversation, tick, join, and history feature
|-chat/ companion_2 chat feature
|-me/ current-user settings feature

## 代办
- Add Agent feature only after verified Agent APIs exist.
