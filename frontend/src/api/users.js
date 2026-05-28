/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { apiRequest, clearToken, setToken } from "./client";

export async function registerUser(payload) {
  const data = await apiRequest("/api/users/register", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  setToken(data.accessToken);
  return data;
}

export async function loginUser(payload) {
  const data = await apiRequest("/api/users/login", {
    method: "POST",
    body: JSON.stringify(payload),
  });
  setToken(data.accessToken);
  return data;
}

export function getCurrentUser() {
  return apiRequest("/api/users/me");
}

export function bindDesktopHandoff(code) {
  return apiRequest("/api/users/desktop-handoff", {
    method: "POST",
    body: JSON.stringify({ code }),
  });
}

export function updateCurrentUser(payload) {
  return apiRequest("/api/users/me", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export function listPromptLogs() {
  return apiRequest("/api/users/me/prompt-logs");
}

export function deletePromptLogs() {
  return apiRequest("/api/users/me/prompt-logs", {
    method: "DELETE",
  });
}

export function listMemoryCards() {
  return apiRequest("/api/memory/me");
}

export function updateMemoryCard(memoryId, status) {
  return apiRequest(`/api/memory/me/${memoryId}`, {
    method: "PATCH",
    body: JSON.stringify({ status }),
  });
}

export function deleteMemoryCard(memoryId) {
  return apiRequest(`/api/memory/me/${memoryId}`, {
    method: "DELETE",
  });
}

export async function logoutUser() {
  try {
    await apiRequest("/api/users/logout", { method: "POST" });
  } finally {
    clearToken();
  }
}
