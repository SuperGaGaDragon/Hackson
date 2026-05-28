## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store React source for the local Desktop Pet prototype.
- 架构思路
  - `App.jsx` owns the shell composition.
  - `main.jsx` mounts the React app.
  - `styles.css` owns the tiny transparent pet window styling.
  - `api/` owns desktop HTTP calls through Tauri native commands.
  - `domain/` owns local pet state timing and labels.
  - `features/` owns React surfaces for the pet.
  - `assets/` stores temporary bundled cat images.
  - Keep copy short and controls minimal.

## folder structure
|-README.md desktop React source guide
|-App.jsx V0.5 cat state UI and local movement loop
|-main.jsx React root mount
|-styles.css desktop pet visual styling
|-api/ desktop API client modules
|-domain/ local pet state definitions and timing rules
|-features/ desktop pet feature components
|-assets/ bundled temporary cat images

## 代办
- Split pet states into `domain/` after Work Mode event mapping is introduced.
