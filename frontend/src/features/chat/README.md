## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Own companion_2 chat using verified conversation and interaction APIs.
- 架构思路
  - Create or reuse a local-session companion conversation.
  - Send messages through `/api/companion/{conversationId}/messages`, not raw append.

## folder structure
|-README.md chat feature guide
|-ChatPage.jsx companion chat page

## 代办
- Add conversation picker after list UX is needed.
