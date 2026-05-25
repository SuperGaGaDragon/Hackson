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
