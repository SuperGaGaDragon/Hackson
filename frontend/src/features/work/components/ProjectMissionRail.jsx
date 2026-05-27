/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
*/
import { ArrowLeft, Plus, UsersRound } from "lucide-react";

function ProjectMissionRail({
  busy,
  employeeName,
  employeeRole,
  employees,
  missionLeadId,
  missionGoal,
  missionTitle,
  missions,
  onAddEmployee,
  onAddToTeam,
  onBackToWorkspace,
  onCreateMission,
  onEmployeeNameChange,
  onEmployeeRoleChange,
  onMissionLeadChange,
  onMissionGoalChange,
  onMissionTitleChange,
  onSelectMission,
  onTeamEmployeeChange,
  selectedMission,
  selectedProject,
  team,
  teamEmployeeId,
}) {
  const availableEmployees = employees.filter((employee) => !team.some((member) => member.employeeId === employee.id));
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
      {selectedProject?.repoPath && <p className="rail-project-path">{selectedProject.repoPath}</p>}
      <div className="panel-head compact rail-section">
        <div>
          <p className="eyebrow">Crew</p>
          <h2>Employees</h2>
        </div>
        <UsersRound size={18} />
      </div>
      <div className="work-create">
        <input
          aria-label="Employee name"
          disabled={busy}
          onChange={(event) => onEmployeeNameChange(event.target.value)}
          placeholder="Name"
          value={employeeName}
        />
        <input
          aria-label="Employee role"
          disabled={busy}
          onChange={(event) => onEmployeeRoleChange(event.target.value)}
          placeholder="Role"
          value={employeeRole}
        />
        <button disabled={busy || !employeeName.trim() || !employeeRole.trim()} onClick={onAddEmployee} type="button">
          <Plus size={16} />
          <span>Add</span>
        </button>
      </div>
      <div className="panel-head compact rail-section">
        <div>
          <p className="eyebrow">Project</p>
          <h2>Team</h2>
        </div>
      </div>
      <div className="work-create">
        <select
          aria-label="Team employee"
          disabled={busy || !selectedProject || availableEmployees.length === 0}
          onChange={(event) => onTeamEmployeeChange(event.target.value)}
          value={teamEmployeeId}
        >
          <option value="">Employee</option>
          {availableEmployees.map((employee) => (
            <option key={employee.id} value={employee.id}>
              {employee.name}
            </option>
          ))}
        </select>
        <button disabled={busy || !selectedProject || !teamEmployeeId} onClick={onAddToTeam} type="button">
          <Plus size={16} />
          <span>Add</span>
        </button>
      </div>
      <div className="team-list">
        {team.map((member) => (
          <div className="team-row" key={member.id}>
            <strong>{member.employee.name}</strong>
            <span>{member.employee.role}</span>
          </div>
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
          <option value="employee_default_lead">Lead</option>
          {team.map((member) => (
            <option key={member.employeeId} value={member.employeeId}>
              {member.employee.name}
            </option>
          ))}
        </select>
        <button
          disabled={busy || !selectedProject || !missionTitle.trim() || !missionGoal.trim()}
          onClick={onCreateMission}
          type="button"
        >
          <Plus size={16} />
          <span>Add</span>
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
