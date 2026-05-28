## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store Rust source for the Desktop Pet Tauri shell.
- 架构思路
  - `main.rs` owns native command registration.
  - V0.5 exposes only window movement and quit helpers.

## folder structure
|-README.md Rust source folder guide
|-main.rs Tauri app entrypoint and V0.5 native commands

## 代办
- Add platform-specific tray commands only after the pet watcher is useful.
