/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex
*/
import { Plus, Send } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { getConversationMessages } from "../../api/conversations";
import { createTask, listTasks, sendTaskMessage } from "../../api/tasks";
import { FALLBACK_AGENTS, normalizeAgents } from "../../domain/agents";
import { sortMessages, uniqueMessages } from "../../domain/messages";
import AgentSlot from "../../shared/components/AgentSlot";
import StatusLine from "../../shared/components/StatusLine";
import Timeline from "../../shared/components/Timeline";

function WorkPage({ agents = FALLBACK_AGENTS }) {
  const agentProfiles = normalizeAgents(agents);
  const [tasks, setTasks] = useState([]);
  const [task, setTask] = useState(null);
  const [messages, setMessages] = useState([]);
  const [objective, setObjective] = useState("");
  const [draft, setDraft] = useState("");
  const [targetAgentId, setTargetAgentId] = useState("agent_2");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const timelineRef = useRef(null);

  useEffect(() => {
    let mounted = true;

    async function loadWork() {
      setLoading(true);
      setError("");
      try {
        const rows = await listTasks();
        const first = rows[0] || null;
        const history = first ? await getConversationMessages(first.conversationId) : { messages: [] };
        if (!mounted) return;
        setTasks(rows);
        setTask(first);
        setMessages(sortMessages(history.messages || []));
      } catch (err) {
        if (mounted) setError(err.message || "Load failed");
      } finally {
        if (mounted) setLoading(false);
      }
    }

    loadWork();
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    timelineRef.current?.scrollTo({
      top: timelineRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages.length, busy]);

  async function addTask() {
    const nextObjective = objective.trim();
    if (!nextObjective || busy) return;
    setBusy(true);
    setError("");
    try {
      const created = await createTask({ objective: nextObjective });
      setTasks((current) => [created, ...current]);
      setTask(created);
      setMessages([]);
      setObjective("");
    } catch (err) {
      setError(err.message || "Create failed");
    } finally {
      setBusy(false);
    }
  }

  async function selectTask(nextTask) {
    if (busy || nextTask.id === task?.id) return;
    setLoading(true);
    setError("");
    try {
      const history = await getConversationMessages(nextTask.conversationId);
      setTask(nextTask);
      setMessages(sortMessages(history.messages || []));
    } catch (err) {
      setError(err.message || "Load failed");
    } finally {
      setLoading(false);
    }
  }

  async function send() {
    const content = draft.trim();
    if (!task || !content || busy) return;
    const pendingMessage = makePendingWorkMessage(task, content, messages);
    setBusy(true);
    setError("");
    setDraft("");
    setMessages((current) => uniqueMessages([...current, pendingMessage]));
    try {
      const data = await sendTaskMessage(task.id, {
        content,
        targetAgentId,
        metadata: {},
      });
      setMessages((current) =>
        uniqueMessages([
          ...current.filter((message) => message.id !== pendingMessage.id),
          data.userMessage,
          data.agentMessage,
        ]),
      );
    } catch (err) {
      setError(err.message || "Send failed");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="chat-grid with-history work-grid">
      <aside className="history-rail">
        <div className="panel-head compact">
          <div>
            <p className="eyebrow">Work</p>
            <h2>Tasks</h2>
          </div>
        </div>
        <div className="task-create">
          <input
            aria-label="Objective"
            disabled={busy || loading}
            onChange={(event) => setObjective(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") addTask();
            }}
            placeholder="Objective"
            value={objective}
          />
          <button disabled={busy || loading || !objective.trim()} onClick={addTask} title="Create" type="button">
            <Plus size={17} />
          </button>
        </div>
        <div className="history-list">
          {tasks.map((item) => (
            <button
              className={`history-item ${item.id === task?.id ? "active" : ""}`}
              key={item.id}
              onClick={() => selectTask(item)}
              type="button"
            >
              <strong>{item.objective}</strong>
              <span>{item.status}</span>
            </button>
          ))}
        </div>
      </aside>
      <section className="timeline-panel">
        <div className="panel-head">
          <div>
            <p className="eyebrow">Work</p>
            <h2>{task?.objective || "Task"}</h2>
          </div>
          <span className="chip">{task?.status || "new"}</span>
        </div>
        <Timeline agents={agentProfiles} messages={messages} timelineRef={timelineRef} />
        <div className="composer">
          <input
            aria-label="Work message"
            disabled={busy || loading || !task}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") send();
            }}
            placeholder="Next step"
            value={draft}
          />
          <button disabled={busy || loading || !task} onClick={send} title="Send" type="button">
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
        <div className="context-item">
          <span>Phase</span>
          <p>{task?.currentPhase || "intake"}</p>
        </div>
        <StatusLine error={error} loading={loading} text={busy ? "Working" : ""} />
      </aside>
    </div>
  );
}

function makePendingWorkMessage(task, content, messages) {
  const maxSequence = Math.max(0, ...messages.map((message) => message.sequence || 0));
  return {
    id: `pending-${crypto.randomUUID()}`,
    conversationId: task.conversationId,
    userId: task.userId,
    mode: "work",
    sequence: maxSequence + 0.5,
    senderType: "user",
    senderId: "me",
    senderSlot: null,
    role: "user",
    content,
    contentType: "text",
    metadata: { pending: true },
    createdAt: new Date().toISOString(),
  };
}

export default WorkPage;
