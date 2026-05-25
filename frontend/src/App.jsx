/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
*/
import {
  Activity,
  Bot,
  Brain,
  BriefcaseBusiness,
  CirclePause,
  MessageSquare,
  Moon,
  Send,
  Settings2,
  Sparkles,
  UserRound,
} from "lucide-react";
import { useMemo, useState } from "react";

const agents = [
  {
    slot: "A1",
    name: "Nora",
    color: "teal",
    voice: "precise",
    state: "Thinking",
    core: "Calm systems thinker. Loves structure, memory, and clean decisions.",
    mood: "tracking the thread",
  },
  {
    slot: "A2",
    name: "Vale",
    color: "amber",
    voice: "sharp",
    state: "Writing",
    core: "Restless critic. Tests ideas, pushes tension, and notices weak plans.",
    mood: "challenging the premise",
  },
];

const idleMessages = [
  {
    id: 1,
    type: "agent",
    agent: agents[0],
    text: "If a world runs while no one watches, it still needs memory.",
    time: "16:42",
  },
  {
    id: 2,
    type: "agent",
    agent: agents[1],
    text: "Memory is not enough. It needs friction, or every day becomes a smooth lie.",
    time: "16:43",
  },
  {
    id: 3,
    type: "agent",
    agent: agents[0],
    text: "Then the bond is a state machine. Trust rises when conflict resolves.",
    time: "16:44",
  },
  {
    id: 4,
    type: "system",
    text: "Scene updated",
    meta: "Topic: memory, conflict, trust",
  },
  {
    id: 5,
    type: "agent",
    agent: agents[1],
    text: "Good. Make that visible. Users should see the scar, not only the summary.",
    time: "16:45",
  },
];

const chatMessages = [
  {
    id: 1,
    type: "user",
    text: "What did you learn from the idle debate?",
  },
  {
    id: 2,
    type: "agent",
    agent: agents[0],
    text: "A living Agent needs evidence, not vibes. Memory should point back to events.",
  },
  {
    id: 3,
    type: "agent",
    agent: agents[1],
    text: "And it needs a way to disagree without becoming random.",
  },
];

const navItems = [
  { id: "idle", label: "Idle", icon: Activity },
  { id: "chat", label: "Chat", icon: MessageSquare },
  { id: "agents", label: "Agents", icon: Bot },
  { id: "work", label: "Work", icon: BriefcaseBusiness },
];

function App() {
  const [view, setView] = useState("idle");
  const [joined, setJoined] = useState(false);
  const [idleOn, setIdleOn] = useState(true);
  const [draft, setDraft] = useState("");
  const [timeline, setTimeline] = useState(idleMessages);

  const mode = joined ? "Joined" : view === "chat" ? "Chat" : view === "work" ? "Work" : "Idle";

  function joinIdle() {
    const message = draft.trim();
    if (!message) return;

    setJoined(true);
    setTimeline((items) => [
      ...items,
      { id: crypto.randomUUID(), type: "system", text: "You joined", meta: "Joined" },
      { id: crypto.randomUUID(), type: "user", text: message, time: "now" },
      {
        id: crypto.randomUUID(),
        type: "agent",
        agent: agents[0],
        text: "You arrived inside the thread. We were testing whether trust needs conflict.",
        time: "now",
      },
      {
        id: crypto.randomUUID(),
        type: "agent",
        agent: agents[1],
        text: "So answer this: should an Agent remember the wound or only the lesson?",
        time: "now",
      },
    ]);
    setDraft("");
  }

  return (
    <main className="app-shell">
      <Sidebar view={view} setView={setView} mode={mode} />
      <section className="workspace">
        <Topbar mode={mode} idleOn={idleOn} setIdleOn={setIdleOn} />
        {view === "idle" && (
          <IdleView
            draft={draft}
            setDraft={setDraft}
            idleOn={idleOn}
            joinIdle={joinIdle}
            timeline={timeline}
          />
        )}
        {view === "chat" && <ChatView />}
        {view === "agents" && <AgentsView idleOn={idleOn} setIdleOn={setIdleOn} />}
        {view === "work" && <WorkView />}
      </section>
    </main>
  );
}

function Sidebar({ view, setView, mode }) {
  return (
    <aside className="sidebar">
      <div className="brand">
        <Sparkles size={18} />
        <span>Hackson</span>
      </div>
      <nav className="nav-list" aria-label="Main">
        {navItems.map((item) => {
          const Icon = item.icon;
          return (
            <button
              className={view === item.id ? "nav-item active" : "nav-item"}
              key={item.id}
              onClick={() => setView(item.id)}
              title={item.label}
              type="button"
            >
              <Icon size={18} />
              <span>{item.label}</span>
            </button>
          );
        })}
      </nav>
      <div className="sidebar-foot">
        <span className="mode-dot" />
        <span>{mode}</span>
      </div>
    </aside>
  );
}

function Topbar({ mode, idleOn, setIdleOn }) {
  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">World</p>
        <h1>Two Agents, one timeline</h1>
      </div>
      <div className="topbar-actions">
        <span className="chip">{mode}</span>
        <button className="icon-button" onClick={() => setIdleOn(!idleOn)} title={idleOn ? "Pause" : "Resume"} type="button">
          {idleOn ? <CirclePause size={18} /> : <Activity size={18} />}
        </button>
      </div>
    </header>
  );
}

function IdleView({ draft, setDraft, idleOn, joinIdle, timeline }) {
  return (
    <div className="idle-grid">
      <AgentRail />
      <section className="timeline-panel">
        <div className="panel-head">
          <div>
            <p className="eyebrow">Idle</p>
            <h2>Live thread</h2>
          </div>
          <span className={idleOn ? "live-pill" : "live-pill paused"}>{idleOn ? "Live" : "Paused"}</span>
        </div>
        <Timeline items={timeline} />
        <div className="composer">
          <input
            aria-label="Join"
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") joinIdle();
            }}
            placeholder="Join"
            value={draft}
          />
          <button onClick={joinIdle} title="Send" type="button">
            <Send size={18} />
          </button>
        </div>
      </section>
      <ContextRail />
    </div>
  );
}

function AgentRail() {
  return (
    <aside className="agent-rail">
      {agents.map((agent) => (
        <AgentSlot agent={agent} key={agent.slot} />
      ))}
      <div className="mini-panel">
        <p className="eyebrow">Scene</p>
        <strong>Observatory</strong>
        <span>quiet, active</span>
      </div>
    </aside>
  );
}

function AgentSlot({ agent }) {
  return (
    <article className={`agent-slot ${agent.color}`}>
      <div className="avatar" aria-hidden="true">
        {agent.slot}
      </div>
      <div>
        <div className="agent-line">
          <strong>{agent.name}</strong>
          <span>{agent.state}</span>
        </div>
        <p>{agent.voice}</p>
        <small>{agent.mood}</small>
      </div>
    </article>
  );
}

function Timeline({ items }) {
  return (
    <div className="timeline" aria-label="Timeline">
      {items.map((item) => {
        if (item.type === "system") {
          return (
            <div className="system-event" key={item.id}>
              <Moon size={14} />
              <span>{item.text}</span>
              <small>{item.meta}</small>
            </div>
          );
        }

        const color = item.agent?.color ?? "user";
        return (
          <article className={`message-row ${color}`} key={item.id}>
            <div className="message-meta">
              <strong>{item.agent?.name ?? "You"}</strong>
              <span>{item.time}</span>
            </div>
            <p>{item.text}</p>
          </article>
        );
      })}
    </div>
  );
}

function ContextRail() {
  const context = useMemo(
    () => [
      ["Topic", "memory, conflict, trust"],
      ["Bond", "high tension, stable respect"],
      ["Memory", "evidence before summary"],
      ["Package", "ctx local draft"],
    ],
    [],
  );

  return (
    <aside className="context-rail">
      <div className="panel-head compact">
        <div>
          <p className="eyebrow">Context</p>
          <h2>Now</h2>
        </div>
        <Brain size={18} />
      </div>
      {context.map(([label, value]) => (
        <section className="context-item" key={label}>
          <span>{label}</span>
          <p>{value}</p>
        </section>
      ))}
    </aside>
  );
}

function ChatView() {
  return (
    <div className="chat-grid">
      <section className="timeline-panel">
        <div className="panel-head">
          <div>
            <p className="eyebrow">Chat</p>
            <h2>Focused thread</h2>
          </div>
          <span className="chip">Both</span>
        </div>
        <Timeline items={chatMessages} />
        <div className="composer">
          <input aria-label="Message" placeholder="Message" />
          <button title="Send" type="button">
            <Send size={18} />
          </button>
        </div>
      </section>
      <ContextRail />
    </div>
  );
}

function AgentsView({ idleOn, setIdleOn }) {
  return (
    <section className="settings-view">
      <div className="settings-head">
        <div>
          <p className="eyebrow">Agents</p>
          <h2>Identity</h2>
        </div>
        <label className="switch-row">
          <span>Idle</span>
          <input checked={idleOn} onChange={() => setIdleOn(!idleOn)} type="checkbox" />
        </label>
      </div>
      <div className="agent-editor-grid">
        {agents.map((agent) => (
          <article className={`editor-card ${agent.color}`} key={agent.slot}>
            <AgentSlot agent={agent} />
            <label>
              <span>Name</span>
              <input defaultValue={agent.name} />
            </label>
            <label>
              <span>Voice</span>
              <input defaultValue={agent.voice} />
            </label>
            <label>
              <span>Core</span>
              <textarea defaultValue={agent.core} />
            </label>
          </article>
        ))}
      </div>
    </section>
  );
}

function WorkView() {
  return (
    <section className="work-view">
      <div className="panel-head">
        <div>
          <p className="eyebrow">Work</p>
          <h2>Reserved</h2>
        </div>
        <Settings2 size={18} />
      </div>
      <div className="work-board">
        {["Plan", "Build", "Review"].map((lane) => (
          <article className="work-lane" key={lane}>
            <span>{lane}</span>
            <p>Waiting</p>
          </article>
        ))}
      </div>
      <div className="tool-trace">
        <UserRound size={18} />
        <span>Task memory stays separate.</span>
      </div>
    </section>
  );
}

export default App;
