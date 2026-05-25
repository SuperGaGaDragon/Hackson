/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
*/
import { useEffect, useState } from "react";
import { logoutUser, updateCurrentUser } from "../../api/users";
import StatusLine from "../../shared/components/StatusLine";

function MePage({ onLogout, onUserUpdate, user }) {
  const [form, setForm] = useState({
    display_name: user?.displayName || "",
    idle_on: user?.idleOn ?? true,
    language_preference: user?.languagePreference || "zh",
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [saved, setSaved] = useState("");

  useEffect(() => {
    setForm({
      display_name: user?.displayName || "",
      idle_on: user?.idleOn ?? true,
      language_preference: user?.languagePreference || "zh",
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
          <input
            onChange={(event) => setForm((current) => ({ ...current, display_name: event.target.value }))}
            value={form.display_name}
          />
        </label>
        <label>
          <span>Lang</span>
          <select
            onChange={(event) => setForm((current) => ({ ...current, language_preference: event.target.value }))}
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
            onChange={(event) => setForm((current) => ({ ...current, idle_on: event.target.checked }))}
            type="checkbox"
          />
        </label>
        <button className="primary-button" disabled={saving} type="submit">
          {saving ? "Wait" : "Save"}
        </button>
        <StatusLine error={error} text={saved} />
      </form>
    </section>
  );
}

export default MePage;
