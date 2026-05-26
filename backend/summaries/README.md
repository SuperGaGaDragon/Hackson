## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Own persisted conversation summaries used by context compaction.
- 架构思路
  - Raw messages remain the source of truth.
  - Summaries are derived, rebuildable records with source message ranges.
  - The module exposes a small service/repository interface so workers can write summaries and interactions/context can read the latest summary without knowing MongoDB details.

## folder structure
|-README.md summaries module guide
|-__init__.py Python package marker
|-model.py summary document conversion helpers
|-repository.py MongoDB summary persistence
|-schemas.py summary request and response schemas
|-service.py summary business rules
|-tests/ summary module tests

## 代办
- Add model-generated summary text once `workers/summary_worker.py` calls the configured model runtime.
- Add context package persistence for audit logs after the prompt package schema is finalized.
