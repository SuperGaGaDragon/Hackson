/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { apiRequest, setToken } from "./client";

export async function claimDesktopHandoff(code, options = {}) {
  const data = await apiRequest("/api/users/desktop-handoff/claim", {
    method: "POST",
    body: { code },
    ...options,
  });
  if (data.status === "authorized" && data.accessToken) {
    setToken(data.accessToken, options.resolvedSourceId);
  }
  return data;
}

export function getCurrentUser(options = {}) {
  return apiRequest("/api/users/me", options);
}
