/*
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
*/
import { CheckCircle2, Loader2, RotateCw, Wrench } from "lucide-react";

const activeTypes = new Set([
  "MODEL_TURN_STARTED",
  "MODEL_TURN_HEARTBEAT",
  "MODEL_TURN_COMPLETED",
  "TOOL_CALLED",
  "MODEL_TURN_RETRYING",
  "WORK_WINDOW_OPENED",
  "WORK_WINDOW_COMPLETED",
  "WORK_WINDOW_FAILED",
  "MISSION_PAUSED_RETRYABLE",
  "MISSION_COMPLETED",
  "MISSION_FAILED",
]);

function ActivityStrip({ events = [], mission }) {
  const latest = [...events].reverse().find((event) => activeTypes.has(event.type)) || null;
  const state = activityState(latest, mission);
  const Icon = state.icon;

  return (
    <div className={`activity-strip ${state.tone}`}>
      <div className="activity-icon">
        <Icon size={16} />
      </div>
      <div>
        <p>{state.title}</p>
        <span>{state.detail}</span>
      </div>
      <small>{state.meta}</small>
    </div>
  );
}

function activityState(event, mission) {
  if (!event) {
    return { icon: Wrench, tone: "idle", title: "Idle", detail: mission?.status || "draft", meta: "" };
  }
  if (event.type === "MODEL_TURN_STARTED" || event.type === "MODEL_TURN_HEARTBEAT") {
    return { icon: Loader2, tone: "live", title: "Thinking", detail: event.message, meta: `#${event.sequence}` };
  }
  if (event.type === "MODEL_TURN_RETRYING") {
    return { icon: RotateCw, tone: "retry", title: "Retrying", detail: event.message, meta: `#${event.sequence}` };
  }
  if (event.type === "TOOL_CALLED") {
    return { icon: Wrench, tone: "live", title: event.title, detail: event.message, meta: `#${event.sequence}` };
  }
  if (event.type === "MISSION_COMPLETED") {
    return { icon: CheckCircle2, tone: "done", title: "Done", detail: event.message, meta: `#${event.sequence}` };
  }
  if (event.type === "MISSION_PAUSED_RETRYABLE" || event.type === "MISSION_FAILED" || event.type === "WORK_WINDOW_FAILED") {
    return { icon: RotateCw, tone: "retry", title: event.title, detail: event.message, meta: `#${event.sequence}` };
  }
  return { icon: Wrench, tone: "idle", title: event.title, detail: event.message, meta: `#${event.sequence}` };
}

export default ActivityStrip;
