/*
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
*/
import { FolderKanban, Plus } from "lucide-react";

function WorkspaceView({
  busy,
  error,
  loading,
  onCreateProject,
  onProjectNameChange,
  onProjectRepoPathChange,
  onSelectProject,
  projectName,
  projectRepoPath,
  projects,
}) {
  return (
    <section className="work-workspace-view">
      <div className="workspace-headline">
        <div>
          <p className="eyebrow">Work</p>
          <h2>Workspace</h2>
        </div>
        <span>{projects.length} Projects</span>
      </div>
      <div className="workspace-body">
        <section className="workspace-projects">
          <div className="panel-head compact">
            <div>
              <p className="eyebrow">Workspace</p>
              <h2>Projects</h2>
            </div>
            <FolderKanban size={18} />
          </div>
          {loading ? (
            <div className="empty-state">Loading</div>
          ) : projects.length === 0 ? (
            <div className="empty-state">No projects</div>
          ) : (
            <div className="workspace-project-grid">
              {projects.map((project) => (
                <button
                  className="workspace-project-card"
                  disabled={busy}
                  key={project.id}
                  onClick={() => onSelectProject(project)}
                  type="button"
                >
                  <strong>{project.name}</strong>
                  <span>{project.status}</span>
                  <small>{project.repoPath}</small>
                </button>
              ))}
            </div>
          )}
        </section>
        <aside className="workspace-new-project">
          <div className="panel-head compact">
            <div>
              <p className="eyebrow">New</p>
              <h2>Project</h2>
            </div>
            <Plus size={18} />
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
              <span>Create</span>
            </button>
          </div>
          {error && <p className="status-line error">{error}</p>}
        </aside>
      </div>
    </section>
  );
}

export default WorkspaceView;
