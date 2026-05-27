/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
*/
import { apiRequest } from "./client";

export function createConversation(payload) {
  return apiRequest("/api/conversations", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listConversations(mode) {
  const query = mode ? `?mode=${encodeURIComponent(mode)}` : "";
  return apiRequest(`/api/conversations${query}`);
}

export function getConversationMessages(conversationId, limit = 100) {
  return apiRequest(`/api/conversations/${conversationId}/messages?limit=${limit}`);
}

export function appendConversationMessage(conversationId, payload) {
  return apiRequest(`/api/conversations/${conversationId}/messages`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function getIdleConversation() {
  return apiRequest("/api/idle/conversation");
}
