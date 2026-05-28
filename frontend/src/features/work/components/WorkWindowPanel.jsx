/*
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { ChevronRight } from "lucide-react";
import { formatEventTime } from "./eventDisplay";

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
          const type = window.metadata?.windowType === "discussion" ? "Discussion" : "Delegate";
          return (
            <details className={`window-row status-${window.status} type-${type.toLowerCase()}`} key={window.id}>
              <summary>
                <ChevronRight size={15} />
                <span>
                  <strong>{window.title}</strong>
                  <small>
                    {type} / {window.agentSlot}
                    {artifact ? ` / ${artifact.title}` : ""}
                  </small>
                </span>
                <em>
                  {window.status}
                  {formatEventTime(window) ? ` / ${formatEventTime(window)}` : ""}
                </em>
              </summary>
              <p>{window.brief}</p>
              {window.metadata?.expectedOutcome && <p>{window.metadata.expectedOutcome}</p>}
              {window.summary && <p>{window.summary}</p>}
              {artifact && <pre className="window-artifact-preview">{artifact.content}</pre>}
            </details>
          );
        })}
      </div>
    </div>
  );
}

export default WorkWindowPanel;
