## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex

## brief intro
- goal for this document.
  - Define the product-level Idle Auto loop before changing code.
- 架构思路
  - Backend owns turn selection and transcript persistence.
  - Frontend owns user controls and lightweight cadence.
  - Topic direction is steering metadata, not a fake user message.

## intended product flow
1. User creates a new Idle topic.
2. The selected topic is saved on the idle conversation as `metadata.topicDirection`.
3. The first Agent reply starts immediately from that topic.
4. If Auto is on, the frontend keeps requesting the next idle turn.
5. The backend decides the next speaking Agent from the saved transcript.
6. If the user says something, that text is saved as a real user interjection in the same idle transcript.
7. The next Agent reply is generated immediately after the interjection.
8. If Auto was on before the interjection, Auto continues after that reply.

## product state machine
| State | Trigger | Backend action | Frontend action |
| --- | --- | --- | --- |
| Empty topic modal | Create topic | `POST /api/conversations` creates idle conversation | Close modal, show topic |
| New idle topic | Create success | `POST /api/idle/{conversationId}/tick` creates first Agent message | Set Auto on by default |
| Auto running | Timer | `POST /api/idle/{conversationId}/tick` creates next Agent message | Append message, schedule next timer |
| User interjects | Say | New idle turn endpoint saves user message then Agent reply | Replace pending user message, append Agent reply, keep Auto state |
| Model unavailable | Tick or Say fails | Return a stable non-201 API error without saving a partial Agent reply | Stop Auto and show the error so the user can retry deliberately |
| Auto paused | Auto toggle off | No backend work | Stop scheduling timers |
| Explicit companion | Join | `POST /api/idle/{conversationId}/join` creates child `companion_1` | Leave Idle Auto mode |

## backend rules
- Idle speaker selection must be server-side.
- If the last visible idle message is from `agent_1`, the next turn should target `agent_2`.
- If the last visible idle message is from `agent_2`, the next turn should target `agent_1`.
- If the last visible idle message is from the user, the backend should pick a valid Agent and answer the user's interjection.
- If no messages exist, the backend should start with `agent_1`.
- Client-provided `targetAgentId` may be treated as a hint only when there is no transcript yet.
- The topic direction must be included in model context on every idle turn.
- Model provider failures must be converted to stable API errors.
- Idle Say must not persist a half-turn when model generation fails.

## frontend rules
- Creating a topic should not leave a blank inactive transcript.
- Auto should be a cadence control, not the source of speaker truth.
- Say should mean natural interjection in the same idle conversation.
- Join should remain the explicit transition into `companion_1`.
- The user should not need to click Tick after Create or Say for the system to continue.
- Auto must stop after any generation failure, including provider rate limits, instead of retrying in a loop.

## test plan
- Backend unit tests:
  - Empty idle topic starts with `agent_1`.
  - Existing last `agent_1` message makes the next reply `agent_2`.
  - User interjection endpoint saves user message then Agent reply in the same idle conversation.
  - User interjection keeps topic direction in the prompt.
  - Model rate limit returns a stable API error instead of an unhandled 500.
  - Failed idle interjection does not leave a user-only half-turn in the transcript.
- Frontend checks:
  - Create topic triggers first Agent reply.
  - Auto can continue after the first reply.
  - Say appends the user message and immediate Agent reply.
  - Auto remains enabled if it was enabled before Say.

## 代办
- Add a backend-owned background idle runner only if product requires idle to continue after the browser closes.
