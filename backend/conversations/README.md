## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex

## brief intro
- goal for this folder.
  - Own conversation containers, messages, and the main chat product flow.
- 架构思路
  - `conversations/` coordinates the request path from user input or idle tick to Agent reply.
  - It saves messages, calls `context/` to build context, calls `model_runtime/` to generate, then saves the result.
  - It does not own context recipes or model-provider details.

## responsibilities
- Create idle, companion_1, companion_2, and future work conversations.
- Save and read messages.
- Maintain conversation status.
- Link companion_1 conversations back to their parent idle conversation.
- Provide API routes for idle tick, idle join, and companion messages.

## not responsible for
- Prompt recipe implementation.
- Model endpoint configuration.
- Long-term memory generation.
- Summary worker execution.
- Agent persona editing.

## planned files
|-README.md module guide
|-__init__.py Python package marker
|-model.py conversation and message document helpers
|-repository.py MongoDB conversation and message persistence
|-routes.py FastAPI conversation routes
|-schemas.py request and response schemas
|-service.py conversation product flow
|-tests/ conversation module tests

## storage design
- Use one `conversations` collection for all modes.
- Use one `messages` collection for all message rows.
- Do not split companion_1 and companion_2 into separate collections. Their storage shape is the same; their context recipes differ.
- Do not embed messages inside conversation documents. Idle can grow indefinitely, so messages need independent pagination and indexing.

## conversation document
Required fields:
- `_id`
- `user_id`
- `mode`: `idle`, `companion_1`, `companion_2`, or `work`
- `status`: `active`, `paused`, or `archived`
- `title`
- `participant_slots`: fixed V1 Agent slots such as `agent_1` and `agent_2`
- `parent_conversation_id`: set for `companion_1`, usually null otherwise
- `message_count`
- `last_message_at`
- `metadata`
- `created_at`
- `updated_at`

V1 Agent slot rule:
- The backend assumes two fixed Agent slots: `agent_1` and `agent_2`.
- These are Agent identity slots, not user-configurable model endpoints.
- Message rows should use `sender_slot` when an Agent speaks.

## message document
Required fields:
- `_id`
- `conversation_id`
- `user_id`
- `mode`
- `sequence`
- `sender_type`: `user`, `agent`, `system`, or `tool`
- `sender_id`
- `sender_slot`: `agent_1`, `agent_2`, or null
- `role`: `user`, `assistant`, `system`, or `tool`
- `content`
- `content_type`: default `text`
- `metadata`
- `created_at`

Sequence rule:
- `sequence` is the stable ordering key inside a conversation.
- Do not rely only on `created_at` for ordering because idle and async writes can happen close together.

## indexes
`conversations` indexes:
- `{ user_id: 1, mode: 1, status: 1, updated_at: -1 }`
- `{ user_id: 1, mode: 1, last_message_at: -1 }`
- `{ parent_conversation_id: 1 }`

`messages` indexes:
- `{ conversation_id: 1, sequence: 1 }`, unique
- `{ conversation_id: 1, created_at: -1 }`
- `{ user_id: 1, created_at: -1 }`
- `{ user_id: 1, sender_slot: 1, created_at: -1 }`

## initial implemented APIs
- `POST /api/conversations`: create a conversation container.
- `GET /api/conversations`: list current user's conversations.
- `GET /api/conversations/{conversation_id}`: read one conversation.
- `POST /api/conversations/{conversation_id}/messages`: append a message.
- `GET /api/conversations/{conversation_id}/messages`: page messages by sequence.
- `GET /api/idle/conversation`: get or create the current active idle conversation for the user.

## main flow
```text
request or idle tick
  -> save input message when there is one
  -> ask context builder for a context package
  -> ask model_runtime for an Agent response
  -> save Agent response message
  -> return response to frontend
```

## version plan
- v1.0: Support idle tick and companion_2 message flow.
- v1.1: Support `/api/idle/join` and companion_1 parent idle linkage.
- v1.2: Read summaries for context compaction.
- v1.5: Add task conversation support for Work Mode boundaries.

## route sketch
- `GET /api/idle/conversation`
- `POST /api/idle/tick`
- `POST /api/idle/join`
- `POST /api/companion/conversations`
- `POST /api/companion/conversations/:conversationId/messages`
