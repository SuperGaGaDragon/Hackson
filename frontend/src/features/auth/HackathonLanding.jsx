/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import {
  ArrowRight,
  BriefcaseBusiness,
  CheckCircle2,
  FileText,
  ScanLine,
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

        <div className="parallex-stage" aria-label="Parallex mission runtime preview">
          <div className="parallex-stage-head">
            <span>Mission 042</span>
            <strong>Inspectable</strong>
          </div>
          <div className="parallex-stage-body">
            <div className="parallex-stage-kpi">
              <span>Trace</span>
              <strong>27</strong>
            </div>
            <div className="parallex-stage-product">
              <span>Product</span>
              <strong>Research brief</strong>
              <p>outline, sources, draft, review</p>
            </div>
            <div className="parallex-stage-kpi amber">
              <span>Risk</span>
              <strong>82</strong>
            </div>
          </div>
          <div className="parallex-stage-rail">
            <RuntimeDot label="Intent" />
            <RuntimeDot active label="Mission" />
            <RuntimeDot label="Product" />
            <RuntimeDot label="Review" />
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
        <Signal icon={ScanLine} label="Context" text="The model sees a curated, auditable package." />
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

function RuntimeDot({ active = false, label }) {
  return (
    <div className={active ? "runtime-dot active" : "runtime-dot"}>
      <CheckCircle2 size={15} />
      <span>{label}</span>
    </div>
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
