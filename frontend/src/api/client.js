/*
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
*/
const TOKEN_KEY = "hackson_access_token";

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "";

export class ApiError extends Error {
  constructor(message, status) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
}

export function clearToken() {
  localStorage.removeItem(TOKEN_KEY);
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
  const data = text ? JSON.parse(text) : null;

  if (!response.ok) {
    throw new ApiError(resolveErrorMessage(data), response.status);
  }

  return data;
}

function resolveErrorMessage(data) {
  if (!data) return "Request failed";
  if (typeof data.detail === "string") return data.detail;
  if (Array.isArray(data.detail)) return data.detail[0]?.msg || "Request failed";
  return data.message || "Request failed";
}
