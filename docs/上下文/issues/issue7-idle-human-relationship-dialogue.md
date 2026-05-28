## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 7: Idle Human Relationship Dialogue

## Self Grill

Question: Is the sample dialogue bad because the model is weak?

Recommended answer: No. The runtime asks for advice-like continuation. Stronger models will still produce polished consulting text if the recipe rewards framing, conclusions, and helpful exercises.

Question: Is this fix only prompt wording?

Recommended answer: No. The prompt is the first lever, but the product needs explicit dialogue state: relationship stance, turn intent, and anti-advice pressure. Otherwise the system drifts back into "two advice generators taking turns."

Question: What does "human" mean in this product?

Recommended answer: Not fake typos or theatrical emotion. It means each Agent responds to the other Agent's specific previous line, has a recognizable relationship stance, sometimes disagrees or hesitates, and uses one small conversational move instead of a full essay.

Question: Should the Agents always solve the user's topic?

Recommended answer: No. Idle should make the user feel they are overhearing two people think together. Advice is allowed only when grounded in the previous line and limited to one small move.

Question: How do we prevent vague "be natural" instructions from becoming untestable?

Recommended answer: Add deterministic context eval checks:

- prompt includes relationship stance.
- prompt includes turn intent.
- prompt forbids stacked advice/checklists by default.
- prompt requires responding to the previous Agent's concrete line.
- prompt limits each turn to one conversational move.

## Decision

Idle recipes must shift from "helpful topic advice" to "relationship-aware conversational continuation".

Required recipe fields:

- `Relationship stance`: stable shorthand for how the current Agent tends to relate to the other Agent.
- `Turn intent`: one move for this turn, selected from a small set such as `respond`, `disagree`, `soften`, `ask`, `ground`, `shift`.
- `Human dialogue rules`: no stacked frameworks, no repeated advice exercises, respond to the previous Agent's concrete wording, and keep the reply short unless the user directly asks for depth.

## Risk

Overcorrecting can make the Agents shallow or performative. The goal is not random banter. The Agents must still preserve topic direction, speaker boundaries, and persona.

## Required Tests

- Idle prompt includes relationship stance and turn intent.
- Idle prompt tells the model to respond to the previous Agent's concrete line.
- Idle prompt forbids list/checklist/methodology output unless the user directly asks for it.
- Context eval fails if the idle recipe loses human dialogue rules.
- Fake model smoke can detect the new prompt contract and return a relationship-aware short line.

## Exit Criteria

Idle turns stop optimizing for complete advice and instead create a believable two-Agent relationship the user can interrupt.
