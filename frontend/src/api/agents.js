/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
*/
import { apiRequest } from "./client";

export function listAgents() {
  return apiRequest("/api/agents");
}

