## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store the Hackson Desktop Pet Tauri application.
- 架构思路
  - V0.8 connects the polished local cat to Hackson Work Mode website state.
  - V0.8.1 makes the watched Hackson source explicit so local and public environments do not get mixed.
  - V0.8.2 removes desktop password entry and uses browser handoff login.
  - Keep desktop runtime separate from the existing web frontend.
  - Use React + Vite for the pet UI and Tauri for the native desktop shell.
  - Use verified Hackson APIs and keep desktop-only behavior separate from backend execution.

## folder structure
|-README.md desktop app folder guide
|-package.json npm scripts and desktop frontend dependencies
|-package-lock.json locked npm dependency graph
|-index.html Vite HTML entry
|-vite.config.js Vite configuration for the desktop app
|-src/ React desktop pet source folder
|-src-tauri/ Tauri native shell folder

## 代办
- Add native notifications after Mission watching is stable.
- Add tray and native notifications after Mission watching is implemented.
