/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { ArrowRight, Brain, BriefcaseBusiness, Cat, MessageSquare, ShieldCheck, Sparkles, UserPlus } from "lucide-react";
import { useState } from "react";
import { quickTryUser } from "../../api/users";
import StatusLine from "../../shared/components/StatusLine";

function HackathonLanding({ onAuthed, onOpenAuth }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function startQuickTry() {
    setLoading(true);
    setError("");
    try {
      const data = await quickTryUser();
      onAuthed(data.user);
    } catch (err) {
      setError(err.message || "Quick Try failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="hackathon-shell">
      <header className="hackathon-nav">
        <div className="hackathon-brand">
          <Sparkles size={18} />
          <span>Hackson</span>
        </div>
        <div className="hackathon-nav-actions">
          <button className="secondary-button" onClick={() => onOpenAuth("login")} type="button">
            Login
          </button>
          <button className="primary-button" disabled={loading} onClick={startQuickTry} type="button">
            Quick Try
          </button>
        </div>
      </header>

      <section className="hackathon-hero">
        <div className="hackathon-copy">
          <p className="eyebrow">TMLS Agentic Hackathon</p>
          <h1>Meet Hackson.</h1>
          <p className="hackathon-lede">
            Two long-lived agents that talk, remember, delegate, and deliver reviewed work.
          </p>
          <p className="hackathon-subcopy">
            Not a chatbot. Not a coding shell. A supervised workspace where your agents plan, split work, keep context,
            and ship a readable Product with a Quality check.
          </p>
          <div className="hackathon-actions">
            <button className="hackathon-primary" disabled={loading} onClick={startQuickTry} type="button">
              <span>{loading ? "Starting" : "Quick Try"}</span>
              <ArrowRight size={18} />
            </button>
            <button className="hackathon-secondary" onClick={() => onOpenAuth("register")} type="button">
              <UserPlus size={17} />
              <span>Create Account</span>
            </button>
          </div>
          <p className="hackathon-note">Temporary session. Close this browser session and the work may be gone.</p>
          <StatusLine error={error} />
        </div>

        <div className="hackathon-visual" aria-label="Hackson desktop pet preview">
          <div className="hackathon-bubble primary">
            <strong>Working</strong>
            <span>Lead is planning a Mission.</span>
          </div>
          <img alt="" src="/assets/companion-cat-preview.png" />
          <div className="hackathon-bubble secondary">
            <strong>Quality</strong>
            <span>Risk checked before delivery.</span>
          </div>
        </div>
      </section>

      <section className="hackathon-pillars" aria-label="Product overview">
        <Pillar icon={MessageSquare} title="Two agents" text="Nora and Vale stay editable, persistent, and present across modes." />
        <Pillar icon={BriefcaseBusiness} title="Mission work" text="Plan, delegate, write, revise, and keep every Product version readable." />
        <Pillar icon={ShieldCheck} title="Quality" text="Evaluator reports risk, evidence, missing requirements, and tool failures." />
        <Pillar icon={Cat} title="Desktop pet" text="The cat turns background Work progress into a visible companion." />
      </section>

      <section className="hackathon-explain" aria-label="How it works">
        <div>
          <p className="eyebrow">Why it matters</p>
          <h2>Agentic work needs memory, supervision, and a result you can actually read.</h2>
        </div>
        <div className="hackathon-flow">
          <FlowStep icon={Brain} label="Context" text="Every call is built from traceable messages, summaries, memory, and agent identity." />
          <FlowStep icon={BriefcaseBusiness} label="Product" text="Work Mode stores deliverables as Product and Artifact lineage, not loose chat." />
          <FlowStep icon={ShieldCheck} label="Review" text="Quality checks stay visible without pretending to be proof of truth." />
        </div>
      </section>

      <div className="hackathon-sticky">
        <span>Try Hackson live</span>
        <button disabled={loading} onClick={startQuickTry} type="button">
          Quick Try
        </button>
      </div>
    </main>
  );
}

function Pillar({ icon: Icon, text, title }) {
  return (
    <article className="hackathon-card">
      <Icon size={18} />
      <h2>{title}</h2>
      <p>{text}</p>
    </article>
  );
}

function FlowStep({ icon: Icon, label, text }) {
  return (
    <article className="hackathon-flow-step">
      <Icon size={18} />
      <div>
        <strong>{label}</strong>
        <p>{text}</p>
      </div>
    </article>
  );
}

export default HackathonLanding;
