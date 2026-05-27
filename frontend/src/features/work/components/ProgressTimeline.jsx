/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex
*/
const timelineTypes = new Set([
  "MISSION_CREATED",
  "MISSION_STARTED",
  "STEP_STARTED",
  "STEP_COMPLETED",
  "MISSION_STOP_REQUESTED",
  "MISSION_STOPPED",
  "MISSION_COMPLETED",
  "MISSION_FAILED",
]);

function ProgressTimeline({ events }) {
  const rows = events.filter((event) => timelineTypes.has(event.type));
  return (
    <div className="work-card timeline-card">
      <div className="card-head">
        <p className="eyebrow">Progress</p>
        <span>{rows.length}</span>
      </div>
      <div className="progress-list">
        {rows.length === 0 && <p className="muted">No events</p>}
        {rows.map((event) => (
          <div className={`progress-row ${event.type.toLowerCase()}`} key={event.id}>
            <span className="progress-dot" />
            <div>
              <strong>{event.title}</strong>
              <p>{event.message}</p>
            </div>
            <small>#{event.sequence}</small>
          </div>
        ))}
      </div>
    </div>
  );
}

export default ProgressTimeline;
