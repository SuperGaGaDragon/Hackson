/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import {
  ArrowRight,
  Brain,
  BriefcaseBusiness,
  CircleDot,
  Layers3,
  MessageSquare,
  ShieldCheck,
  UserPlus,
} from "lucide-react";
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
          <span className="hackathon-brand-mark">P</span>
          <span>Parallex</span>
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
          <h1>Agentic work, made inspectable.</h1>
          <p className="hackathon-lede">
            Parallex turns rough intent into missions, product history, and reliability checks.
          </p>
          <p className="hackathon-subcopy">
            Two persistent agents can brainstorm, delegate, revise, and leave a trail you can actually read.
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

        <div className="parallex-preview" aria-label="Parallex mission runtime preview">
          <div className="parallex-preview-head">
            <span>Mission Runtime</span>
            <strong>live trace</strong>
          </div>
          <div className="parallex-thread">
            <PreviewStep detail="rough brief" icon={CircleDot} label="Intent" />
            <PreviewStep active detail="delegate + revise" icon={BriefcaseBusiness} label="Mission" />
            <PreviewStep detail="versioned draft" icon={Layers3} label="Product" />
            <PreviewStep accent detail="82 / review" icon={ShieldCheck} label="Reliability" />
          </div>
          <div className="parallex-product-strip">
            <span>Current product</span>
            <strong>Source-backed essay</strong>
            <p>Readable deliverable. Auditable trace.</p>
          </div>
        </div>
      </section>

      <section className="hackathon-loop" aria-label="Parallex work loop">
        <LoopStep label="Brainstorm" />
        <LoopStep label="Mission" />
        <LoopStep label="Product" />
        <LoopStep label="Quality" />
        <LoopStep label="Memory" />
      </section>

      <section className="hackathon-section-head">
        <p className="eyebrow">Core runtime</p>
        <h2>The runtime behind the agents.</h2>
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
        <Pillar icon={BriefcaseBusiness} title="Work" text="A supervised Mission loop for products that need structure, review, and delivery." />
      </section>

      <section className="hackathon-explain" aria-label="How it works">
        <div>
          <p className="eyebrow">Why it matters</p>
          <h2>The product is the trace.</h2>
        </div>
        <div className="hackathon-flow">
          <FlowStep icon={Brain} label="Memory governance" text="Useful context is retained with boundaries; raw Work trace does not leak everywhere." />
          <FlowStep icon={BriefcaseBusiness} label="Readable delivery" text="Work Mode keeps a clean Product while preserving the revision trail." />
          <FlowStep icon={ShieldCheck} label="Supervision" text="AgentLens makes risk visible without pretending the score is absolute truth." />
        </div>
      </section>
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

function PreviewStep({ active = false, accent = false, detail, icon: Icon, label }) {
  const className = active ? "parallex-step active" : accent ? "parallex-step accent" : "parallex-step";
  return (
    <div className={className}>
      <Icon size={17} />
      <div>
        <strong>{label}</strong>
        <span>{detail}</span>
      </div>
    </div>
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
