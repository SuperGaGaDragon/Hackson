/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex
*/
function WarningCard({ events }) {
  const warnings = events.filter((event) => event.type === "WARNING" || event.type === "MISSION_FAILED");
  return (
    <div className="work-card warning-panel">
      <div className="card-head">
        <p className="eyebrow">Warnings</p>
        <span>{warnings.length}</span>
      </div>
      {warnings.length === 0 && <p className="muted">Clear</p>}
      {warnings.map((event) => (
        <div className="warning-item" key={event.id}>
          <strong>{event.title}</strong>
          <p>{event.message}</p>
        </div>
      ))}
    </div>
  );
}

export default WarningCard;
