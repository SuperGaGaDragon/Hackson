/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex
*/
function SummaryCard({ events }) {
  const summaries = events.filter((event) => event.type === "SUMMARY");
  return (
    <div className="work-card">
      <div className="card-head">
        <p className="eyebrow">Summary</p>
        <span>{summaries.length}</span>
      </div>
      {summaries.length === 0 && <p className="muted">None</p>}
      {summaries.map((event) => (
        <div className="summary-block" key={event.id}>
          <strong>{event.title}</strong>
          <ul>
            {(event.payload?.items || [event.message]).map((item) => (
              <li key={item}>{item}</li>
            ))}
          </ul>
        </div>
      ))}
    </div>
  );
}

export default SummaryCard;
