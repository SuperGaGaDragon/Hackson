/*
Created at: 2026-10-19
Created by: Codex
Last Modified at: 2026-10-19
Last Modified by: Codex
*/

import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";

const workerSource = await readFile(new URL("../public/_worker.js", import.meta.url), "utf8");
const workerModule = await import(`data:text/javascript;base64,${Buffer.from(workerSource).toString("base64")}`);
const originalFetch = globalThis.fetch;
const originCalls = [];

globalThis.fetch = async (request) => {
  const url = new URL(request.url);
  originCalls.push({
    authorization: request.headers.get("Authorization"),
    body: request.method === "GET" || request.method === "HEAD" ? "" : await request.text(),
    forwardedHost: request.headers.get("X-Forwarded-Host"),
    method: request.method,
    pathname: url.pathname,
    search: url.search,
  });
  if (url.pathname === "/api/fail") throw new Error("origin down");
  if (url.pathname === "/api/work/missions/m1/events/stream") {
    return new Response('event: work_event\ndata: {"sequence":1}\n\n', {
      headers: { "Content-Type": "text/event-stream" },
    });
  }
  if (url.pathname.startsWith("/api/")) {
    return Response.json({ ok: true, path: `${url.pathname}${url.search}` });
  }
  if (url.pathname === "/health") return Response.json({ status: "ok" });
  if (url.pathname.startsWith("/assets/downloads/")) {
    return new Response("zip-bytes", { headers: { "Content-Type": "application/zip" } });
  }
  return new Response("origin missing", { status: 404 });
};

const env = {
  ASSETS: {
    async fetch(request) {
      const pathname = new URL(request.url).pathname;
      if (pathname === "/") {
        return new Response("<!doctype html><title>Parallax</title>", {
          headers: { "Content-Type": "text/html; charset=utf-8" },
        });
      }
      if (pathname === "/assets/app.js") {
        return new Response("export {};", { headers: { "Content-Type": "text/javascript" } });
      }
      return new Response("asset missing", { status: 404 });
    },
  },
};

try {
  assert.equal(workerModule.shouldProxyPath("/api/agents"), true);
  assert.equal(workerModule.shouldProxyPath("/health"), true);
  assert.equal(workerModule.shouldProxyPath("/assets/downloads/pet.zip"), true);
  assert.equal(workerModule.shouldProxyPath("/assets/app.js"), false);

  const apiResponse = await workerModule.handleRequest(
    new Request("https://parallax-epv.pages.dev/api/agents?limit=2", {
      headers: { Authorization: "Bearer smoke" },
    }),
    env,
  );
  assert.equal(apiResponse.status, 200);
  assert.equal(apiResponse.headers.get("Cache-Control"), "no-store");
  assert.deepEqual(await apiResponse.json(), { ok: true, path: "/api/agents?limit=2" });
  assert.equal(originCalls.at(-1).authorization, "Bearer smoke");
  assert.equal(originCalls.at(-1).forwardedHost, "parallax-epv.pages.dev");

  const postResponse = await workerModule.handleRequest(
    new Request("https://parallax-epv.pages.dev/api/work/projects", {
      body: JSON.stringify({ name: "Edge smoke" }),
      headers: { "Content-Type": "application/json" },
      method: "POST",
    }),
    env,
  );
  assert.equal(postResponse.status, 200);
  assert.equal(originCalls.at(-1).method, "POST");
  assert.equal(originCalls.at(-1).body, '{"name":"Edge smoke"}');

  const healthResponse = await workerModule.handleRequest(
    new Request("https://parallax-epv.pages.dev/health"),
    env,
  );
  assert.deepEqual(await healthResponse.json(), { status: "ok" });

  const streamResponse = await workerModule.handleRequest(
    new Request("https://parallax-epv.pages.dev/api/work/missions/m1/events/stream"),
    env,
  );
  assert.match(streamResponse.headers.get("Content-Type"), /text\/event-stream/);
  assert.match(await streamResponse.text(), /work_event/);

  const downloadResponse = await workerModule.handleRequest(
    new Request("https://parallax-epv.pages.dev/assets/downloads/pet.zip"),
    env,
  );
  assert.equal(downloadResponse.headers.get("Content-Type"), "application/zip");
  assert.equal(await downloadResponse.text(), "zip-bytes");

  const callsBeforeLocalDownload = originCalls.length;
  const localDownloadResponse = await workerModule.handleRequest(
    new Request("https://parallax-epv.pages.dev/assets/downloads/local.zip"),
    {
      ASSETS: {
        async fetch() {
          return new Response("local-zip", { headers: { "Content-Type": "application/zip" } });
        },
      },
    },
  );
  assert.equal(await localDownloadResponse.text(), "local-zip");
  assert.equal(originCalls.length, callsBeforeLocalDownload);

  const assetResponse = await workerModule.handleRequest(
    new Request("https://parallax-epv.pages.dev/assets/app.js"),
    env,
  );
  assert.equal(assetResponse.status, 200);
  assert.match(assetResponse.headers.get("Content-Type"), /text\/javascript/);

  const spaResponse = await workerModule.handleRequest(
    new Request("https://parallax-epv.pages.dev/work_mission/example", {
      headers: { Accept: "text/html" },
    }),
    env,
  );
  assert.equal(spaResponse.status, 200);
  assert.match(await spaResponse.text(), /Parallax/);
  assert.equal(spaResponse.headers.get("X-Frame-Options"), "DENY");
  assert.match(spaResponse.headers.get("Content-Security-Policy"), /frame-ancestors 'none'/);

  const missingAsset = await workerModule.handleRequest(
    new Request("https://parallax-epv.pages.dev/assets/missing.png", {
      headers: { Accept: "image/png" },
    }),
    env,
  );
  assert.equal(missingAsset.status, 404);

  const failedApi = await workerModule.handleRequest(
    new Request("https://parallax-epv.pages.dev/api/fail"),
    env,
  );
  assert.equal(failedApi.status, 502);
  assert.deepEqual(await failedApi.json(), { detail: "upstream_unavailable" });

  console.log(`pages_edge_worker_smoke=ok origin_calls=${originCalls.length}`);
} finally {
  globalThis.fetch = originalFetch;
}
