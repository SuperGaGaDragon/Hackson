/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { MessageSquarePlus, Pause, Play, RotateCcw, ShieldCheck } from "lucide-react";

function MissionHeader({
  answerText = "",
  busy,
  followUpText = "",
  inputRequest,
  mission,
  onAnswer,
  onAnswerTextChange = () => {},
  onEvaluate,
  onFollowUp = () => {},
  onFollowUpTextChange = () => {},
  onPause,
  onStart,
}) {
  const waiting = mission?.status === "waiting_input";
  const completed = mission?.status === "completed";
  const resumable = ["paused", "paused_retryable", "failed", "stopped", "blocked"].includes(mission?.status);
  const running = mission?.status === "running";
  const stopping = mission?.status === "stopping";
  const canPrimary = mission && !waiting && !completed && !stopping && (running || mission.status === "draft" || resumable);
  const canEvaluate = mission && !["draft", "running", "stopping"].includes(mission.status);
  const title = mission?.title || "Create mission";
  const suggestedOptions = inputRequest?.payload?.suggestedOptions || [];
  const primaryLabel = running ? "Pause" : stopping ? "Pausing" : resumable ? "Resume" : "Start";
  const PrimaryIcon = running ? Pause : resumable ? RotateCcw : Play;
  const primaryAction = running ? onPause : onStart;

  return (
    <div className="panel-head mission-head">
      <div className="mission-head-main">
        <div>
          <p className="eyebrow">Mission</p>
          <h2>{title}</h2>
          {mission?.goal && <p className="mission-goal">{mission.goal}</p>}
        </div>
        <div className="panel-actions">
          <span className="chip">{mission?.status || "empty"}</span>
          <button className="primary-button" disabled={busy || !canPrimary} onClick={primaryAction} type="button">
            <PrimaryIcon size={16} />
            <span>{primaryLabel}</span>
          </button>
          <button className="secondary-button" disabled={busy || !canEvaluate} onClick={onEvaluate} type="button">
            <ShieldCheck size={16} />
            <span>Check</span>
          </button>
        </div>
      </div>
      {waiting && (
        <form className="mission-answer" onSubmit={onAnswer}>
          <div>
            <p className="eyebrow">Input Requested</p>
            <strong>{inputRequest?.message || mission?.lastError || "The lead agent needs input."}</strong>
            {inputRequest?.payload?.reason && <span>{inputRequest.payload.reason}</span>}
          </div>
          {suggestedOptions.length > 0 && (
            <div className="answer-options">
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
          <div className="answer-row">
            <textarea
              aria-label="Mission input answer"
              disabled={busy}
              onChange={(event) => onAnswerTextChange(event.target.value)}
              placeholder="Answer the lead agent"
              value={answerText}
            />
            <button className="primary-button" disabled={busy || !answerText.trim()} type="submit">
              Reply
            </button>
          </div>
        </form>
      )}
      {completed && (
        <form className="mission-answer mission-followup" onSubmit={onFollowUp}>
          <div>
            <p className="eyebrow">Continue</p>
            <strong>Continue with the same leader.</strong>
          </div>
          <div className="answer-row">
            <textarea
              aria-label="Mission follow-up request"
              disabled={busy}
              onChange={(event) => onFollowUpTextChange(event.target.value)}
              placeholder="Add a revision or next pass"
              value={followUpText}
            />
            <button className="primary-button" disabled={busy || !followUpText.trim()} type="submit">
              <MessageSquarePlus size={16} />
              <span>Continue</span>
            </button>
          </div>
        </form>
      )}
    </div>
  );
}

export default MissionHeader;
