## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 22: Product Reader Polish And Artifact Navigation

## 1. Self Grill

Q: What is wrong in the current Product reader?

A: The Artifact lineage is rendered as a wrapping card grid. Long Chinese titles control row height, short titles leave dead space, and the selected `All` card is visually heavier than the actual reader. This makes the Product surface feel like debug output rather than a polished deliverable reader.

Q: Why is “make cards equal height” not enough?

A: Equal-height cards still put long generated titles in the main visual rhythm. The user is trying to read a Product, not compare title cards. A product-grade reader should make navigation stable and let the text content own the space.

Q: What should the Product reader optimize for?

A: Scanning the Artifact sequence, selecting one Artifact, and reading long-form content. The navigation should be calm, predictable, and dense. The content area should be spacious.

Q: What is the better pattern?

A: A split Product reader:

- Left: fixed-width Artifact navigator.
- Right: full-content reader.
- Navigator rows have fixed rhythm, two-line title clamp, short type badge, and optional active marker.
- `All` is a normal first row, not a giant selected card.

Q: What must not happen?

A: Do not hide earlier Artifacts. Do not make the Product reader look like a marketing card deck. Do not let generated title length resize the whole panel. Do not add explanatory UI copy that competes with the content.

## 2. Decision

- Replace the wrapping Artifact card grid with a two-column `Artifact nav + Reader` layout on desktop.
- Collapse to one column on mobile.
- Keep Product tabs compact and above the split only when there are multiple Products.
- Use fixed-height Artifact navigation rows with clamped titles.
- Keep the reader's typography steady and long-form friendly.
- Preserve the existing `All` and single-Artifact behavior.

## 3. Acceptance

- Long and short Artifact titles no longer create uneven card rows.
- `All` does not dominate the Product reader.
- Artifact navigation remains readable and clickable.
- The reader shows full content for `All` and selected Artifact modes.
- Desktop and mobile browser smoke screenshots show no overlapping text or horizontal overflow.
