/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { MessageSquarePlus, Play, ShieldCheck, Square } from "lucide-react";

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
  onStart,
  onStop,
}) {
  const canStart = mission && !["running", "stopping", "completed"].includes(mission.status);
  const canStop = mission?.status === "running";
  const canEvaluate = mission && !["draft", "running", "stopping"].includes(mission.status);
  const title = mission?.title || "Create mission";
  const waiting = mission?.status === "waiting_input";
  const completed = mission?.status === "completed";
  const suggestedOptions = inputRequest?.payload?.suggestedOptions || [];

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
          <button className="primary-button" disabled={busy || !canStart || waiting} onClick={onStart} type="button">
            <Play size={16} />
            <span>Start</span>
          </button>
          <button className="secondary-button" disabled={busy || !canStop} onClick={onStop} type="button">
            <Square size={16} />
            <span>Stop</span>
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
