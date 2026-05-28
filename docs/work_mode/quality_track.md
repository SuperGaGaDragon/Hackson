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

## 3. Version Sequence

| Version | Name | Scope | Release Gate |
| --- | --- | --- | --- |
| V1.0.1 | Progress Details And New Mission UI | Expandable Progress rows, Mission create modal/drawer, no permanent create form after selection. | Browser smoke verifies Progress detail expansion and selected Project rail cleanup. |
| V1.0.2 | Deterministic Product Checks | Programmatic checks for CJK count, outline/chapter/final presence, lineage, and final references. | Full smoke fails if final Product is too short, outline-only, or hides lineage. |
| V1.0.3 | Review And Discussion Tools | Add `review_product` and `discuss_with_delegate` as model-visible tools. | A review/discussion smoke creates Review and Discussion Artifacts without changing Product content. |
| V1.0.4 | Revision Lineage | Add revision workflow and UI history grouping. | Revision smoke preserves original Artifact and shows review -> discussion -> revision lineage. |

## 4. V1.0.1 UI Contract

Progress details:

- `mission_plan` details show plan steps.
- `work_product` details show Product id, Artifact id, kind, summary, short excerpt, and Product link.
- `delegate_agent` details show brief, expected output, target Product, source Artifacts, and result summary.
- `review_product` details show verdict, score, findings summary, and Review Artifact link.
- `discuss_with_delegate` details show participants, linked Artifact/Window, summary, and Discussion Artifact link.
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

## 8. Open Risks

- Review can become vague unless findings are structured and evidence-backed.
- Discussion can become a chat sink unless turn count and scope are hard bounded.
- Context can overflow if review/discussion include full long-form content.
- UI can become noisy if Review, Discussion, and Revision are flat siblings with no grouping.

## 9. 代办

- Implement V1.0.1 first because it is low-risk and improves current usability.
- Implement V1.0.2 before model review tools so release gates stay deterministic.
- Implement V1.0.3 only after Review and Discussion Artifacts are represented in Product lineage.
