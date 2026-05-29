## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Work Mode Quality Track

## 1. Purpose

This document defines the V1.0.x quality track after the base V1.0 Mission Runtime works.

It covers:

- V1.0.1 Progress and creation UI cleanup.
- V1.0.2 deterministic product checks.
- V1.0.3 Lead review and Delegate discussion tools.
- V1.0.4 revision lineage.
- V1.0.5 controlled Web Search tool.

This track does not replace the main roadmap versions. Provider-native tool calling remains V1.1. Streaming remains V1.2.

## 2. Self-Grilled Decisions

### 2.1 Is Progress duplication acceptable?

Yes.

`Product` and `Progress` can show related information because they answer different user questions.

- Product answers: what can I read or use?
- Progress answers: what did the Lead decide and when?

Decision:

- Progress MAY show summaries of Product, Plan, Review, Discussion, and Revision events.
- Progress MUST NOT become the full long-form reader.
- Large content opens in Product or a bounded inline details drawer.

### 2.2 Should Progress details open inline or in a modal?

Inline.

Decision:

- Mission Progress rows expand inline.
- One expanded row at a time is preferred.
- Details are bounded summaries, not unbounded Product text.
- Diagnostics remains the raw payload surface.

### 2.3 Should creation controls stay visible after a Mission is selected?

No.

Decision:

- Project rail should show Project, Agents, and Mission list by default.
- Mission creation should move behind a `New Mission` button.
- `New Mission` opens a modal or drawer.
- Completed/running Mission reading should not compete with a permanent create form.

### 2.4 Should review be another hidden model pass?

No for the first version.

Decision:

- `review_product` is a Lead-visible tool.
- The Lead reads bounded Product/Artifact content from context or inspection and calls `review_product`.
- The backend persists a Review Artifact.
- `review_product` does not modify Products and does not finish the Mission.

### 2.5 Should the Lead and Delegate be allowed to discuss?

Yes, with hard bounds.

Decision:

- Add `discuss_with_delegate`.
- It creates a visible Discussion Window.
- It is bound to existing Product, Artifact, or Work Window ids.
- The discussion is short and scoped.
- The discussion produces a Discussion Artifact.
- Discussion does not directly modify Product content.

### 2.6 Should review or discussion overwrite content?

No.

Decision:

- Artifacts remain immutable.
- Review creates a Review Artifact.
- Discussion creates a Discussion Artifact.
- Revision creates a Revision Artifact.
- Final assembly references the chosen current Artifacts.

### 2.7 Should Work Mode allow联网搜索?

Yes, as a controlled backend tool.

Decision:

- Add `web_search` after review/discussion and revision lineage are stable.
- `web_search` returns bounded search results with source links.
- It does not open a browser, execute shell commands, or expose Codex CLI as a tool.
- Search output is an observation and visible event; user-facing writing still requires `work_product`.

### 2.8 Can Codex CLI be the Web Search implementation?

Only behind a provider interface, not as the product tool.

Decision:

- The model-visible tool name remains `web_search`.
- Backend MAY implement a `SearchProvider` using an HTTP search API, model-native search, or a constrained Codex CLI search adapter.
- The provider MUST return the same structured result schema.
- Provider-specific logs MUST stay in Diagnostics, not the Lead context by default.

## 3. Version Sequence

| Version | Name | Scope | Release Gate |
| --- | --- | --- | --- |
| V1.0.1 | Progress Details And New Mission UI | Expandable Progress rows, Mission create modal/drawer, no permanent create form after selection. | Browser smoke verifies Progress detail expansion and selected Project rail cleanup. |
| V1.0.2 | Deterministic Product Checks | Programmatic checks for CJK count, outline/chapter/final presence, lineage, and final references. | Full smoke fails if final Product is too short, outline-only, or hides lineage. |
| V1.0.3 | Review And Discussion Tools | Add `review_product` and `discuss_with_delegate` as model-visible tools. | A review/discussion smoke creates Review and Discussion Artifacts without changing Product content. |
| V1.0.4 | Revision Lineage | Add revision workflow and UI history grouping. | Revision smoke preserves original Artifact and shows review -> discussion -> revision lineage. |
| V1.0.5 | Controlled Web Search | Add `web_search` as a Lead-visible read-only research tool. | Search smoke creates a visible search event, returns bounded sourced results, and a later Product references the search observation without bypassing `work_product`. |
| V1.0.6 | Evaluator Tool And Paper Gate | Add `evaluate_product`, deterministic paper final-draft completion checks, replay mode, lifecycle events, report tool failures, and Reliability UI field coverage. | A paper/research smoke cannot finish with outline-only content, can run Reliability, shows started/reported/failed lifecycle, and blocks completion on no-evidence needs-review reports. |
| V1.0.8 | Command Rail And Compact Reading UI | Refactor selected Project rail into Directory plus Composer and enforce compact default rows for long text. | Browser smoke proves Mission navigation, waiting-input answer, completed follow-up, and long text clamping are usable on desktop and mobile. |
| V1.0.9 | Progress Filters | Add multi-select Progress filters for Thinking, Reliability, Products, Windows, Search, Inputs, and Issues. | Browser smoke proves focused and combined filters isolate matching events without affecting Diagnostics. |

## 4. V1.0.1 UI Contract

Progress details:

- `mission_plan` details show plan steps.
- `work_product` details show Product id, Artifact id, kind, summary, short excerpt, and Product link.
- `delegate_agent` details show brief, expected output, target Product, source Artifacts, and result summary.
- `review_product` details show verdict, score, findings summary, and Review Artifact link.
- `discuss_with_delegate` details show participants, linked Artifact/Window, summary, and Discussion Artifact link.
- `web_search` details show query, result count, source links, and whether results were truncated.
- Full long-form content stays in Product.

Project rail:

- Default selected-project rail shows Project name, Agents, Mission list, and `New Mission`.
- Create fields are hidden until the user opens the modal/drawer.
- Completed Missions should present reading/review context, not permanent creation controls.

## 5. V1.0.2 Deterministic Checks

Deterministic checks are backend-owned and model-independent.

Initial checks:

- `final_artifact_cjk_min`.
- `has_outline_artifact`.
- `has_chapter_artifact`.
- `has_final_artifact`.
- `final_product_ids_exist`.
- `final_artifact_ids_exist`.
- `product_lineage_visible_in_api`.
- `not_outline_only_final`.

These checks may run inside smoke tests first. They may later become a model-visible `check_product` tool if the Lead needs structured observations before finishing.

## 6. V1.0.3 Tool Design

### 6.1 `review_product`

Purpose:

- Let the Lead create a structured review of Products or Artifacts.

Output:

- Persist a Review Artifact.
- Emit `PRODUCT_REVIEWED`.
- Return review status to Lead.

It MUST NOT:

- Modify Product content.
- Mark Mission completed.
- Call Delegate.

### 6.2 `discuss_with_delegate`

Purpose:

- Let the Lead ask the non-lead Agent a short scoped question about prior work.

Output:

- Create a Discussion Window.
- Persist a Discussion Artifact.
- Emit discussion window events.
- Return a summary observation to Lead.

It MUST NOT:

- Modify Product content.
- Finish Mission.
- Delegate recursively.
- Run unbounded chat.

## 7. V1.0.4 Revision Design

Revision creates new Artifacts.

Expected lineage:

```text
Original Artifact
  -> Review Artifact
  -> Discussion Artifact optional
  -> Revision Artifact
  -> Final Artifact
```

Product UI:

- Default reader shows current recommended content.
- History is available per section/artifact.
- Original, Review, Discussion, and Revision are all retained.
- V1.0.4 can start without diff view; version chain is required.

## 8. V1.0.5 Web Search Design

`web_search` is a read-only research tool.

Purpose:

- Let the Lead retrieve external facts or references when the Mission needs current or niche information.
- Keep source links visible to the user.
- Keep provider behavior behind a backend interface.

Output:

- Emit `WEB_SEARCH_COMPLETED`.
- Return a bounded observation containing query, results, source URLs, snippets, and truncation metadata.
- MAY persist a Research Artifact when results need to be referenced in Product lineage.

It MUST NOT:

- Modify Product content.
- Finish Mission.
- Run browser automation.
- Run shell/file/Codex CLI as a model-visible tool.
- Inject unbounded page text into the Lead context.

Provider rule:

- Codex CLI MAY be used only as an internal `SearchProvider` implementation after a smoke proves it returns structured search results.
- The model-visible contract MUST remain stable if the provider changes.

## 9. Open Risks

- Review can become vague unless findings are structured and evidence-backed.
- Discussion can become a chat sink unless turn count and scope are hard bounded.
- Context can overflow if review/discussion include full long-form content.
- UI can become noisy if Review, Discussion, and Revision are flat siblings with no grouping.
- Web search can pollute writing with weak sources unless result count, snippets, and source visibility are bounded.
- Search providers can fail or rate-limit independently from the model provider, so failures must become tool observations or retryable pauses, not silent hallucinated facts.
- Evaluator reports can feel authoritative unless no-evidence and unsupported-profile cases are visibly capped at human review.
- Paper/research gates can accidentally hard-code a workflow if they validate process instead of final deliverable shape.
- A persistent Composer can become a fake chat box unless every action maps to a persisted Mission event.
- Long-text clamping can hide important failure detail unless every compact row has an explicit expansion path.
- Progress filters can hide important work if the selected state is unclear; counts and an obvious `All` filter are required.

## 10. 代办

- Implement V1.0.1 first because it is low-risk and improves current usability.
- Implement V1.0.2 before model review tools so release gates stay deterministic.
- Implement V1.0.3 only after Review and Discussion Artifacts are represented in Product lineage.
- Implement V1.0.5 only after `web_search` has deterministic fake-provider tests and target-machine smoke coverage.
- Implement V1.0.6 only as a quality gate and model-visible evaluator tool; do not hard-code research writing order.
- Implement `issues/issue14-tool-rejection-recovery.md` before target release because deterministic quality gates must be model-correctable, not background-runner crashes.
- Implement `issues/issue33-command-rail-and-compact-reading-ui.md` after resume/follow-up/input endpoints are stable; do not expose running-message UI until backend event semantics exist.
- Implement `issues/issue34-progress-filters.md` with client-side filtering first; server-side event filtering is not needed until event volume proves it.
