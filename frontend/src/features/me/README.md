## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Own current user settings, Agent editing, memory controls, and Debug controls backed by verified user APIs.
- 架构思路
  - Keep the first viewport focused on account basics and the user's two Agent profiles.
  - Keep the user's own context under concise `Style` and `Background` labels.
  - Let users disable or delete saved memory cards after primary profile controls.
  - Keep Full Prompt Logging and retained prompt text in collapsed Debug by default.
  - Never expose model runtime settings.

## folder structure
|-README.md me feature guide
|-MePage.jsx current user settings, two-Agent profile editor, memory controls, and collapsed Debug prompt logs

## 代办
- Move Agent editing to a dedicated page if profile editing becomes too dense.
