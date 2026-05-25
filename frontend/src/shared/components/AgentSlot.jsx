/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
*/
function AgentSlot({ agent, state = "Ready" }) {
  return (
    <article className={`agent-slot ${agent.color}`}>
      <div className="avatar" aria-hidden="true">
        {agent.short}
      </div>
      <div>
        <div className="agent-line">
          <strong>{agent.name}</strong>
          <span>{state}</span>
        </div>
        <p>{agent.voice}</p>
      </div>
    </article>
  );
}

export default AgentSlot;
