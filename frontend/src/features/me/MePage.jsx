/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
*/
import { useEffect, useState } from "react";
import { logoutUser, updateCurrentUser } from "../../api/users";
import { normalizeUserAgentProfiles } from "../../domain/agents";
import StatusLine from "../../shared/components/StatusLine";

function MePage({ onLogout, onUserUpdate, user }) {
  const [form, setForm] = useState({
    display_name: user?.displayName || "",
    idle_on: user?.idleOn ?? true,
    language_preference: user?.languagePreference || "zh",
    personality: user?.personality || "",
    story: user?.story || "",
    agentProfiles: normalizeUserAgentProfiles(user),
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState("");

  useEffect(() => {
    setForm({
      display_name: user?.displayName || "",
      idle_on: user?.idleOn ?? true,
      language_preference: user?.languagePreference || "zh",
      personality: user?.personality || "",
      story: user?.story || "",
      agentProfiles: normalizeUserAgentProfiles(user),
    });
  }, [user]);

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
        <label className="switch-row">
          <span>Idle</span>
          <input
            checked={form.idle_on}
            onChange={(event) => updateField("idle_on", event.target.checked)}
            type="checkbox"
          />
        </label>
        <label>
          <span>Personality · {form.personality.length}/1200</span>
          <textarea
            maxLength={1200}
            onChange={(event) => updateField("personality", event.target.value)}
            placeholder="quiet, direct, product-minded"
            rows={5}
            value={form.personality}
          />
        </label>
        <label>
          <span>Story · {form.story.length}/4000</span>
          <textarea
            maxLength={4000}
            onChange={(event) => updateField("story", event.target.value)}
            placeholder="I am building..."
            rows={8}
            value={form.story}
          />
        </label>
        <div className="agent-editor-grid">
          {form.agentProfiles.map((agent) => (
            <section className={`agent-editor ${agent.color}`} key={agent.slot}>
              <div className="agent-editor-head">
                <span>{agent.short}</span>
                <strong>{agent.name || agent.slot}</strong>
              </div>
              <label>
                <span>Name</span>
                <input
                  maxLength={32}
                  onChange={(event) => updateAgent(agent.slot, "name", event.target.value)}
                  value={agent.name}
                />
              </label>
              <label>
                <span>Voice · {agent.voice.length}/80</span>
                <input
                  maxLength={80}
                  onChange={(event) => updateAgent(agent.slot, "voice", event.target.value)}
                  value={agent.voice}
                />
              </label>
              <label>
                <span>Personality · {agent.personality.length}/1200</span>
                <textarea
                  maxLength={1200}
                  onChange={(event) => updateAgent(agent.slot, "personality", event.target.value)}
                  rows={5}
                  value={agent.personality}
                />
              </label>
              <label>
                <span>Story · {agent.story.length}/4000</span>
                <textarea
                  maxLength={4000}
                  onChange={(event) => updateAgent(agent.slot, "story", event.target.value)}
                  rows={6}
                  value={agent.story}
                />
              </label>
            </section>
          ))}
        </div>
        <button className="primary-button" disabled={saving} type="submit">
          {saving ? "Wait" : "Save"}
        </button>
        <StatusLine error={error} text={saved} />
      </form>
    </section>
  );
}

export default MePage;
