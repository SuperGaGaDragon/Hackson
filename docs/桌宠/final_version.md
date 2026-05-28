## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Desktop Pet Final Version Roadmap

## 1. Product North Star

Desktop Pet is the ambient work presence for Hackson Work Mode.

The user gives Hackson a Mission. The web Work Console remains the full control room. Desktop Pet stays on the desktop and shows that the Agent runtime is alive, what kind of work is happening, and when the user should return.

The product must make background Agent work legible without forcing the user to watch the browser.

Core loop:

```text
User starts or resumes a Work Mode Mission
  -> Desktop Pet watches the selected Mission
  -> Work Mode events map to pet state
  -> pet animates quiet progress
  -> pet escalates only when user action matters
  -> click opens latest Product or Work Console
```

## 2. V1 Product Promise

V1.0 MUST be a Work Mode progress pet.

V1.0 MUST NOT be a general chatbot, screen-control agent, file-control agent, or independent task executor.

V1.0 promises:

- Bind to a Hackson account.
- Select one active Work Mode Mission.
- Reflect current Mission state from persisted Work Mode events.
- Show quiet desktop presence while the Mission is running.
- Escalate when the Mission is waiting, paused, completed, or failed.
- Open the web Work Console for full control.
- Open or preview the latest Product when a Product exists.

## 3. Hard Product Constraints

- Desktop Pet MUST NOT create its own agent identity.
- Desktop Pet MUST reuse the authenticated user's two Agent profiles.
- Desktop Pet MUST NOT call model providers directly.
- Desktop Pet MUST NOT execute shell, file, browser, Codex CLI, or computer-control tools.
- Desktop Pet MUST NOT mutate Mission state except through verified Work Mode APIs.
- Desktop Pet MUST NOT expose raw model logs as normal user content.
- Desktop Pet MUST treat Work Mode persisted state as source of truth.
- Desktop Pet MUST degrade to a disconnected state when auth or network fails.
- Desktop Pet MUST avoid constant interruption; only action-worthy states can notify.
- Desktop Pet MUST provide an obvious quit and pause-notifications control.

## 4. User Value

Desktop Pet solves four Work Mode problems:

- Visibility: background Agent work no longer feels like a frozen webpage.
- Trust: the user can see whether the Agent is thinking, delegating, writing, retrying, or done.
- Attention: the user can leave the console and return only when needed.
- Control: the user has a small desktop handle for opening the Mission, pausing notifications, and checking the latest Product.

The product value is not cuteness alone. The pet is a body for Agent labor.

## 5. Experience Principles

- Calm by default.
- Minimal text.
- State before detail.
- Notification only when useful.
- Web console for complex control.
- Desktop pet for presence, glanceability, and return points.

## 6. V1 Surface

V1 has four surfaces:

- Pet window: small transparent or shaped always-on-top window.
- Popover: compact Mission detail opened by click.
- Tray menu: account, Mission selection, notification mode, open console, quit.
- Native notification: only for waiting, paused, completed, or failed states.

## 7. Initial State Vocabulary

V1 pet states:

- `idle`: no Mission selected or Mission is draft.
- `thinking`: Lead Agent model turn started.
- `working`: model turn heartbeat or tool execution in progress.
- `delegating`: Delegate work window is running.
- `writing`: Product or Artifact is being created.
- `reviewing`: Product inspection or review is happening.
- `retrying`: transient runtime retry is underway.
- `waiting`: user input is required.
- `paused`: retryable pause or blocked state.
- `done`: Mission completed.
- `failed`: Mission failed.
- `offline`: API, auth, or network unavailable.

See `state_mapping.md`.

## 8. Runtime Choice

V1 SHOULD use Tauri with the existing React + Vite frontend stack.

Rationale:

- The repository already uses React + Vite.
- Desktop Pet needs a lightweight desktop shell, tray, always-on-top window, and native notifications.
- The app should eventually ship as a downloadable desktop app without bundling a full browser runtime when avoidable.

Electron remains fallback only if Tauri transparent-window or tray behavior blocks a polished V1 on target platforms.

## 9. Backend Strategy

V1 SHOULD start with existing verified APIs:

- `/api/users/login`
- `/api/users/me`
- `/api/work/projects`
- `/api/work/projects/{projectId}/missions`
- `/api/work/missions/{missionId}`
- `/api/work/missions/{missionId}/events`

V1 MAY add a thin dashboard API only if repeated polling across projects becomes wasteful:

```text
GET /api/work/desktop/summary
```

That API would return active Missions and latest event summaries. It must be documented in root `api.md` only after verification.

## 10. Non-Goals

V1 does not include:

- Idle conversation.
- Companion chat.
- Voice.
- Screen reading.
- File reading.
- Computer control.
- Arbitrary command execution.
- Multiple simultaneous pets.
- A plugin marketplace.
- User-created animation scripting.

These are later versions only after V1 proves Work Mode presence.

## 11. Release Gate

V1.0 is releasable when:

- A user can install or run the desktop app locally.
- Login works against the verified public Hackson service.
- The user can select an active Mission.
- The pet changes state from real Work Mode events.
- Waiting, paused, completed, and failed states produce controlled notifications.
- Clicking the pet opens Mission detail or the web Work Console.
- The app has quit, hide, and pause-notification controls.
- A 30-minute Mission watch smoke shows no runaway polling, notification spam, or stale state after Mission completion.
