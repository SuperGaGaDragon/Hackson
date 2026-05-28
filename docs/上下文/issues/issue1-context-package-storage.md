## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 1: Context Package Storage

## Decision

Context packages use an independent `context_packages` persistence boundary.

Assistant message metadata stores only lookup and safe summary fields:

- `context_package_id`
- `prompt_hash`
- `token_estimate`
- model metadata

## Risk

If package metadata is embedded only in assistant messages, implementation becomes hard to query, hard to expire, and hard to separate from message history.

If full prompt text is stored directly on messages, prompt retention and deletion become coupled to the Raw Message source of truth.

## Constraints

- Raw Messages remain the historical source of truth.
- Context Package records are diagnostic artifacts.
- Full prompt text lives only on the package record and only when Full Prompt Logging is enabled.
- Deleting retained prompt logs must not delete Raw Messages or package metadata.

## Required Tests

- Creating an assistant reply stores a package record.
- Assistant message metadata references the package id.
- Prompt hash matches the persisted package.
- Deleting prompt logs removes prompt text but preserves package metadata and Raw Messages.
