## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-10-19
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Own login and register UI backed by verified user APIs.
- 架构思路
  - Store token through the shared API client.
  - Root traffic first sees the preserved Parallax public home, including when an authenticated user returns to `/`.
  - Quick Try uses a backend-created temporary user and session storage, not a frontend-only fake account.
  - Quick Try navigates to Work before mounting authenticated content so Idle does not briefly start background reads.
  - Work, Idle, Chat, and Me home links create a real temporary user only when needed, then open the requested Hackson surface.
  - Public brand copy says Parallax while internal token keys and backend infrastructure keep Hackson names.
  - Keep copy short and expose only fields supported by the backend.

## folder structure
|-README.md auth feature guide
|-AuthPage.jsx login and register page
|-HackathonLanding.jsx preserved Parallax public home with product entry handoff

## 代办
- Add password reset only if backend supports it.
