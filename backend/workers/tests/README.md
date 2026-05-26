## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store worker module tests.
- 架构思路
  - Worker tests verify that derived work is best-effort and rebuildable from raw messages.

## folder structure
|-README.md tests folder guide
|-test_derived_jobs.py derived job and worker behavior tests

## 代办
- Add retry and dead-letter tests after a background runner exists.
