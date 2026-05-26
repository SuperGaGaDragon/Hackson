/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex
*/
import { Activity, BriefcaseBusiness, MessageSquare, Sparkles, UserRound } from "lucide-react";
import { useEffect, useState } from "react";
import { listAgents } from "./api/agents";
import { getToken } from "./api/client";
import { getCurrentUser } from "./api/users";
import { FALLBACK_AGENTS, normalizeAgents } from "./domain/agents";
import AuthPage from "./features/auth/AuthPage";
import ChatPage from "./features/chat/ChatPage";
import IdlePage from "./features/idle/IdlePage";
import MePage from "./features/me/MePage";
import WorkPage from "./features/work/WorkPage";
import StatusLine from "./shared/components/StatusLine";

const navItems = [
  { id: "idle", label: "Idle", icon: Activity },
  { id: "chat", label: "Chat", icon: MessageSquare },
  { id: "work", label: "Work", icon: BriefcaseBusiness },
  { id: "me", label: "Me", icon: UserRound },
];

function App() {
  const [view, setView] = useState("idle");
  const [user, setUser] = useState(null);
  const [agents, setAgents] = useState(FALLBACK_AGENTS);
  const [booting, setBooting] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let mounted = true;

    async function boot() {
      if (!getToken()) {
        setBooting(false);
        return;
      }

      try {
        const currentUser = await getCurrentUser();
        if (!mounted) return;
        setUser(currentUser);
        try {
          setAgents(await loadAgentProfiles());
        } catch (err) {
          setAgents(FALLBACK_AGENTS);
          setError(err.message || "Agents failed");
        }
      } catch (err) {
        if (mounted) setError(err.message || "Auth failed");
      } finally {
        if (mounted) setBooting(false);
      }
    }

    boot();
    return () => {
      mounted = false;
    };
  }, []);

  if (booting) {
    return (
      <main className="auth-shell">
        <StatusLine loading text="Loading" />
      </main>
    );
  }

  if (!user) {
    return <AuthPage onAuthed={(nextUser) => handleAuthed(nextUser, setUser, setAgents, setError)} />;
  }

  return (
    <main className="app-shell">
      <Sidebar setView={setView} user={user} view={view} />
      <section className="workspace">
        <Topbar error={error} view={view} />
        {view === "idle" && <IdlePage agents={agents} />}
        {view === "chat" && <ChatPage agents={agents} />}
        {view === "work" && <WorkPage agents={agents} />}
        {view === "me" && (
          <MePage
            onLogout={() => {
              setUser(null);
              setView("idle");
            }}
            onUserUpdate={setUser}
            user={user}
          />
        )}
      </section>
    </main>
  );
}

async function loadAgentProfiles() {
  return normalizeAgents(await listAgents());
}

async function handleAuthed(nextUser, setUser, setAgents, setError) {
  setUser(nextUser);
  try {
    setAgents(await loadAgentProfiles());
  } catch (err) {
    setAgents(FALLBACK_AGENTS);
    setError(err.message || "Agents failed");
  }
}

function Sidebar({ setView, user, view }) {
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
        <span>{user.username}</span>
      </div>
    </aside>
  );
}

function Topbar({ error, view }) {
  const title =
    view === "idle" ? "Live timeline" : view === "chat" ? "Companion" : view === "work" ? "Work" : "Settings";

  return (
    <header className="topbar">
      <div>
        <p className="eyebrow">Hackson</p>
        <h1>{title}</h1>
      </div>
      <div className="topbar-actions">
        <span className="chip">{view}</span>
        {error && <span className="chip error-chip">{error}</span>}
      </div>
    </header>
  );
}

export default App;
