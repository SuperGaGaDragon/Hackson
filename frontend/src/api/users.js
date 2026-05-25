/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
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

export function updateCurrentUser(payload) {
  return apiRequest("/api/users/me", {
    method: "PATCH",
    body: JSON.stringify(payload),
  });
}

export async function logoutUser() {
  try {
    await apiRequest("/api/users/logout", { method: "POST" });
  } finally {
    clearToken();
  }
}
