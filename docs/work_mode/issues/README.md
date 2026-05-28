## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Track technical risks and open implementation issues for the Work Mode final roadmap.
- 架构思路
  - Each issue is a bounded engineering note with decision, risk, and required constraints.
  - `../final_version.md` links to these issues when a version depends on them.
  - Issues are not tickets by themselves; `implementation_plan.md` turns accepted decisions into build steps.

## folder structure
|-README.md issues folder guide
|-issue1-native-tool-calling.md native tool calling migration and JSON fallback
|-issue2-context-budget.md context budget, product manifest, and artifact retrieval
|-issue3-delegate-window.md sequential delegate Agent windows and visibility
|-issue4-retry-resume.md retryable failures, resume semantics, and persistence
|-issue5-streaming.md future streaming and partial tool progress
|-issue6-full-smoke.md full 8000 CJK character smoke acceptance
|-issue7-long-turn-progress.md long model turn progress, bounded retry, and timeout UX
|-issue8-delegate-result-tolerance.md tolerant Delegate result ingestion after public smoke failure

## 代办
- Add implementation issue notes only when the risk changes the Work Mode architecture.
