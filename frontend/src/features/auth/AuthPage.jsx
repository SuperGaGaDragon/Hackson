/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
*/
import { useState } from "react";
import { loginUser, registerUser } from "../../api/users";
import StatusLine from "../../shared/components/StatusLine";

function AuthPage({ onAuthed }) {
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({
    username: "",
    email: "",
    identifier: "",
    password: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function submit(event) {
    event.preventDefault();
    setLoading(true);
    setError("");

    try {
      const data =
        mode === "login"
          ? await loginUser({ identifier: form.identifier, password: form.password })
          : await registerUser({
              username: form.username,
              email: form.email,
              password: form.password,
            });
      onAuthed(data.user);
    } catch (err) {
      setError(err.message || "Failed");
    } finally {
      setLoading(false);
    }
  }

  function updateField(field, value) {
    setForm((current) => ({ ...current, [field]: value }));
  }

  return (
    <main className="auth-shell">
      <section className="auth-panel">
        <p className="eyebrow">Hackson</p>
        <h1>Enter</h1>
        <div className="segmented">
          <button className={mode === "login" ? "active" : ""} onClick={() => setMode("login")} type="button">
            Login
          </button>
          <button className={mode === "register" ? "active" : ""} onClick={() => setMode("register")} type="button">
            Register
          </button>
        </div>
        <form className="auth-form" onSubmit={submit}>
          {mode === "register" && (
            <>
              <label>
                <span>User</span>
                <input
                  autoComplete="username"
                  onChange={(event) => updateField("username", event.target.value)}
                  required
                  value={form.username}
                />
              </label>
              <label>
                <span>Email</span>
                <input
                  autoComplete="email"
                  onChange={(event) => updateField("email", event.target.value)}
                  required
                  type="email"
                  value={form.email}
                />
              </label>
            </>
          )}
          {mode === "login" && (
            <label>
              <span>User</span>
              <input
                autoComplete="username"
                onChange={(event) => updateField("identifier", event.target.value)}
                required
                value={form.identifier}
              />
            </label>
          )}
          <label>
            <span>Pass</span>
            <input
              autoComplete={mode === "login" ? "current-password" : "new-password"}
              minLength={8}
              onChange={(event) => updateField("password", event.target.value)}
              required
              type="password"
              value={form.password}
            />
          </label>
          <button className="primary-button" disabled={loading} type="submit">
            {loading ? "Wait" : "Enter"}
          </button>
          <StatusLine error={error} />
        </form>
      </section>
    </main>
  );
}

export default AuthPage;
