/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { Activity, BriefcaseBusiness, Download, MessageSquare, Sparkles, UserRound } from "lucide-react";
import { useEffect, useState } from "react";
import { listAgents } from "./api/agents";
import { getToken } from "./api/client";
import { bindDesktopHandoff, getCurrentUser } from "./api/users";
import { FALLBACK_AGENTS, normalizeAgents } from "./domain/agents";
import AuthPage from "./features/auth/AuthPage";
import HackathonLanding from "./features/auth/HackathonLanding";
import ChatPage from "./features/chat/ChatPage";
import CompanionDownloadPage from "./features/download/CompanionDownloadPage";
import IdlePage from "./features/idle/IdlePage";
import MePage from "./features/me/MePage";
import WorkPage from "./features/work/WorkPage";
import StatusLine from "./shared/components/StatusLine";

const navItems = [
  { id: "idle", label: "Idle", icon: Activity },
  { id: "chat", label: "Chat", icon: MessageSquare },
  { id: "work", label: "Work", icon: BriefcaseBusiness },
  { id: "me", label: "Me", icon: UserRound },
  { id: "download", label: "Mac", icon: Download },
];

function App() {
  const initialRoute = readRouteFromLocation();
  const [view, setView] = useState(initialRoute.view);
  const [routeParams, setRouteParams] = useState(initialRoute.params);
  const [user, setUser] = useState(null);
  const [agents, setAgents] = useState(FALLBACK_AGENTS);
  const [booting, setBooting] = useState(true);
  const [error, setError] = useState("");
  const [authMode, setAuthMode] = useState("landing");
  const desktopAuthCode = getDesktopAuthCode();

  useEffect(() => {
    function handlePopState() {
      const route = readRouteFromLocation();
      setView(route.view);
      setRouteParams(route.params);
    }
    window.addEventListener("popstate", handlePopState);
    return () => window.removeEventListener("popstate", handlePopState);
  }, []);

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
        if (desktopAuthCode) await completeDesktopHandoff(desktopAuthCode, setError);
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
  }, [desktopAuthCode]);

  if (view === "download") {
    return <CompanionDownloadPage onOpenApp={() => navigateTo("idle", setView, setRouteParams)} />;
  }

  if (booting) {
    return (
      <main className="auth-shell">
        <StatusLine loading text="Loading" />
      </main>
    );
  }

  if (!user) {
    const handleAuth = (nextUser) => handleAuthed(nextUser, setUser, setAgents, setError, desktopAuthCode);
    const handleQuickAuth = async (nextUser) => {
      await handleAuth(nextUser);
      navigateTo("work", setView, setRouteParams);
    };
    if (authMode === "landing") {
      return <HackathonLanding onAuthed={handleQuickAuth} onOpenAuth={(mode) => setAuthMode(mode)} />;
    }
    return <AuthPage initialMode={authMode} onAuthed={handleAuth} onBack={() => setAuthMode("landing")} />;
  }

  const visibleAgents = normalizeAgents(user.agentProfiles || agents);

  return (
    <main className="app-shell">
      <Sidebar setRouteParams={setRouteParams} setView={setView} user={user} view={view} />
      <section className="workspace">
        <Topbar error={error} view={view} />
        {view === "idle" && <IdlePage agents={visibleAgents} user={user} />}
        {view === "chat" && <ChatPage agents={visibleAgents} user={user} />}
        {view === "work" && <WorkPage agents={visibleAgents} initialRoute={routeParams} />}
        {view === "me" && (
          <MePage
            onLogout={() => {
              setUser(null);
              navigateTo("idle", setView, setRouteParams);
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

async function handleAuthed(nextUser, setUser, setAgents, setError, desktopAuthCode = "") {
  setUser(nextUser);
  if (desktopAuthCode) await completeDesktopHandoff(desktopAuthCode, setError);
  try {
    setAgents(await loadAgentProfiles());
  } catch (err) {
    setAgents(FALLBACK_AGENTS);
    setError(err.message || "Agents failed");
  }
}

function getDesktopAuthCode() {
  return new URLSearchParams(window.location.search).get("desktopAuth") || "";
}

async function completeDesktopHandoff(code, setError) {
  try {
    await bindDesktopHandoff(code);
    const url = new URL(window.location.href);
    url.searchParams.delete("desktopAuth");
    window.history.replaceState({}, "", `${url.pathname}${url.search}${url.hash}`);
  } catch (err) {
    setError(err.message || "Desktop link failed");
  }
}

function readRouteFromLocation() {
  const pathname = window.location.pathname.replace(/\/+$/, "") || "/";
  if (pathname === "/download/companion") return { view: "download", params: {} };
  if (pathname === "/companion") return { view: "chat", params: {} };
  if (pathname === "/work") return { view: "work", params: {} };
  if (pathname.startsWith("/work_project/")) {
    return { view: "work", params: { projectId: decodeRoutePart(pathname.split("/")[2]) } };
  }
  if (pathname.startsWith("/work_mission/")) {
    return { view: "work", params: { missionId: decodeRoutePart(pathname.split("/")[2]) } };
  }
  if (pathname === "/me") return { view: "me", params: {} };
  return { view: "idle", params: {} };
}

function decodeRoutePart(value = "") {
  try {
    return decodeURIComponent(value);
  } catch {
    return value;
  }
}

function navigateTo(view, setView, setRouteParams, params = {}) {
  const path = pathForView(view, params);
  if (window.location.pathname !== path) {
    window.history.pushState({}, "", path);
  }
  setView(view);
  setRouteParams(params);
}

function pathForView(view, params = {}) {
  if (view === "chat") return "/companion";
  if (view === "work") {
    if (params.projectId) return `/work_project/${encodeURIComponent(params.projectId)}`;
    if (params.missionId) return `/work_mission/${encodeURIComponent(params.missionId)}`;
    return "/work";
  }
  if (view === "me") return "/me";
  if (view === "download") return "/download/companion";
  return "/idle";
}

function Sidebar({ setRouteParams, setView, user, view }) {
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
              onClick={() => navigateTo(item.id, setView, setRouteParams)}
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
