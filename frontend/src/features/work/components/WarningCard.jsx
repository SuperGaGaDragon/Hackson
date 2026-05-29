/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex
*/
const WARNING_TYPES = new Set([
  "WARNING",
  "MISSION_FAILED",
  "MISSION_BLOCKED",
  "MISSION_PAUSED_RETRYABLE",
  "MISSION_PAUSE_REQUESTED",
  "MISSION_PAUSED",
  "MODEL_TURN_RETRYING",
  "WORK_WINDOW_FAILED",
  "USER_INPUT_REQUESTED",
  "MODEL_TURN_INVALID",
  "EVALUATION_FAILED",
  "WEB_SEARCH_FAILED",
]);

function WarningCard({ events = [], mission = null }) {
  const { active, resolved } = deriveWarnings(events, mission);
  return (
    <div className="work-card warning-panel">
      <div className="card-head">
        <p className="eyebrow">Warnings</p>
        <span>{active.length}</span>
      </div>
      {active.length === 0 && <p className="muted">Clear</p>}
      {active.map((event) => (
        <div className="warning-item" key={event.id}>
          <strong>{event.title}</strong>
          <p>{event.message}</p>
        </div>
      ))}
      {resolved.length > 0 && (
        <details className="warning-resolved">
          <summary>{resolved.length} resolved</summary>
          {resolved.slice(0, 4).map((event) => (
            <p key={event.id}>{event.title}</p>
          ))}
        </details>
      )}
    </div>
  );
}

function deriveWarnings(events, mission) {
  const warnings = events.filter((event) => WARNING_TYPES.has(event.type));
  const terminalSequence = latestSequence(
    events,
    new Set(["MISSION_COMPLETED", "MISSION_STOPPED", "MISSION_BLOCKED", "MISSION_FAILED", "MISSION_PAUSED"]),
  );
  const inputReceivedSequence = latestSequence(events, new Set(["USER_INPUT_RECEIVED"]));
  const modelRecoveredSequence = latestSequence(events, new Set(["MODEL_TURN_COMPLETED", "TOOL_CALLED", "MISSION_COMPLETED"]));
  const active = [];
  const resolved = [];

  for (const event of warnings) {
    if (isActiveWarning(event, mission, terminalSequence, inputReceivedSequence, modelRecoveredSequence)) {
      active.push(event);
    } else {
      resolved.push(event);
    }
  }
  return {
    active: active.slice(-4).reverse(),
    resolved: resolved.reverse(),
  };
}

function isActiveWarning(event, mission, terminalSequence, inputReceivedSequence, modelRecoveredSequence) {
  const sequence = event.sequence || 0;
  if (event.type === "MISSION_FAILED") return mission?.status === "failed";
  if (event.type === "MISSION_BLOCKED") return mission?.status === "blocked";
  if (event.type === "MISSION_PAUSED_RETRYABLE") return mission?.status === "paused_retryable";
  if (event.type === "MISSION_PAUSE_REQUESTED") return mission?.status === "stopping";
  if (event.type === "MISSION_PAUSED") return mission?.status === "paused";
  if (event.type === "USER_INPUT_REQUESTED") {
    return mission?.status === "waiting_input" && inputReceivedSequence < sequence;
  }
  if (event.type === "MODEL_TURN_RETRYING" || event.type === "MODEL_TURN_INVALID") {
    return mission?.status === "running" && modelRecoveredSequence < sequence && terminalSequence < sequence;
  }
  if (event.type === "WORK_WINDOW_FAILED") return ["running", "failed", "blocked", "paused_retryable"].includes(mission?.status);
  if (event.type === "EVALUATION_FAILED" || event.type === "WEB_SEARCH_FAILED") return mission?.status === "running";
  return terminalSequence < sequence && !["completed", "stopped"].includes(mission?.status);
}

function latestSequence(events, types) {
  return Math.max(0, ...events.filter((event) => types.has(event.type)).map((event) => event.sequence || 0));
}

export default WarningCard;
