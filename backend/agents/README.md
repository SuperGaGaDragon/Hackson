## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex

## brief intro
- goal for this folder.
  - Own Agent identity, display profile, and persona data.
- 架构思路
  - `agents/` stores what an Agent is.
  - It does not build prompts, call models, or save conversation messages.
  - `context/` reads Agent persona from this module when constructing model context.

## responsibilities
- Create and update user-owned Agents.
- Store Agent name, avatar, core persona, speaking style, and episode state.
- Provide stable Agent records to conversations and context.
- Keep core persona user-controlled in V1.

## not responsible for
- Model provider calls.
- Prompt assembly.
- Conversation message flow.
- Automatic long-term personality rewriting.
- Diary or relationship generation.

## planned files
|-README.md module guide
|-__init__.py Python package marker
|-model.py Agent document helpers
|-repository.py MongoDB Agent persistence
|-routes.py FastAPI Agent routes
|-schemas.py request and response schemas
|-service.py Agent business rules
|-tests/ Agent module tests

## v1 minimum fields
- `id`
- `owner_user_id`
- `name`
- `avatar_url`
- `core_persona`
- `speaking_style`
- `episode_state`
- `created_at`
- `updated_at`

## version plan
- v1.0: Create, read, update, and list the current user's two Agents.
- v1.2: Provide persona snapshots for context packages.
- v1.4: Expose diary and relationship-derived state without overwriting core persona.

## interface expectation
- Other modules should ask this module for Agent records or persona snapshots.
- Other modules should not directly mutate Agent persona fields except through this module.
