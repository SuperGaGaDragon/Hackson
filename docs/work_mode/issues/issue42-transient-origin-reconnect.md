## header
Created at: 2026-05-29
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex

# Issue 42: Transient Origin Reconnect UX

## Problem

During public deployment, `hackson-domain-8145.service` was restarted while users had Work and Idle pages open.
Cloudflare tunnel returned `502` because the origin at `127.0.0.1:8145` refused connections during the restart window.

The browser then showed repeated failed requests such as:

- `/api/work/missions/{id}`;
- `/api/work/missions/{id}/events?afterSequence=...`;
- `/api/conversations?mode=idle`;
- `/api/conversations?mode=companion_2`.

The backend recovered, but the user experience looked like a crash.

## Root Cause

This was an origin availability gap, not a Work Mode application exception. Logs showed:

- systemd stopped `hackson-domain-8145.service`;
- uvicorn waited for active connections and background tasks;
- cloudflared could not connect to `127.0.0.1:8145`;
- the service restarted and later requests returned `200`.

The Work page made the failure noisier because its SSE fallback used a fixed `1.5s` polling interval after stream
disconnects.

## Decision

Frontend event sync must treat transient origin failures as a reconnecting state:

- do not turn every sync failure into a hard user error;
- use bounded exponential backoff up to `30s`;
- show a compact "Reconnecting to mission updates" notice in the Mission header;
- clear the notice once an event or poll succeeds;
- tolerate non-JSON error bodies from proxies/CDNs without throwing JSON parse errors.

Deployment discipline remains: do not restart public backend while Work Missions or Work Windows are running unless the
user explicitly accepts the interruption.

## Acceptance

- Work event fallback no longer polls every `1.5s` forever during origin downtime.
- A transient 502 produces a reconnecting notice rather than a noisy permanent error.
- API client handles HTML/text proxy error bodies without crashing JSON parsing.
- Static-only frontend updates are deployed without restarting backend services.
