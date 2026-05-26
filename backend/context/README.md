## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex

## brief intro
- goal for this folder.
  - Own context construction: decide what the model should see for each mode.
- 架构思路
  - `context/` is a product module for prompt inputs, not a model-calling module.
  - It builds context packages for idle, companion_1, companion_2, and future work mode.
  - It should stay small and deep in V1. Do not split into many nested folders too early.

## responsibilities
- Build mode-aware context packages.
- Implement idle, companion_1, companion_2, and work recipes.
- Generate Transition Context for users joining idle.
- Combine recent messages with summaries once compaction exists.
- Record context package metadata for debugging.

## not responsible for
- HTTP routes.
- Direct model provider calls.
- User authentication.
- MongoDB connection lifecycle.
- Long-running worker scheduling.

## files
|-README.md module guide
|-__init__.py Python package marker
|-builder.py Context Builder entrypoint
|-recipes.py idle, companion_1, companion_2, and work recipes
|-transition.py Transition Context generation for user joining idle
|-compaction.py summary + recent messages compaction strategy
|-packages.py context package logging, prompt hash, and token estimate helpers
|-schemas.py context input and output schemas
|-tests/ context module tests

## core boundary
```text
context decides: what should the model see?
model_runtime decides: how do we call the model?
conversations decides: how does the product flow proceed?
```

## recipe plan
- `idle`: strong Agent persona, recent idle messages, idle seed, optional summary.
- `companion_1`: Transition Context on join, user message, recent child companion messages, recent idle messages, idle summary, Agent persona.
- `companion_2`: user message, current chat recent messages, Agent persona, lightweight profile.
- `work`: user objective, task state, tool traces, role instructions.

## version plan
- v1.0: `builder.py` and `recipes.py` for idle and companion_2. Implemented as pure context construction.
- v1.1: `transition.py` and companion_1 recipe. Implemented as pure Transition Context generation.
- v1.2: `compaction.py` and `packages.py`. Implemented as lightweight recent-message selection and context package metadata.
- v1.3: Read lightweight memory cards.
- v1.5: Add work recipe.

## implementation notes
- This module does not call model providers.
- This module does not save messages.
- This module does not mutate Agent source records.
- Callers must pass Agent persona snapshots from `agents/`.
- Callers must pass recent messages and summaries from conversation storage.
