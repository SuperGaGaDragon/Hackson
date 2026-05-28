/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { useEffect, useState } from "react";
import {
  deleteMemoryCard,
  deletePromptLogs,
  listMemoryCards,
  listPromptLogs,
  logoutUser,
  updateCurrentUser,
  updateMemoryCard,
} from "../../api/users";
import { normalizeUserAgentProfiles } from "../../domain/agents";
import StatusLine from "../../shared/components/StatusLine";

function MePage({ onLogout, onUserUpdate, user }) {
  const [form, setForm] = useState({
    display_name: user?.displayName || "",
    idle_on: user?.idleOn ?? true,
    backgroundIdleOn: user?.backgroundIdleOn ?? false,
    fullPromptLoggingOn: user?.fullPromptLoggingOn ?? true,
    language_preference: user?.languagePreference || "zh",
    personality: user?.personality || "",
    story: user?.story || "",
    agentProfiles: normalizeUserAgentProfiles(user),
  });
  const [saving, setSaving] = useState(false);
  const [loadingLogs, setLoadingLogs] = useState(false);
  const [loadingMemory, setLoadingMemory] = useState(false);
  const [deletingLogs, setDeletingLogs] = useState(false);
  const [promptLogs, setPromptLogs] = useState([]);
  const [memoryCards, setMemoryCards] = useState([]);
  const [memoryBusyId, setMemoryBusyId] = useState("");
  const [error, setError] = useState("");
  const [saved, setSaved] = useState("");

  useEffect(() => {
    setForm({
      display_name: user?.displayName || "",
      idle_on: user?.idleOn ?? true,
      backgroundIdleOn: user?.backgroundIdleOn ?? false,
      fullPromptLoggingOn: user?.fullPromptLoggingOn ?? true,
      language_preference: user?.languagePreference || "zh",
      personality: user?.personality || "",
      story: user?.story || "",
      agentProfiles: normalizeUserAgentProfiles(user),
    });
  }, [user]);

  useEffect(() => {
    let mounted = true;

    async function loadPromptLogs() {
      setLoadingLogs(true);
      try {
        const data = await listPromptLogs();
        if (mounted) setPromptLogs(data.promptLogs || []);
      } catch (err) {
        if (mounted) setError(err.message || "Logs failed");
      } finally {
        if (mounted) setLoadingLogs(false);
      }
    }

    loadPromptLogs();
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    let mounted = true;

    async function loadMemory() {
      setLoadingMemory(true);
      try {
        const data = await listMemoryCards();
        if (mounted) setMemoryCards(data.memoryCards || []);
      } catch (err) {
        if (mounted) setError(err.message || "Memory failed");
      } finally {
        if (mounted) setLoadingMemory(false);
      }
    }

    loadMemory();
    return () => {
      mounted = false;
    };
  }, []);

  async function save(event) {
    event.preventDefault();
    setSaving(true);
    setError("");
    setSaved("");
    try {
      const updated = await updateCurrentUser(form);
      onUserUpdate(updated);
      setSaved("Saved");
    } catch (err) {
      setError(err.message || "Save failed");
    } finally {
      setSaving(false);
    }
  }

  async function logout() {
    await logoutUser();
    onLogout();
  }

  async function clearLogs() {
    setDeletingLogs(true);
    setError("");
    setSaved("");
    try {
      const response = await deletePromptLogs();
      setPromptLogs([]);
      setSaved(`Deleted ${response.deletedPromptLogs || 0}`);
    } catch (err) {
      setError(err.message || "Delete failed");
    } finally {
      setDeletingLogs(false);
    }
  }

  async function setMemoryStatus(memoryId, status) {
    setMemoryBusyId(memoryId);
    setError("");
    setSaved("");
    try {
      const updated = await updateMemoryCard(memoryId, status);
      setMemoryCards((cards) => cards.map((card) => (card.id === memoryId ? updated : card)));
      setSaved("Saved");
    } catch (err) {
      setError(err.message || "Memory failed");
    } finally {
      setMemoryBusyId("");
    }
  }

  async function removeMemory(memoryId) {
    setMemoryBusyId(memoryId);
    setError("");
    setSaved("");
    try {
      await deleteMemoryCard(memoryId);
      setMemoryCards((cards) => cards.filter((card) => card.id !== memoryId));
      setSaved("Deleted");
    } catch (err) {
      setError(err.message || "Delete failed");
    } finally {
      setMemoryBusyId("");
    }
  }

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  function updateAgent(slot, field, value) {
    setForm((current) => ({
      ...current,
      agentProfiles: current.agentProfiles.map((agent) =>
        agent.slot === slot ? { ...agent, [field]: value } : agent,
      ),
    }));
  }

  return (
    <section className="settings-view">
      <div className="settings-head">
        <div>
          <p className="eyebrow">Me</p>
          <h2>{user?.username}</h2>
        </div>
        <button className="secondary-button" onClick={logout} type="button">
          Logout
        </button>
      </div>
      <form className="settings-form" onSubmit={save}>
        <section className="me-section account-section">
          <div className="section-title">
            <p className="eyebrow">Account</p>
            <h3>Profile</h3>
          </div>
          <div className="account-grid">
            <label>
              <span>Name</span>
              <input onChange={(event) => updateField("display_name", event.target.value)} value={form.display_name} />
            </label>
            <label>
              <span>Lang</span>
              <select
                onChange={(event) => updateField("language_preference", event.target.value)}
                value={form.language_preference}
              >
                <option value="zh">zh</option>
                <option value="en">en</option>
              </select>
            </label>
          </div>
          <div className="settings-toggle-grid">
            <ToggleControl
              checked={form.idle_on}
              label="Idle"
              onChange={(checked) => updateField("idle_on", checked)}
            />
            <ToggleControl
              checked={form.backgroundIdleOn}
              label="Away idle"
              onChange={(checked) => updateField("backgroundIdleOn", checked)}
            />
          </div>
        </section>

        <section className="me-section">
          <div className="section-title">
            <p className="eyebrow">Agents</p>
            <h3>Nora & Vale</h3>
          </div>
          <div className="agent-editor-grid">
            {form.agentProfiles.map((agent) => (
              <AgentEditor agent={agent} key={agent.slot} onUpdate={updateAgent} />
            ))}
          </div>
        </section>

        <section className="me-section">
          <div className="section-title">
            <p className="eyebrow">You</p>
            <h3>Context</h3>
          </div>
          <div className="user-context-grid">
            <label>
              <span>Style · {form.personality.length}/1200</span>
              <textarea
                maxLength={1200}
                onChange={(event) => updateField("personality", event.target.value)}
                placeholder="Direct, reflective, low-fluff..."
                rows={4}
                value={form.personality}
              />
            </label>
            <label>
              <span>Background · {form.story.length}/4000</span>
              <textarea
                maxLength={4000}
                onChange={(event) => updateField("story", event.target.value)}
                placeholder="What should they keep in mind about you?"
                rows={4}
                value={form.story}
              />
            </label>
          </div>
        </section>

        <MemorySection
          busyId={memoryBusyId}
          cards={memoryCards}
          loading={loadingMemory}
          onDelete={removeMemory}
          onStatus={setMemoryStatus}
        />

        <details className="debug-panel">
          <summary>
            <span>Debug</span>
            <small>
              Logs · {loadingLogs ? "..." : promptLogs.length}
            </small>
          </summary>
          <div className="debug-content">
            <ToggleControl
              checked={form.fullPromptLoggingOn}
              label="Prompt log"
              onChange={(checked) => updateField("fullPromptLoggingOn", checked)}
            />
            <div className="prompt-log-head">
              <span>Prompt logs</span>
              <button
                className="secondary-button"
                disabled={deletingLogs || promptLogs.length === 0}
                onClick={clearLogs}
                type="button"
              >
                {deletingLogs ? "Wait" : "Delete"}
              </button>
            </div>
            {promptLogs.length > 0 && (
              <div className="prompt-log-list">
                {promptLogs.map((log) => (
                  <details className="prompt-log-item" key={log.id}>
                    <summary>
                      <span>{log.mode}</span>
                      <code>{shortHash(log.promptHash)}</code>
                    </summary>
                    <pre>{log.fullPromptText}</pre>
                  </details>
                ))}
              </div>
            )}
          </div>
        </details>

        <div className="settings-actions">
          <button className="primary-button" disabled={saving} type="submit">
            {saving ? "Wait" : "Save"}
          </button>
          <StatusLine error={error} text={saved} />
        </div>
      </form>
    </section>
  );
}

function ToggleControl({ checked, label, onChange }) {
  return (
    <label className="toggle-control">
      <input checked={checked} onChange={(event) => onChange(event.target.checked)} type="checkbox" />
      <span>{label}</span>
      <strong>{checked ? "On" : "Off"}</strong>
    </label>
  );
}

function AgentEditor({ agent, onUpdate }) {
  return (
    <section className={`agent-editor ${agent.color}`}>
      <div className="agent-editor-head">
        <span>{agent.short}</span>
        <strong>{agent.name || agent.slot}</strong>
      </div>
      <div className="agent-editor-row">
        <label>
          <span>Name</span>
          <input maxLength={32} onChange={(event) => onUpdate(agent.slot, "name", event.target.value)} value={agent.name} />
        </label>
        <label>
          <span>Voice · {agent.voice.length}/80</span>
          <input maxLength={80} onChange={(event) => onUpdate(agent.slot, "voice", event.target.value)} value={agent.voice} />
        </label>
      </div>
      <label>
        <span>Personality · {agent.personality.length}/1200</span>
        <textarea
          maxLength={1200}
          onChange={(event) => onUpdate(agent.slot, "personality", event.target.value)}
          rows={4}
          value={agent.personality}
        />
      </label>
      <label>
        <span>Story · {agent.story.length}/4000</span>
        <textarea
          maxLength={4000}
          onChange={(event) => onUpdate(agent.slot, "story", event.target.value)}
          rows={4}
          value={agent.story}
        />
      </label>
    </section>
  );
}

function MemorySection({ busyId, cards, loading, onDelete, onStatus }) {
  return (
    <section className="me-section memory-panel">
      <div className="section-title memory-title">
        <div>
          <p className="eyebrow">Memory</p>
          <h3>{loading ? "..." : cards.length}</h3>
        </div>
      </div>
      {cards.length === 0 ? (
        <p className="empty-note">No saved memory yet.</p>
      ) : (
        <div className="memory-list">
          {cards.map((card) => (
            <article className="memory-item" key={card.id}>
              <div>
                <span>
                  {card.scope} · {card.memoryType} · {card.status} · {Math.round((card.confidence || 0) * 100)}%
                </span>
                <p>{card.summary}</p>
              </div>
              <div className="memory-actions">
                {card.status === "active" ? (
                  <button className="secondary-button" disabled={busyId === card.id} onClick={() => onStatus(card.id, "disabled")} type="button">
                    Off
                  </button>
                ) : (
                  <button className="secondary-button" disabled={busyId === card.id} onClick={() => onStatus(card.id, "active")} type="button">
                    On
                  </button>
                )}
                <button className="secondary-button" disabled={busyId === card.id} onClick={() => onDelete(card.id)} type="button">
                  Delete
                </button>
              </div>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

function shortHash(hash) {
  return hash ? hash.slice(0, 10) : "no hash";
}

export default MePage;
