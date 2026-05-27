/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
*/
import { ArrowLeft, Plus, UsersRound } from "lucide-react";

function ProjectMissionRail({
  agents,
  busy,
  missionLeadId,
  missionGoal,
  missionTitle,
  missions,
  onBackToWorkspace,
  onCreateMission,
  onMissionLeadChange,
  onMissionGoalChange,
  onMissionTitleChange,
  onSelectMission,
  selectedMission,
  selectedProject,
}) {
  return (
    <aside className="history-rail work-rail">
      <div className="panel-head compact">
        <div>
          <p className="eyebrow">Project</p>
          <h2>{selectedProject?.name || "Project"}</h2>
        </div>
        <button className="icon-button" disabled={busy} onClick={onBackToWorkspace} title="Workspace" type="button">
          <ArrowLeft size={16} />
        </button>
      </div>
      <div className="panel-head compact rail-section">
        <div>
          <p className="eyebrow">Lead</p>
          <h2>Agents</h2>
        </div>
        <UsersRound size={18} />
      </div>
      <div className="agent-choice-list">
        {agents.map((agent) => (
          <button
            aria-pressed={missionLeadId === agent.slot}
            className={`agent-choice ${agent.color} ${missionLeadId === agent.slot ? "active" : ""}`}
            disabled={busy}
            key={agent.slot}
            onClick={() => onMissionLeadChange(agent.slot)}
            type="button"
          >
            <span className="avatar">{agent.short}</span>
            <span>
              <strong>{agent.name}</strong>
              <small>{agent.voice}</small>
            </span>
          </button>
        ))}
      </div>
      <div className="panel-head compact rail-section">
        <div>
          <p className="eyebrow">Project</p>
          <h2>Missions</h2>
        </div>
      </div>
      <div className="work-create">
        <input
          aria-label="Mission title"
          disabled={busy || !selectedProject}
          onChange={(event) => onMissionTitleChange(event.target.value)}
          placeholder="Mission"
          value={missionTitle}
        />
        <textarea
          aria-label="Mission goal"
          disabled={busy || !selectedProject}
          onChange={(event) => onMissionGoalChange(event.target.value)}
          placeholder="Goal"
          value={missionGoal}
        />
        <select
          aria-label="Mission lead"
          disabled={busy || !selectedProject}
          onChange={(event) => onMissionLeadChange(event.target.value)}
          value={missionLeadId}
        >
          {agents.map((agent) => (
            <option key={agent.slot} value={agent.slot}>
              {agent.name}
            </option>
          ))}
        </select>
        <button
          disabled={busy || !selectedProject || !missionTitle.trim() || !missionGoal.trim()}
          onClick={onCreateMission}
          type="button"
        >
          <Plus size={16} />
          <span>Create</span>
        </button>
      </div>
      <div className="history-list">
        {missions.map((mission) => (
          <button
            className={`history-item ${mission.id === selectedMission?.id ? "active" : ""}`}
            key={mission.id}
            onClick={() => onSelectMission(mission)}
            type="button"
          >
            <strong>{mission.title}</strong>
            <span>{mission.status}</span>
          </button>
        ))}
      </div>
    </aside>
  );
}

export default ProjectMissionRail;
