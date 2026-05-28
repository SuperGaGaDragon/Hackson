## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Public Routes

## 1. Purpose

This document defines Hackson public website paths that should be stable enough for users, browser bookmarks, and the Desktop Pet.

The root domain can still open the default product workspace, but user-visible features should no longer depend on one undifferentiated `https://hackson.catachess.com/` URL.

## 2. Route Contract

| Path | Product Surface | Auth | Behavior |
| --- | --- | --- | --- |
| `/` | Idle | Required | Opens the authenticated Idle workspace, or Auth if signed out. |
| `/idle` | Idle | Required | Opens Idle directly. |
| `/companion` | Companion chat | Required | Opens the Companion chat workspace. |
| `/work` | Work | Required | Opens Work project list. |
| `/work_project/:projectId` | Work project detail | Required | Opens Work and preselects the Project when the Project belongs to the user. |
| `/work_mission/:missionId` | Work Mission detail | Required | Opens Work and preselects the Mission when discoverable through the user's Projects. |
| `/me` | Settings | Required | Opens Me. |
| `/download/companion` | Desktop Pet download page | Public | Shows the Mac Desktop Companion download and setup guide. |
| `/assets/downloads/hackson-pet-mac-arm64.zip` | Desktop Pet app artifact | Public | Downloads the current Mac Apple Silicon alpha build through the existing static asset mount. |

## 3. Product Rules

- `Companion` in `/companion` means the web Companion chat, not the installer.
- Desktop Pet distribution uses `/download/companion` because users think of the pet as a companion surface.
- Deep links should update browser history when the user changes top-level views.
- Auth flows must preserve the requested route after login when possible.
- Unknown paths should fall back to Idle rather than showing a blank page.
- Work Project and Mission deep links are best-effort. If the id cannot be found, Work opens the project list and shows a short error.

## 4. Download Page Rules

- The page is public so a signed-out user can install first.
- The page must say `Mac alpha` and `Apple Silicon` until other builds exist.
- The page must not imply notarization or App Store distribution before those are real.
- The primary call to action is a direct `.app.zip` download.
- Download artifacts live under `frontend/dist/assets/downloads/` at release time, because the public backend already serves `/assets/*` without needing a backend service restart.
- The setup guide is short:
  - Download.
  - Unzip.
  - Move app to Applications or open it directly.
  - Double-click the cat to sign in through the browser.
  - Start Work on the website and watch the cat reflect progress.

## 5. Release Gate

- `npm run build` passes in `frontend/`.
- The built frontend contains `dist/assets/downloads/hackson-pet-mac-arm64.zip`.
- Local browser smoke verifies `/download/companion`, `/idle`, `/companion`, `/work`, `/me`, and a Work project path render without a blank page.
- Public smoke verifies `https://hackson.catachess.com/download/companion` and `https://hackson.catachess.com/assets/downloads/hackson-pet-mac-arm64.zip` return `200`.
