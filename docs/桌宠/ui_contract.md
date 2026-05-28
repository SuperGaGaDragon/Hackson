## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Desktop Pet UI Contract

## 1. Purpose

This document defines the V1 Desktop Pet surfaces and interaction rules.

The UI must be compact, readable, and quiet. It follows `agents/frontend_restrictions.md`.

## 2. Surfaces

V1 surfaces:

- Pet window.
- Click popover.
- Tray menu.
- Native notification.

The Work Console remains the full detail UI.

## 3. Pet Window

Required behavior:

- Always-on-top by default.
- Draggable.
- Small footprint.
- No large text blocks.
- No nested cards.
- No model logs.
- No raw JSON.
- Clear state through pose, icon, and one short label.

Required controls:

- Click opens popover.
- Secondary click opens tray-like quick menu where platform allows.
- Drag moves the pet.
- Quit is available through tray/menu.

## 4. Popover

Popover content:

- Mission title.
- Current state.
- Latest event title.
- Latest event time.
- Latest Product title when available.
- Buttons: `Open`, `Product`, `Pause alerts`.

Popover must not become a full Work Console clone.

## 5. Tray Menu

Tray menu items:

- Open Hackson.
- Select Mission.
- Pause alerts.
- Sign out.
- Quit.

Tray menu should be usable even if the pet window is hidden.

## 6. Native Notifications

Allowed notifications:

- User input needed.
- Mission paused.
- Mission completed.
- Mission failed.

Notification content:

- Title: Mission title or short product name.
- Body: one sentence with current state.
- Action: open Work Console or show popover.

Do not include full private artifact content in notification body.

## 7. Mission Picker

Mission picker can be a compact app panel in V1.

Required behavior:

- List active or recent Projects.
- List Missions for selected Project.
- Prefer running, waiting, paused, and recently completed Missions.
- Show terminal state clearly.
- Let user clear selection.

V1 does not need full Project or Mission creation. Creation remains in the web app.

## 8. Visual Asset Direction

V1 should use simple generated bitmap or lightweight animated asset states.

The visual system must communicate work states without requiring text:

- thinking
- working
- delegating
- writing
- reviewing
- waiting
- done
- failed

Do not start with complex character customization. State clarity is more important.

## 9. Accessibility

Required:

- State text is available in the popover.
- Notifications can be paused.
- Animations should have a reduced-motion option.
- Pet should not block core desktop interactions permanently.
- Click-through mode can be considered after drag and recovery controls are reliable.

## 10. Copy Rules

Allowed short labels:

- Idle
- Thinking
- Working
- Delegate
- Writing
- Review
- Waiting
- Paused
- Done
- Failed
- Offline

Avoid:

- Explaining how the product works in the UI.
- Long motivational text.
- Raw event names unless shown in developer diagnostics.

## 11. Diagnostics

V1 developer diagnostics may show:

- backend base URL
- selected Mission id
- latest event sequence
- polling status
- last API error

Diagnostics must be hidden by default and must not include secrets.
