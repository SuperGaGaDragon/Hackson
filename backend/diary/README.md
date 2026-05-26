## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Own derived Agent diary entries.
- 架构思路
  - Diary entries are user-visible narrative artifacts, not the historical fact source.
  - Diary entries must reference source messages or memory cards so they can be audited and rebuilt.

## folder structure
|-README.md diary module guide
|-__init__.py Python package marker
|-model.py diary document conversion helpers
|-repository.py MongoDB diary persistence
|-schemas.py diary schemas
|-service.py diary business rules
|-tests/ diary module tests

## 代办
- Add frontend diary views after backend entries are generated and verified.
