## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 2: Notification Trust

## Question

How does Desktop Pet avoid becoming noisy?

## Recommendation

Notify only when the user can or should act.

Allowed V1 notification states:

- `waiting`
- `paused`
- `done`
- `failed`

## Risk

If every Work Mode event triggers a notification, users will mute or quit the app. The pet then loses its core value as a trusted ambient surface.

## Decision Rule

Animation can reflect every state. Native notifications cannot.

Deduplicate notifications by:

- Mission id
- event sequence
- pet state

## Acceptance Probe

A 30-minute running Mission must produce no notification spam. It should notify at most once per action-worthy transition.
