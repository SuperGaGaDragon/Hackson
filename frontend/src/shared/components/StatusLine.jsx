/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
*/
function StatusLine({ error, loading, text }) {
  if (error) return <p className="status-line error">{error}</p>;
  if (loading) return <p className="status-line">{text || "Loading"}</p>;
  if (text) return <p className="status-line">{text}</p>;
  return null;
}

export default StatusLine;
