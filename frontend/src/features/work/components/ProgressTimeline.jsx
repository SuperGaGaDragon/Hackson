/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
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
  "WORK_WINDOW_OPENED",
  "WORK_WINDOW_COMPLETED",
  "WORK_WINDOW_BLOCKED",
  "WORK_WINDOW_FAILED",
  "USER_INPUT_REQUESTED",
  "MISSION_PAUSED_RETRYABLE",
  "MISSION_BLOCKED",
  "MISSION_STOP_REQUESTED",
  "MISSION_STOPPED",
  "MISSION_COMPLETED",
  "MISSION_FAILED",
]);

function ProgressTimeline({ events }) {
  const rows = compactTimeline(events.filter((event) => timelineTypes.has(event.type)));
  return (
    <div className="work-card timeline-card">
      <div className="card-head">
        <p className="eyebrow">Progress</p>
        <span>{rows.length}</span>
      </div>
      <div className="progress-list">
        {rows.length === 0 && <p className="muted">No events</p>}
        {rows.map((event) => {
          const view = eventView(event);
          const Icon = view.icon;
          return (
            <div className={`progress-row event-${view.tone} ${event.type.toLowerCase()}`} key={event.id}>
              <span className="event-icon">
                <Icon size={15} />
              </span>
              <div className="progress-copy">
                <span>
                  <strong>{view.title}</strong>
                  {view.label && <em>{view.label}</em>}
                </span>
                <p>{view.detail}</p>
              </div>
              <small className="event-meta">
                {view.time && <span className="event-time">{view.time}</span>}
                {view.sequence && <span>{view.sequence}</span>}
              </small>
            </div>
          );
        })}
      </div>
    </div>
  );
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
