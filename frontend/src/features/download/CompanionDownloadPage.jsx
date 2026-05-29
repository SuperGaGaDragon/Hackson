/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { ArrowRight, Download, ExternalLink, Monitor, ShieldCheck, Sparkles } from "lucide-react";

export const DESKTOP_COMPANION_DOWNLOAD_URL = "/assets/downloads/hackson-pet-mac-arm64.zip";

function CompanionDownloadPage({ onOpenApp }) {
  return (
    <main className="download-shell">
      <header className="download-nav">
        <div className="download-brand">
          <Sparkles size={18} />
          <span>Parallex</span>
        </div>
        <button className="secondary-button download-nav-button" onClick={onOpenApp} type="button">
          <ExternalLink size={16} />
          <span>Open app</span>
        </button>
      </header>
      <section className="download-hero">
        <div className="download-copy">
          <p className="eyebrow">Mac alpha</p>
          <h1>Desktop Companion</h1>
          <p>
            A small cat that lives on your desktop and mirrors Parallex Work progress: active Missions, pauses,
            waiting input, and recent Progress events.
          </p>
          <div className="download-actions">
            <a className="primary-button download-primary" href={DESKTOP_COMPANION_DOWNLOAD_URL}>
              <Download size={17} />
              <span>Download for Mac</span>
            </a>
            <button className="secondary-button" onClick={onOpenApp} type="button">
              <span>Start Work</span>
              <ArrowRight size={17} />
            </button>
          </div>
          <p className="download-note">Apple Silicon alpha. Browser login. Work Mode required for live status.</p>
        </div>
        <div className="download-preview" aria-label="Desktop Companion preview">
          <div className="pet-demo-bubble">
            <strong>Working</strong>
            <span>[Research paper] Thinking</span>
          </div>
          <img alt="" src="/assets/companion-cat-preview.png" />
        </div>
      </section>
      <section className="download-grid" aria-label="Setup">
        <GuideCard icon={Download} title="Install" text="Download the zip, unzip it, then move Parallex Pet to Applications." />
        <GuideCard icon={ShieldCheck} title="Login" text="Double-click the cat and sign in through the website. The app never asks for your password." />
        <GuideCard icon={Monitor} title="Watch" text="Start a Work Mission. The cat follows the active Mission and expands into current Progress." />
      </section>
    </main>
  );
}

function GuideCard({ icon: Icon, text, title }) {
  return (
    <article className="download-card">
      <Icon size={18} />
      <h2>{title}</h2>
      <p>{text}</p>
    </article>
  );
}

export default CompanionDownloadPage;
