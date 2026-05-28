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
export const activeMissionPriority = {
  running: 100,
  waiting_input: 90,
  paused_retryable: 80,
  blocked: 70,
  stopping: 60,
};

export function deriveSitePetState({ activeSummary = null, authenticated, selectedMission, missionDetail, events, error }) {
  if (error) return state("offline", "Offline", "网站连不上。", "offline");
  if (!authenticated) return state("signedOut", "Sign in", "先登录。", "idle");
  if (!selectedMission) return state("noActiveWork", "No work", "No active work", "idle");

  const mission = missionDetail?.mission || selectedMission;
  const latestEvent = latestRelevantEvent(events || []);
  const latestWindow = latestRunningWindow(missionDetail?.workWindows || []);
  const status = mission?.status || "draft";
  const missionTitle = formatMissionTitle(activeSummary?.primaryTitle || mission?.title || "");
  const missionLabel = missionTitle ? `[${missionTitle}]` : "";
  const line = activeSummary?.activeCount > 1 ? `${missionLabel} +${activeSummary.activeCount - 1}` : missionLabel;

  if (failedStatuses.has(status) || latestEvent?.type === "MISSION_FAILED") {
    return state("failed", "Failed", line || "任务失败。", "failed", latestEvent);
  }
  if (doneStatuses.has(status) || latestEvent?.type === "MISSION_COMPLETED") {
    return state("done", "Done", line || "任务完成。", "done", latestEvent);
  }
  if (waitingStatuses.has(status) || latestEvent?.type === "USER_INPUT_REQUESTED") {
    return state("waiting", "Waiting", line || "需要你。", "waiting", latestEvent);
  }
  if (pausedStatuses.has(status) || ["MISSION_PAUSED_RETRYABLE", "MISSION_BLOCKED"].includes(latestEvent?.type)) {
    return state("paused", "Paused", line || "任务暂停。", "paused", latestEvent);
  }
  if (latestEvent?.type === "MODEL_TURN_RETRYING") {
    return state("retrying", "Retry", line || "正在重试。", "retrying", latestEvent);
  }
  if (latestWindow || latestEvent?.type === "WORK_WINDOW_OPENED") {
    return state("delegating", "Delegate", line || "分工中。", "active", latestEvent);
  }
  if (["PRODUCT_UPDATED"].includes(latestEvent?.type)) {
    return state("writing", "Writing", line || "产物更新。", "active", latestEvent);
  }
  if (["PRODUCT_INSPECTED", "PRODUCT_REVIEWED"].includes(latestEvent?.type)) {
    return state("reviewing", "Review", line || "检查中。", "active", latestEvent);
  }
  if (latestEvent?.type === "MODEL_TURN_STARTED") {
    return state("thinking", "Thinking", line || "思考中。", "active", latestEvent);
  }
  if (["MODEL_TURN_HEARTBEAT", "MODEL_TURN_COMPLETED", "TOOL_CALLED"].includes(latestEvent?.type)) {
    return state("working", "Working", line || "执行中。", "active", latestEvent);
  }
  if (runningStatuses.has(status)) {
    return state("working", "Working", line || "运行中。", "active", latestEvent);
  }
  return state("idle", "Ready", line || "等待开始。", "idle", latestEvent);
}

export function latestSequence(events = []) {
  return Math.max(0, ...events.map((event) => Number(event.sequence || 0)));
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
