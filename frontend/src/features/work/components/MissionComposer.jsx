/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { MessageSquarePlus, Play, RotateCcw, SendHorizontal } from "lucide-react";

const resumableStatuses = new Set(["paused", "paused_retryable", "failed", "stopped", "blocked"]);

function MissionComposer({
  busy,
  inputRequest,
  mission,
  onAnswer,
  onAnswerTextChange,
  onFollowUp,
  onFollowUpTextChange,
  onInstruction,
  onInstructionTextChange,
  onStart,
  answerText = "",
  followUpText = "",
  instructionText = "",
}) {
  const mode = composerMode(mission);
  const question = inputRequest?.message || mission?.lastError || "";
  const suggestedOptions = inputRequest?.payload?.suggestedOptions || [];

  if (!mission) {
    return (
      <section className="mission-composer empty">
        <p className="eyebrow">Command</p>
        <strong>No mission</strong>
        <span>Select or create a mission.</span>
      </section>
    );
  }

  if (mode === "waiting") {
    return (
      <form className="mission-composer" onSubmit={onAnswer}>
        <ComposerHead eyebrow="Reply" title={question || "Input requested"} detail={inputRequest?.payload?.reason} />
        {suggestedOptions.length > 0 && (
          <div className="composer-options">
            {suggestedOptions.map((option) => (
              <button
                className="secondary-button"
                disabled={busy}
                key={option}
                onClick={() => onAnswerTextChange(option)}
                type="button"
              >
                {option}
              </button>
            ))}
          </div>
        )}
        <ComposerInput
          action="Reply"
          busy={busy}
          disabled={!answerText.trim()}
          icon={SendHorizontal}
          onChange={onAnswerTextChange}
          placeholder="Answer the lead"
          value={answerText}
        />
      </form>
    );
  }

  if (mode === "completed") {
    return (
      <form className="mission-composer" onSubmit={onFollowUp}>
        <ComposerHead eyebrow="Continue" title="Same lead, same mission." />
        <ComposerInput
          action="Continue"
          busy={busy}
          disabled={!followUpText.trim()}
          icon={MessageSquarePlus}
          onChange={onFollowUpTextChange}
          placeholder="Revision or next pass"
          value={followUpText}
        />
      </form>
    );
  }

  if (mode === "running") {
    return (
      <form className="mission-composer" onSubmit={onInstruction}>
        <ComposerHead eyebrow="Command" title="Add instruction" />
        <ComposerInput
          action="Send"
          busy={busy}
          disabled={!instructionText.trim()}
          icon={SendHorizontal}
          onChange={onInstructionTextChange}
          placeholder="Tell the lead what to adjust"
          value={instructionText}
        />
      </form>
    );
  }

  if (mode === "resume") {
    return (
      <form className="mission-composer" onSubmit={onStart}>
        <ComposerHead eyebrow="Resume" title={mission.lastError || "Continue from checkpoint"} />
        <ComposerInput
          action="Resume"
          busy={busy}
          disabled={false}
          icon={RotateCcw}
          onChange={onInstructionTextChange}
          placeholder="Optional correction"
          value={instructionText}
        />
      </form>
    );
  }

  if (mode === "draft") {
    return (
      <form className="mission-composer" onSubmit={onStart}>
        <ComposerHead eyebrow="Start" title="Ready to run" />
        <ComposerInput
          action="Start"
          busy={busy}
          disabled={false}
          icon={Play}
          onChange={onInstructionTextChange}
          placeholder="Optional first instruction"
          value={instructionText}
        />
      </form>
    );
  }

  return (
    <section className="mission-composer empty">
      <p className="eyebrow">Command</p>
      <strong>{mission.status}</strong>
      <span>Wait for the current transition.</span>
    </section>
  );
}

function ComposerHead({ detail, eyebrow, title }) {
  return (
    <div className="composer-head">
      <p className="eyebrow">{eyebrow}</p>
      <strong>{title}</strong>
      {detail && <span>{detail}</span>}
    </div>
  );
}

function ComposerInput({ action, busy, disabled, icon: Icon, onChange, placeholder, value }) {
  return (
    <div className="composer-input">
      <textarea
        aria-label={placeholder}
        disabled={busy}
        onChange={(event) => onChange(event.target.value)}
        placeholder={placeholder}
        value={value}
      />
      <button className="primary-button" disabled={busy || disabled} type="submit">
        <Icon size={15} />
        <span>{action}</span>
      </button>
    </div>
  );
}

function composerMode(mission) {
  if (!mission) return "empty";
  if (mission.status === "waiting_input") return "waiting";
  if (mission.status === "completed") return "completed";
  if (mission.status === "running") return "running";
  if (mission.status === "draft") return "draft";
  if (resumableStatuses.has(mission.status)) return "resume";
  return "locked";
}

export default MissionComposer;
