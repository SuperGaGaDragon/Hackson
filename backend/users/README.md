## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
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
- Users own a bounded human profile: `personality` and `story`.
- Users own exactly two editable Agent profiles seeded from Nora and Vale.
- Users own the Full Prompt Logging setting used by Context Runtime debugging.
- Users own the Background Idle setting used by future server-owned idle cadence.
- Users can list and delete retained prompt logs from Me, but cannot edit historical prompt text.
- Browser-to-desktop auth handoff lets the web login authorize Desktop Pet without exposing passwords in the desktop window.

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

## current profile fields
- `display_name`: public display name.
- `idle_on`: whether Idle should be enabled in product UI.
- `background_idle_on`: whether future server-owned idle cadence may run while the browser is closed. Defaults to `false`.
- `language_preference`: lightweight language preference.
- `personality`: bounded human personality note for context.
- `story`: bounded human background story for context.
- `agent_profiles`: the user's two editable Agent profiles for `agent_1` and `agent_2`.
- `full_prompt_logging_on`: whether future context package records may retain full prompt text. Defaults to `true` for new users.

## current Agent profile fields
- `slot`: fixed slot, `agent_1` or `agent_2`.
- `name`: visible Agent name.
- `short`: backend-controlled short label.
- `color`: backend-controlled display color.
- `voice`: visible voice label and speaking style.
- `personality`: Agent core persona.
- `story`: Agent background or episode state.

## 代办
- Add email verification if the demo needs public signup.
- Add refresh tokens if sessions need to survive long periods.
- Add rate limiting before exposing auth endpoints on the public internet.
- Add paginated prompt-log UI if early debugging produces too many retained package records.
- Replace Desktop Pet handoff polling with a native deep link only after packaging needs it.
