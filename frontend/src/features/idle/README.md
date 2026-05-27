## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Own Idle product flow using verified idle APIs.
- 架构思路
  - Load idle history, select one idle conversation, tick one Agent reply, accept a user interjection with an immediate Agent reply, explicitly join into companion_1, then continue the child conversation.
  - Create a clean idle topic through the verified conversation API.
  - Start the first Agent reply immediately after topic creation and turn Auto on.
  - Treat Auto as a frontend cadence control; backend decides which Agent speaks next from transcript.
  - Stop Auto on any generation failure so rate limits or provider errors do not loop.
  - Keep parent idle context above child companion turns instead of globally sorting their independent sequence values together.
  - Pin the transcript to the latest child turn without waiting for smooth-scroll timing.
  - Send `Topic` as `discussionDirection`; never render it as a transcript message unless the backend returns it as one.
  - Treat `Say` as an idle transcript message and `Join` as the only mode transition into companion_1.

## folder structure
|-README.md idle feature guide
|-IdlePage.jsx idle history, new topic modal, timeline, auto cadence, tick, say, join, and status UI

## 代办
- Move Auto to a backend-owned runner only if Idle must continue after the browser closes.
