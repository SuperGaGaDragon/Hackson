## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 3: Auth Token Storage

## Question

Where should Desktop Pet store the Hackson JWT?

## Recommendation

Use OS-backed secure storage when available. Avoid plain local files for production builds.

## Risk

Desktop clients are harder to secure than browser sessions. Token leakage would expose user Missions, Products, and profile data.

## Decision Rule

V1 must:

- never log tokens
- support sign out
- clear token on 401
- keep backend URL fixed to the public Hackson domain unless developer mode exists

## Acceptance Probe

After login:

- app restart keeps session
- sign out removes session
- 401 clears session
- logs do not include Authorization headers
