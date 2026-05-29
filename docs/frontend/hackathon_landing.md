## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Parallex Hackathon Landing Page

## Purpose

`https://hackson.catachess.com/` is the QR-code entry for the TMLS Agentic Hackathon. The domain and backend deployment
remain on the existing Hackson infrastructure, but the public product brand shown to visitors is `Parallex`.

The unauthenticated root route must feel like a polished product entry, not a login/register form and not a mascot-led
prototype. It should explain the product with strong typography, restrained interaction-system visuals, and a low-friction
trial path.

## Self-Grilled Decisions

Question: Should the QR code point to a separate `/demo` path?

Decision: No for the hackathon. The confirmed QR target is `https://hackson.catachess.com/`, so the root route must
be the landing page when the visitor is not authenticated.

Question: Should the public product still be called Hackson?

Decision: No. The user-facing brand is `Parallex`. Do not rename backend packages, database names, environment variable
names, smoke script filenames, or existing public URL in this pass. Those are infrastructure compatibility details. The
landing page, auth page, and app shell brand labels should say `Parallex`.

Question: Is Quick Try allowed to be a frontend-only fake user?

Decision: No. Work, Idle, Me, Product lineage, memory, and permissions all depend on real backend user identity. Quick
Try must create a real temporary user and return a normal JWT.

Question: Should temporary progress be recoverable?

Decision: Not in V1. The CTA copy must be explicit: Quick Try is fast, temporary, and not recoverable if the browser
session is closed or the user switches accounts.

Question: Should registration still exist?

Decision: Yes, but it becomes the secondary path. Normal account creation is for people who want to keep progress.

Question: What should the product say in one line?

Decision: Use a concrete agentic-product line, not hype. The page should lead with:

```text
Agentic work, made inspectable.
```

Supporting copy may explain that Parallex turns rough intent into missions, product history, and reliability checks.

Question: Should the cat remain on the landing page?

Decision: No. The cat makes the public landing feel less modern and shifts attention away from the core runtime. Keep
the Desktop Pet product concept out of the landing hero. The landing visual should be a CSS-built operator surface:
mission state, product lineage, and reliability signal. Do not use the cat image on this page.

Question: Should the page rely on a long feature explanation?

Decision: No. The previous page asked judges to read too much. The new page must use short, confident copy blocks, more
white space, and a visible system loop. Every paragraph should earn its place.

Question: Should the landing present Idle and Companion as core product value?

Decision: No. The landing must not sell "two AIs chatting" or "another chatbot." It should present the product
hierarchy clearly:

- Core runtime: Context Runtime, Work Mission Runtime, Product/Artifact Lineage, AgentLens Reliability, Memory
  Governance.
- Entry surfaces: Brainstorm, Companion, Work.

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

Question: What visual direction is allowed?

Decision: Typography-led, product-system-led, and calm. Use dark graphite, off-white text, restrained teal, and small
amber/green accents. Avoid cute mascots, gradient blobs/orbs, fake decorative SVG illustrations, and huge paragraphs.
Cards must stay functional, not nested decoration.

## Required Experience

Unauthenticated root page:

- Brand label: `Parallex`.
- Hackathon label: `TMLS Agentic Hackathon`.
- Hero title: `Agentic work, made inspectable.`
- Support line: `Parallex turns rough intent into missions, product history, and reliability checks.`
- CSS-built product preview showing mission runtime, product lineage, and reliability state.
- Primary CTA: `Quick Try`.
- Secondary CTA: `Create Account`.
- Clear temporary-session note near Quick Try.
- A compact product explanation below the hero.
- No cat image.
- No sticky CTA if it adds clutter. The first viewport should make the primary actions obvious.

Authenticated root behavior:

- Existing app behavior remains. Authenticated users enter the app shell, whose visible brand label should be `Parallex`.

Quick Try backend:

- Endpoint creates a real user with generated username/email/password hash.
- User metadata marks it as temporary.
- JWT auth response uses the same shape as register/login.
- Frontend stores this token in session storage so closing the tab loses the quick session.

## Copy Direction

Primary headline:

```text
Agentic work, made inspectable.
```

Hero support:

```text
Parallex turns rough intent into missions, product history, and reliability checks.
```

Short explanation:

```text
Two persistent agents can brainstorm, delegate, revise, and leave a trail you can actually read.
```

CTA copy:

- `Quick Try`
- `Create Account`
- `Temporary session. Close this browser session and the work may be gone.`

Product pillars:

- `Two agents`
- `Mission work`
- `Quality`

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
- `Work`

Forbidden copy:

- `Two agents chat by themselves`
- `AI chatbot`
- `Autonomous employee`
- `Meet Hackson`
- Cat-led or pet-led first-viewport positioning.
- Claims that Companion can inspect Work artifacts by default.
- Claims that Idle already has one-click mission promotion.

## Acceptance

- Logged-out `GET /` renders the hackathon landing, not the old auth form.
- Quick Try creates a real authenticated temporary user and enters the app.
- Create Account opens the normal auth form in register mode.
- Existing login remains accessible.
- Desktop and mobile screenshots have no horizontal overflow and no cramped text columns.
- Public `https://hackson.catachess.com/` serves the landing after deployment.
- Landing copy clearly separates core runtime from entry surfaces.
- Landing does not overclaim unshipped Idle Summary Card, Promote to Work Mission, or Companion Work-context attachment.
- Landing and auth-entry user-visible brand says `Parallex`, while internal route/API names may remain unchanged.
- Landing does not render `/assets/companion-cat-preview.png`.
