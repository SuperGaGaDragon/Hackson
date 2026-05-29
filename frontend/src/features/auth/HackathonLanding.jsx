/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex
*/
import {
  ArrowRight,
  FileText,
  MessageSquareText,
  ShieldCheck,
  UserPlus,
  Workflow,
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
          <h1>Parallex</h1>
          <p className="hackathon-lede">Agentic work, made inspectable.</p>
          <p className="hackathon-subcopy">Intent to product, with the trace intact.</p>
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

        <div className="parallex-feature-panel" aria-label="Parallex product capabilities">
          <div className="parallex-feature-list">
            <FeatureItem
              accent="teal"
              icon={MessageSquareText}
              kicker="Idle Mode"
              title="Brainstorm with multiple AI agents."
            />
            <FeatureItem
              accent="green"
              icon={Workflow}
              kicker="Work Mode"
              title="Visualize missions, progress, windows, and products."
            />
            <FeatureItem
              accent="amber"
              icon={ShieldCheck}
              kicker="Evaluator"
              title="Reduce hallucination risk with evidence-gap checks."
            />
            <FeatureItem
              accent="slate"
              icon={FileText}
              kicker="Product History"
              title="Keep drafts, reviews, revisions, and finals readable."
            />
          </div>
        </div>
      </section>

      <section className="workflow-section" aria-label="Parallex visual workflow">
        <div className="workflow-copy">
          <p className="eyebrow">Visual workflow</p>
          <h2>Brainstorm to final, visibly.</h2>
        </div>
        <div className="workflow-track">
          <WorkflowStep index="01" label="Brainstorm" text="Multiple AI directions" />
          <WorkflowStep index="02" label="Assign" text="Supervised mission" />
          <WorkflowStep index="03" label="Watch" text="Live progress" />
          <WorkflowStep index="04" label="Deliver" text="Drafts to final" />
          <WorkflowStep index="05" label="Evaluate" text="Evidence gaps" />
        </div>
      </section>

      <section className="memory-section" aria-label="Parallex universal memory">
        <div>
          <p className="eyebrow">Permanent agents</p>
          <h2>Universal memory.</h2>
        </div>
        <div className="memory-grid">
          <MemoryPoint label="Nora / Vale" text="Same two agents" />
          <MemoryPoint label="Approved memory" text="Context you allow" />
          <MemoryPoint label="Controlled context" text="Only what matters" />
        </div>
      </section>
    </main>
  );
}

function FeatureItem({ accent, icon: Icon, kicker, title }) {
  return (
    <article className={`parallex-feature-item ${accent}`}>
      <Icon size={21} />
      <div>
        <span>{kicker}</span>
        <strong>{title}</strong>
      </div>
    </article>
  );
}

function WorkflowStep({ index, label, text }) {
  return (
    <article className="workflow-step">
      <span>{index}</span>
      <strong>{label}</strong>
      <p>{text}</p>
    </article>
  );
}

function MemoryPoint({ label, text }) {
  return (
    <article className="memory-point">
      <strong>{label}</strong>
      <p>{text}</p>
    </article>
  );
}

export default HackathonLanding;
