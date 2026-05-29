## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Hackathon Landing Page

## Purpose

`https://hackson.catachess.com/` is the QR-code entry for the TMLS Agentic Hackathon. It must not drop first-time
visitors into a plain login/register form. The first screen has to explain the product, show the Desktop Pet cat, and
let judges try the system without account friction.

## Self-Grilled Decisions

Question: Should the QR code point to a separate `/demo` path?

Decision: No for the hackathon. The confirmed QR target is `https://hackson.catachess.com/`, so the root route must
be the landing page when the visitor is not authenticated.

Question: Is Quick Try allowed to be a frontend-only fake user?

Decision: No. Work, Idle, Me, Product lineage, memory, and permissions all depend on real backend user identity. Quick
Try must create a real temporary user and return a normal JWT.

Question: Should temporary progress be recoverable?

Decision: Not in V1. The CTA copy must be explicit: Quick Try is fast, temporary, and not recoverable if the browser
session is closed or the user switches accounts.

Question: Should registration still exist?

Decision: Yes, but it becomes the secondary path. Normal account creation is for people who want to keep progress.

Question: What should the product say in one line?

Decision: Use a concrete agentic-product line, not hype:

```text
Two long-lived agents that talk, remember, delegate, and deliver reviewed work.
```

Question: Should the landing present Idle and Companion as core product value?

Decision: No. The landing must not sell "two AIs chatting" or "another chatbot." It should present the product
hierarchy clearly:

- Core runtime: Context Runtime, Work Mission Runtime, Product/Artifact Lineage, AgentLens Reliability, Memory
  Governance.
- Entry surfaces: Idle, Companion, Desktop Pet.

Idle is described as a low-friction brainstorm entry where a rough topic can become a clearer Work direction. Do not
claim the future `Promote to Work Mission` button exists until that closed loop ships.

Companion is described as a conversational surface for the same two editable Agents and approved memory. Do not claim
it can inspect arbitrary Work artifacts or Reliability reports until explicit context attachment ships.

Question: What should judges understand in the first minute?

Decision: The landing should show the system loop, not a feature list:

```text
Brainstorm -> Mission -> Product -> Quality -> Memory
```

This explains why Idle, Work, AgentLens, and Memory belong together. It also makes Desktop Pet feel like visible
presence rather than the product's main capability.

## Required Experience

Unauthenticated root page:

- Hero title: `TMLS Agentic Hackathon`.
- Strong product line: `Meet Hackson`.
- Cat visual from `frontend/public/assets/companion-cat-preview.png`.
- Primary CTA: `Quick Try`.
- Secondary CTA: `Create Account`.
- Clear temporary-session note near Quick Try.
- A compact product explanation below the hero.
- Sticky or repeated Quick Try CTA so visitors can start from any scroll position.

Authenticated root behavior:

- Existing app behavior remains. Authenticated users enter the Hackson app shell.

Quick Try backend:

- Endpoint creates a real user with generated username/email/password hash.
- User metadata marks it as temporary.
- JWT auth response uses the same shape as register/login.
- Frontend stores this token in session storage so closing the tab loses the quick session.

## Copy Direction

Primary headline:

```text
TMLS Agentic Hackathon
```

Hero support:

```text
Meet Hackson: two long-lived agents that talk, remember, delegate, and deliver reviewed work.
```

Short explanation:

```text
Not a chatbot. Not a coding shell. A supervised workspace where your agents plan, split work, keep context, and ship a
readable Product with a Quality check.
```

CTA copy:

- `Quick Try`
- `Create Account`
- `Temporary session. Close this browser session and the work may be gone.`

Product pillars:

- `Two agents`
- `Mission work`
- `Quality`
- `Desktop pet`

Product architecture copy:

- `Core runtime`
- `Context`
- `Missions`
- `Lineage`
- `Quality`
- `Memory`
- `Entry surfaces`
- `Brainstorm`
- `Companion`
- `Desktop pet`

Forbidden copy:

- `Two agents chat by themselves`
- `AI chatbot`
- `Autonomous employee`
- Claims that Companion can inspect Work artifacts by default.
- Claims that Idle already has one-click mission promotion.

## Acceptance

- Logged-out `GET /` renders the hackathon landing, not the old auth form.
- Quick Try creates a real authenticated temporary user and enters the app.
- Create Account opens the normal auth form in register mode.
- Existing login remains accessible.
- Desktop and mobile screenshots have no horizontal overflow.
- Public `https://hackson.catachess.com/` serves the landing after deployment.
- Landing copy clearly separates core runtime from entry surfaces.
- Landing does not overclaim unshipped Idle Summary Card, Promote to Work Mission, or Companion Work-context attachment.
