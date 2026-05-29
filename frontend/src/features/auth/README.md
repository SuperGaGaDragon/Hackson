## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-29
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Own login and register UI backed by verified user APIs.
- 架构思路
  - Store token through the shared API client.
  - Unauthenticated root traffic first sees the Parallex Hackathon landing; the form is opened from Create Account or Login.
  - Quick Try uses a backend-created temporary user and session storage, not a frontend-only fake account.
  - Quick Try navigates to Work before mounting authenticated content so Idle does not briefly start background reads.
  - Public brand copy says Parallex even while the existing deployment domain and internal token keys keep Hackson names.
  - Keep copy short and expose only fields supported by the backend.

## folder structure
|-README.md auth feature guide
|-AuthPage.jsx login and register page
|-HackathonLanding.jsx QR-code landing page with Quick Try and product intro

## 代办
- Add password reset only if backend supports it.
