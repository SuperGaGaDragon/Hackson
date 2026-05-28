## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 10: Default Agent Origin Stories

## Problem

Nora and Vale currently seed with thin episode-state text such as helping Hackson run a V1 demo. That makes the two-Agent world feel like a prompt scaffold instead of two persistent characters with a relationship, memory surface, and psychological continuity.

For a hackathon demo, first contact matters. Empty or shallow Agent stories weaken the product promise that Hackson is a living two-Agent context runtime.

## Self Grill

Q: Should the default stories be short?

A: No. The `story` field is already a bounded editable context field, not a badge. A short line works for a status label but not for the Agent's life history.

Q: Should the stories be fantasy lore?

A: No. They should feel human and psychologically specific. The product shock should come from depth, contrast, and continuity, not from supernatural framing.

Q: Should the stories mention Hackson?

A: Only indirectly through their current operating posture. The story should explain why Nora and Vale behave the way they do across Idle, Companion, and Work, not advertise the app.

Q: Should existing users be forced to use the new stories?

A: Existing user edits must be preserved. Empty Agent story fields and known old demo placeholders may be normalized to the new defaults because they are not meaningful user-authored content.

Q: Are user-editable Skills part of this change?

A: No. Skills are a promising next layer, but they require a separate product contract: who owns them, whether they affect prompts, how they are scoped, and how misuse is prevented. This issue only upgrades default Agent stories.

## Decision

- Seed Nora and Vale with detailed English origin stories.
- Keep the stories under the current 4000-character bound per Agent.
- Use the same default stories in backend registration, backend normalization, prompt snapshots, and frontend fallback.
- Normalize old empty or demo-placeholder Agent stories to the richer defaults.
- Do not implement user-editable Skills in this slice.

## Acceptance

- New registered users receive non-empty Nora and Vale stories.
- Existing profiles with empty story or the old demo placeholder get the richer default on read.
- Existing user-authored Agent stories are preserved.
- Frontend fallback `Me` state shows the same default stories when backend user data is not available.
- User tests and frontend build pass before deployment.
