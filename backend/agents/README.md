## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex

## brief intro
- goal for this folder.
  - Own Agent identity, display profile, and persona data.
- 架构思路
  - `agents/` stores what an Agent is.
  - It does not build prompts, call models, or save conversation messages.
  - `interactions/` reads Agent persona records from this module, then passes snapshots into `context/`.
  - V1 keeps two backend-owned fixed Agent slots and uses the catalog to seed each user's editable Agent profiles.

## responsibilities
- Store default Agent name, color, short label, voice label, core persona, speaking style, and detailed editable origin story.
- Provide stable Agent records to conversations and context.
- Provide frontend-safe display profiles without exposing hidden prompt-only fields.
- Seed and normalize user-owned Agent profiles without allowing extra slots.

## not responsible for
- Model provider calls.
- Prompt assembly.
- Conversation message flow.
- Automatic long-term personality rewriting.
- Diary or relationship generation.

## folder structure
|-README.md module guide
|-__init__.py Python package marker
|-catalog.py fixed V1 Agent identity and persona catalog
|-routes.py FastAPI Agent routes
|-schemas.py Agent API response schemas
|-tests/ Agent catalog and route tests

## v1 minimum fields
- `slot`
- `name`
- `short`
- `color`
- `voice`
- `core_persona`
- `speaking_style`
- `episode_state`
- `episode_state` seeds the editable Agent `story`; it should be a product-grade origin story, not a transient demo status line.

## version plan
- v1.0: List the backend-owned two fixed demo Agents.
- v1.1: Seed and normalize each user's two editable Agent profiles.
- v1.2: Move profile persistence into a dedicated Agent module while keeping the same route contract.
- v1.4: Expose diary and relationship-derived state without overwriting core persona.

## interface expectation
- Other modules should ask this module for Agent records or persona snapshots.
- Other modules should not directly mutate Agent persona fields except through this module.

## 代办
- Replace the fixed catalog with MongoDB persistence when Agent editing becomes part of V1.x.
