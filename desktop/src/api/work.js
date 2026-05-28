/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { apiRequest } from "./client";

export function listProjects(options = {}) {
  return apiRequest("/api/work/projects", options);
}

export function listProjectMissions(projectId, options = {}) {
  return apiRequest(`/api/work/projects/${projectId}/missions`, options);
}

export function getMission(missionId, options = {}) {
  return apiRequest(`/api/work/missions/${missionId}`, options);
}

export function listMissionEvents(missionId, afterSequence = null, options = {}) {
  const query = afterSequence == null ? "" : `?afterSequence=${encodeURIComponent(afterSequence)}`;
  return apiRequest(`/api/work/missions/${missionId}/events${query}`, options);
}
