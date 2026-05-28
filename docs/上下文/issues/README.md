## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Track technical risks and open implementation issues for the Context Runtime roadmap.
- 架构思路
  - Each issue is a bounded engineering note with decision, risk, and required constraints.
  - `../final_version.md` links to these issues when a version depends on them.
  - Issues are not tickets by themselves; `../implementation_plan.md` turns accepted decisions into build steps.

## folder structure
|-README.md issues folder guide
|-issue1-context-package-storage.md context package storage and lookup boundary
|-issue2-full-prompt-logging.md full prompt logging privacy, retention, and user controls
|-issue3-background-idle-budget.md background idle budget, cooldown, and default-off constraints
|-issue4-companion1-memory-scope.md companion_1 memory import scope and isolation rule
|-issue5-idle-turn-lock.md idle turn lock and idempotency constraints before background cadence
|-issue6-idle-interruption-queue.md user interjection while idle generation is in flight
|-issue7-idle-human-relationship-dialogue.md relationship-aware idle dialogue quality rules
|-issue8-me-page-information-architecture.md Me page hierarchy, Debug placement, and memory quality
|-issue9-derived-worker-backlog.md derived worker backlog, scoped smoke, and memory freshness

## 代办
- Add implementation issue notes only when the risk changes the Context Runtime architecture.
