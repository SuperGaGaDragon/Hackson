## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Own the V1 user identity system: registration, login, current user lookup, and basic user settings.
- 架构思路
  - Keep HTTP routing in `routes.py`.
  - Keep request/response contracts in `schemas.py`.
  - Keep business rules in `service.py`.
  - Keep MongoDB access in `repository.py`.
  - Keep route dependencies in `auth.py`.
  - Users own later agents, conversations, memory, diary, and relationship state through `user_id`.
  - Users do not own model endpoint, API key, provider, Claude/OpenAI key, or local model path in V1.

## folder structure
|-README.md users module guide
|-__init__.py Python package marker
|-auth.py current-user dependency for protected routes
|-model.py user document helpers
|-repository.py MongoDB user persistence
|-routes.py FastAPI users routes
|-schemas.py request and response schemas
|-service.py user business logic
|-tests/ user module tests

## 代办
- Add email verification if the demo needs public signup.
- Add refresh tokens if sessions need to survive long periods.
- Add rate limiting before exposing auth endpoints on the public internet.
