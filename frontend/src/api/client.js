/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
const TOKEN_KEY = "hackson_access_token";
const SESSION_TOKEN_KEY = "hackson_quick_access_token";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export function getToken() {
  return sessionStorage.getItem(SESSION_TOKEN_KEY) || localStorage.getItem(TOKEN_KEY);
}

export function hasSessionToken() {
  return Boolean(sessionStorage.getItem(SESSION_TOKEN_KEY));
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
  sessionStorage.removeItem(SESSION_TOKEN_KEY);
}

export function setSessionToken(token) {
  sessionStorage.setItem(SESSION_TOKEN_KEY, token);
  localStorage.removeItem(TOKEN_KEY);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
  sessionStorage.removeItem(SESSION_TOKEN_KEY);
}

export async function apiRequest(path, options = {}) {
  const headers = new Headers(options.headers || {});
  const token = getToken();

  if (!headers.has("Content-Type") && options.body) {
    headers.set("Content-Type", "application/json");
  }

  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (response.status === 401) {
    clearToken();
  }

  if (response.status === 204) {
    if (!response.ok) {
      throw new ApiError("Request failed", response.status);
    }
    return null;
  }

  const text = await response.text();
  const data = parseResponseBody(text);

  if (!response.ok) {
    throw new ApiError(resolveErrorMessage(data, response.status), response.status);
  }

  return data;
}

function parseResponseBody(text) {
  if (!text) return null;
  try {
    return JSON.parse(text);
  } catch (_err) {
    return { message: text };
  }
}

function resolveErrorMessage(data, status = 0) {
  if (status === 502 || status === 503 || status === 504) {
    return "Service temporarily unavailable. Try again shortly.";
  }
  if (!data) return "Request failed";
  if (typeof data.detail === "string") return KNOWN_ERROR_MESSAGES[data.detail] || data.detail;
  if (Array.isArray(data.detail)) return data.detail[0]?.msg || "Request failed";
  if (typeof data.message === "string" && !data.message.trim().startsWith("<")) return data.message;
  return "Request failed";
}

const KNOWN_ERROR_MESSAGES = {
  model_rate_limited: "Model busy",
  model_unavailable: "Model unavailable",
  conversation_must_be_idle: "Select an Idle discussion first.",
  idle_brainstorm_requires_messages: "Add a few Idle messages first.",
  mission_instruction_unavailable: "Command is updating. Refresh or retry shortly.",
};
