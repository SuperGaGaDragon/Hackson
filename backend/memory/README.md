## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex

## brief intro
- goal for this folder.
  - Own long-term memory cards and memory governance.
- 架构思路
  - V1.3 introduces memory slowly and only for high-value, evidence-backed facts.
  - Raw messages remain the source of truth.
  - Memory is a derived layer used by context, not a replacement for conversation history.

## responsibilities
- Store memory cards.
- Accept or reject memory candidates.
- Require evidence message ids.
- Provide mode-appropriate memory to `context/`.

## not responsible for
- Saving raw messages.
- Replacing summaries.
- Automatically modifying core persona.
- Full GraphRAG.
- Multi-hop retrieval.

## planned files
|-README.md module guide
|-__init__.py Python package marker
|-repository.py MongoDB memory card persistence
|-governor.py memory candidate acceptance rules
|-schemas.py memory card and candidate schemas
|-tests/ memory module tests

## minimum memory card fields
- `id`
- `owner_type`
- `owner_id`
- `memory_type`
- `summary`
- `source_message_ids`
- `importance_score`
- `confidence`
- `created_at`
- `updated_at`

## v1.3 allowed memory types
- Explicit user preferences.
- Explicit user facts.
- Key user-Agent interactions.
- Small Agent-Agent relationship summaries.

## write rule
- No source message id, no long-term memory write.
