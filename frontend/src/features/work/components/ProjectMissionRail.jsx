/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex
*/
import { FolderKanban, Plus } from "lucide-react";

function ProjectMissionRail({
  busy,
  missionGoal,
  missionTitle,
  missions,
  onCreateMission,
  onCreateProject,
  onMissionGoalChange,
  onMissionTitleChange,
  onProjectNameChange,
  onProjectRepoPathChange,
  onSelectMission,
  onSelectProject,
  projectName,
  projectRepoPath,
  projects,
  selectedMission,
  selectedProject,
}) {
  return (
    <aside className="history-rail work-rail">
      <div className="panel-head compact">
        <div>
          <p className="eyebrow">Work</p>
          <h2>Projects</h2>
        </div>
        <FolderKanban size={18} />
      </div>
      <div className="work-create">
        <input
          aria-label="Project name"
          disabled={busy}
          onChange={(event) => onProjectNameChange(event.target.value)}
          placeholder="Project"
          value={projectName}
        />
        <input
          aria-label="Repo path"
          disabled={busy}
          onChange={(event) => onProjectRepoPathChange(event.target.value)}
          placeholder="Repo path"
          value={projectRepoPath}
        />
        <button disabled={busy || !projectName.trim() || !projectRepoPath.trim()} onClick={onCreateProject} type="button">
          <Plus size={16} />
          <span>Add</span>
        </button>
      </div>
      <div className="history-list compact-list">
        {projects.map((project) => (
          <button
            className={`history-item ${project.id === selectedProject?.id ? "active" : ""}`}
            key={project.id}
            onClick={() => onSelectProject(project)}
            type="button"
          >
            <strong>{project.name}</strong>
            <span>{project.status}</span>
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
