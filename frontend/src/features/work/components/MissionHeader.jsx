/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { Pause, RotateCcw, ShieldCheck } from "lucide-react";

function MissionHeader({
  busy,
  mission,
  onEvaluate,
  onPause,
}) {
  const running = mission?.status === "running";
  const stopping = mission?.status === "stopping";
  const showPrimary = running || stopping;
  const canEvaluate = mission && !["draft", "running", "stopping"].includes(mission.status);
  const title = mission?.title || "Create mission";
  const primaryLabel = stopping ? "Pausing" : "Pause";
  const PrimaryIcon = stopping ? RotateCcw : Pause;

  return (
    <div className="panel-head mission-head">
      <div className="mission-head-main">
        <div>
          <p className="eyebrow">Mission</p>
          <h2>{title}</h2>
          {mission?.goal && <p className="mission-goal">{mission.goal}</p>}
        </div>
        <div className="panel-actions">
          <span className="chip">{mission?.status || "empty"}</span>
          {showPrimary && (
            <button className="primary-button" disabled={busy || stopping} onClick={onPause} type="button">
              <PrimaryIcon size={16} />
              <span>{primaryLabel}</span>
            </button>
          )}
          <button className="secondary-button" disabled={busy || !canEvaluate} onClick={onEvaluate} type="button">
            <ShieldCheck size={16} />
            <span>Check</span>
          </button>
        </div>
      </div>
    </div>
  );
}

export default MissionHeader;
