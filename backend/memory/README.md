## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

## brief intro
- goal for this folder.
  - Own long-term memory cards and memory governance.
- 架构思路
  - V1.3 introduces memory slowly and only for high-value, evidence-backed facts.
  - Raw messages remain the source of truth.
  - Memory is a derived layer used by context, not a replacement for conversation history.
  - `account` memory is shared across Idle, Companion, and Work for user-level continuity.
  - Mode-private memory is still isolated by `user_id`, `scope`, `owner_type`, and `owner_id` so raw Work trace cannot pollute Companion Mode.

## responsibilities
- Store memory cards.
- Accept or reject memory candidates.
- Require evidence message ids.
- Provide mode-appropriate memory to `context/`.
- Expose user-owned memory controls for list, disable, enable, and delete.

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
|-service.py memory write/read business rules
|-routes.py authenticated memory control routes
|-tests/ memory module tests

## minimum memory card fields
- `id`
- `user_id`
- `scope`
- `owner_type`
- `owner_id`
- `memory_type`
- `summary`
- `source_message_ids`
- `importance_score`
- `confidence`
- `status`
- `metadata`
- `created_at`
- `updated_at`

## v1.3 allowed memory types
- Explicit user preferences.
- Explicit user facts.
- Key user-Agent interactions.
- Small Agent-Agent relationship summaries.

## write rule
- No source message id, no long-term memory write.
- User fact and preference memory must come from user-authored evidence, not Agent guesses.
- `account` scoped memory can be read by Idle, Companion, and Work recipes.
- `work` scoped task-private memory cannot be read by idle or companion recipes by default.
- Disabled or deleted memory cannot enter context packages.
- Delete is a soft delete to preserve audit metadata until a later privacy policy defines hard delete.
- Deprecated generic relationship cards are hidden from user-facing reads; they are legacy noise, not useful memory.

## indexes
- `user_id + scope + owner_type + owner_id + memory_type + updated_at`
- `user_id + status + importance_score + updated_at`
- `user_id + source_message_ids`
- `user_id + dedupe_hash` unique where possible
