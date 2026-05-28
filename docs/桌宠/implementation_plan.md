## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Desktop Pet Implementation Plan

## 1. Purpose

This document is the engineer-facing build order for Desktop Pet V0.5 and V1.0.

Follow this plan after reading `final_version.md`, `architecture.md`, `state_mapping.md`, `ui_contract.md`, and `versions.md`.

## 2. Preflight

Before implementation:

```bash
git status --short
find docs/桌宠 -maxdepth 2 -type f | sort
```

Rules:

- Do not edit Work Mode backend behavior for Desktop Pet until the client proves the need.
- Do not update root `api.md` for speculative APIs.
- Do not add screen, file, shell, browser, Codex CLI, or computer-control features in V1.
- Do not expose model runtime settings in the desktop UI.
- Add README files before adding implementation folders.

## 3. Loop 1: Runtime Spike

## 3. V0.5: Local Cat Pet

Goal: make the pet appear on the maintainer's desktop before backend integration.

Likely files:

- `desktop/README.md`
- `desktop/package.json`
- `desktop/index.html`
- `desktop/vite.config.js`
- `desktop/src/README.md`
- `desktop/src/App.jsx`
- `desktop/src/styles.css`
- `desktop/src/assets/README.md`
- `desktop/src-tauri/README.md`
- `desktop/src-tauri/tauri.conf.json`
- `desktop/src-tauri/src/main.rs`

Required behavior:

- Show a local desktop cat window.
- Support three states: stand, walk, sleep.
- Use existing local cat images as temporary assets.
- Provide a small speech bubble.
- Provide manual state buttons.
- Move slightly while walking.
- Quit cleanly.
- Do not connect backend APIs.

Exit criteria:

- `npm run build` passes.
- `npm run tauri build` generates a local macOS app bundle.
- `Hackson Pet.app` opens on the desktop.

## 4. V0.6: Polished Local Cat

Goal: make the local cat feel like a polished product surface before backend work.

Likely files:

- `desktop/src/domain/petStates.js`
- `desktop/src/features/pet/PetWindow.jsx`
- `desktop/src/styles.css`
- `desktop/src/assets/*_cutout.png`
- `desktop/src-tauri/tauri.conf.json`

Required behavior:

- Use transparent cropped cat assets so the pet reads as a desktop creature, not a square image.
- Keep stand, walk, and sleep states.
- Add calmer state timing and manual override.
- Add compact mode so controls can get out of the way.
- Keep drag and quit reliable.
- Keep backend disconnected.

Exit criteria:

- `npm run build` passes.
- `npm run tauri build` passes.
- Local `.app` opens and displays the polished cat.
- All new source directories have README files.

## 5. V0.7: Site-Aware Watcher

Goal: connect Desktop Pet back to Hackson so the cat reflects real Work Mode website state.

Likely files:

- `desktop/src/api/README.md`
- `desktop/src/api/client.js`
- `desktop/src/api/users.js`
- `desktop/src/api/work.js`
- `desktop/src/domain/missionState.js`
- `desktop/src/features/auth/README.md`
- `desktop/src/features/auth/AuthPanel.jsx`
- `desktop/src/features/mission-picker/README.md`
- `desktop/src/features/mission-picker/MissionPicker.jsx`
- `desktop/src/features/pet/PetWindow.jsx`
- `desktop/src-tauri/src/main.rs`
- `desktop/src-tauri/capabilities/default.json`

Required behavior:

- Login against `https://hackson.catachess.com`.
- Store token locally in desktop `localStorage` for V0.7.
- List Projects and Missions through verified Work Mode APIs.
- Select one Mission to watch.
- Persist selected Project and Mission ids locally.
- Poll selected Mission detail.
- Poll new Mission events with `afterSequence`.
- Map real Mission status and latest event to cat behavior.
- Keep drag and quit reliable.
- Double-click the cat or bubble to open the Hackson website.
- Provide a compact `Site` action on the login panel to open the web login page.
- Show signed-out, no-Mission, offline, and stale states clearly.
- Do not create Missions or execute Work Mode commands.

Exit criteria:

- `npm run build` passes.
- `npm run tauri build` passes.
- User can login, select a Mission, and see the cat state change from real website data.
- If auth fails or network is unavailable, the cat shows a site-disconnected state instead of pretending to be idle.

## 6. V0.8: Auto Mission Watcher

Goal: remove the manual-selection trap. If a Mission is started on the website, the cat should discover it and react.

Likely files:

- `desktop/src/App.jsx`
- `desktop/src/domain/missionState.js`
- `desktop/src/features/mission-picker/MissionPicker.jsx`

Required behavior:

- After login, scan all Projects and their Missions.
- Rank active Missions by status and recency.
- Automatically bind only the best active Mission.
- If no active Mission exists, clear the watched Mission and show `No active work`.
- If multiple active Missions exist, show the primary Mission title plus the active count in the pet bubble.
- Keep manual selection available from the cat.
- Periodically rescan so a new website-started Mission can be discovered without using a picker.
- Periodic rescan must also run while an active Mission is selected, so a new `running` Mission can replace an older `paused_retryable` or `blocked` Mission.
- When a selected Mission leaves active status, stop pointing at it and rescan for another active Mission.
- Show watched Mission title in the cat panel.

Exit criteria:

- Starting a Mission on the website can be discovered by clicking `Sync` or by periodic rescan.
- Starting a new `running` Mission after an older paused Mission exists makes the cat switch to the new Mission automatically.
- The user no longer has to know which Project contains the active Mission before the cat can react.
- With zero active Missions, the pet says `No active work` instead of showing a stale draft, completed, or failed Mission.
- With two or more active Missions, the pet bubble includes the primary Mission title and an additional active count.

## 6.1. V0.8.1: Environment-Aware Watcher Fix

Goal: make the cat watch the same Hackson environment the maintainer is actually using.

Problem this fixes:

- The desktop app can successfully run while watching `https://hackson.catachess.com`, but the maintainer may be testing a local or tunneled Hackson instance.
- When the website and Desktop Pet point at different API origins, the cat looks idle or signed out even though Work Mode is running somewhere else.
- HTML fallback responses must not surface as raw JSON parse errors such as `desktop_api_json_invalid`.

Likely files:

- `desktop/src/api/client.js`
- `desktop/src/App.jsx`
- `desktop/src/features/auth/AuthPanel.jsx`
- `desktop/src/features/mission-picker/MissionPicker.jsx`
- `desktop/src-tauri/src/main.rs`
- `desktop/src/styles.css`

Required behavior:

- Default API source should be `Auto`.
- `Auto` should try local Hackson first, then fall back to the public domain.
- User can switch API source from the cat panel without editing files.
- Site open action should open the matching frontend source when possible.
- Native HTTP should allow only explicit Hackson API origins.
- Non-JSON API responses should map to a readable desktop state, not a raw parser error.
- The cat state must be derived from the selected source's Work Mode APIs only.

Exit criteria:

- Login panel shows a readable source selector.
- Running against a missing local API falls back to the public source without crashing.
- Non-JSON responses show `Site session unavailable` or a similarly product-readable message.
- `npm run build` and `npm run tauri build` pass.

## 6.2. V0.8.2: Browser Handoff Login

Goal: remove the desktop login form and let the browser account session authorize the desktop pet.

Product decision:

- The desktop pet must not ask for email or password.
- The desktop pet must not try to read browser cookies or localStorage.
- Double-clicking the cat opens Hackson in the browser with a short-lived desktop handoff code.
- After the user logs in or is already logged in, the website binds that handoff code to the authenticated user.
- The desktop pet polls the handoff code, receives a normal JWT once, stores it locally, and starts the Work Mode watcher.

Likely files:

- `backend/users/schemas.py`
- `backend/users/repository.py`
- `backend/users/service.py`
- `backend/users/routes.py`
- `backend/users/tests/test_user_service.py`
- `backend/users/tests/test_user_routes.py`
- `frontend/src/App.jsx`
- `frontend/src/api/users.js`
- `desktop/src/App.jsx`
- `desktop/src/api/users.js`
- `desktop/src/features/pet/PetWindow.jsx`
- `desktop/src/styles.css`
- `desktop/src-tauri/tauri.conf.json`

Required behavior:

- Signed-out desktop state shows only the cat and a small bubble.
- No desktop email/password inputs.
- No visible top `x`, `+`, or `-` controls.
- Double-click cat or bubble starts browser handoff login.
- Website consumes `desktopAuth` query param after normal auth.
- Handoff code is one-time and short-lived.
- Desktop app automatically starts scanning Missions after claim succeeds.
- If the handoff is still pending, the cat stays in a waiting/login state without noisy controls.

Exit criteria:

- Backend service and route tests cover bind, claim, one-time use, and pending state.
- Frontend build passes.
- Desktop build and Tauri package pass.
- Screenshot shows no bottom login panel and no top window controls.
- Public `8145` serves `POST /api/users/desktop-handoff/claim` as `200`, not frontend fallback `405`.
- Browser smoke covers both already-logged-in and login-then-bind `desktopAuth` flows.

## 7. Loop 1: Runtime Spike

Goal: prove the desktop shell.

Likely files:

- `desktop/README.md`
- `desktop/package.json`
- `desktop/src/README.md`
- `desktop/src-tauri/README.md`

Required behavior:

- Start a Tauri window with React + Vite.
- Render a tiny always-on-top pet window.
- Support drag, quit, and reopen.
- Verify macOS transparent or shaped-window behavior.

Exit criteria:

- Local desktop window runs without backend dependency.
- User can close and quit reliably.

## 8. Loop 2: API Client And Auth

Goal: login and read current user.

Likely files:

- `desktop/src/api/README.md`
- `desktop/src/api/client.js`
- `desktop/src/api/users.js`
- `desktop/src/features/auth/README.md`

Required behavior:

- Login against the public Hackson service.
- Store token locally.
- Read `/api/users/me`.
- Sign out clears token.

Exit criteria:

- Auth works after app restart.
- Token is not logged.

## 9. Loop 3: Mission Picker

Goal: choose one Work Mode Mission to watch.

Likely files:

- `desktop/src/api/work.js`
- `desktop/src/features/mission-picker/README.md`

Required behavior:

- List Projects.
- List Missions for a selected Project.
- Select one Mission.
- Persist selected Mission id locally.
- Clear selection.

Exit criteria:

- User can select an existing Mission without using browser dev tools.

## 10. Loop 4: Mission Watcher

Goal: poll Work Mode events and keep local state current.

Likely files:

- `desktop/src/domain/README.md`
- `desktop/src/domain/missionState.js`
- `desktop/src/features/pet/README.md`

Required behavior:

- Fetch Mission detail.
- Poll events with `afterSequence`.
- Merge events by id.
- Stop fast polling on terminal states.
- Back off on network errors.

Exit criteria:

- A running Mission updates the desktop client from real events.

## 11. Loop 5: Pet State Reducer

Goal: deterministic event-to-pet-state mapping.

Likely files:

- `desktop/src/domain/petState.js`

Required tests:

- Draft Mission maps to `idle`.
- `MODEL_TURN_STARTED` maps to `thinking`.
- `WORK_WINDOW_OPENED` maps to `delegating`.
- `PRODUCT_UPDATED` maps to `writing`.
- `USER_INPUT_REQUESTED` maps to `waiting`.
- `MISSION_COMPLETED` maps to `done`.
- API failure maps to `offline`.

Exit criteria:

- State mapping matches `state_mapping.md`.

## 12. Loop 6: Pet UI

Goal: render a polished small desktop presence.

Likely files:

- `desktop/src/features/pet/PetWindow.jsx`
- `desktop/src/features/pet/PetPopover.jsx`
- `desktop/src/styles.css`

Required behavior:

- Render state label and visual state.
- Click opens compact popover.
- Popover can open Work Console.
- Popover can open latest Product path or Mission page when URL routing supports it.

Exit criteria:

- UI is readable at small size.
- No text overflow.
- No noisy explanatory copy.

## 13. Loop 7: Notifications And Tray

Goal: add desktop-native controls.

Likely files:

- `desktop/src/features/tray/README.md`
- Tauri command and capability files.

Required behavior:

- Notify only on `waiting`, `paused`, `done`, `failed`.
- Avoid repeated notifications for the same event sequence.
- Tray menu supports Open, Select Mission, Pause alerts, Sign out, Quit.

Exit criteria:

- 30-minute watch smoke does not spam notifications.

## 14. Loop 8: Packaging

Goal: create a local downloadable build.

Required behavior:

- Build desktop app.
- Run install or local bundle.
- Confirm login, Mission selection, event polling, notification, quit.

Exit criteria:

- macOS local bundle works.
- Packaging limitations are documented before public distribution.

## 15. V1.0 Acceptance Smoke

Manual smoke:

1. Start a real Work Mode Mission in the web app.
2. Open Desktop Pet.
3. Login.
4. Select the Mission.
5. Start or resume Mission.
6. Confirm state changes during model turn, tool call, delegate window, Product update, and completion.
7. Confirm clicking opens Work Console.
8. Confirm terminal notification fires once.
9. Confirm quit stops polling.

Automated smoke should cover reducer logic, polling merge logic, and API error handling before native UI automation is added.
