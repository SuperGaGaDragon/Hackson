/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex
*/
import { Send } from "lucide-react";
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { getConversationMessages, getIdleConversation } from "../../api/conversations";
import { joinIdle, sendCompanionMessage, tickIdle } from "../../api/interactions";
import { FALLBACK_AGENTS, nextAgentSlot, normalizeAgents } from "../../domain/agents";
import { makePendingUserMessage, makeSystemMessage, sortMessages, uniqueMessages } from "../../domain/messages";
import AgentSlot from "../../shared/components/AgentSlot";
import StatusLine from "../../shared/components/StatusLine";
import Timeline from "../../shared/components/Timeline";

function IdlePage({ agents = FALLBACK_AGENTS }) {
  const agentProfiles = normalizeAgents(agents);
  const [conversation, setConversation] = useState(null);
  const [idleConversation, setIdleConversation] = useState(null);
  const [idleMessages, setIdleMessages] = useState([]);
  const [companionMessages, setCompanionMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [targetAgentId, setTargetAgentId] = useState("agent_1");
  const [mode, setMode] = useState("idle");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [autoIdle, setAutoIdle] = useState(false);
  const [error, setError] = useState("");
  const timelineRef = useRef(null);
  const isIdle = mode === "idle";
  const timelineMessages = isIdle ? idleMessages : [...idleMessages, ...companionMessages];

  useEffect(() => {
    let mounted = true;

    async function loadIdle() {
      setLoading(true);
      setError("");
      try {
        const idle = await getIdleConversation();
        const history = await getConversationMessages(idle.id);
        if (!mounted) return;
        setIdleConversation(idle);
        setConversation(idle);
        setIdleMessages(sortMessages(history.messages || []));
        setCompanionMessages([]);
      } catch (err) {
        if (mounted) setError(err.message || "Load failed");
      } finally {
        if (mounted) setLoading(false);
      }
    }

    loadIdle();
    return () => {
      mounted = false;
    };
  }, []);

  useLayoutEffect(() => {
    if (!timelineRef.current) return;
    timelineRef.current.scrollTop = timelineRef.current.scrollHeight;
  }, [timelineMessages.length, busy]);

  useEffect(() => {
    if (!autoIdle || !isIdle || busy || loading) return undefined;
    const timer = window.setTimeout(() => {
      tick();
    }, idleMessages.length ? 3500 : 800);
    return () => window.clearTimeout(timer);
  }, [autoIdle, isIdle, busy, loading, idleMessages.length, targetAgentId]);

  async function tick() {
    if (!idleConversation || busy || !isIdle) return;
    setBusy(true);
    setError("");
    const activeTarget = targetAgentId;
    try {
      const data = await tickIdle(idleConversation.id, {
        targetAgentId: activeTarget,
        idleSeed: "继续 idle 对话，保持自然、简短、有生活感。",
        metadata: {},
      });
      setConversation((current) => ({ ...current, ...data.conversation }));
      setIdleMessages((current) => uniqueMessages([...current, data.agentMessage]));
      setTargetAgentId(nextAgentSlot(activeTarget, agentProfiles));
    } catch (err) {
      setError(err.message || "Tick failed");
    } finally {
      setBusy(false);
    }
  }

  async function join() {
    const content = draft.trim();
    if (!idleConversation || !content || busy) return;
    if (!isIdle) {
      await sendCompanionTurn(content);
      return;
    }
    setBusy(true);
    setError("");
    setDraft("");
    const joinMarker = makeSystemMessage("Joined");
    const pendingMessage = makePendingUserMessage(
      { ...idleConversation, mode: "companion_1" },
      content,
      [],
    );
    setCompanionMessages([joinMarker, pendingMessage]);
    try {
      const data = await joinIdle(idleConversation.id, {
        content,
        targetAgentId,
        metadata: {},
      });
      setMode("companion_1");
      setAutoIdle(false);
      setConversation(data.conversation);
      setCompanionMessages([joinMarker, data.userMessage, data.agentMessage]);
      setTargetAgentId(nextAgentSlot(targetAgentId, agentProfiles));
    } catch (err) {
      setError(err.message || "Join failed");
      setCompanionMessages([]);
    } finally {
      setBusy(false);
    }
  }

  async function sendCompanionTurn(content) {
    if (!conversation || conversation.mode !== "companion_1") return;
    const pendingMessage = makePendingUserMessage(conversation, content, companionMessages);
    setBusy(true);
    setError("");
    setDraft("");
    setCompanionMessages((current) => uniqueMessages([...current, pendingMessage]));
    try {
      const data = await sendCompanionMessage(conversation.id, {
        content,
        targetAgentId,
        metadata: {},
      });
      setConversation((current) => ({ ...current, ...data.conversation }));
      setCompanionMessages((current) =>
        uniqueMessages([
          ...current.filter((message) => message.id !== pendingMessage.id),
          data.userMessage,
          data.agentMessage,
        ]),
      );
      setTargetAgentId(nextAgentSlot(targetAgentId, agentProfiles));
    } catch (err) {
      setError(err.message || "Send failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="idle-grid">
      <aside className="agent-rail">
        {agentProfiles.map((agent) => (
          <AgentSlot agent={agent} key={agent.slot} state={targetAgentId === agent.slot ? "Target" : "Ready"} />
        ))}
        <section className="mini-panel">
          <p className="eyebrow">Target</p>
          <select onChange={(event) => setTargetAgentId(event.target.value)} value={targetAgentId}>
            {agentProfiles.map((agent) => (
              <option key={agent.slot} value={agent.slot}>
                {agent.name}
              </option>
            ))}
          </select>
        </section>
      </aside>
      <section className="timeline-panel">
        <div className="panel-head">
          <div>
            <p className="eyebrow">{isIdle ? "Idle" : "Companion"}</p>
            <h2>Timeline</h2>
          </div>
          <div className="panel-actions">
            <button
              className={autoIdle ? "secondary-button active" : "secondary-button"}
              disabled={loading || !isIdle}
              onClick={() => setAutoIdle((current) => !current)}
              type="button"
            >
              Auto
            </button>
            <button className="secondary-button" disabled={busy || loading || !isIdle} onClick={tick} type="button">
              {busy ? "Wait" : "Tick"}
            </button>
          </div>
        </div>
        <Timeline agents={agentProfiles} messages={timelineMessages} timelineRef={timelineRef} />
        <div className="composer">
          <input
            aria-label="Join"
            disabled={busy || loading}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") join();
            }}
            placeholder={isIdle ? "Join" : "Message"}
            value={draft}
          />
          <button disabled={busy || loading} onClick={join} title="Send" type="button">
            <Send size={18} />
          </button>
        </div>
      </section>
      <aside className="context-rail">
        <div className="panel-head compact">
          <div>
            <p className="eyebrow">State</p>
            <h2>{isIdle ? "Idle" : "Companion"}</h2>
          </div>
        </div>
        <section className="context-item">
          <span>ID</span>
          <p>{conversation?.id || "none"}</p>
        </section>
        {!isIdle && (
          <section className="context-item">
            <span>Parent</span>
            <p>{idleConversation?.id || "none"}</p>
          </section>
        )}
        <section className="context-item">
          <span>Count</span>
          <p>{timelineMessages.length}</p>
        </section>
        <section className="context-item">
          <span>Auto</span>
          <p>{autoIdle ? "on" : "off"}</p>
        </section>
        <StatusLine error={error} loading={loading} text={busy ? "Working" : ""} />
      </aside>
    </div>
  );
}

export default IdlePage;
