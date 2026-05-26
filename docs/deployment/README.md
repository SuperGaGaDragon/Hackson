## header
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex

## brief intro
- goal for this folder.
  - Store production deployment notes for the target machine.
- 架构思路
  - Keep production topology, ports, process manager, and verification commands separate from smoke-test notes.
  - Production deployment must use the target machine documented in `docs/数据库/machine.md`.
  - Production verification results must be copied back into root `api.md`.

## folder structure
|-README.md deployment folder guide
|-production.md production deployment plan and verification record

## 代办
- Add rollback steps after the first production service has been running long enough to define release cadence.
