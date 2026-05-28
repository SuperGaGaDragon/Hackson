## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 1: Desktop Runtime Choice

## Question

Should Desktop Pet use Tauri or Electron?

## Recommendation

Use Tauri for V1.

The repository already uses React + Vite, and Desktop Pet needs a lightweight shell, native window controls, tray, and notifications. Tauri fits that shape.

## Risk

Transparent always-on-top desktop pet windows can have platform-specific behavior. macOS transparent windows may constrain App Store distribution.

## Decision Rule

Keep Electron as fallback only if the Tauri spike cannot deliver:

- stable always-on-top window
- drag behavior
- tray/menu
- notifications
- acceptable transparent or shaped-window presentation

## Acceptance Probe

Build V0.1 before any backend work:

- open a tiny window
- keep it on top
- drag it
- hide and show it
- quit it
- verify it does not trap input
