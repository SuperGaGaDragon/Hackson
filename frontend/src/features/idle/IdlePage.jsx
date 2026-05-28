/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { Send } from "lucide-react";
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import {
  createConversation,
  getConversationMessages,
  getIdleConversation,
  listConversations,
} from "../../api/conversations";
import { joinIdle, sendCompanionMessage, sendIdleMessage, tickIdle } from "../../api/interactions";
import { FALLBACK_AGENTS, nextAgentSlot, normalizeAgents } from "../../domain/agents";
import {
  makeClientId,
  makePendingUserMessage,
  makeQueuedUserMessage,
  makeSystemMessage,
  sortMessages,
  uniqueMessages,
} from "../../domain/messages";
import AgentSlot from "../../shared/components/AgentSlot";
import StatusLine from "../../shared/components/StatusLine";
import Timeline from "../../shared/components/Timeline";

function IdlePage({ agents = FALLBACK_AGENTS }) {
  const agentProfiles = normalizeAgents(agents);
  const [idleConversations, setIdleConversations] = useState([]);
  const [conversation, setConversation] = useState(null);
  const [idleConversation, setIdleConversation] = useState(null);
  const [idleMessages, setIdleMessages] = useState([]);
  const [companionMessages, setCompanionMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [topic, setTopic] = useState("");
  const [newTopic, setNewTopic] = useState("");
  const [showNewTopic, setShowNewTopic] = useState(false);
  const [targetAgentId, setTargetAgentId] = useState("agent_1");
  const [mode, setMode] = useState("idle");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [queuedIdleMessage, setQueuedIdleMessage] = useState(null);
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
        const rows = await listConversations("idle");
        const idle = rows[0] || (await getIdleConversation());
        const history = await getConversationMessages(idle.id);
        if (!mounted) return;
        setIdleConversations(localizeIdleTitles(rows.length ? rows : [idle]));
        setIdleConversation(idle);
        setConversation(idle);
        setTopic(topicFromConversation(idle));
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
    if (!autoIdle || !isIdle || busy || loading || queuedIdleMessage) return undefined;
    const timer = window.setTimeout(() => {
      tick();
    }, idleMessages.length ? 3500 : 800);
    return () => window.clearTimeout(timer);
  }, [autoIdle, isIdle, busy, loading, idleMessages.length, targetAgentId, queuedIdleMessage]);

  useEffect(() => {
    if (!queuedIdleMessage || busy || loading || !isIdle || !idleConversation) return;
    const queued = queuedIdleMessage;
    setQueuedIdleMessage(null);
    sendIdleInterjection(queued.content, {
      pendingId: queued.id,
      idempotencyKey: queued.idempotencyKey,
    });
  }, [queuedIdleMessage, busy, loading, isIdle, idleConversation]);

  async function tick() {
    if (!idleConversation || busy || !isIdle) return;
    setBusy(true);
    setError("");
    const activeTarget = targetAgentId;
    const direction = topic.trim();
    try {
      const data = await requestIdleTick(idleConversation, {
        targetAgentId: activeTarget,
        discussionDirection: direction || undefined,
      });
      applyIdleTurn(data);
      setTargetAgentId(nextAgentSlot(data.agentMessage.senderSlot, agentProfiles));
    } catch (err) {
      setAutoIdle(false);
      setError(err.message || "Tick failed");
    } finally {
      setBusy(false);
    }
  }

  async function startNewIdle(event) {
    event.preventDefault();
    const direction = newTopic.trim();
    if (!direction || busy) return;
    setBusy(true);
    setError("");
    try {
      const idle = await createConversation({
        mode: "idle",
        title: makeIdleTitle(direction),
        metadata: { topicDirection: direction },
      });
      const item = { ...idle, localTitle: makeIdleTitle(direction) };
      setIdleConversations((current) => localizeIdleTitles([item, ...current]));
      setIdleConversation(idle);
      setConversation(idle);
      setIdleMessages([]);
      setCompanionMessages([]);
      setTopic(direction);
      setDraft("");
      setMode("idle");
      setShowNewTopic(false);
      setNewTopic("");
      const data = await requestIdleTick(idle, { discussionDirection: direction });
      applyIdleTurn(data);
      setAutoIdle(true);
      setTargetAgentId(nextAgentSlot(data.agentMessage.senderSlot, agentProfiles));
    } catch (err) {
      setAutoIdle(false);
      setError(err.message || "New failed");
    } finally {
      setBusy(false);
    }
  }

  async function selectIdle(nextConversation) {
    if (busy || nextConversation.id === idleConversation?.id) return;
    setLoading(true);
    setError("");
    try {
      const history = await getConversationMessages(nextConversation.id);
      setIdleConversation(nextConversation);
      setConversation(nextConversation);
      setIdleMessages(sortMessages(history.messages || []));
      setCompanionMessages([]);
      setTopic(topicFromConversation(nextConversation));
      setDraft("");
      setMode("idle");
      setAutoIdle(false);
    } catch (err) {
      setError(err.message || "Load failed");
    } finally {
      setLoading(false);
    }
  }

  async function sendDraft() {
    const content = draft.trim();
    if (!content) return;
    if (busy && isIdle && idleConversation) {
      queueIdleInterjection(content);
      return;
    }
    if (busy) return;
    if (!isIdle) {
      await sendCompanionTurn(content);
      return;
    }
    if (!idleConversation) return;
    await sendIdleInterjection(content);
  }

  function queueIdleInterjection(content) {
    const idempotencyKey = `idle-say-${makeClientId()}`;
    const queuedMessage = {
      ...makeQueuedUserMessage(idleConversation, content, idleMessages),
      idempotencyKey,
    };
    setDraft("");
    setAutoIdle(false);
    setQueuedIdleMessage(queuedMessage);
    setIdleMessages((current) => uniqueMessages([...current, queuedMessage]));
  }

  async function sendIdleInterjection(content, options = {}) {
    const pendingMessage =
      options.pendingId
        ? idleMessages.find((message) => message.id === options.pendingId) ||
          makePendingUserMessage(idleConversation, content, idleMessages)
        : makePendingUserMessage(idleConversation, content, idleMessages);
    setBusy(true);
    setError("");
    setDraft("");
    setIdleMessages((current) => uniqueMessages([...current, pendingMessage]));
    try {
      const data = await sendIdleMessage(idleConversation.id, {
        content,
        discussionDirection: topic.trim() || undefined,
        idempotencyKey: options.idempotencyKey || `idle-say-${makeClientId()}`,
        metadata: {},
      });
      setIdleMessages((current) =>
        uniqueMessages([
          ...current.filter((item) => item.id !== pendingMessage.id),
          data.userMessage,
          data.agentMessage,
        ]),
      );
      applyIdleConversation(data.conversation);
      setTargetAgentId(nextAgentSlot(data.agentMessage.senderSlot, agentProfiles));
    } catch (err) {
      setAutoIdle(false);
      setError(err.message || "Say failed");
      setIdleMessages((current) => current.filter((item) => item.id !== pendingMessage.id));
    } finally {
      setBusy(false);
    }
  }

  async function joinCompanion() {
    const content = draft.trim();
    if (!idleConversation || !content || busy || !isIdle) return;
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

  async function requestIdleTick(targetConversation, overrides = {}) {
    const direction = overrides.discussionDirection ?? topicFromConversation(targetConversation);
    return tickIdle(targetConversation.id, {
      targetAgentId: overrides.targetAgentId,
      discussionDirection: direction || undefined,
      idleSeed: "继续 idle 对话，保持自然、简短、有生活感。",
      metadata: {},
    });
  }

  function applyIdleTurn(data) {
    applyIdleConversation(data.conversation);
    setIdleMessages((current) => uniqueMessages([...current, data.agentMessage]));
  }

  function applyIdleConversation(nextConversation) {
    setConversation((current) => ({ ...current, ...nextConversation }));
    setIdleConversation((current) => ({ ...current, ...nextConversation }));
    setIdleConversations((current) =>
      localizeIdleTitles(
        current.map((item) =>
          item.id === nextConversation.id
            ? {
                ...item,
                ...nextConversation,
              }
            : item,
        ),
      ),
    );
  }

  return (
    <div className="idle-grid">
      <aside className="history-rail">
        <div className="panel-head compact">
          <div>
            <p className="eyebrow">Idle</p>
            <h2>History</h2>
          </div>
        </div>
        <button
          className="secondary-button history-new"
          disabled={busy || loading}
          onClick={() => setShowNewTopic(true)}
          type="button"
        >
          New
        </button>
        <div className="history-list">
          {idleConversations.map((item) => (
            <button
              className={`history-item ${item.id === idleConversation?.id ? "active" : ""}`}
              key={item.id}
              onClick={() => selectIdle(item)}
              type="button"
            >
              <strong>{item.localTitle || item.title || "Idle"}</strong>
              <span>{item.messageCount || 0}</span>
            </button>
          ))}
        </div>
      </aside>
      <section className="timeline-panel">
        <div className="panel-head">
          <div>
            <p className="eyebrow">{isIdle ? "Idle" : "Companion"}</p>
            <h2>{isIdle ? idleTitle(idleConversation) : "Companion"}</h2>
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
            {isIdle && (
              <button
                className="secondary-button"
                disabled={busy || loading || !draft.trim()}
                onClick={joinCompanion}
                type="button"
              >
                Join
              </button>
            )}
          </div>
        </div>
        <Timeline agents={agentProfiles} messages={timelineMessages} timelineRef={timelineRef} />
        <div className="composer">
          <input
            aria-label={isIdle ? "Say" : "Message"}
            disabled={loading || (!isIdle && busy)}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") sendDraft();
            }}
            placeholder={isIdle ? "Say" : "Message"}
            value={draft}
          />
          <button disabled={loading || (!isIdle && busy)} onClick={sendDraft} title="Send" type="button">
            <Send size={18} />
          </button>
        </div>
      </section>
      <aside className="context-rail">
        <div className="panel-head compact">
          <div>
            <p className="eyebrow">Target</p>
            <h2>Agent</h2>
          </div>
        </div>
        {agentProfiles.map((agent) => (
          <button
            className={`agent-target ${targetAgentId === agent.slot ? "active" : ""}`}
            key={agent.slot}
            onClick={() => setTargetAgentId(agent.slot)}
            type="button"
          >
            <AgentSlot agent={agent} state={targetAgentId === agent.slot ? "On" : "Off"} />
          </button>
        ))}
        <section className="context-item">
          <span>Topic</span>
          <p>{topic.trim() || "none"}</p>
        </section>
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
      {showNewTopic && (
        <div className="modal-layer" role="presentation">
          <form className="topic-modal" onSubmit={startNewIdle}>
            <div className="panel-head compact">
              <div>
                <p className="eyebrow">Idle</p>
                <h2>New topic</h2>
              </div>
            </div>
            <label>
              <span>Topic · {newTopic.length}/1000</span>
              <textarea
                autoFocus
                maxLength={1000}
                onChange={(event) => setNewTopic(event.target.value)}
                rows={6}
                value={newTopic}
              />
            </label>
            <div className="modal-actions">
              <button className="secondary-button" onClick={() => setShowNewTopic(false)} type="button">
                Cancel
              </button>
              <button className="primary-button" disabled={!newTopic.trim() || busy} type="submit">
                Create
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
}

function localizeIdleTitles(conversations) {
  return conversations.map((conversation) => ({
    ...conversation,
    localTitle: idleTitle(conversation),
  }));
}

function idleTitle(conversation) {
  if (!conversation) return "Idle";
  const topic = topicFromConversation(conversation);
  if (topic) return makeIdleTitle(topic);
  if (conversation.title && conversation.title !== "Idle") return conversation.title;
  if (conversation.lastMessageAt) {
    return `Idle ${new Date(conversation.lastMessageAt).toLocaleDateString([], { month: "short", day: "numeric" })}`;
  }
  return "Untitled";
}

function topicFromConversation(conversation) {
  return conversation?.metadata?.topicDirection || conversation?.metadata?.discussionDirection || "";
}

function makeIdleTitle(content) {
  const trimmed = content.replace(/\s+/g, " ").trim();
  if (trimmed.length <= 18) return trimmed || "Idle";
  return `${trimmed.slice(0, 18)}...`;
}

export default IdlePage;
