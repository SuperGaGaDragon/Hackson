/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex
*/
import { apiRequest } from "./client";

export function createTask(payload) {
  return apiRequest("/api/tasks", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export function listTasks() {
  return apiRequest("/api/tasks");
}

export function sendTaskMessage(taskId, payload) {
  return apiRequest(`/api/tasks/${taskId}/messages`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
}
