## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Store the Tauri native shell for Desktop Pet.
- 架构思路
  - Configure a small transparent desktop window for the V0.5 pet.
  - Keep native commands minimal: window movement and clean quit only.
  - Do not add backend, filesystem, shell, or screen-control permissions in V0.5.

## folder structure
|-README.md Tauri shell guide
|-Cargo.toml Rust package and Tauri dependency config
|-build.rs Tauri build script
|-tauri.conf.json Tauri application and window configuration
|-src/ Rust shell source
|-capabilities/ Tauri permission capability files
|-icons/ temporary app icons generated from the V0.5 cat idle image

## 代办
- Add tray capability after V1 Mission watching begins.
