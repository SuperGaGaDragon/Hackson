## header
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Lst Modified by: Codex

## brief intro
- goal for this folder.
  - Tests for context construction, recipes, transition context, and context packages.
- 架构思路
  - Test context behavior without databases or model providers.
  - Keep context deterministic so prompt package changes are easy to review.

## folder structure
|-README.md tests folder guide
|-test_context_builder.py context builder behavior tests

## 代办
- Add focused tests for token compaction and prompt package hashes.
