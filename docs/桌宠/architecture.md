## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Desktop Pet Architecture

## 1. Purpose

This document defines ownership boundaries for Desktop Pet.

Desktop Pet is a desktop client for Work Mode state. It is not a new backend runtime.

## 2. Product Boundary

Desktop Pet owns:

- Desktop app shell.
- Authentication token storage on the desktop client.
- Mission selection UI.
- Mission state polling.
- Event-to-pet-state mapping.
- Pet animation state.
- Native notification policy.
- Deep link or browser open into the Work Console.

Desktop Pet does not own:

- Agent identity.
- Mission execution.
- Tool execution.
- Model calls.
- Product and Artifact persistence.
- Work Mode event definitions.
- Context construction.
- Memory, diary, or summaries.

## 3. Recommended Folder Layout

The implementation SHOULD add a new top-level `desktop/` folder when code work begins.

Planned structure:

```text
desktop/
  README.md
  package.json
  index.html
  src/
    README.md
    main.jsx
    App.jsx
    api/
      README.md
      client.js
      work.js
      users.js
    domain/
      README.md
      missionState.js
      petState.js
    features/
      README.md
      auth/
      mission-picker/
      pet/
      tray/
    shared/
      README.md
      components/
  src-tauri/
    README.md
    tauri.conf.json
    capabilities/
```

Every folder must include a README before code lands, following `agents/restrictions.md`.

## 4. Runtime Components

```text
Tauri shell
  -> React app
    -> API client
      -> Hackson public backend
    -> Mission watcher
      -> Work Mode event polling
      -> pet state reducer
    -> Pet renderer
    -> Popover
    -> Tray command adapter
```

## 5. Data Flow

```text
Login
  -> store token locally
  -> load current user
  -> list projects and missions
  -> user selects Mission
  -> fetch Mission detail
  -> poll Mission events after latest sequence
  -> merge events
  -> derive pet state
  -> render animation and notification
```

## 6. Source Of Truth

Source of truth order:

1. Work Mode Mission detail response.
2. Work Mode event timeline.
3. Local desktop state cache.

Local desktop cache is only a convenience layer. It must not override backend Mission status.

## 7. API Strategy

V1 uses polling because Work Mode already exposes verified event polling.

Polling default:

- Active running Mission: every 1500 ms.
- Retry, waiting, paused, completed, failed: stop fast polling and refresh every 30 seconds.
- Offline: exponential backoff up to 60 seconds.

Future streaming belongs to V1.2 after Work Mode exposes a verified stream API.

## 8. Security Model

- Use HTTPS public domain for normal login.
- Store JWT in OS-backed secure storage when available.
- Never write raw tokens into logs.
- Never expose model provider keys.
- Do not support arbitrary backend URL entry in V1 unless a developer mode is explicitly added.
- Native notifications must not include full private Artifact content by default.

## 9. Platform Model

V1 target platforms:

- macOS first.
- Windows second.
- Linux optional for developer testing.

The V1 prototype should validate:

- Transparent or visually shaped window.
- Always-on-top behavior.
- Tray/menu support.
- Native notifications.
- Drag positioning.
- Auto-start disabled by default.

## 10. Failure Handling

Desktop Pet must handle:

- Expired token: show signed-out state.
- API unreachable: show offline state.
- Mission deleted or inaccessible: clear selection and show picker.
- Event polling error: keep last known state but mark stale.
- Version mismatch: show update-required state only after an update channel exists.

## 11. Why Not Browser-Only

A browser-only widget cannot deliver the core product promise. The pet must remain visible when the user leaves the Work Console.

Desktop presence is the feature.
