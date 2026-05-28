/*
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
*/
import { invoke } from "@tauri-apps/api/core";

const TOKEN_PREFIX = "hackson_desktop_pet_token";
const LEGACY_TOKEN_KEY = "hackson_desktop_pet_token";
const API_SOURCE_KEY = "hackson_desktop_pet_api_source";
const PUBLIC_SOURCE_ID = "public";
const LOCAL_PROXY_SOURCE_ID = "local";
const LOCAL_BACKEND_SOURCE_ID = "localBackend";
const LOCAL_PUBLIC_SOURCE_ID = "localPublic";
const AUTO_SOURCE_ID = "auto";

export const API_SOURCES = {
  [AUTO_SOURCE_ID]: {
    id: AUTO_SOURCE_ID,
    label: "Auto",
    siteUrl: "https://hackson.catachess.com",
    candidateIds: [LOCAL_PROXY_SOURCE_ID, LOCAL_BACKEND_SOURCE_ID, LOCAL_PUBLIC_SOURCE_ID, PUBLIC_SOURCE_ID],
  },
  [LOCAL_PROXY_SOURCE_ID]: {
    id: LOCAL_PROXY_SOURCE_ID,
    label: "Local",
    apiBaseUrl: "http://127.0.0.1:18126",
    siteUrl: "http://127.0.0.1:5173",
    candidateIds: [LOCAL_PROXY_SOURCE_ID, LOCAL_BACKEND_SOURCE_ID, LOCAL_PUBLIC_SOURCE_ID],
  },
  [LOCAL_BACKEND_SOURCE_ID]: {
    id: LOCAL_BACKEND_SOURCE_ID,
    label: "Backend",
    apiBaseUrl: "http://127.0.0.1:8000",
    siteUrl: "http://127.0.0.1:5173",
    candidateIds: [LOCAL_BACKEND_SOURCE_ID],
  },
  [LOCAL_PUBLIC_SOURCE_ID]: {
    id: LOCAL_PUBLIC_SOURCE_ID,
    label: "Local 8145",
    apiBaseUrl: "http://127.0.0.1:8145",
    siteUrl: "http://127.0.0.1:8145",
    candidateIds: [LOCAL_PUBLIC_SOURCE_ID],
  },
  [PUBLIC_SOURCE_ID]: {
    id: PUBLIC_SOURCE_ID,
    label: "Public",
    apiBaseUrl: "https://hackson.catachess.com",
    siteUrl: "https://hackson.catachess.com",
    candidateIds: [PUBLIC_SOURCE_ID],
  },
};

export class DesktopApiError extends Error {
  constructor(message, status = null, code = "") {
    super(message);
    this.name = "DesktopApiError";
    this.status = status;
    this.code = code;
  }
}

export function getApiSourceId() {
  const saved = window.localStorage.getItem(API_SOURCE_KEY);
  return API_SOURCES[saved] ? saved : AUTO_SOURCE_ID;
}

export function setApiSourceId(sourceId) {
  const nextSourceId = API_SOURCES[sourceId] ? sourceId : AUTO_SOURCE_ID;
  window.localStorage.setItem(API_SOURCE_KEY, nextSourceId);
  return nextSourceId;
}

export function getApiSource(sourceId = getApiSourceId()) {
  return API_SOURCES[sourceId] || API_SOURCES[AUTO_SOURCE_ID];
}

export function getResolvedSourceId(sourceId = getApiSourceId()) {
  return sourceId === AUTO_SOURCE_ID ? PUBLIC_SOURCE_ID : sourceId;
}

export function getToken(sourceId = getResolvedSourceId()) {
  const token = window.localStorage.getItem(tokenKey(sourceId));
  if (token) return token;
  if (sourceId === PUBLIC_SOURCE_ID) return window.localStorage.getItem(LEGACY_TOKEN_KEY);
  return null;
}

export function setToken(token, sourceId = getResolvedSourceId()) {
  window.localStorage.setItem(tokenKey(sourceId), token);
}

export function clearToken(sourceId = null) {
  if (sourceId) {
    window.localStorage.removeItem(tokenKey(sourceId));
    if (sourceId === PUBLIC_SOURCE_ID) window.localStorage.removeItem(LEGACY_TOKEN_KEY);
    return;
  }
  for (const id of [LOCAL_PROXY_SOURCE_ID, LOCAL_BACKEND_SOURCE_ID, LOCAL_PUBLIC_SOURCE_ID, PUBLIC_SOURCE_ID]) {
    window.localStorage.removeItem(tokenKey(id));
  }
  window.localStorage.removeItem(LEGACY_TOKEN_KEY);
}

export function getSiteUrl(sourceId = getApiSourceId(), resolvedSourceId = "") {
  if (sourceId === AUTO_SOURCE_ID && resolvedSourceId && API_SOURCES[resolvedSourceId]) {
    return API_SOURCES[resolvedSourceId].siteUrl;
  }
  const source = getApiSource(sourceId);
  if (sourceId === AUTO_SOURCE_ID) return API_SOURCES[PUBLIC_SOURCE_ID].siteUrl;
  return source.siteUrl;
}

export async function resolveApiSource(sourceId = getApiSourceId()) {
  const source = getApiSource(sourceId);
  let lastError = null;
  for (const candidateId of source.candidateIds) {
    const candidate = API_SOURCES[candidateId];
    try {
      await nativeRequest(candidate.apiBaseUrl, "/health", { method: "GET", sourceId: candidateId, token: null });
      return candidateId;
    } catch (error) {
      lastError = error;
    }
  }
  if (lastError && sourceId !== AUTO_SOURCE_ID) throw normalizeError(lastError);
  throw new DesktopApiError("Site offline", null, "desktop_api_unreachable");
}

export async function apiRequest(path, options = {}) {
  const sourceId = options.sourceId || getApiSourceId();
  const resolvedSourceId = options.resolvedSourceId || (await resolveApiSource(sourceId));
  try {
    return await nativeRequest(API_SOURCES[resolvedSourceId].apiBaseUrl, path, {
      method: options.method || "GET",
      sourceId: resolvedSourceId,
      token: getToken(resolvedSourceId),
      body: options.body || null,
    });
  } catch (error) {
    const apiError = normalizeError(error);
    if (apiError.status === 401) clearToken(resolvedSourceId);
    throw apiError;
  }
}

async function nativeRequest(baseUrl, path, options) {
  return invoke("http_request", {
    payload: {
      method: options.method || "GET",
      url: `${baseUrl}${path}`,
      token: options.token,
      body: options.body || null,
    },
  });
}

function normalizeError(error) {
  const message = String(error || "desktop_api_request_failed");
  const match = message.match(/^(\d+):(.*)$/);
  if (!match) return new DesktopApiError(resolveMessage(message), null, message);
  return new DesktopApiError(resolveMessage(match[2]), Number(match[1]), match[2]);
}

function resolveMessage(message) {
  const known = {
    desktop_api_unreachable: "Site offline",
    desktop_api_non_json_response: "Site session unavailable",
    desktop_api_request_failed: "Request failed",
    desktop_api_url_not_allowed: "Source blocked",
    desktop_api_validation_failed: "Check fields",
    invalid_token: "Login expired",
    invalid_credentials: "Login failed",
    model_rate_limited: "Model busy",
    model_unavailable: "Model unavailable",
  };
  return known[message] || message;
}

function tokenKey(sourceId) {
  return `${TOKEN_PREFIX}_${sourceId}`;
}
