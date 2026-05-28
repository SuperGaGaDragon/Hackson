## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 8: Me Page Information Architecture And Memory Quality

## 1. Self Grill

Q: What is broken?

A: `Me` currently treats debug artifacts, memory cards, user profile fields, and Agent profile editing as one long form. The ordering is wrong for a product surface: Prompt Logs appear before the user's Agents even though logs are debugging material, not a daily user workflow.

Q: Why does it feel unprofessional?

A: The page has no hierarchy. It shows raw counts, hashes, and large textareas before explaining what the user can actually control. Checkbox rows are visually weak, Prompt Logs flood the viewport, and Agent editing starts below debugging and memory noise.

Q: Should Prompt Logs be visible?

A: Yes, because Full Prompt Logging is user-controlled and useful for debugging. But it belongs under a collapsed `Debug` section. Users should be able to click a log and view full prompt text, but the default page should not be dominated by hashes.

Q: Why is Memory weak?

A: The current relationship worker writes one generic card: `Nora and Vale shared another idle interaction.` This creates the illusion of memory without learning anything. A product-grade memory surface must show useful cards or show nothing. Generic filler memory should not be created.

Q: Should user `Personality` and `Story` exist?

A: Yes, but the names are product-hostile. They are not Agent personality; they are the user's own profile context. They should be grouped under `About You` and labeled as `Style` and `Background`, after Agent editing.

Q: What is the product-grade order?

A:

1. Account basics and compact toggles.
2. Agent profile editor.
3. About You.
4. Memory.
5. Debug, collapsed by default.

Q: What must not happen?

A: Do not hide controls so deeply that debugging becomes impossible. Do not expose raw hidden prompt text by default. Do not create fake memory cards. Do not make the page longer by adding explanatory copy everywhere.

## 2. Decision

- Make Agent editing the primary content of `Me`.
- Move Full Prompt Logging and Prompt Logs into a collapsed Debug area.
- Keep prompt logs clickable with full text visible only when a user expands a row.
- Rename user `Personality` to `Style` and user `Story` to `Background`.
- Redesign memory cards as compact controls grouped below user profile.
- Stop writing generic relationship memories.
- Hide legacy generic relationship memories from user-facing memory reads.
- Relationship memories must summarize evidence from the current idle source messages and require at least two Agent messages.
- Idle relationship jobs must include enough evidence when enqueued; a stricter worker is useless if every job only carries one Agent turn.
- Derived workers must be able to process the current user's jobs even when old global pending jobs exist.

## 3. Acceptance

- First desktop viewport shows account basics and Agent editing, not prompt log rows.
- Prompt Logs are not visible until the user opens `Debug`.
- A prompt log can be expanded and its full prompt text can be read.
- Memory no longer creates `Nora and Vale shared another idle interaction.` from every idle turn.
- Existing legacy cards with that exact generic summary do not appear in Me or context reads.
- Relationship memory, when created, contains content-derived detail from the source messages.
- Public smoke can force-run the current conversation's derived jobs without being blocked by unrelated historical backlog.
- Me browser smoke verifies Debug collapsed by default, Agent editor visible before logs, and prompt log expansion still works.
