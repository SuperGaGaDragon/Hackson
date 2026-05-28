/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { useEffect, useMemo, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { Footprints, Moon, Pause } from "lucide-react";
import { getPetState, petStateOrder, petStates, sitePetStateByTone } from "../../domain/petStates";

const stateIcons = {
  stand: Pause,
  walk: Footprints,
  sleep: Moon,
};

function PetWindow({ busy, onOpenSite, siteState }) {
  const [petState, setPetState] = useState("stand");
  const [frameIndex, setFrameIndex] = useState(0);
  const [manualUntil, setManualUntil] = useState(0);
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
  }, [active.nudgePx, petState]);

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

  return (
    <main className={`pet-shell ${petState} ${busy ? "busy" : ""}`}>
      <section className="bubble" data-tauri-drag-region onDoubleClick={onOpenSite}>
        <div>
          <strong>{display.label}</strong>
          <span>{display.line}</span>
        </div>
        <small>{display.tone || active.mood}</small>
      </section>

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

function renderStateIcon(state) {
  const Icon = stateIcons[state];
  return <Icon size={16} strokeWidth={2.2} />;
}

export default PetWindow;
