## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 4: Mission Polling And Staleness

## Question

Is polling enough for Desktop Pet V1?

## Recommendation

Yes. Use existing verified Work Mode event polling for V1.

Streaming is valuable later, but V1 should not depend on unverified streaming APIs.

## Risk

Polling can become stale or wasteful, especially if V1.3 watches multiple Missions.

## Decision Rule

V1 polling:

- 1500 ms for running Mission.
- 30 seconds for terminal or paused states.
- exponential backoff on offline failures.
- no fast polling when no Mission is selected.

## Acceptance Probe

During a real Mission:

- pet updates within 2 seconds of event availability
- terminal state stops fast polling
- offline state backs off
- stale running state is visible in popover after 90 seconds without events
