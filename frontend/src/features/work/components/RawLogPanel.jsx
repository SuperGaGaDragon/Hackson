/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex
*/
function RawLogPanel({ events }) {
  const logs = events.filter((event) => event.type === "RAW_LOG");
  return (
    <div className="raw-log-panel">
      <div className="card-head">
        <p className="eyebrow">Logs</p>
        <span>{logs.length}</span>
      </div>
      <pre>{logs.map((event) => `[${event.sequence}] ${event.payload?.text || event.message}`).join("\n") || "No logs"}</pre>
    </div>
  );
}

export default RawLogPanel;
