/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
const failedStatuses = new Set(["failed"]);
const doneStatuses = new Set(["completed"]);
const waitingStatuses = new Set(["waiting_input"]);
const pausedStatuses = new Set(["paused_retryable", "blocked", "stopped", "paused"]);
const runningStatuses = new Set(["running", "stopping"]);
const progressEventTypes = new Set([
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
  "WEB_SEARCH_FAILED",
  "RELIABILITY_REPORTED",
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
  "MISSION_BLOCKED",
  "MISSION_STOP_REQUESTED",
  "MISSION_STOPPED",
  "MISSION_COMPLETED",
  "MISSION_FAILED",
]);
const eventTitles = {
  MISSION_CREATED: "Mission created",
  MISSION_STARTED: "Started",
  STEP_STARTED: "Step started",
  STEP_COMPLETED: "Step done",
  MISSION_PLAN_UPDATED: "Plan",
  MODEL_TURN_STARTED: "Thinking",
  MODEL_TURN_HEARTBEAT: "Working",
  MODEL_TURN_COMPLETED: "Tool selected",
  MODEL_TURN_RETRYING: "Retrying",
  MODEL_TURN_INVALID: "Invalid turn",
  TOOL_CALLED: "Tool",
  PRODUCT_UPDATED: "Product",
  PRODUCT_INSPECTED: "Inspect",
  PRODUCT_REVIEWED: "Review",
  WEB_SEARCH_COMPLETED: "Search",
  WEB_SEARCH_FAILED: "Search failed",
  RELIABILITY_REPORTED: "Reliability",
  WORK_WINDOW_OPENED: "Window",
  WORK_WINDOW_COMPLETED: "Window done",
  WORK_WINDOW_BLOCKED: "Window blocked",
  WORK_WINDOW_FAILED: "Window failed",
  DISCUSSION_WINDOW_OPENED: "Discussion",
  DISCUSSION_WINDOW_COMPLETED: "Discussion done",
  DISCUSSION_WINDOW_BLOCKED: "Discussion blocked",
  DISCUSSION_WINDOW_FAILED: "Discussion failed",
  USER_INPUT_REQUESTED: "Input requested",
  MISSION_PAUSED_RETRYABLE: "Paused",
  MISSION_BLOCKED: "Blocked",
  MISSION_STOP_REQUESTED: "Stopping",
  MISSION_STOPPED: "Stopped",
  MISSION_COMPLETED: "Done",
  MISSION_FAILED: "Failed",
};
export const activeMissionPriority = {
  running: 100,
  waiting_input: 90,
  paused_retryable: 80,
  blocked: 70,
  stopping: 60,
};

export function deriveSitePetState({ activeSummary = null, authenticated, selectedMission, missionDetail, events, error }) {
  if (error) return state("offline", "Offline", "Site offline", "offline");
  if (!authenticated) return state("signedOut", "Sign in", "Sign in", "idle");
  if (!selectedMission) return state("noActiveWork", "No work", "No active work", "idle");

  const mission = missionDetail?.mission || selectedMission;
  const latestEvent = latestRelevantEvent(events || []);
  const latestWindow = latestRunningWindow(missionDetail?.workWindows || []);
  const status = mission?.status || "draft";
  const missionTitle = formatMissionTitle(activeSummary?.primaryTitle || mission?.title || "");
  const missionLabel = missionTitle ? `[${missionTitle}]` : "";
  const line = activeSummary?.activeCount > 1 ? `${missionLabel} +${activeSummary.activeCount - 1}` : missionLabel;

  if (failedStatuses.has(status) || latestEvent?.type === "MISSION_FAILED") {
    return state("failed", "Failed", line || "Task failed", "failed", latestEvent);
  }
  if (doneStatuses.has(status) || latestEvent?.type === "MISSION_COMPLETED") {
    return state("done", "Done", line || "Task done", "done", latestEvent);
  }
  if (waitingStatuses.has(status) || latestEvent?.type === "USER_INPUT_REQUESTED") {
    return state("waiting", "Waiting", line || "Needs you", "waiting", latestEvent);
  }
  if (pausedStatuses.has(status) || ["MISSION_PAUSED_RETRYABLE", "MISSION_BLOCKED"].includes(latestEvent?.type)) {
    return state("paused", "Paused", line || "Task paused", "paused", latestEvent);
  }
  if (latestEvent?.type === "MODEL_TURN_RETRYING") {
    return state("retrying", "Retry", line || "Retrying", "retrying", latestEvent);
  }
  if (latestWindow || latestEvent?.type === "WORK_WINDOW_OPENED") {
    return state("delegating", "Delegate", line || "Delegating", "active", latestEvent);
  }
  if (["PRODUCT_UPDATED"].includes(latestEvent?.type)) {
    return state("writing", "Writing", line || "Writing", "active", latestEvent);
  }
  if (["PRODUCT_INSPECTED", "PRODUCT_REVIEWED"].includes(latestEvent?.type)) {
    return state("reviewing", "Review", line || "Reviewing", "active", latestEvent);
  }
  if (latestEvent?.type === "MODEL_TURN_STARTED") {
    return state("thinking", "Thinking", line || "Thinking", "active", latestEvent);
  }
  if (["MODEL_TURN_HEARTBEAT", "MODEL_TURN_COMPLETED", "TOOL_CALLED"].includes(latestEvent?.type)) {
    return state("working", "Working", line || "Working", "active", latestEvent);
  }
  if (runningStatuses.has(status)) {
    return state("working", "Working", line || "Running", "active", latestEvent);
  }
  return state("idle", "Ready", line || "Ready", "idle", latestEvent);
}

export function latestSequence(events = []) {
  return Math.max(0, ...events.map((event) => Number(event.sequence || 0)));
}

export function deriveProgressSummary({ mission, state: siteState, events = [] }) {
  const title = mission?.title || siteState?.line || "No active work";
  const rows = compactProgressEvents(events)
    .reverse()
    .map(progressRow);
  return {
    title: title || "No active work",
    status: siteState?.label || "Ready",
    detail: siteState?.line || "",
    rows,
    empty: rows.length ? "" : "No progress yet",
  };
}

export function chooseBestMission(rows = [], preferredMissionId = "") {
  const activeRows = activeMissionRows(rows);
  if (!activeRows.length) return null;

  return [...activeRows].sort(compareMissionCandidate)[0] || null;
}

export function summarizeActiveMissions(rows = []) {
  const activeRows = activeMissionRows(rows).sort(compareMissionCandidate);
  if (!activeRows.length) return { activeCount: 0, primaryTitle: "", primaryMissionId: "" };
  const selected = activeRows[0];
  return {
    activeCount: activeRows.length,
    primaryMissionId: selected.mission.id,
    primaryTitle: selected.mission.title || "Work",
  };
}

export function isActiveMissionStatus(status) {
  return Boolean(activeMissionPriority[status]);
}

export function isTerminalMissionStatus(status) {
  return ["completed", "failed", "stopped", "blocked"].includes(status);
}

function state(key, label, line, tone, event = null) {
  return { key, label, line, tone, event };
}

function compareMissionCandidate(left, right) {
  const leftPriority = activeMissionPriority[left.mission.status] || 0;
  const rightPriority = activeMissionPriority[right.mission.status] || 0;
  if (leftPriority !== rightPriority) return rightPriority - leftPriority;
  return timestamp(right.mission.updatedAt) - timestamp(left.mission.updatedAt);
}

function activeMissionRows(rows) {
  return rows.filter((row) => isActiveMissionStatus(row.mission?.status));
}

function compactProgressEvents(events) {
  const rows = [];
  for (const event of events.filter((row) => progressEventTypes.has(row.type))) {
    const previous = rows[rows.length - 1];
    const sameHeartbeat =
      event.type === "MODEL_TURN_HEARTBEAT" &&
      previous?.type === "MODEL_TURN_HEARTBEAT" &&
      previous.payload?.turn === event.payload?.turn;
    if (sameHeartbeat) {
      rows[rows.length - 1] = event;
    } else {
      rows.push(event);
    }
  }
  return rows.sort((left, right) => Number(left.sequence || 0) - Number(right.sequence || 0));
}

function progressRow(event) {
  return {
    id: event.id || `${event.type}-${event.sequence || ""}`,
    title: event.title || eventTitles[event.type] || event.type || "Progress",
    detail: event.message || progressDetailFromPayload(event.payload || {}),
    sequence: event.sequence ? `#${event.sequence}` : "",
    time: formatProgressTime(event.createdAt || event.created_at),
  };
}

function progressDetailFromPayload(payload) {
  if (payload.summary) return payload.summary;
  if (payload.reason) return payload.reason;
  if (payload.tool) return payload.tool;
  if (payload.query) return payload.query;
  return "";
}

function formatProgressTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return new Intl.DateTimeFormat(undefined, {
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

function formatMissionTitle(value) {
  const text = String(value || "").trim();
  if (!text) return "";
  return text.length > 18 ? `${text.slice(0, 17)}...` : text;
}

function timestamp(value) {
  const date = new Date(value || 0);
  return Number.isNaN(date.getTime()) ? 0 : date.getTime();
}

function latestRelevantEvent(events) {
  return [...events]
    .sort((a, b) => Number(a.sequence || 0) - Number(b.sequence || 0))
    .reverse()
    .find((event) => Boolean(event?.type));
}

function latestRunningWindow(workWindows) {
  return [...workWindows]
    .sort((a, b) => String(b.updatedAt || "").localeCompare(String(a.updatedAt || "")))
    .find((window) => window.status === "running");
}
