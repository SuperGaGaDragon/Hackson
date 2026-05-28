## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

## brief intro
- Goal: close the Work Mode `waiting_input` product loop so `ask_user` is not a dead end.
- Architecture: persist user answers as first-class Mission events, resume the same Mission run, and expose a visible answer form in the Mission control area.

## problem
- Current Lead tools can call `ask_user`.
- Backend marks the Mission as `waiting_input` and emits `USER_INPUT_REQUESTED`.
- Public UI shows the request in Progress, but there is no answer form.
- Public API has no endpoint for submitting the answer.
- Result: a user-facing Mission can become stuck even though the model made a valid request.

## product contract
- When Mission status is `waiting_input`, the top Mission control area MUST show:
  - the model question;
  - suggested options when present;
  - a text answer box;
  - a submit command.
- Submitting an answer MUST:
  - reject empty answers;
  - append `USER_INPUT_RECEIVED`;
  - preserve the original `USER_INPUT_REQUESTED`;
  - set the Mission back to `running`;
  - resume the model loop automatically.
- The model MUST see the answer in `recentEvents` before selecting the next tool.
- The Start button MUST NOT be the primary way out of `waiting_input`.

## implementation plan
- Add `MissionAnswerRequest`.
- Add `USER_INPUT_RECEIVED` to public event schema.
- Add `POST /api/work/missions/{missionId}/answer`.
- Add `WorkModeService.answer_mission_input`.
- Add route regression test for `waiting_input -> answer -> running/resumed`.
- Add frontend API helper.
- Add Mission header answer form and progress display support.
- Add browser smoke coverage for the visible input form.

## verification
- Unit route regression.
- Work Mode backend tests.
- Frontend build.
- Target-machine isolated/public smoke before promotion.

## 代办
- Later versions may support multiple pending questions and richer structured inputs.
