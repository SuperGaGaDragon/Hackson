/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex
*/
import StatusLine from "../../../shared/components/StatusLine";

function InspectorPanel({ agentCount = 0, busy, error, mission, project }) {
  return (
    <div className="inspector-panel">
      <div className="panel-head compact">
        <div>
          <p className="eyebrow">Inspector</p>
          <h2>Status</h2>
        </div>
      </div>
      <div className="context-item">
        <span>Project</span>
        <p>{project?.name || "None"}</p>
      </div>
      <div className="context-item">
        <span>Lead</span>
        <p>{mission?.leadEmployeeName || "Lead"}</p>
      </div>
      <div className="context-item">
        <span>Agents</span>
        <p>{agentCount}</p>
      </div>
      <div className="context-item">
        <span>Step</span>
        <p>{mission?.currentStep || "Idle"}</p>
      </div>
      <div className="context-item">
        <span>Policy</span>
        <p>Supervised</p>
      </div>
      <div className="context-item">
        <span>Approval</span>
        <p>V1 text</p>
      </div>
      <StatusLine error={error} loading={busy} text={busy ? "Working" : ""} />
    </div>
  );
}

export default InspectorPanel;
