/*
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
*/
import { ChevronRight } from "lucide-react";

function WorkWindowPanel({ artifacts = [], workWindows = [] }) {
  const artifactById = new Map(artifacts.map((artifact) => [artifact.id, artifact]));

  return (
    <div className="work-card window-panel">
      <div className="card-head">
        <p className="eyebrow">Windows</p>
        <span>{workWindows.length}</span>
      </div>
      <div className="window-list">
        {workWindows.length === 0 && <p className="muted">None</p>}
        {workWindows.map((window) => {
          const artifact = artifactById.get(window.resultArtifactId);
          return (
            <details className="window-row" key={window.id}>
              <summary>
                <ChevronRight size={15} />
                <span>
                  <strong>{window.title}</strong>
                  <small>{window.agentSlot}</small>
                </span>
                <em>{window.status}</em>
              </summary>
              <p>{window.brief}</p>
              {window.summary && <p>{window.summary}</p>}
              {artifact && <pre>{artifact.content}</pre>}
            </details>
          );
        })}
      </div>
    </div>
  );
}

export default WorkWindowPanel;
