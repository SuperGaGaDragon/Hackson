## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store worker module tests.
- 架构思路
  - Worker tests verify that derived work is best-effort and rebuildable from raw messages.

## folder structure
|-README.md tests folder guide
|-test_derived_jobs.py derived job and worker behavior tests
|-test_memory_worker.py memory candidate extraction tests
|-test_relationship_worker.py relationship memory evidence and summary tests
|-test_worker_runner.py composed runner tests across summary, memory, diary, and relationship

## 代办
- Add retry and dead-letter tests after a long-running background process exists.
