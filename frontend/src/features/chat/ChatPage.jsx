/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex
*/
import { Send } from "lucide-react";
import { useEffect, useRef, useState } from "react";
import { createConversation, getConversationMessages, listConversations } from "../../api/conversations";
import { sendCompanionMessage } from "../../api/interactions";
import { FALLBACK_AGENTS, normalizeAgents } from "../../domain/agents";
import { makePendingUserMessage, sortMessages, uniqueMessages } from "../../domain/messages";
import AgentSlot from "../../shared/components/AgentSlot";
import StatusLine from "../../shared/components/StatusLine";
import Timeline from "../../shared/components/Timeline";

function ChatPage({ agents = FALLBACK_AGENTS }) {
  const agentProfiles = normalizeAgents(agents);
  const [conversations, setConversations] = useState([]);
  const [conversation, setConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [draft, setDraft] = useState("");
  const [targetAgentId, setTargetAgentId] = useState("agent_2");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const timelineRef = useRef(null);

  useEffect(() => {
    let mounted = true;

    async function loadChat() {
      setLoading(true);
      setError("");
      try {
        const conversations = await listConversations("companion_2");
        const existing = conversations[0];
        const chat = existing || (await createConversation({ mode: "companion_2", title: "Chat" }));
        const history = await getConversationMessages(chat.id);
        const titledConversations = await enrichConversationTitles(conversations.length ? conversations : [chat]);
        if (!mounted) return;
        setConversations(titledConversations);
        setConversation(titledConversations.find((item) => item.id === chat.id) || chat);
        setMessages(sortMessages(history.messages || []));
      } catch (err) {
        if (mounted) setError(err.message || "Load failed");
      } finally {
        if (mounted) setLoading(false);
      }
    }

    loadChat();
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    timelineRef.current?.scrollTo({
      top: timelineRef.current.scrollHeight,
      behavior: "smooth",
    });
  }, [messages.length, busy]);

  async function startNew() {
    if (busy) return;
    setBusy(true);
    setError("");
    try {
      const chat = await createConversation({ mode: "companion_2", title: "Chat" });
      setConversations((current) => localizeConversationTitles([chat, ...current]));
      setConversation(chat);
      setMessages([]);
    } catch (err) {
      setError(err.message || "New failed");
    } finally {
      setBusy(false);
    }
  }

  async function send() {
    const content = draft.trim();
    if (!conversation || !content || busy) return;
    const pendingMessage = makePendingUserMessage(conversation, content, messages);
    setBusy(true);
    setError("");
    setDraft("");
    setConversation((current) => ({
      ...current,
      localTitle: nextLocalTitle(current || conversation, content),
    }));
    setConversations((current) =>
      localizeConversationTitles(
        current.map((item) =>
          item.id === conversation.id
            ? {
                ...item,
                localTitle: nextLocalTitle(item, content),
              }
            : item,
        ),
      ),
    );
    setMessages((current) => uniqueMessages([...current, pendingMessage]));
    try {
      const data = await sendCompanionMessage(conversation.id, {
        content,
        targetAgentId,
        metadata: {},
      });
      setConversation((current) => ({
        ...current,
        ...data.conversation,
        localTitle: nextLocalTitle(current || conversation, content),
      }));
      setConversations((current) =>
        localizeConversationTitles(
          current.map((item) =>
            item.id === conversation.id
              ? {
                  ...item,
                  ...data.conversation,
                  localTitle: nextLocalTitle(item, content),
                }
              : item,
          ),
        ),
      );
      setMessages((current) =>
        uniqueMessages([
          ...current.filter((message) => message.id !== pendingMessage.id),
          data.userMessage,
          data.agentMessage,
        ]),
      );
    } catch (err) {
      setError(err.message || "Send failed");
    } finally {
      setBusy(false);
    }
  }

  async function selectConversation(nextConversation) {
    if (busy || nextConversation.id === conversation?.id) return;
    setLoading(true);
    setError("");
    try {
      const history = await getConversationMessages(nextConversation.id);
      setConversation(nextConversation);
      setMessages(sortMessages(history.messages || []));
    } catch (err) {
      setError(err.message || "Load failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="chat-grid with-history">
      <aside className="history-rail">
        <div className="panel-head compact">
          <div>
            <p className="eyebrow">Chat</p>
            <h2>History</h2>
          </div>
        </div>
        <button className="secondary-button history-new" disabled={busy || loading} onClick={startNew} type="button">
          New chat
        </button>
        <div className="history-list">
          {conversations.map((item) => (
            <button
              className={`history-item ${item.id === conversation?.id ? "active" : ""}`}
              key={item.id}
              onClick={() => selectConversation(item)}
              type="button"
            >
              <strong>{item.localTitle || item.title || "Chat"}</strong>
              <span>{item.messageCount || 0}</span>
            </button>
          ))}
        </div>
      </aside>
      <section className="timeline-panel">
        <div className="panel-head">
          <div>
            <p className="eyebrow">Chat</p>
            <h2>{conversation?.localTitle || conversation?.title || "Companion"}</h2>
          </div>
          <span className="chip">{conversation?.messageCount || messages.length}</span>
        </div>
        <Timeline agents={agentProfiles} messages={messages} timelineRef={timelineRef} />
        <div className="composer">
          <input
            aria-label="Message"
            disabled={busy || loading}
            onChange={(event) => setDraft(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") send();
            }}
            placeholder="Message"
            value={draft}
          />
          <button disabled={busy || loading} onClick={send} title="Send" type="button">
            <Send size={18} />
          </button>
        </div>
      </section>
      <aside className="context-rail">
        <div className="panel-head compact">
          <div>
            <p className="eyebrow">Target</p>
            <h2>Agent</h2>
          </div>
        </div>
        {agentProfiles.map((agent) => (
          <button
            className={`agent-target ${targetAgentId === agent.slot ? "active" : ""}`}
            key={agent.slot}
            onClick={() => setTargetAgentId(agent.slot)}
            type="button"
          >
            <AgentSlot agent={agent} state={targetAgentId === agent.slot ? "On" : "Off"} />
          </button>
        ))}
        <StatusLine error={error} loading={loading} text={busy ? "Working" : ""} />
      </aside>
    </div>
  );
}

function localizeConversationTitles(conversations) {
  return conversations.map((conversation) => ({
    ...conversation,
    localTitle: conversation.localTitle || readableTitle(conversation),
  }));
}

async function enrichConversationTitles(conversations) {
  const enriched = await Promise.all(
    conversations.map(async (conversation) => {
      const base = localizeConversationTitles([conversation])[0];
      if (!isGenericTitle(base.localTitle)) return base;

      try {
        const history = await getConversationMessages(conversation.id, 10);
        const firstUserMessage = sortMessages(history.messages || []).find(
          (message) => message.senderType === "user" && message.content,
        );
        return {
          ...base,
          localTitle: firstUserMessage ? makeLocalTitle(firstUserMessage.content) : base.localTitle,
        };
      } catch {
        return base;
      }
    }),
  );

  return enriched;
}

function readableTitle(conversation) {
  if (conversation.title && conversation.title !== "Chat" && conversation.title !== "Demo Chat") {
    return conversation.title;
  }
  if (conversation.lastMessageAt) {
    return `Chat ${new Date(conversation.lastMessageAt).toLocaleDateString([], { month: "short", day: "numeric" })}`;
  }
  return "Untitled";
}

function nextLocalTitle(conversation, content) {
  if (!isGenericTitle(conversation.localTitle)) return conversation.localTitle;
  return makeLocalTitle(content);
}

function isGenericTitle(title) {
  return !title || title === "Chat" || title === "New chat" || title === "Untitled";
}

function makeLocalTitle(content) {
  const trimmed = content.replace(/\s+/g, " ").trim();
  if (trimmed.length <= 18) return trimmed || "Chat";
  return `${trimmed.slice(0, 18)}...`;
}

export default ChatPage;
