## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Context Runtime Architecture

## 1. Purpose

This document defines the Context Runtime architecture for Idle, Companion, and future Work context sharing.

The runtime turns raw product state into model-visible context packages. It does not call model providers, save visible messages, or mutate Agent core persona.

## 2. Target Shape

```text
React UI
  -> FastAPI interaction routes
    -> InteractionService
      -> ConversationService
      -> ContextRuntime
        -> ContextSourceLoader
        -> ContextRecipe
        -> ContextBudgeter
        -> ContextPackageRepository
      -> HacksonOrchestrator
      -> ConversationService.append_message
      -> DerivedJobService.enqueue
    -> WorkerRunner
      -> SummaryWorker
      -> MemoryWorker
      -> RelationshipWorker
      -> DiaryWorker
```

## 3. Responsibility Boundaries

### 3.1 InteractionService

InteractionService MUST:

- Own product flow after a user action or idle tick.
- Decide target Agent through mode policy.
- Ask ContextRuntime for a package.
- Call orchestration.
- Persist visible messages.
- Enqueue derived jobs.

InteractionService MUST NOT:

- Build prompt sections inline.
- Execute summary or memory generation synchronously.
- Mutate Agent core persona.

### 3.2 ContextRuntime

ContextRuntime MUST:

- Load or receive source snapshots needed by the recipe.
- Build deterministic context packages.
- Apply mode-specific recipes.
- Apply budget policy.
- Persist context package metadata.
- Return model-ready messages to orchestration.

ContextRuntime MUST NOT:

- Call model providers.
- Save visible conversation messages.
- Decide HTTP response shapes.
- Run background jobs.

Implementation decision:

- `ContextRuntime` is a facade, not a wholesale replacement for `ContextBuilder`.
- Existing deterministic recipe functions remain behind the facade until a refactor is justified by tests or storage needs.

### 3.3 ContextSourceLoader

ContextSourceLoader MUST:

- Read recent raw messages.
- Read latest summaries.
- Read governed memory cards.
- Read Agent and user profile snapshots.

It must keep storage details out of recipes.

### 3.4 ContextRecipe

Each mode has a recipe:

- `idle`
- `idle_say`
- `companion_1_join`
- `companion_1_followup`
- `companion_2`
- `work`

Recipes define priority, allowed memory scopes, and output constraints.

### 3.5 ContextBudgeter

ContextBudgeter MUST:

- Use model-aware budget config when available.
- Keep high-priority fields stable.
- Prefer latest raw turns over older full transcript.
- Record what was dropped or summarized.

### 3.6 ContextPackageRepository

ContextPackageRepository MUST persist safe metadata for diagnosis:

- package id.
- prompt hash.
- recipe version.
- source ids.
- token estimate.
- budget decision notes.
- model response id when available.

Storage decision:

- Use an independent `context_packages` collection.
- Do not rely only on assistant message metadata for package records.
- Assistant messages should store `context_package_id` and `prompt_hash` for lookup.
- Full prompt text lives only on the package record and only when Full Prompt Logging is enabled.

## 4. Existing Code Mapping

Existing backend modules already cover the first implementation slice:

- `backend/context/` contains builder, recipes, transition, compaction, packages, and schemas.
- `backend/interactions/` owns Idle and Companion product flow.
- `backend/summaries/`, `backend/memory/`, and `backend/workers/` contain early derived-state modules.

The first rewrite should deepen these modules rather than create a parallel runtime.

## 5. Non-Goals

V1.0 MUST NOT implement:

- Full GraphRAG.
- Model-written core persona updates.
- User-owned model endpoint settings.
- Raw chain-of-thought capture.
- Work Mode tool execution changes.

## 6. 代办

- Add exact `context_packages` indexes during implementation.
