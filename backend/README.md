## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Hackson backend service. V1 starts with the user identity boundary and keeps each product capability in its own module.
- 架构思路
  - Use FastAPI as the HTTP layer.
  - Keep business modules split by domain, starting with `users/`.
  - Keep shared runtime concerns in `core/`.
  - Use MongoDB as the persistence layer on the target machine.
  - V1 demo model endpoint is platform-managed and is not part of user data.

## folder structure
|-README.md backend folder guide
|-requirements.txt Python runtime dependencies
|-main.py FastAPI application entrypoint
|-core/ shared config, database, and security utilities
|-users/ user system module

## 代办
- Add deployment scripts after the target port and process manager are finalized.
- Add agents, conversations, and context modules after the user ownership boundary is stable.
