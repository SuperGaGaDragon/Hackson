/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
*/
import { toTimelineItem } from "../../domain/messages";

function Timeline({ messages, timelineRef }) {
  const items = messages.map(toTimelineItem);

  return (
    <div className="timeline" aria-label="Timeline" ref={timelineRef}>
      {items.length === 0 && <div className="empty-state">No messages</div>}
      {items.map((item) => {
        if (item.type !== "agent" && item.type !== "user") {
          return (
            <div className="system-event" key={item.id}>
              <span>{item.author}</span>
              <small>{item.text}</small>
            </div>
          );
        }

        return (
          <article className={`message-row ${item.agent?.color || "user"}`} key={item.id}>
            <div className="message-meta">
              <strong>{item.author}</strong>
              <span>{item.sequence ? `#${item.sequence}` : item.time}</span>
            </div>
            <p>{item.text}</p>
          </article>
        );
      })}
    </div>
  );
}

export default Timeline;
