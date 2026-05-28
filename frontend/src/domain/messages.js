/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { FALLBACK_AGENT_BY_SLOT, resolveAgent } from "./agents";

export function sortMessages(messages) {
  return [...messages].sort((a, b) => {
    const left = a.sequence ?? 0;
    const right = b.sequence ?? 0;
    return left - right;
  });
}

export function uniqueMessages(messages) {
  const map = new Map();
  for (const message of messages) {
    const key = message.id || `${message.conversationId}-${message.sequence}-${message.content}`;
    map.set(key, message);
  }
  return sortMessages([...map.values()]);
}

export function toTimelineItem(message, agentBySlot = FALLBACK_AGENT_BY_SLOT) {
  const agent = resolveAgent(message.senderSlot, agentBySlot);
  const type = message.type || (message.senderType === "agent" ? "agent" : message.senderType);

  return {
    id: message.id || `${message.conversationId}-${message.sequence}`,
    type,
    agent,
    author: agent?.name || (message.senderType === "user" ? "You" : message.senderType || "System"),
    text: message.content,
    sequence: message.sequence,
    time: formatTime(message.createdAt),
  };
}

export function makeSystemMessage(content, sequence = null) {
  return {
    id: `system-${makeClientId()}`,
    type: "system",
    senderType: "system",
    content,
    sequence,
    createdAt: new Date().toISOString(),
  };
}

export function makePendingUserMessage(conversation, content, messages, sequence = null) {
  const maxSequence = Math.max(0, ...messages.map((message) => message.sequence || 0));
  return {
    id: `pending-${makeClientId()}`,
    conversationId: conversation.id,
    userId: conversation.userId,
    mode: conversation.mode,
    sequence: sequence ?? maxSequence + 0.5,
    senderType: "user",
    senderId: "me",
    senderSlot: null,
    role: "user",
    content,
    contentType: "text",
    metadata: { pending: true },
    createdAt: new Date().toISOString(),
  };
}

export function makeQueuedUserMessage(conversation, content, messages, sequence = null) {
  return {
    ...makePendingUserMessage(conversation, content, messages, sequence),
    id: `queued-${makeClientId()}`,
    metadata: { pending: true, queued: true },
  };
}

export function makeClientId() {
  if (globalThis.crypto?.randomUUID) {
    return globalThis.crypto.randomUUID();
  }
  const randomPart = Math.random().toString(36).slice(2);
  return `${Date.now().toString(36)}-${randomPart}`;
}

function formatTime(value) {
  if (!value) return "";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return "";
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}
