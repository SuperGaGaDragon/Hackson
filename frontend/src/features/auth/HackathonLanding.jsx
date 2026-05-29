/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import {
  ArrowRight,
  BriefcaseBusiness,
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
          <div className="parallex-feature-head">
            <span>What judges can try</span>
            <strong>Live product</strong>
          </div>
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

      <section className="hackathon-loop" aria-label="Parallex work loop">
        <LoopStep label="Intent" />
        <LoopStep label="Mission" />
        <LoopStep label="Product" />
        <LoopStep label="Review" />
      </section>

      <section className="hackathon-proof" aria-label="What Parallex makes visible">
        <div className="hackathon-proof-copy">
          <p className="eyebrow">What changes</p>
          <h2>Not a chat stream. A supervised work surface.</h2>
        </div>
        <div className="hackathon-metrics" aria-label="Parallex proof points">
          <Metric value="2" label="persistent agents" />
          <Metric value="1" label="clean product" />
          <Metric value="∞" label="traceable steps" />
        </div>
      </section>

      <section className="hackathon-signal" aria-label="Parallex runtime signals">
        <Signal icon={Workflow} label="Context" text="The model sees a curated, auditable package." />
        <Signal icon={BriefcaseBusiness} label="Mission" text="Work moves through selected tools, not hidden vibes." />
        <Signal icon={FileText} label="Lineage" text="Drafts, reviews, and final products stay readable." />
        <Signal icon={ShieldCheck} label="Review" text="AgentLens marks evidence gaps and delivery risk." />
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

function Metric({ label, value }) {
  return (
    <div className="hackathon-metric">
      <strong>{value}</strong>
      <span>{label}</span>
    </div>
  );
}

function Signal({ icon: Icon, label, text }) {
  return (
    <article className="hackathon-signal-item">
      <Icon size={18} />
      <strong>{label}</strong>
      <p>{text}</p>
    </article>
  );
}

export default HackathonLanding;
