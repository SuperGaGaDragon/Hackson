/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { ArrowLeft, Plus, UserRound } from "lucide-react";
import MissionComposer from "./MissionComposer";

function ProjectMissionRail({
  agents,
  answerText,
  busy,
  followUpText,
  inputRequest,
  instructionText,
  missionLeadId,
  missionGoal,
  missionTitle,
  missions,
  onAnswer,
  onAnswerTextChange,
  onBackToWorkspace,
  onCreateMission,
  onFollowUp,
  onFollowUpTextChange,
  onInstruction,
  onInstructionTextChange,
  onMissionLeadChange,
  onMissionGoalChange,
  onMissionTitleChange,
  onSelectMission,
  onShowCreateMission,
  onStart,
  selectedMission,
  selectedProject,
  showMissionCreate,
}) {
  const activeLeadId = selectedMission?.leadEmployeeId || missionLeadId;
  const selectedLead = agents.find((agent) => agent.slot === activeLeadId) || agents[0];
  return (
    <aside className="history-rail work-rail">
      <div className="rail-directory">
        <div className="panel-head compact">
          <div>
            <p className="eyebrow">Project</p>
            <h2>{selectedProject?.name || "Project"}</h2>
          </div>
          <button className="icon-button" disabled={busy} onClick={onBackToWorkspace} title="Workspace" type="button">
            <ArrowLeft size={16} />
          </button>
        </div>
        <div className="rail-lead">
          <span className="lead-icon">
            <UserRound size={15} />
          </span>
          <span>
            <small>Lead</small>
            <strong>{selectedLead?.name || "Agent"}</strong>
          </span>
          <em>{selectedLead?.voice || selectedMission?.leadEmployeeRole || ""}</em>
        </div>
        <div className="panel-head compact rail-section">
          <div>
            <p className="eyebrow">Directory</p>
            <h2>Missions</h2>
          </div>
          <button
            className="icon-button"
            disabled={busy || !selectedProject}
            onClick={onShowCreateMission}
            title="New Mission"
            type="button"
          >
            <Plus size={16} />
          </button>
        </div>
        <div className="history-list mission-list">
          {missions.length === 0 && <p className="muted">No missions</p>}
          {missions.map((mission) => (
            <button
              className={`history-item mission-nav-item ${mission.id === selectedMission?.id ? "active" : ""}`}
              key={mission.id}
              onClick={() => onSelectMission(mission)}
              type="button"
            >
              <strong>{mission.title}</strong>
              <span>{mission.status}</span>
            </button>
          ))}
        </div>
      </div>
      <MissionComposer
        answerText={answerText}
        busy={busy}
        followUpText={followUpText}
        inputRequest={inputRequest}
        instructionText={instructionText}
        mission={selectedMission}
        onAnswer={onAnswer}
        onAnswerTextChange={onAnswerTextChange}
        onFollowUp={onFollowUp}
        onFollowUpTextChange={onFollowUpTextChange}
        onInstruction={onInstruction}
        onInstructionTextChange={onInstructionTextChange}
        onStart={onStart}
      />
      <MissionCreateModal
        agents={agents}
        busy={busy}
        missionGoal={missionGoal}
        missionLeadId={missionLeadId}
        missionTitle={missionTitle}
        onCreateMission={onCreateMission}
        onMissionGoalChange={onMissionGoalChange}
        onMissionLeadChange={onMissionLeadChange}
        onMissionTitleChange={onMissionTitleChange}
        onShowCreateMission={onShowCreateMission}
        selectedProject={selectedProject}
        showMissionCreate={showMissionCreate}
      />
    </aside>
  );
}

function MissionCreateModal({
  agents,
  busy,
  missionGoal,
  missionLeadId,
  missionTitle,
  onCreateMission,
  onMissionGoalChange,
  onMissionLeadChange,
  onMissionTitleChange,
  onShowCreateMission,
  selectedProject,
  showMissionCreate,
}) {
  if (!showMissionCreate) return null;
  return (
    <div className="modal-layer" role="presentation">
      <div aria-modal="true" className="topic-modal mission-create-modal" role="dialog">
        <div className="panel-head compact">
          <div>
            <p className="eyebrow">New Mission</p>
            <h2>{selectedProject.name}</h2>
          </div>
          <button className="icon-button" disabled={busy} onClick={onShowCreateMission} title="Close" type="button">
            <ArrowLeft size={16} />
          </button>
        </div>
        <div className="work-create">
          <input
            aria-label="Mission title"
            disabled={busy}
            onChange={(event) => onMissionTitleChange(event.target.value)}
            placeholder="Mission"
            value={missionTitle}
          />
          <textarea
            aria-label="Mission goal"
            disabled={busy}
            onChange={(event) => onMissionGoalChange(event.target.value)}
            placeholder="Goal"
            value={missionGoal}
          />
          <select
            aria-label="Mission lead"
            disabled={busy}
            onChange={(event) => onMissionLeadChange(event.target.value)}
            value={missionLeadId}
          >
            {agents.map((agent) => (
              <option key={agent.slot} value={agent.slot}>
                {agent.name}
              </option>
            ))}
          </select>
          <div className="modal-actions">
            <button className="secondary-button" disabled={busy} onClick={onShowCreateMission} type="button">
              Cancel
            </button>
            <button
              className="primary-button"
              disabled={busy || !missionTitle.trim() || !missionGoal.trim()}
              onClick={onCreateMission}
              type="button"
            >
              <Plus size={16} />
              <span>Create</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default ProjectMissionRail;
