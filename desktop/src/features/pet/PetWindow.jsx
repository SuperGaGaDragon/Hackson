/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { useEffect, useMemo, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { LogicalSize } from "@tauri-apps/api/dpi";
import { getCurrentWindow } from "@tauri-apps/api/window";
import { ChevronDown, ExternalLink, Footprints, Moon, Pause } from "lucide-react";
import { getPetState, petStateOrder, petStates, sitePetStateByTone } from "../../domain/petStates";

const stateIcons = {
  stand: Pause,
  walk: Footprints,
  sleep: Moon,
};

const compactWindowSize = new LogicalSize(300, 300);
const expandedWindowSize = new LogicalSize(360, 430);

function PetWindow({ busy, onOpenSite, progressSummary, siteState }) {
  const [petState, setPetState] = useState("stand");
  const [frameIndex, setFrameIndex] = useState(0);
  const [manualUntil, setManualUntil] = useState(0);
  const [expanded, setExpanded] = useState(false);
  const active = getPetState(petState);
  const display = siteState || active;
  const image = active.frames[frameIndex % active.frames.length];

  useEffect(() => {
    if (!siteState) return;
    setPetState(sitePetStateByTone[siteState.tone] || "siteIdle");
  }, [siteState]);

  useEffect(() => {
    setFrameIndex(0);
  }, [petState]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      setFrameIndex((current) => current + 1);
    }, active.frameCadenceMs);
    return () => window.clearInterval(timer);
  }, [active.frameCadenceMs, petState]);

  useEffect(() => {
    const timer = window.setInterval(() => {
      if (Date.now() < manualUntil) return;
      setPetState((current) => getPetState(current).nextState);
    }, active.nextAfterMs);
    return () => window.clearInterval(timer);
  }, [active.nextAfterMs, manualUntil, petState]);

  useEffect(() => {
    if (!active.nudgePx) return undefined;
    if (expanded) return undefined;
    let direction = 1;
    const timer = window.setInterval(async () => {
      try {
        await invoke("nudge_window", { dx: active.nudgePx * direction, dy: 0 });
        direction *= -1;
      } catch {
        window.clearInterval(timer);
      }
    }, 680);
    return () => window.clearInterval(timer);
  }, [active.nudgePx, expanded, petState]);

  useEffect(() => {
    getCurrentWindow()
      .setSize(expanded ? expandedWindowSize : compactWindowSize)
      .catch(() => {});
  }, [expanded]);

  const controls = useMemo(
    () =>
      petStateOrder.map((state) => (
        <button
          aria-pressed={petState === state}
          aria-label={petStates[state].label}
          className={petState === state ? "active" : ""}
          key={state}
          onClick={() => chooseState(state)}
          title={petStates[state].label}
          type="button"
        >
          {renderStateIcon(state)}
        </button>
      )),
    [petState],
  );

  function chooseState(nextState) {
    setManualUntil(Date.now() + 18000);
    setPetState(nextState);
  }

  function toggleProgress(event) {
    event.stopPropagation();
    setExpanded((current) => !current);
  }

  return (
    <main className={`pet-shell ${petState} ${expanded ? "expanded" : ""} ${busy ? "busy" : ""}`}>
      <button
        aria-expanded={expanded}
        aria-label={expanded ? "Hide progress" : "Show progress"}
        className="bubble"
        onClick={toggleProgress}
        onDoubleClick={onOpenSite}
        type="button"
      >
        <div>
          <strong>{display.label}</strong>
          <span>{display.line}</span>
        </div>
        <small>{display.tone || active.mood}</small>
        <ChevronDown className="bubble-chevron" size={14} strokeWidth={2.2} />
      </button>

      {expanded ? <ProgressGlance onOpenSite={onOpenSite} summary={progressSummary} /> : null}

      <div className="cat-stage" data-tauri-drag-region onDoubleClick={onOpenSite}>
        <div className="halo" />
        <img alt="" className="cat" draggable="false" src={image} />
        <div className="ground" />
        {["sleep", "sitePaused", "siteOffline"].includes(petState) ? (
          <div className="sleep-mark" aria-hidden="true">
            z
          </div>
        ) : null}
      </div>

      {!siteState ? (
        <nav className="controls" aria-label="Pet state">
          {controls}
        </nav>
      ) : null}
    </main>
  );
}

function ProgressGlance({ onOpenSite, summary }) {
  const rows = summary?.rows || [];
  return (
    <section className="progress-glance">
      <div className="glance-head">
        <div>
          <p>Progress</p>
          <strong>{summary?.status || "Ready"}</strong>
        </div>
        <button aria-label="Open site" onClick={onOpenSite} title="Open site" type="button">
          <ExternalLink size={15} strokeWidth={2.2} />
        </button>
      </div>
      <h2>{summary?.title || "No active work"}</h2>
      {summary?.detail ? <p className="glance-detail">{summary.detail}</p> : null}
      <div className="glance-list">
        {rows.length === 0 ? <p className="glance-empty">{summary?.empty || "No progress yet"}</p> : null}
        {rows.map((row) => (
          <article className="glance-row" key={row.id}>
            <div>
              <strong>{row.title}</strong>
              {row.detail ? <p>{row.detail}</p> : null}
            </div>
            <small>
              {row.time ? <span>{row.time}</span> : null}
              {row.sequence ? <span>{row.sequence}</span> : null}
            </small>
          </article>
        ))}
      </div>
    </section>
  );
}

function renderStateIcon(state) {
  const Icon = stateIcons[state];
  return <Icon size={16} strokeWidth={2.2} />;
}

export default PetWindow;
