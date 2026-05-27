/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
*/
import { Play, Square } from "lucide-react";

function MissionHeader({ busy, mission, onStart, onStop }) {
  const canStart = mission && !["running", "stopping", "completed"].includes(mission.status);
  const canStop = mission?.status === "running";
  const title = mission?.title || "Create mission";

  return (
    <div className="panel-head mission-head">
      <div>
        <p className="eyebrow">Mission</p>
        <h2>{title}</h2>
        {mission?.goal && <p className="mission-goal">{mission.goal}</p>}
      </div>
      <div className="panel-actions">
        <span className="chip">{mission?.status || "empty"}</span>
        <button className="primary-button" disabled={busy || !canStart} onClick={onStart} type="button">
          <Play size={16} />
          <span>Start</span>
        </button>
        <button className="secondary-button" disabled={busy || !canStop} onClick={onStop} type="button">
          <Square size={16} />
          <span>Stop</span>
        </button>
      </div>
    </div>
  );
}

export default MissionHeader;
