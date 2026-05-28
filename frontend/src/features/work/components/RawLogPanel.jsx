/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { formatEventTime } from "./eventDisplay";

function RawLogPanel({ events }) {
  return (
    <details className="raw-log-panel">
      <summary>
        <p className="eyebrow">Diagnostics</p>
        <span>{events.length}</span>
      </summary>
      <pre>{events.map(formatDiagnosticEvent).join("\n\n") || "No events"}</pre>
    </details>
  );
}

function formatDiagnosticEvent(event) {
  const payload = Object.keys(event.payload || {}).length > 0 ? `\n${JSON.stringify(event.payload, null, 2)}` : "";
  return `[${event.sequence}] ${formatEventTime(event)} ${event.type} ${event.title || ""}\n${event.message || ""}${payload}`;
}

export default RawLogPanel;
