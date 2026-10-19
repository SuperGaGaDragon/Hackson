/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-10-19
Last Modified by: Codex
*/
import { ArrowRight, UserPlus } from "lucide-react";
import { useState } from "react";
import BrandWordmark from "../../shared/components/BrandWordmark";
import StatusLine from "../../shared/components/StatusLine";

const productModes = [
  {
    description: "Two agents handle your task, with steps you can review.",
    href: "/work",
    label: "Open Work",
    title: "Work",
    view: "work",
  },
  {
    description: "Sort out your thoughts and explore ideas before acting.",
    href: "/idle",
    label: "Open Idle",
    title: "Idle",
    view: "idle",
  },
  {
    description: "Talk with an AI companion, or simply think out loud.",
    href: "/companion",
    label: "Open Chat",
    title: "Chat",
    view: "chat",
  },
];

function HackathonLanding({ onOpenAuth, onOpenRoute }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function openRoute(event, view) {
    if (isModifiedClick(event)) return;
    event.preventDefault();
    if (loading) return;
    setLoading(view);
    setError("");
    try {
      await onOpenRoute(view);
    } catch (err) {
      setError(err.message || "Could not open this page");
    } finally {
      setLoading("");
    }
  }

  return (
    <div className="home-shell">
      <div className="home-inner">
        <header className="home-header">
          <BrandWordmark />
          <a className="home-header-link" href="/work" onClick={(event) => openRoute(event, "work")}>
            <span>Open workspace</span>
            <ArrowRight aria-hidden="true" size={15} strokeWidth={1.8} />
          </a>
        </header>

        <main>
          <section className="home-hero" aria-label="About Parallax">
            <h1>
              <span>Think with AI.</span>
              <span>Work with agents.</span>
            </h1>
            <p className="home-subtitle">
              <span>With your personalized agents,</span>
              <span>talk things through, get things done.</span>
            </p>
            <div className="home-actions">
              <a
                aria-busy={loading === "work"}
                className="try-first"
                href="/work"
                onClick={(event) => openRoute(event, "work")}
              >
                <span>{loading === "work" ? "Starting" : "Try first"}</span>
                <ArrowRight aria-hidden="true" size={15} strokeWidth={1.8} />
              </a>
              <button className="create-account" onClick={() => onOpenAuth("register")} type="button">
                <UserPlus aria-hidden="true" size={15} strokeWidth={1.8} />
                <span>Create account</span>
              </button>
            </div>
            <StatusLine error={error} />
          </section>

          <section className="home-modes" aria-label="Ways to use Parallax">
            {productModes.map((mode) => (
              <article className="home-mode" key={mode.view}>
                <h2>{mode.title}</h2>
                <p>{mode.description}</p>
                <a href={mode.href} onClick={(event) => openRoute(event, mode.view)}>
                  <span>{mode.label}</span>
                  <ArrowRight aria-hidden="true" size={15} strokeWidth={1.8} />
                </a>
              </article>
            ))}
          </section>

          <section className="home-secondary" aria-label="Agent customization and Desktop Pet">
            <article>
              <h2>
                <a href="/me" onClick={(event) => openRoute(event, "me")}>
                  <span>Customize your agents</span>
                  <ArrowRight aria-hidden="true" size={15} strokeWidth={1.8} />
                </a>
              </h2>
              <p>Choose how your agents work with you.</p>
            </article>
            <article>
              <h2>
                <a href="/download/companion" onClick={(event) => openRoute(event, "download")}>
                  <span>Try Desktop Pet</span>
                  <ArrowRight aria-hidden="true" size={15} strokeWidth={1.8} />
                </a>
              </h2>
              <p>A small cat that lives on your desktop and mirrors Parallax Work progress.</p>
            </article>
          </section>
        </main>

        <footer className="home-footer">
          <span>Parallax</span>
          <span>Work. Idle. Chat.</span>
        </footer>
      </div>
    </div>
  );
}

function isModifiedClick(event) {
  return event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey;
}

export default HackathonLanding;
