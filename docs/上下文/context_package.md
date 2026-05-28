## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Context Package Design

## 1. Purpose

This document defines what a model sees and what the backend records for diagnosis.

## 2. Required Package Metadata

Every model-backed turn SHOULD produce:

```json
{
  "id": "context_package_1",
  "mode": "idle",
  "recipeVersion": "idle_v1",
  "conversationId": "conversation_1",
  "targetAgentId": "agent_1",
  "promptHash": "sha256...",
  "tokenEstimate": 1200,
  "budget": {
    "maxContextTokens": 6000,
    "recentMessageLimit": 12
  },
  "includedMessageIds": ["message_1"],
  "includedSummaryIds": ["summary_1"],
  "includedMemoryIds": ["memory_1"],
  "includedAgentIds": ["agent_1", "agent_2"],
  "debugNotes": ["mode=idle", "summary=enabled"],
  "fullPromptLogging": {
    "enabled": true,
    "promptTextStored": true
  }
}
```

Full Prompt Logging defaults on for new users in V1.0. A user can disable it, and packages created after disablement must omit full prompt text while still storing auditable metadata.

Retention:

- Full prompt text is retained for 30 days.
- Turning Full Prompt Logging off does not delete existing retained full prompt text.
- Delete Prompt Logs removes retained full prompt text while keeping package metadata.

## 3. Source Priority

High priority:

- system safety policy.
- current mode.
- current user action.
- target Agent core persona.
- speaker boundary rules.

Medium priority:

- recent raw visible messages.
- current topic direction.
- transition context.
- user profile fields.

Low priority:

- older summaries.
- memory cards.
- diary or relationship background.

## 4. Recipe Rules

### Idle

Idle includes:

- current speaking Agent.
- other Agent brief.
- user profile when relevant.
- topic direction as steering metadata.
- latest idle transcript.
- idle summary.
- idle relationship memory.
- relationship stance between the two Agents.
- one turn intent for the current reply.

Idle must not include:

- Work task memory.
- Companion-only private memory by default.
- hidden debug notes as visible output.
- stacked advice frameworks unless the user directly asks for a method.

Idle dialogue rules:

- Respond to the previous Agent's concrete line.
- Make one conversational move, not a full essay.
- Allow disagreement, softening, or uncertainty when it fits persona.
- Prefer short human turns over polished coaching.

### Companion 1

Companion 1 includes:

- current user message.
- transition context from parent idle.
- child conversation recent messages.
- parent idle recent messages as background.
- parent idle summary.
- idle relationship memory for parent Idle background.
- companion user memory for user preferences.

Companion 1 must not include Work memory by default.

### Companion 2

Companion 2 includes:

- current user message.
- current companion recent messages.
- target Agent persona.
- user profile.
- companion memory.

## 5. Budget Rules

- Keep newest raw turns.
- Summarize or omit older turns.
- Record omissions in debug notes.
- Use model-aware token limits when runtime config exposes them.
- Do not rely on raw character count as the final budget mechanism for production.

Latency targets:

- Idle Tick: p50 under 6s, p95 under 20s.
- Idle Say: p50 under 8s, p95 under 25s.
- Idle Join: p50 under 10s, p95 under 30s.
- Companion turns: p50 under 8s, p95 under 25s.

## 6. 代办

- Add storage schema once the repository implementation is selected.
