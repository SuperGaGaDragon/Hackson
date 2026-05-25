/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
*/
import { apiRequest } from "./client";

export function tickIdle(conversationId, payload) {
  return apiRequest(`/api/idle/${conversationId}/tick`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function joinIdle(conversationId, payload) {
  return apiRequest(`/api/idle/${conversationId}/join`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function sendCompanionMessage(conversationId, payload) {
  return apiRequest(`/api/companion/${conversationId}/messages`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
