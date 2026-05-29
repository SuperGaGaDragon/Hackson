/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex
*/
import { ArrowRight, BriefcaseBusiness, Check, ChevronDown, RefreshCw, Send } from "lucide-react";
import { useEffect, useLayoutEffect, useRef, useState } from "react";
import {
  createConversation,
  getConversationMessages,
  getIdleConversation,
  listConversations,
} from "../../api/conversations";
import { getIdleBrainstormCard, joinIdle, sendCompanionMessage, sendIdleMessage, tickIdle } from "../../api/interactions";
import { createMission, createProject, getMission, listProjects } from "../../api/workMode";
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
  const [brainstormCard, setBrainstormCard] = useState(null);
  const [brainstormOpen, setBrainstormOpen] = useState(false);
  const [brainstormLoading, setBrainstormLoading] = useState(false);
  const [promoteOpen, setPromoteOpen] = useState(false);
  const [projects, setProjects] = useState([]);
  const [selectedProjectId, setSelectedProjectId] = useState("");
  const [newProjectName, setNewProjectName] = useState("");
  const [missionTitle, setMissionTitle] = useState("");
  const [missionGoal, setMissionGoal] = useState("");
  const [missionLeadId, setMissionLeadId] = useState("agent_1");
  const [promoteBusy, setPromoteBusy] = useState(false);
  const [createdMission, setCreatedMission] = useState(null);
  const timelineRef = useRef(null);
  const isIdle = mode === "idle";
  const timelineMessages = isIdle ? idleMessages : [...idleMessages, ...companionMessages];
  const sessionStatus = loading ? "Loading" : queuedIdleMessage ? "Queued" : busy ? "Working" : "Ready";

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
        resetBrainstormState();
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
      resetBrainstormState();
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
      resetBrainstormState();
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

  async function refreshBrainstormCard() {
    if (!idleConversation || brainstormLoading) return;
    setBrainstormLoading(true);
    setError("");
    try {
      const card = await getIdleBrainstormCard(idleConversation.id);
      setBrainstormCard(card);
      setBrainstormOpen(true);
      setMissionTitle(card.suggestedMission?.title || "");
      setMissionGoal(card.suggestedMission?.goal || "");
      setMissionLeadId(targetAgentId || "agent_1");
      setCreatedMission(null);
    } catch (err) {
      setError(err.message || "Brief failed");
    } finally {
      setBrainstormLoading(false);
    }
  }

  async function openPromoteMission() {
    if (!brainstormCard) return;
    setPromoteBusy(true);
    setError("");
    try {
      const rows = await listProjects();
      setProjects(rows || []);
      setSelectedProjectId(rows?.[0]?.id || "");
      setNewProjectName("");
      setMissionTitle(brainstormCard.suggestedMission?.title || "");
      setMissionGoal(brainstormCard.suggestedMission?.goal || "");
      setMissionLeadId(targetAgentId || "agent_1");
      setCreatedMission(null);
      setPromoteOpen(true);
    } catch (err) {
      setError(err.message || "Projects failed");
    } finally {
      setPromoteBusy(false);
    }
  }

  async function promoteBrainstorm() {
    if (!brainstormCard || promoteBusy || !missionTitle.trim() || !missionGoal.trim()) return;
    if (!selectedProjectId && !newProjectName.trim()) return;
    setPromoteBusy(true);
    setError("");
    try {
      let projectId = selectedProjectId;
      if (!projectId) {
        const project = await createProject({
          name: newProjectName.trim(),
          metadata: {
            source: "idle_brainstorm",
            idleConversationId: idleConversation?.id,
          },
        });
        projectId = project.id;
        setProjects((current) => [project, ...current]);
        setSelectedProjectId(project.id);
      }
      const mission = await createMission({
        projectId,
        title: missionTitle.trim(),
        goal: missionGoal.trim(),
        leadEmployeeId: missionLeadId,
        metadata: {
          source: "idle_brainstorm",
          idleConversationId: idleConversation?.id,
          sourceMessageIds: brainstormCard.sourceMessageIds,
          sourceMessageCount: brainstormCard.sourceMessageCount,
          brainstormGeneratedAt: brainstormCard.generatedAt,
          brainstormTopic: brainstormCard.topic,
        },
      });
      const detail = await getMission(mission.id);
      setCreatedMission(detail.mission || mission);
    } catch (err) {
      setError(err.message || "Promote failed");
    } finally {
      setPromoteBusy(false);
    }
  }

  function resetBrainstormState() {
    setBrainstormCard(null);
    setBrainstormOpen(false);
    setPromoteOpen(false);
    setCreatedMission(null);
    setSelectedProjectId("");
    setNewProjectName("");
    setMissionTitle("");
    setMissionGoal("");
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
        <section className="idle-brief-panel">
          <div className="idle-brief-head">
            <div>
              <span>Brainstorm</span>
              <strong>{brainstormCard ? "Ready" : "Work brief"}</strong>
            </div>
            <button
              className="icon-button"
              disabled={loading || brainstormLoading || idleMessages.length === 0}
              onClick={refreshBrainstormCard}
              title="Refresh brief"
              type="button"
            >
              <RefreshCw size={15} />
            </button>
          </div>
          {brainstormCard ? (
            <IdleBrainstormCard
              card={brainstormCard}
              open={brainstormOpen}
              onPromote={openPromoteMission}
              onToggle={() => setBrainstormOpen((current) => !current)}
              promoteBusy={promoteBusy}
            />
          ) : (
            <p className="muted">Turn this discussion into a draft Mission.</p>
          )}
        </section>
        <section className="idle-session-panel" aria-label="Session status">
          <div className="idle-session-row">
            <span>Auto</span>
            <strong>{autoIdle ? "On" : "Off"}</strong>
          </div>
          <div className="idle-session-row">
            <span>Status</span>
            <strong>{sessionStatus}</strong>
          </div>
        </section>
        <details className="idle-debug-details">
          <summary>
            <span>Debug</span>
            <small>Details</small>
          </summary>
          <dl>
            <div>
              <dt>Conversation</dt>
              <dd>{conversation?.id || "none"}</dd>
            </div>
            {!isIdle && (
              <div>
                <dt>Parent</dt>
                <dd>{idleConversation?.id || "none"}</dd>
              </div>
            )}
            <div>
              <dt>Turns</dt>
              <dd>{timelineMessages.length}</dd>
            </div>
          </dl>
        </details>
        <StatusLine error={error} />
      </aside>
      {promoteOpen && brainstormCard && (
        <PromoteMissionModal
          agents={agentProfiles}
          busy={promoteBusy}
          createdMission={createdMission}
          missionGoal={missionGoal}
          missionLeadId={missionLeadId}
          missionTitle={missionTitle}
          newProjectName={newProjectName}
          onClose={() => setPromoteOpen(false)}
          onMissionGoalChange={setMissionGoal}
          onMissionLeadChange={setMissionLeadId}
          onMissionTitleChange={setMissionTitle}
          onNewProjectNameChange={setNewProjectName}
          onPromote={promoteBrainstorm}
          onSelectedProjectChange={setSelectedProjectId}
          projects={projects}
          selectedProjectId={selectedProjectId}
          sourceCount={brainstormCard.sourceMessageCount}
        />
      )}
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

function IdleBrainstormCard({ card, onPromote, onToggle, open, promoteBusy }) {
  return (
    <div className="idle-brief-card">
      <button className="idle-brief-toggle" onClick={onToggle} type="button">
        <span>{card.suggestedMission?.title || card.topic}</span>
        <ChevronDown className={open ? "rotated" : ""} size={15} />
      </button>
      {open && (
        <div className="idle-brief-body">
          <BriefList label="Key ideas" rows={card.keyIdeas} />
          <BriefList label="Disagreements" rows={card.disagreements} empty="No material disagreement." />
          <section>
            <span>Decision</span>
            <p>{card.decision}</p>
          </section>
          <BriefList label="Open questions" rows={card.openQuestions} empty="No open questions captured." />
          <section>
            <span>Sources</span>
            <p>{card.sourceMessageCount} messages</p>
            <details className="brief-source-details">
              <summary>IDs</summary>
              <code>{card.sourceMessageIds.join(", ")}</code>
            </details>
          </section>
        </div>
      )}
      <button className="primary-button idle-brief-promote" disabled={promoteBusy} onClick={onPromote} type="button">
        <BriefcaseBusiness size={15} />
        <span>Promote</span>
      </button>
    </div>
  );
}

function BriefList({ empty = "Nothing captured.", label, rows }) {
  return (
    <section>
      <span>{label}</span>
      {rows?.length ? (
        <ul>
          {rows.map((row, index) => (
            <li key={`${index}-${row}`}>{row}</li>
          ))}
        </ul>
      ) : (
        <p>{empty}</p>
      )}
    </section>
  );
}

function PromoteMissionModal({
  agents,
  busy,
  createdMission,
  missionGoal,
  missionLeadId,
  missionTitle,
  newProjectName,
  onClose,
  onMissionGoalChange,
  onMissionLeadChange,
  onMissionTitleChange,
  onNewProjectNameChange,
  onPromote,
  onSelectedProjectChange,
  projects,
  selectedProjectId,
  sourceCount,
}) {
  const canCreate = Boolean(missionTitle.trim() && missionGoal.trim() && (selectedProjectId || newProjectName.trim()));
  return (
    <div className="modal-layer" role="presentation">
      <div aria-modal="true" className="topic-modal promote-modal" role="dialog">
        <div className="panel-head compact">
          <div>
            <p className="eyebrow">Promote</p>
            <h2>Draft Mission</h2>
          </div>
          <span className="chip">{sourceCount} sources</span>
        </div>
        {createdMission ? (
          <div className="promote-success">
            <Check size={18} />
            <strong>{createdMission.title}</strong>
            <p>Draft Mission created.</p>
            <div className="modal-actions">
              <button className="secondary-button" onClick={onClose} type="button">
                Stay
              </button>
              <button
                className="primary-button"
                onClick={() => {
                  window.history.pushState({}, "", `/work_mission/${encodeURIComponent(createdMission.id)}`);
                  window.dispatchEvent(new Event("popstate"));
                }}
                type="button"
              >
                <ArrowRight size={16} />
                <span>Open</span>
              </button>
            </div>
          </div>
        ) : (
          <div className="work-create">
            <label>
              <span>Project</span>
              <select
                aria-label="Project"
                disabled={busy}
                onChange={(event) => onSelectedProjectChange(event.target.value)}
                value={selectedProjectId}
              >
                <option value="">New project</option>
                {projects.map((project) => (
                  <option key={project.id} value={project.id}>
                    {project.name}
                  </option>
                ))}
              </select>
            </label>
            {!selectedProjectId && (
              <label>
                <span>New project</span>
                <input
                  aria-label="New project"
                  disabled={busy}
                  onChange={(event) => onNewProjectNameChange(event.target.value)}
                  placeholder="Project"
                  value={newProjectName}
                />
              </label>
            )}
            <label>
              <span>Title</span>
              <input
                aria-label="Mission title"
                disabled={busy}
                onChange={(event) => onMissionTitleChange(event.target.value)}
                value={missionTitle}
              />
            </label>
            <label>
              <span>Goal</span>
              <textarea
                aria-label="Mission goal"
                disabled={busy}
                onChange={(event) => onMissionGoalChange(event.target.value)}
                value={missionGoal}
              />
            </label>
            <label>
              <span>Lead</span>
              <select
                aria-label="Lead"
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
            </label>
            <div className="modal-actions">
              <button className="secondary-button" disabled={busy} onClick={onClose} type="button">
                Cancel
              </button>
              <button className="primary-button" disabled={busy || !canCreate} onClick={onPromote} type="button">
                <BriefcaseBusiness size={16} />
                <span>Create</span>
              </button>
            </div>
          </div>
        )}
      </div>
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
