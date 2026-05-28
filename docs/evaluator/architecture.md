## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Evaluator Runtime Architecture

## 1. Purpose

This document defines the V1.0 Research Reliability Report architecture.

Evaluator Runtime inspects a Work Mission and produces a Reliability Report. It does not execute the Mission, replace the Lead Agent, mutate final Product content, or run arbitrary tools.

## 2. Target Shape

```text
React Work Console
  -> FastAPI Work routes
    -> WorkModeService
      -> EvaluatorRuntime
        -> TraceReader
        -> EvidenceLedgerBuilder
        -> RequirementChecker
        -> ClaimExtractor
        -> EvidenceMatcher
        -> FailureModeDetector
        -> ScoreCalculator
        -> ReportWriter
          -> EventRepository
          -> ProductRepository
          -> ArtifactRepository
          -> EvaluationReportRepository
```

V1.0 MAY persist reports as Work Artifacts plus Mission events before adding dedicated evaluation collections. The public architecture still treats Reliability Report, Reliability Issue, and Evidence Ledger as distinct concepts.

## 3. Responsibility Boundaries

### 3.1 Work Routes

Routes MUST:

- Authenticate current user.
- Parse evaluation requests.
- Call WorkModeService or EvaluatorRuntime.
- Return public report response shapes.

Routes MUST NOT:

- Run individual checks inline.
- Build evaluator prompts.
- Hide evaluator limitations.

### 3.2 WorkModeService

WorkModeService MUST:

- Enforce Mission ownership.
- Provide Mission detail: Mission, runs, events, Products, Artifacts, Work Windows.
- Persist report events and report Artifacts through existing Work Mode primitives.

WorkModeService MUST NOT:

- Decide evaluator score itself.
- Mutate Product content based on an evaluation.
- Treat evaluator score as Mission completion truth.

### 3.3 EvaluatorRuntime

EvaluatorRuntime MUST:

- Load one Mission's visible state.
- Build an Evidence Ledger from allowed trace material.
- Run deterministic and model-assisted checks.
- Produce structured Reliability Issues.
- Compute a score from issue weights.
- Persist a Reliability Report.

EvaluatorRuntime MUST NOT:

- Read hidden chain-of-thought.
- Search the web directly in V1.0 unless through the same controlled Work Mode search provider.
- Store raw unbounded webpages.
- Rewrite the final Product.
- Finish, block, or stop the Mission directly.

### 3.4 TraceReader

TraceReader MUST:

- Read Work Mode events in sequence order.
- Normalize tool calls, tool observations, model-turn failures, and terminal events.
- Preserve event ids and sequence numbers for report references.

TraceReader MUST NOT:

- Infer hidden reasoning.
- Treat all event payloads as evidence.

### 3.5 EvidenceLedgerBuilder

EvidenceLedgerBuilder MUST:

- Collect allowed source material from search events, Research Artifacts, inspected snippets, and source-linked Artifacts.
- Normalize source urls.
- Preserve snippet boundaries.
- Track which trace event or Artifact produced each evidence item.

EvidenceLedgerBuilder MUST NOT:

- Include arbitrary final answer text as external evidence.
- Inflate snippets into unsupported page content.

### 3.6 Check Modules

Check modules MUST:

- Return structured issues, not free-form prose.
- Include severity, issue type, references, and suggested fix.
- Distinguish unsupported from weakly supported when possible.

Check modules SHOULD:

- Use deterministic rules where they are reliable.
- Use model-assisted judging only behind structured schemas.

### 3.7 ReportWriter

ReportWriter MUST:

- Persist the report payload.
- Persist a user-readable report Artifact.
- Emit `RELIABILITY_REPORTED`.
- Preserve report version and evaluation profile.

ReportWriter MUST NOT:

- Overwrite previous reports.
- Hide previous report versions.

## 4. Data Flow

```text
POST /api/work/missions/{missionId}/evaluate
  -> require Mission ownership
  -> detail = WorkModeService.get_mission_detail()
  -> trace = TraceReader.from_detail(detail)
  -> ledger = EvidenceLedgerBuilder.from_trace(trace)
  -> requirements = RequirementChecker.extract(goal)
  -> claims = ClaimExtractor.extract(final artifacts)
  -> issues = checks(requirements, claims, ledger, trace)
  -> score = ScoreCalculator.compute(issues)
  -> report = ReportWriter.persist(score, issues, ledger summary)
  -> return Mission detail with report
```

V1.0 may also run evaluation automatically after `MISSION_COMPLETED` for Research Missions.

## 5. Persistence Concepts

Evaluator Runtime records:

- Evaluation Run: one attempt to evaluate a Mission.
- Reliability Report: the versioned outcome of an Evaluation Run.
- Reliability Issue: one concrete failure or risk.
- Evidence Item: one source snippet or trace-backed support item.
- Requirement Item: one atomic requirement derived from the Mission goal.
- Claim Item: one factual claim extracted from Product content.

First implementation options:

- Store report JSON in `work_artifacts.metadata.reportPayload`.
- Store user-readable report as a `report` Artifact.
- Emit report lifecycle through `work_events`.

Later implementation MAY add dedicated collections:

- `work_evaluation_runs`
- `work_reliability_reports`
- `work_reliability_issues`

## 6. Existing Code Mapping

Likely backend additions:

- `backend/work_mode/evaluator.py`
- `backend/work_mode/evaluator_schemas.py`
- `backend/work_mode/evaluator_prompts.py`
- `backend/work_mode/evaluator_repository.py` if dedicated collections are needed.
- `backend/work_mode/search.py` for controlled search if not already implemented.
- tests under `backend/work_mode/tests/`

Likely frontend additions:

- `frontend/src/features/work/components/ReliabilityPanel.jsx`
- report badges in `InspectorPanel`
- report event rendering in `ProgressTimeline`

## 7. Model Use

Evaluator Runtime may call a model for:

- Requirement extraction.
- Claim extraction.
- Claim-to-evidence support judgement.
- Report summary wording.

Every evaluator model call MUST:

- Use structured JSON output.
- Be recoverable with deterministic fallback or explicit failure issue.
- Avoid asking "is this good?" as a vague prompt.
- Include only bounded evidence snippets.

## 8. Non-Goals

V1.0 MUST NOT implement:

- Universal agent evaluation.
- Full browser browsing.
- Full page crawling.
- Formal truth verification.
- User-configurable custom evaluator prompts.
- Continuous project-level analytics.
- Autonomous email sending.
- Product auto-rewrite after evaluation.
