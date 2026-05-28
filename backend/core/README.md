## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-26
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Shared backend runtime utilities that are not owned by a single product module.
- 架构思路
  - `config.py` reads platform-side backend configuration.
  - `database.py` owns MongoDB connection lifecycle and the `mongomock://` in-memory test URI.
  - `security.py` owns password hashing and JWT primitives.
  - Production static frontend hosting is controlled by `HACKSON_STATIC_FRONTEND_DIR`.
  - Derived worker freshness is controlled by `HACKSON_DERIVED_WORKER_ENABLED`, `HACKSON_DERIVED_WORKER_INTERVAL_SECONDS`, and `HACKSON_DERIVED_WORKER_BATCH_SIZE`.
  - User-selected model endpoint configuration is intentionally absent from user-facing settings in V1.

## folder structure
|-README.md core folder guide
|-__init__.py Python package marker
|-config.py platform runtime settings
|-database.py MongoDB connection lifecycle
|-security.py password hashing and token helpers

## 代办
- Move secrets to a real secret manager before production.
- Add structured logging and request correlation IDs.
