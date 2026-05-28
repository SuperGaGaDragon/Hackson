## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store the local Desktop Pet UI components.
- 架构思路
  - `PetWindow.jsx` renders the complete V0.6 pet surface.
  - V0.8.2 keeps the pet control-free: double-click opens or authorizes the website, while drag remains on the cat and bubble.
  - V0.8.3 lets the bubble expand into a compact read-only Progress glance without adding Work Mode controls.
  - Keep animation state small enough for the tiny desktop window.

## folder structure
|-README.md pet feature folder guide
|-PetWindow.jsx polished local cat pet surface

## 代办
- Split popover and controls into separate files if Mission detail is added.
