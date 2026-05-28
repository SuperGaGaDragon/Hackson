## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Desktop Pet Versions

## 1. Purpose

This document defines Desktop Pet release versions, product scope, and release gates.

Desktop Pet should grow from a narrow Work Mode progress surface into a broader Hackson desktop presence only after the Work Mode loop is trustworthy.

## 2. Version Summary

| Version | Name | Product Result | Runtime Result | Release Gate |
| --- | --- | --- | --- | --- |
| V0.1 | Desktop Shell Spike | A tiny desktop window can stay on top, move, close, and reopen. | Tauri + React + Vite prototype. | Local shell runs on macOS without backend. |
| V0.2 | Authenticated Watcher | User can login and select a Mission. | Desktop API client calls verified Hackson APIs. | Login persists across restart and selected Mission reloads. |
| V0.3 | Event Presence | Pet state reflects real Work Mode events. | Polling watcher and deterministic state reducer. | Running Mission changes pet state from real event timeline. |
| V0.5 | Local Cat Pet | A cat appears on the user's desktop and can stand, walk, or sleep. | Local-only Tauri app using bundled cat images; no backend, auth, Work Mode, tray, or packaging requirement. | On the maintainer's macOS desktop, the cat window appears, can be dragged, changes between stand/walk/sleep, and can quit cleanly. |
| V0.6 | Polished Local Cat | The local cat feels like a small product instead of a shell test. | Transparent cutout assets, calmer visual system, compact mode, better state timing, and cleaner app-only build. | The cat looks natural on the desktop, controls do not dominate, and build/open loop remains stable. |
| V0.7 | Site-Aware Watcher | The cat reflects the real Hackson Work Mode Mission selected by the user. | Desktop login, Project/Mission picker, event polling, and deterministic Work Mode to pet-state mapping through verified APIs. | Login succeeds, a Mission can be selected, status updates from real website state, and drag remains reliable. |
| V0.8 | Auto Mission Watcher | The cat automatically discovers and follows the most relevant active Work Mode Mission started on the website. | Project scan, active Mission ranking, automatic binding, manual override from the cat, and periodic rescan. | Starting a Mission on the website makes the cat react without requiring manual Project/Mission lookup first. |
| V0.8.1 | Environment-Aware Watcher Fix | The cat watches the same Hackson source the maintainer is using, not a hard-coded website by accident. | Auto/local/public API source selection, readable native HTTP errors, and matching Site open action. | Missing local API falls back cleanly, source can be switched in the cat panel, and raw JSON parser errors never appear in the UI. |
| V0.8.2 | Browser Handoff Login | The desktop pet has no password form; browser login authorizes it automatically. | Short-lived desktop handoff code, website bind endpoint, desktop claim polling, and control-free pet UI. | Public `8145` handoff API and browser `desktopAuth` bind pass; double-click cat opens browser login, website binds the code after auth, desktop claims token, and no form/control chrome appears on the pet. |
| V0.8.3 | Bubble Progress Glance | Clicking the cat bubble expands a compact view of current Work Mode progress. | Desktop-only Progress summary from selected Mission events, compact event rows, and temporary window resize. | Single click expands/collapses progress; double-click still opens the website; build and screenshot smoke pass. |
| V1.0 | Work Mode Progress Pet | User can leave the browser and still see Agent work status on desktop. | Packaged desktop app with pet window, popover, tray, notifications, and Work Console open action. | 30-minute Mission watch smoke passes with no notification spam or stale terminal state. |
| V1.1 | Product Glance | User can preview latest Product and Artifact summary from the pet. | Product manifest and latest Artifact reader in compact popover. | Latest Product opens quickly and never displays raw diagnostics as user content. |
| V1.2 | Streaming Presence | Pet reacts faster during long model turns. | Uses verified Work Mode stream API when available, with polling fallback. | Stream disconnect falls back to polling without duplicated notifications. |
| V1.3 | Multi-Mission Radar | User can watch several Missions with one primary pet state and a Mission list. | Desktop summary API may be added if polling many Missions is wasteful. | Multiple Missions do not create confusing notification storms. |
| V1.5 | Idle Bridge | When no Work Mission is active, the pet can surface Idle mode and turn ideas into Missions through the web app. | Reads Idle conversation state; Mission creation remains verified web/API flow. | Idle never interrupts an active Work Mission. |
| V2.0 | Desktop Command Center | Pet can accept short user commands for the selected Mission. | Sends user-approved actions through verified Work Mode APIs. | Commands cannot bypass Work Mode validation or approval rules. |
| V2.5 | Read-Only Screen Context | User can explicitly share a screenshot or active-window context. | Permissioned one-shot context capture, no background surveillance. | No screen data is captured without visible user action. |
| V3.0 | Hackson OS Presence | Pet becomes the persistent Hackson desktop entry point for Work, Idle, memory, and daily briefs. | Unified desktop runtime with account, notifications, summaries, and optional auto-start. | User can understand and control every active background behavior. |

## 3. V1.0 Scope

V1.0 includes:

- Account login.
- Mission selection.
- Pet window.
- Event-based state.
- Compact popover.
- Tray menu.
- Native notifications for action-worthy states.
- Open Work Console.
- Local packaging.

V1.0 excludes:

- Voice.
- Idle chat.
- Screen reading.
- File reading.
- Computer control.
- Work creation from desktop.
- Multi-Mission watch.
- App auto-update.

## 4. V0.5 Local Cat Pet

V0.5 is a local feel prototype.

V0.5 includes:

- local macOS desktop window
- three visible states: stand, walk, sleep
- small speech bubble
- drag area
- manual state buttons
- lightweight automatic idle cycle
- quit control
- bundled temporary cat images from local source assets

V0.5 excludes:

- login
- backend API
- Work Mode event polling
- native notifications
- tray menu
- installer
- public distribution
- screen, file, shell, or computer control

V0.5 state mapping:

| State | Asset | Behavior |
| --- | --- | --- |
| stand | `cat_idle1.png` and `cat_idle2.png` | Calm breathing switch between idle frames. |
| walk | `cat_walk1.png` | Window nudges horizontally while speech bubble says it is walking. |
| sleep | `cat_sleep.png` | Still sleeping pose with quiet speech bubble. |

## 5. V0.7 Site-Aware Watcher

V0.7 restores the core product purpose: the cat reflects Hackson website state.

V0.7 includes:

- login against the verified Hackson public service
- token stored locally in the desktop app
- Project and Mission picker
- selected Mission persistence
- Work Mode Mission detail polling
- Work Mode event polling with `afterSequence`
- deterministic Mission state to pet behavior mapping
- clear disconnected and signed-out states
- drag support preserved on the cat and bubble

V0.7 excludes:

- Mission creation
- native notifications
- tray menu
- Work Mode command controls
- screen, file, shell, browser, or computer control

V0.7 state mapping:

| Hackson state | Cat behavior |
| --- | --- |
| signed out | still, asks user to sign in |
| no Mission selected | still, asks user to choose a Mission |
| `draft` | stand |
| `running` with model/tool events | walk or working state |
| active Work Window | walk with delegate label |
| `waiting_input` | attention label |
| `paused_retryable`, `blocked`, `stopped` | sleep or paused label |
| `completed` | stand with done label |
| `failed` | still with failed label |
| offline/API error | still with offline label |

## 6. V0.8 Auto Mission Watcher

V0.8 fixes the core discovery gap: if a user starts Work Mode on the website, the cat should find it.

V0.8 includes:

- scan all current Projects after login
- list Missions for each Project
- rank active Missions by status and recency
- automatically bind only the best active Mission
- show `No active work` when there is no `running`, `waiting_input`, `paused_retryable`, `blocked`, or `stopping` Mission
- show the primary Mission title and active count when multiple Missions are active
- periodically rescan even while an active Mission is selected, so newly-started website Missions can be discovered
- replace an older lower-priority active Mission, such as `paused_retryable`, when a higher-priority `running` Mission appears
- preserve manual Project/Mission selection from the cat
- show which Mission is being watched

Active Mission priority:

1. `running`
2. `waiting_input`
3. `paused_retryable`
4. `blocked`
5. `stopping`

V0.8 still excludes:

- Mission creation from desktop
- start/stop/resume commands
- native notifications

## 6.1. V0.8.1 Environment-Aware Watcher Fix

V0.8.1 fixes the environment mismatch that makes the cat appear disconnected while Work Mode is active elsewhere.

V0.8.1 includes:

- `Auto` API source mode
- local API source
- public API source
- source selector in the compact pet panel
- native HTTP allowlist for known Hackson origins
- readable handling for HTML or non-JSON API responses
- matching Site open behavior for the selected source

V0.8.1 excludes:

- arbitrary custom API URLs
- public installer work
- Mission start/stop commands from desktop
- cross-browser session sharing

## 6.2. V0.8.2 Browser Handoff Login

V0.8.2 removes the desktop login form and makes the browser the login authority.

V0.8.2 includes:

- double-click cat or bubble to open Hackson login
- short-lived `desktopAuth` handoff code
- authenticated website bind endpoint
- unauthenticated desktop claim endpoint
- local token storage after successful claim
- no bottom login panel
- no visible top quit or compact buttons
- public `https://hackson.catachess.com` support for `pending -> linked -> authorized` handoff

V0.8.2 excludes:

- browser cookie reading from the desktop app
- custom URL scheme registration
- QR-code pairing
- arbitrary source configuration UI
- native menu/tray quit controls

V0.8.2 verification:

- target public user service and route tests: `9 passed`
- target frontend build: `/assets/index-CTj8ztQu.js`, `/assets/index-DTBHuMeq.css`
- public API smoke: pending claim, authenticated bind, authorized one-time claim, second claim pending
- public browser smoke: already-logged-in `?desktopAuth=` bind and login-then-bind both pass

## 7. V1.1 Product Glance

V1.1 adds read-only Product awareness.

The user should be able to click the pet after a Product update and see:

- latest Product title
- Product status
- latest Artifact title
- short summary
- open full Work Console

The compact reader must not become the full Product Panel. Full reading remains in the web app.

## 8. V1.2 Streaming Presence

V1.2 depends on Work Mode exposing a verified stream API.

The pet can react faster to long model turns, but it must not expose raw chain-of-thought or unvalidated model content.

Polling remains fallback.

## 9. V1.3 Multi-Mission Radar

V1.3 lets users track more than one Mission.

Design rule:

- The pet has one primary visible state.
- A compact list can show other Missions.
- Notifications are deduped by Mission id and event sequence.

If polling becomes expensive, add a backend summary endpoint and document it in root `api.md` after verification.

## 10. V1.5 Idle Bridge

V1.5 connects Desktop Pet to Idle only when Work Mode is not active.

Use cases:

- The pet idles with lightweight Agent presence.
- User can jot a thought.
- The thought can become a Work Mission through a verified flow.

Idle must never dilute V1's Work Mode clarity.

## 11. V2.0 Desktop Command Center

V2.0 allows short commands:

- pause
- resume
- retry
- open product
- add note to Mission
- ask what changed

Every command must route through backend APIs and respect Work Mode state validation.

## 12. V2.5 Read-Only Screen Context

V2.5 may add explicit screenshot or active-window capture.

Rules:

- User must trigger capture.
- The app must show what was captured.
- No continuous background screen reading.
- No computer control.
- No file-system crawl.

## 13. V3.0 Hackson OS Presence

V3.0 is the long-term platform direction.

Desktop Pet becomes the user's persistent Hackson surface:

- daily brief
- active Missions
- waiting decisions
- completed artifacts
- Idle companion
- memory highlights

This version only makes sense after Work Mode, Context Runtime, and notification trust are solid.
