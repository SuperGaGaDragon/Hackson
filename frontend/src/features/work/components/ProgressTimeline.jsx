/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex
*/
import { ChevronDown } from "lucide-react";
import { useState } from "react";
import { eventView } from "./eventDisplay";

const timelineTypes = new Set([
  "MISSION_CREATED",
  "MISSION_STARTED",
  "STEP_STARTED",
  "STEP_COMPLETED",
  "MISSION_PLAN_UPDATED",
  "MODEL_TURN_STARTED",
  "MODEL_TURN_HEARTBEAT",
  "MODEL_TURN_COMPLETED",
  "MODEL_TURN_RETRYING",
  "MODEL_TURN_INVALID",
  "TOOL_CALLED",
  "PRODUCT_UPDATED",
  "PRODUCT_INSPECTED",
  "PRODUCT_REVIEWED",
  "WEB_SEARCH_COMPLETED",
  "SEARCH_SUMMARY_CREATED",
  "WEB_SEARCH_FAILED",
  "EVALUATION_STARTED",
  "RELIABILITY_REPORTED",
  "EVALUATION_FAILED",
  "WORK_WINDOW_OPENED",
  "WORK_WINDOW_COMPLETED",
  "WORK_WINDOW_BLOCKED",
  "WORK_WINDOW_FAILED",
  "DISCUSSION_WINDOW_OPENED",
  "DISCUSSION_WINDOW_COMPLETED",
  "DISCUSSION_WINDOW_BLOCKED",
  "DISCUSSION_WINDOW_FAILED",
  "USER_INPUT_REQUESTED",
  "MISSION_PAUSED_RETRYABLE",
  "USER_INPUT_RECEIVED",
  "USER_FOLLOWUP_REQUESTED",
  "USER_INSTRUCTION_ADDED",
  "WARNING",
  "MISSION_PAUSE_REQUESTED",
  "MISSION_PAUSED",
  "MISSION_BLOCKED",
  "MISSION_STOP_REQUESTED",
  "MISSION_STOPPED",
  "MISSION_COMPLETED",
  "MISSION_FAILED",
]);

const progressFilters = [
  { id: "all", label: "All" },
  { id: "thinking", label: "Thinking" },
  { id: "reliability", label: "Reliability" },
  { id: "products", label: "Products" },
  { id: "windows", label: "Windows" },
  { id: "search", label: "Search" },
  { id: "inputs", label: "Inputs" },
  { id: "issues", label: "Issues" },
];

const allFilterId = "all";

const filterTypes = {
  thinking: new Set(["MODEL_TURN_STARTED", "MODEL_TURN_HEARTBEAT", "MODEL_TURN_COMPLETED", "MODEL_TURN_RETRYING", "MODEL_TURN_INVALID", "TOOL_CALLED"]),
  reliability: new Set(["EVALUATION_STARTED", "RELIABILITY_REPORTED", "EVALUATION_FAILED"]),
  products: new Set(["PRODUCT_UPDATED", "PRODUCT_INSPECTED", "PRODUCT_REVIEWED"]),
  windows: new Set([
    "WORK_WINDOW_OPENED",
    "WORK_WINDOW_COMPLETED",
    "WORK_WINDOW_BLOCKED",
    "WORK_WINDOW_FAILED",
    "DISCUSSION_WINDOW_OPENED",
    "DISCUSSION_WINDOW_COMPLETED",
    "DISCUSSION_WINDOW_BLOCKED",
    "DISCUSSION_WINDOW_FAILED",
  ]),
  search: new Set(["WEB_SEARCH_COMPLETED", "SEARCH_SUMMARY_CREATED", "WEB_SEARCH_FAILED"]),
  inputs: new Set(["USER_INPUT_REQUESTED", "USER_INPUT_RECEIVED", "USER_FOLLOWUP_REQUESTED", "USER_INSTRUCTION_ADDED"]),
  issues: new Set([
    "MODEL_TURN_RETRYING",
    "MODEL_TURN_INVALID",
    "WEB_SEARCH_FAILED",
    "EVALUATION_FAILED",
    "WORK_WINDOW_BLOCKED",
    "WORK_WINDOW_FAILED",
    "DISCUSSION_WINDOW_BLOCKED",
    "DISCUSSION_WINDOW_FAILED",
    "MISSION_PAUSED_RETRYABLE",
    "MISSION_BLOCKED",
    "MISSION_FAILED",
    "WARNING",
  ]),
};

function ProgressTimeline({ events }) {
  const [expandedId, setExpandedId] = useState(null);
  const [activeFilters, setActiveFilters] = useState([]);
  const allRows = compactTimeline(events.filter((event) => timelineTypes.has(event.type)));
  const rows = filterRows(allRows, activeFilters);
  const counts = progressFilterCounts(allRows);
  const activeFilterSet = new Set(activeFilters);
  const allFiltersActive = activeFilterSet.size === 0;
  const progressCount = allFiltersActive ? allRows.length : `${rows.length} / ${allRows.length}`;
  const toggleFilter = (filterId) => {
    setExpandedId(null);
    if (filterId === allFilterId) {
      setActiveFilters([]);
      return;
    }
    setActiveFilters((current) => {
      if (current.includes(filterId)) {
        return current.filter((item) => item !== filterId);
      }
      return [...current, filterId];
    });
  };
  return (
    <div className="work-card timeline-card">
      <div className="card-head progress-head">
        <div>
          <p className="eyebrow">Progress</p>
          <span>{progressCount}</span>
        </div>
        <div className="progress-filters" aria-label="Progress filters">
          {progressFilters.map((filter) => {
            const active = filter.id === allFilterId ? allFiltersActive : activeFilterSet.has(filter.id);
            return (
              <button
                aria-pressed={active}
                className={active ? "active" : ""}
                key={filter.id}
                onClick={() => toggleFilter(filter.id)}
                type="button"
              >
                <span>{filter.label}</span>
                <small>{counts[filter.id]}</small>
              </button>
            );
          })}
        </div>
      </div>
      <div className="progress-list">
        {rows.length === 0 && <p className="muted">{allFiltersActive ? "No events" : "No matching events"}</p>}
        {rows.map((event) => {
          const view = eventView(event);
          const Icon = view.icon;
          const expanded = expandedId === event.id;
          return (
            <div className={`progress-row-shell event-${view.tone} ${event.type.toLowerCase()}`} key={event.id}>
              <button
                aria-expanded={expanded}
                className="progress-row"
                onClick={() => setExpandedId(expanded ? null : event.id)}
                type="button"
              >
                <span className="event-icon">
                  <Icon size={15} />
                </span>
                <span className="progress-copy">
                  <span>
                    <strong>{view.title}</strong>
                    {view.label && <em>{view.label}</em>}
                  </span>
                  <p>{view.detail}</p>
                </span>
                <small className="event-meta">
                  {view.time && <span className="event-time">{view.time}</span>}
                  {view.sequence && <span>{view.sequence}</span>}
                  <ChevronDown className="progress-expand-icon" size={14} />
                </small>
              </button>
              {expanded && <ProgressDetail event={event} />}
            </div>
          );
        })}
      </div>
    </div>
  );
}

function filterRows(rows, activeFilters) {
  if (!activeFilters.length) return rows;
  const accepted = new Set();
  for (const activeFilter of activeFilters) {
    const types = filterTypes[activeFilter];
    if (!types) continue;
    for (const type of types) accepted.add(type);
  }
  if (!accepted.size) return rows;
  return rows.filter((event) => accepted.has(event.type));
}

function progressFilterCounts(rows) {
  const counts = { all: rows.length };
  for (const filter of progressFilters) {
    if (filter.id === allFilterId) continue;
    counts[filter.id] = filterRows(rows, [filter.id]).length;
  }
  return counts;
}

function ProgressDetail({ event }) {
  return (
    <div className="progress-detail">
      {progressDetails(event).map((detail) => (
        <div className="progress-detail-item" key={detail.label}>
          <span>{detail.label}</span>
          {detail.kind === "sources" ? <SourceList sources={detail.value} /> : <p>{detail.value}</p>}
        </div>
      ))}
    </div>
  );
}

function SourceList({ sources }) {
  return (
    <ul className="source-list">
      {sources.map((source) => (
        <li key={source.url || source.title}>
          <a href={source.url} rel="noreferrer" target="_blank">
            {source.title || source.source || source.url}
          </a>
          {source.snippet && <p>{source.snippet}</p>}
        </li>
      ))}
    </ul>
  );
}

function progressDetails(event) {
  const payload = event.payload || {};
  const details = [];
  if (payload.reason) details.push({ label: "Reason", value: payload.reason });
  if (payload.tool) details.push({ label: "Tool", value: payload.tool });
  if (payload.planTitle) details.push({ label: "Plan", value: payload.planTitle });
  if (Array.isArray(payload.steps) && payload.steps.length > 0) {
    details.push({
      label: "Steps",
      value: payload.steps.map((step) => `${step.status}: ${step.title}${step.notes ? ` - ${step.notes}` : ""}`).join("\n"),
    });
  }
  if (payload.productId || payload.artifactId || payload.reviewArtifactId) {
    details.push({
      label: "Product",
      value: [
        payload.productId ? `Product ${payload.productId}` : "",
        payload.artifactId ? `Artifact ${payload.artifactId}` : "",
        payload.reviewArtifactId ? `Review ${payload.reviewArtifactId}` : "",
        payload.kind ? `Kind ${payload.kind}` : "",
      ]
        .filter(Boolean)
        .join("\n"),
    });
  }
  if (payload.summary) details.push({ label: "Summary", value: payload.summary });
  if (event.type === "WEB_SEARCH_COMPLETED" || event.type === "WEB_SEARCH_FAILED") {
    details.push({
      label: "Search",
      value: [
        payload.query ? `Query: ${payload.query}` : "",
        payload.provider ? `Provider: ${payload.provider}` : "",
        payload.results ? `Results: ${payload.results.length}` : "",
        payload.truncated != null ? `Truncated: ${payload.truncated ? "yes" : "no"}` : "",
        payload.code ? `Code: ${payload.code}` : "",
      ]
        .filter(Boolean)
        .join("\n"),
    });
    if (Array.isArray(payload.results) && payload.results.length > 0) {
      details.push({ label: "Sources", value: payload.results.slice(0, 5), kind: "sources" });
    }
  }
  if (event.type === "SEARCH_SUMMARY_CREATED") {
    details.push({
      label: "Search summary",
      value: [
        payload.query ? `Query: ${payload.query}` : "",
        payload.effectiveQuery ? `Effective: ${payload.effectiveQuery}` : "",
        payload.productId ? `Product ${payload.productId}` : "",
        payload.artifactId ? `Artifact ${payload.artifactId}` : "",
        payload.sourceCount != null ? `Sources: ${payload.sourceCount}` : "",
      ]
        .filter(Boolean)
        .join("\n"),
    });
  }
  if (payload.arguments) {
    const args = payload.arguments;
    const value = [
      args.productTitle ? `Product: ${args.productTitle}` : "",
      args.artifactTitle ? `Artifact: ${args.artifactTitle}` : "",
      args.artifactKind ? `Kind: ${args.artifactKind}` : "",
      args.contentPreview ? `Excerpt: ${args.contentPreview}` : "",
      args.briefPreview ? `Brief: ${args.briefPreview}` : "",
    ]
      .filter(Boolean)
      .join("\n");
    if (value) details.push({ label: "Arguments", value });
  }
  if (payload.windowId) {
    details.push({
      label: "Window",
      value: [
        `Window ${payload.windowId}`,
        payload.agentSlot ? `Agent ${payload.agentSlot}` : "",
        payload.recommendation ? `Recommendation: ${payload.recommendation}` : "",
      ]
        .filter(Boolean)
        .join("\n"),
    });
  }
  if (payload.verdict || payload.score != null || payload.findings) {
    details.push({
      label: "Review",
      value: [
        payload.verdict ? `Verdict: ${payload.verdict}` : "",
        payload.score != null ? `Score: ${payload.score}` : "",
        Array.isArray(payload.findings)
          ? payload.findings.map((finding) => `${finding.severity}: ${finding.claim}`).join("\n")
          : "",
      ]
        .filter(Boolean)
        .join("\n"),
    });
  }
  if (event.type === "RELIABILITY_REPORTED") {
    details.push({
      label: "Reliability",
      value: [
        payload.score != null ? `Score: ${payload.score}` : "",
        payload.status ? `Status: ${payload.status}` : "",
        payload.mode ? `Mode: ${payload.mode}` : "",
        payload.issueCounts ? `Issues: ${formatIssueCounts(payload.issueCounts)}` : "",
        payload.reportArtifactId ? `Report: ${payload.reportArtifactId}` : "",
      ]
        .filter(Boolean)
        .join("\n"),
    });
  }
  if (event.type === "EVALUATION_STARTED" || event.type === "EVALUATION_FAILED") {
    details.push({
      label: "Evaluation",
      value: [
        payload.profile ? `Profile: ${payload.profile}` : "",
        payload.mode ? `Mode: ${payload.mode}` : "",
        payload.evaluatorVersion ? `Version: ${payload.evaluatorVersion}` : "",
        payload.code ? `Code: ${payload.code}` : "",
      ]
        .filter(Boolean)
        .join("\n"),
    });
  }
  if (payload.error) details.push({ label: "Error", value: payload.error });
  if (payload.question || payload.answer) {
    details.push({
      label: "Input",
      value: [payload.question ? `Question: ${payload.question}` : "", payload.answer ? `Answer: ${payload.answer}` : ""]
        .filter(Boolean)
        .join("\n"),
    });
  }
  if (details.length === 0) {
    details.push({ label: "Event", value: event.message || event.type });
  }
  return details;
}

function formatIssueCounts(issueCounts) {
  return Object.entries(issueCounts)
    .filter(([, count]) => count)
    .map(([key, count]) => `${key} ${count}`)
    .join(", ");
}

function compactTimeline(rows) {
  const compacted = [];
  for (const event of rows) {
    const previous = compacted[compacted.length - 1];
    const sameHeartbeat =
      event.type === "MODEL_TURN_HEARTBEAT" &&
      previous?.type === "MODEL_TURN_HEARTBEAT" &&
      previous.payload?.turn === event.payload?.turn;
    if (sameHeartbeat) {
      compacted[compacted.length - 1] = event;
    } else {
      compacted.push(event);
    }
  }
  return compacted;
}

export default ProgressTimeline;
