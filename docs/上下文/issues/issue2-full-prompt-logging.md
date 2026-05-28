## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 2: Full Prompt Logging

## Decision

Full Prompt Logging is user-controlled and defaults on in V1.0.

Full prompt text is retained for 30 days. Turning the setting off affects future packages only. A separate Delete Prompt Logs action removes retained full prompt text while keeping package metadata.

## Risk

Full prompt text may contain user profile, Agent profile, transcript, summaries, memory, and hidden instructions. Storing it improves debugging but increases privacy, deletion, and access-control requirements.

## Constraints

- Full Prompt Logging setting belongs in Me.
- Users can view and delete retained prompt text.
- Users cannot edit historical prompt text.
- Full prompt text must never expose raw chain-of-thought.
- Package metadata is stored even when full prompt text is omitted.

## Required Tests

- New users default to Full Prompt Logging enabled.
- Disabling logging omits full prompt text for later packages.
- Delete Prompt Logs clears retained prompt text only.
- Retention cleanup can identify prompt text older than 30 days.
