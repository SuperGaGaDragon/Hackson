/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
*/
import { apiRequest } from "./client";

export function createProject(payload) {
  return apiRequest("/api/work/projects", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listProjects() {
  return apiRequest("/api/work/projects");
}

export function createMission(payload) {
  return apiRequest("/api/work/missions", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listProjectMissions(projectId) {
  return apiRequest(`/api/work/projects/${projectId}/missions`);
}

export function getMission(missionId) {
  return apiRequest(`/api/work/missions/${missionId}`);
}

export function startMission(missionId) {
  return apiRequest(`/api/work/missions/${missionId}/start`, {
    method: "POST",
    body: JSON.stringify({}),
  });
}

export function stopMission(missionId, payload = {}) {
  return apiRequest(`/api/work/missions/${missionId}/stop`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listMissionEvents(missionId, afterSequence = null) {
  const query = afterSequence == null ? "" : `?afterSequence=${encodeURIComponent(afterSequence)}`;
  return apiRequest(`/api/work/missions/${missionId}/events${query}`);
}
