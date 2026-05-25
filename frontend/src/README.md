## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store React application source for the Hackson frontend.
- 架构思路
  - `App.jsx` owns top-level authenticated routing and app shell.
  - `main.jsx` mounts the React app.
  - `styles.css` defines the full product visual system for the prototype.
  - `api/` owns HTTP calls to verified APIs.
  - `domain/` owns message and Agent display mapping.
  - `features/` owns product flows for Auth, Idle, Chat, and Me.
  - `shared/` owns reusable UI components.
  - Keep copy short and keep mode boundaries visible.

## folder structure
|-README.md source folder guide
|-App.jsx app shell and authenticated route switching
|-main.jsx React root mount
|-styles.css frontend visual system and responsive layout
|-api/ verified backend API client modules
|-domain/ frontend domain mapping helpers
|-features/ product feature modules
|-shared/ reusable UI components

## 代办
- Add streaming support if backend model runtime exposes it.
