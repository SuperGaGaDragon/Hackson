## header
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

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
|-issue9-work-ui-information-architecture.md Work UI hierarchy, Product lineage, Progress, and Diagnostics decisions
|-issue10-product-reader-final-lineage.md final Product reader must keep all Artifacts readable after Done
|-issue11-progress-details-and-create-modal.md Progress inline details and selected Project rail creation cleanup
|-issue12-review-discussion-tools.md Lead review and Delegate discussion tool design
|-issue13-revision-lineage.md immutable revision lineage after review/discussion
|-issue16-web-search-tool.md controlled read-only Web Search tool for external references
|-issue17-restart-recovery.md startup recovery for interrupted running Missions
|-issue18-codex-cli-process-lifecycle.md Codex CLI provider process-group cleanup after success, failure, and timeout
|-issue19-lead-delegate-timeout-budget.md role-specific timeout budgets for Lead, Delegate, and provider calls
|-issue20-tool-use-soft-guidance.md Lead context guidance for more active use of search, review, and discussion tools
|-issue21-v12-streaming-execution-spec.md SSE event-log streaming contract and implementation constraints
|-issue22-web-search-query-fallback.md web search query fallback, domain post-filtering, and effective query visibility
|-issue23-product-reader-polish.md Product reader split layout and fixed-rhythm Artifact navigation
|-issue24-empty-model-output-retryable.md empty model output maps to retryable pause instead of hard Mission failure
|-issue25-model-context-json-safety.md model-call context serialization boundary for datetime/ObjectId safety
|-issue26-latest-event-window.md Mission detail must return the latest bounded event window
|-issue27-completed-mission-follow-up.md completed Missions can continue through user follow-up runs
|-issue28-requirement-grill.md bounded Lead requirement clarification protocol
|-issue29-research-paper-final-draft-gate.md deterministic final-draft gate for paper/research deliverables
|-issue30-evaluator-leader-tool.md backend-owned Reliability evaluator as a model-visible Leader tool
|-issue31-discussion-result-tolerance-and-schema-feedback.md tolerant Discussion ingestion and actionable Lead schema feedback
|-issue32-resumable-failure-and-pause-resume-controls.md resumable invalid-turn exhaustion and stateful Start/Pause/Resume controls
|-issue33-command-rail-and-compact-reading-ui.md selected Project rail as Directory plus Composer, and compact long-text display rules

## 代办
- Add implementation issue notes only when the risk changes the Work Mode architecture.
