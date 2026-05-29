/*
Created at: 2026-05-29
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex
*/
import { Activity, Boxes, FileText, ListChecks, ShieldCheck, TerminalSquare } from "lucide-react";

function MissionMapPanel({
  diagnosticsCount = 0,
  mission,
  onOpenQuality,
  onScrollToSection,
  productsCount = 0,
  progressCount = 0,
  qualitySummary = null,
  windowsCount = 0,
}) {
  const sections = [
    { id: "activity", icon: Activity, label: "Activity", value: mission?.status || "idle" },
    { id: "product", icon: FileText, label: "Product", value: countLabel(productsCount, "product") },
    { id: "windows", icon: Boxes, label: "Windows", value: countLabel(windowsCount, "window") },
    { id: "progress", icon: ListChecks, label: "Progress", value: countLabel(progressCount, "event") },
    { id: "diagnostics", icon: TerminalSquare, label: "Diagnostics", value: countLabel(diagnosticsCount, "event") },
  ];

  return (
    <aside className="mission-map-panel" aria-label="Mission map">
      <div className="panel-head compact">
        <div>
          <p className="eyebrow">Navigate</p>
          <h2>Mission map</h2>
        </div>
      </div>
      <div className="mission-map-list">
        {sections.map((section) => (
          <button
            className="mission-map-row"
            key={section.id}
            onClick={() => onScrollToSection(section.id)}
            type="button"
          >
            <section.icon size={16} />
            <span>{section.label}</span>
            <small>{section.value}</small>
          </button>
        ))}
      </div>
      <button
        className={qualitySummary ? "quality-trigger has-report" : "quality-trigger"}
        disabled={!qualitySummary}
        onClick={onOpenQuality}
        type="button"
      >
        <ShieldCheck size={18} />
        <span>
          <strong>Quality</strong>
          <small>{qualitySummary ? qualitySummary.status : "No report"}</small>
        </span>
        <em>{qualitySummary ? `${qualitySummary.score} / 100` : "Check"}</em>
      </button>
    </aside>
  );
}

function countLabel(count, noun) {
  const safeCount = Number(count || 0);
  return `${safeCount} ${noun}${safeCount === 1 ? "" : "s"}`;
}

export default MissionMapPanel;
