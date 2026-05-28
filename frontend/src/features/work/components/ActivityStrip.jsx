/*
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { Wrench } from "lucide-react";
import { eventView } from "./eventDisplay";

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
  const view = eventView(event);
  const tone = view.tone === "done" ? "done" : view.tone === "retry" || view.tone === "danger" ? "retry" : "live";
  return { icon: view.icon, tone, title: view.title, detail: view.detail, meta: view.time || view.sequence };
}

export default ActivityStrip;
