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
            A supervised workspace for two long-lived agents.
          </p>
          <p className="hackathon-subcopy">
            Explore rough ideas, run them as Missions, keep every Product version readable, and check delivery
            risk before it ships.
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

      <section className="hackathon-loop" aria-label="Hackson work loop">
        <LoopStep label="Brainstorm" />
        <LoopStep label="Mission" />
        <LoopStep label="Product" />
        <LoopStep label="Quality" />
        <LoopStep label="Memory" />
      </section>

      <section className="hackathon-section-head">
        <p className="eyebrow">Core runtime</p>
        <h2>Agentic work needs more than a chat box.</h2>
      </section>

      <section className="hackathon-pillars" aria-label="Core runtime">
        <Pillar icon={Brain} title="Context" text="Calls are built from traceable messages, summaries, memory, and agent identity." />
        <Pillar icon={BriefcaseBusiness} title="Missions" text="Lead agents plan, delegate, review, and keep work moving inside a supervised loop." />
        <Pillar icon={MessageSquare} title="Lineage" text="Deliverables live as Product and Artifact history, not loose transcript fragments." />
        <Pillar icon={ShieldCheck} title="AgentLens" text="Quality reports risk, evidence gaps, missing requirements, and tool failures." />
      </section>

      <section className="hackathon-section-head compact">
        <p className="eyebrow">Entry surfaces</p>
        <h2>Start where the work feels natural.</h2>
      </section>

      <section className="hackathon-pillars hackathon-entry" aria-label="Entry surfaces">
        <Pillar icon={MessageSquare} title="Idle" text="A low-friction brainstorm room where Nora and Vale explore a topic before Work." />
        <Pillar icon={Brain} title="Companion" text="A conversational surface for the same editable agents and approved memory." />
        <Pillar icon={Cat} title="Desktop pet" text="The cat turns background Mission state into visible presence." />
      </section>

      <section className="hackathon-explain" aria-label="How it works">
        <div>
          <p className="eyebrow">Why it matters</p>
          <h2>The product is the runtime, not the chat.</h2>
        </div>
        <div className="hackathon-flow">
          <FlowStep icon={Brain} label="Memory governance" text="Useful context is retained with boundaries; raw Work trace does not leak everywhere." />
          <FlowStep icon={BriefcaseBusiness} label="Readable delivery" text="Work Mode keeps a clean Product while preserving the revision trail." />
          <FlowStep icon={ShieldCheck} label="Supervision" text="AgentLens makes risk visible without pretending the score is absolute truth." />
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

function LoopStep({ label }) {
  return (
    <div className="hackathon-loop-step">
      <span>{label}</span>
    </div>
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
