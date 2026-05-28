/*
Created at: 2026-05-26
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { API_BASE_URL, ApiError, apiRequest, clearToken, getToken } from "./client";

export function createProject(payload) {
  return apiRequest("/api/work/projects", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listProjects() {
  return apiRequest("/api/work/projects");
}

export function createEmployee(payload) {
  return apiRequest("/api/work/employees", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listEmployees() {
  return apiRequest("/api/work/employees");
}

export function addProjectEmployee(projectId, payload) {
  return apiRequest(`/api/work/projects/${projectId}/employees`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listProjectEmployees(projectId) {
  return apiRequest(`/api/work/projects/${projectId}/employees`);
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

export function answerMission(missionId, payload) {
  return apiRequest(`/api/work/missions/${missionId}/answer`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function evaluateMission(missionId, payload = {}) {
  return apiRequest(`/api/work/missions/${missionId}/evaluate`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listMissionEvents(missionId, afterSequence = null) {
  const query = afterSequence == null ? "" : `?afterSequence=${encodeURIComponent(afterSequence)}`;
  return apiRequest(`/api/work/missions/${missionId}/events${query}`);
}

export async function streamMissionEvents(missionId, afterSequence = null, handlers = {}) {
  if (!window.ReadableStream) {
    throw new ApiError("Streaming unsupported", 0);
  }
  const query = afterSequence == null ? "" : `?afterSequence=${encodeURIComponent(afterSequence)}`;
  const headers = new Headers({ Accept: "text/event-stream" });
  const token = getToken();
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  const response = await fetch(`${API_BASE_URL}/api/work/missions/${missionId}/events/stream${query}`, {
    headers,
    signal: handlers.signal,
  });
  if (response.status === 401) {
    clearToken();
  }
  if (!response.ok || !response.body) {
    throw new ApiError("Stream failed", response.status);
  }
  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  while (true) {
    const { done, value } = await reader.read();
    if (done) break;
    buffer += decoder.decode(value, { stream: true });
    const parts = buffer.split("\n\n");
    buffer = parts.pop() || "";
    for (const part of parts) {
      await dispatchSseBlock(part, handlers);
    }
  }
  buffer += decoder.decode();
  if (buffer.trim()) {
    await dispatchSseBlock(buffer, handlers);
  }
}

async function dispatchSseBlock(block, handlers) {
  const message = parseSseBlock(block);
  if (message.event === "work_event" && message.data) {
    await handlers.onEvent?.(message.data);
  } else if (message.event === "ping") {
    await handlers.onPing?.(message.data);
  }
}

function parseSseBlock(block) {
  const dataLines = [];
  let event = "message";
  let id = null;
  for (const rawLine of block.split(/\r?\n/)) {
    if (!rawLine || rawLine.startsWith(":")) continue;
    const separatorIndex = rawLine.indexOf(":");
    const field = separatorIndex >= 0 ? rawLine.slice(0, separatorIndex) : rawLine;
    let value = separatorIndex >= 0 ? rawLine.slice(separatorIndex + 1) : "";
    if (value.startsWith(" ")) value = value.slice(1);
    if (field === "event") event = value;
    if (field === "id") id = value;
    if (field === "data") dataLines.push(value);
  }
  const dataText = dataLines.join("\n").trim();
  return {
    event,
    id,
    data: dataText ? JSON.parse(dataText) : null,
  };
}
