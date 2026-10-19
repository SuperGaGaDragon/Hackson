/*
Created at: 2026-10-19
Created by: Codex
Last Modified at: 2026-10-19
Last Modified by: Codex
*/

const HACKSON_ORIGIN = "https://hackson.catachess.com";

export default {
  async fetch(request, env) {
    return handleRequest(request, env);
  },
};

export async function handleRequest(request, env) {
  const url = new URL(request.url);

  if (url.pathname.startsWith("/assets/downloads/")) {
    const localDownload = await env.ASSETS.fetch(request);
    if (localDownload.status !== 404) return localDownload;
  }

  if (shouldProxyPath(url.pathname)) {
    return proxyToHackson(request, url);
  }

  const assetResponse = await env.ASSETS.fetch(request);
  if (assetResponse.status !== 404 || !isHtmlNavigation(request)) {
    return withBrowserSecurityHeaders(assetResponse);
  }

  const indexUrl = new URL("/", url);
  const indexRequest = new Request(indexUrl, {
    headers: request.headers,
    method: "GET",
  });
  return withBrowserSecurityHeaders(await env.ASSETS.fetch(indexRequest));
}

export function shouldProxyPath(pathname) {
  return (
    pathname === "/health" ||
    pathname === "/api" ||
    pathname.startsWith("/api/") ||
    pathname.startsWith("/assets/downloads/")
  );
}

async function proxyToHackson(request, publicUrl) {
  const upstreamUrl = new URL(`${publicUrl.pathname}${publicUrl.search}`, HACKSON_ORIGIN);
  const headers = new Headers(request.headers);
  headers.set("X-Forwarded-Host", publicUrl.host);
  headers.set("X-Forwarded-Proto", "https");

  const init = {
    headers,
    method: request.method,
    redirect: "manual",
  };
  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = await request.arrayBuffer();
  }

  try {
    const upstreamResponse = await fetch(new Request(upstreamUrl, init));
    const responseHeaders = new Headers(upstreamResponse.headers);
    if (publicUrl.pathname === "/api" || publicUrl.pathname.startsWith("/api/")) {
      responseHeaders.set("Cache-Control", "no-store");
    }
    responseHeaders.set("X-Content-Type-Options", "nosniff");
    return new Response(upstreamResponse.body, {
      headers: responseHeaders,
      status: upstreamResponse.status,
      statusText: upstreamResponse.statusText,
    });
  } catch (_error) {
    const isApi = publicUrl.pathname === "/api" || publicUrl.pathname.startsWith("/api/");
    if (isApi || publicUrl.pathname === "/health") {
      return Response.json(
        { detail: "upstream_unavailable" },
        { status: 502, headers: { "Cache-Control": "no-store" } },
      );
    }
    return new Response("Download temporarily unavailable", {
      status: 502,
      headers: { "Cache-Control": "no-store", "Content-Type": "text/plain; charset=utf-8" },
    });
  }
}

function isHtmlNavigation(request) {
  if (request.method !== "GET" && request.method !== "HEAD") return false;
  return (request.headers.get("Accept") || "").includes("text/html");
}

function withBrowserSecurityHeaders(response) {
  const contentType = response.headers.get("Content-Type") || "";
  if (!contentType.includes("text/html")) return response;

  const headers = new Headers(response.headers);
  headers.set(
    "Content-Security-Policy",
    "default-src 'self'; base-uri 'self'; connect-src 'self'; font-src 'self' data:; form-action 'self'; frame-ancestors 'none'; img-src 'self' data:; object-src 'none'; script-src 'self'; style-src 'self' 'unsafe-inline'",
  );
  headers.set("Permissions-Policy", "camera=(), geolocation=(), microphone=()");
  headers.set("Referrer-Policy", "strict-origin-when-cross-origin");
  headers.set("X-Content-Type-Options", "nosniff");
  headers.set("X-Frame-Options", "DENY");
  return new Response(response.body, {
    headers,
    status: response.status,
    statusText: response.statusText,
  });
}
