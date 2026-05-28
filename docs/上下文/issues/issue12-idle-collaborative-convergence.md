## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 12: Idle Collaborative Convergence Protocol

## Problem

Idle already has Relationship Stance, Turn Intent, and anti-checklist rules, but it still does not force Nora and Vale to converge. The result can be two polished Agents repeatedly adding adjacent advice, repeating disagreement in new words, and never deciding whether the remaining difference changes action.

This is not top-tier product behavior. A believable two-Agent discussion should preserve relationship and tension, but it should also know when the group has reached enough agreement.

## Self Grill

Question: Was the collaborative reasoning protocol already implemented?

Answer: No. Existing Idle prompts ask for one conversational move and a response to the previous Agent's concrete line, but they do not require explicit agreement acknowledgment, decision-relevant disagreement, non-repetition, or a stop condition when only emphasis remains.

Question: Should the visible reply always include a formal "what we agree on / unresolved / deciding evidence" block?

Answer: No. That would make Idle feel like meeting minutes. The model should update that shared conclusion internally and use it to choose the next natural conversational move. The formal checklist appears only if the user asks for methodical reasoning.

Question: Should Agents always avoid disagreement?

Answer: No. Meaningful disagreement is part of the product. The rule is that disagreement must change the decision: challenge an assumption, expose a tradeoff, identify a practical risk, improve the criterion, or change the recommended action.

Question: What happens when the remaining disagreement is just tone or emphasis?

Answer: The Agent stops debating. It can say a short settling line and let the next turn move on, rather than inventing another angle.

## Decision

Add an Idle-only Collaborative Convergence Protocol to the context recipe:

- First acknowledge valid reasoning in the previous Agent message.
- Only disagree when the disagreement is decision-relevant.
- Do not restate the same disagreement in different words.
- If no new decision-relevant information exists, settle with a natural equivalent of: "No new disagreement. I accept the current direction."
- Before writing, internally update shared conclusion: what is agreed, what remains unresolved, and what would decide the unresolved point.
- If the remaining disagreement is only about emphasis, stop debating and give a concise settling line.

## Product Constraint

The visible reply remains one human conversational move. The protocol is a reasoning guardrail, not permission to output a formal framework, coaching checklist, or debate report by default.

If the previous visible message is from the user, the Agent answers the user first. The convergence protocol then governs any Agent-Agent reasoning continued afterward; it must not turn a user interjection into a fake debate prompt.

## Required Tests

- Idle prompt includes `Collaborative convergence protocol`.
- Idle prompt includes agreement acknowledgment.
- Idle prompt defines decision-relevant disagreement.
- Idle prompt includes the no-new-disagreement settlement sentence.
- Idle prompt includes the shared conclusion check.
- Idle prompt includes the emphasis-only stop condition.
- Idle prompt keeps user interjections higher priority than Agent-Agent convergence.
- Context eval and HTTP smoke assert that prompt logs retain the protocol after deployment.

## Exit Criteria

Idle Agent-Agent turns can still disagree, but they stop looping once the disagreement no longer changes the recommendation, action, or decision criterion.
