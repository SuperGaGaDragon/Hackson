## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-10-20
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store React application source for the Parallax public home and Hackson product frontend.
- 架构思路
  - `App.jsx` owns the public home, temporary-user handoff, authenticated routing, and app shell.
  - `main.jsx` mounts the React app.
  - `styles.css` defines the full product visual system for the prototype.
  - `light-theme.css` applies the authenticated Parallax light product theme after the base component layout rules.
  - `api/` owns HTTP calls to verified APIs.
  - `domain/` owns message and Agent display mapping.
  - `features/` owns product flows for Auth, Idle, Chat, and Me.
  - `Me` owns editable settings, prompt logs, and memory controls.
  - `shared/` owns reusable UI components.
  - Browser-to-desktop handoff is completed in `App.jsx` after normal auth so Desktop Pet can authorize without a desktop password form.
  - User-facing brand labels should say Parallax; legacy Hackson names remain in internal API keys, filenames, and deployment docs.
  - Keep copy short and keep mode boundaries visible.

## folder structure
|-README.md source folder guide
|-App.jsx app shell and authenticated route switching
|-main.jsx React root mount
|-styles.css frontend visual system and responsive layout
|-light-theme.css semantic light palette and authenticated product surface overrides
|-api/ verified backend API client modules
|-domain/ frontend domain mapping helpers
|-features/ product feature modules
|-shared/ reusable UI components

## 代办
- Add streaming support if backend model runtime exposes it.
