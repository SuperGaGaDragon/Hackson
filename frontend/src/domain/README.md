## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-26
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store frontend domain mapping helpers and backend Agent display normalization.
- 架构思路
  - Backend owns fixed MVP Agent slots before Agent persistence exists.
  - Frontend keeps only fallback display data for loading and degraded states.
  - Message display mapping belongs here so product features stay simple.
  - Pending outgoing user-message construction belongs here so Chat and companion_1 continuation use the same optimistic turn shape.
  - Client-only ids must work on the target-machine HTTP production URL, not only on secure local contexts.

## folder structure
|-README.md domain folder guide
|-agents.js backend Agent display normalization and fallback data
|-messages.js message sorting and display mapping

## 代办
- Remove fallback Agent labels after app boot can block on Agent API with a polished loading state.
