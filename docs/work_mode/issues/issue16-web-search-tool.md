## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 16: Controlled Web Search Tool

## Problem

Work Mode can currently reason over Mission state, Products, Artifacts, and Delegate output. It cannot fetch external information when the Mission needs current facts, niche references, or source-backed research.

Without a controlled search tool, the Lead may either hallucinate facts or ask the user for information that the system could safely retrieve.

## Decision

Add `web_search` as a Lead-visible read-only tool in V1.0.5.

`web_search` is a backend-owned search wrapper. It is not browser automation, shell execution, file access, or direct Codex CLI control.

The model-visible contract MUST remain stable even if the backend search provider changes.

## Self-Grilled Decisions

### Should `web_search` be available before computer-control tools?

Yes.

Search is read-only and fits the V1.0 text Mission loop. It gives the Lead better evidence without granting filesystem, shell, browser, or computer-control power.

### Should Codex CLI be exposed as the search tool?

No.

Codex CLI MAY be an internal `SearchProvider` only after it proves it can return the same structured result schema. The Lead must still see and call only `web_search`.

### Should search results directly become Product content?

No.

Search results are observations. The Lead must call `work_product` later to create or revise user-visible deliverables.

### Should search create Artifacts?

Optional.

V1.0.5 MUST persist a visible event. It MAY also persist a Research Artifact when source trails need to appear in Product lineage. The first implementation can start with events and observations, then add Research Artifacts if UI/lineage needs it.

### Should search be automatic?

No.

The model decides when to call `web_search`. The backend must not hard-code that research tasks always search.

## Tool Schema

```json
{
  "reason": "string",
  "query": "string",
  "searchType": "general|news|technical|reference",
  "maxResults": 5,
  "recencyDays": 30,
  "allowedDomains": ["string"],
  "blockedDomains": ["string"]
}
```

## Result Schema

```json
{
  "tool": "web_search",
  "status": "ok",
  "query": "string",
  "searchType": "general|news|technical|reference",
  "results": [
    {
      "title": "string",
      "url": "string",
      "source": "string",
      "snippet": "string",
      "publishedAt": "string|null"
    }
  ],
  "truncated": false,
  "provider": "string"
}
```

## Constraints

- MUST be read-only.
- MUST emit `WEB_SEARCH_COMPLETED` on success.
- MUST emit `WEB_SEARCH_FAILED` or return a rejected observation on failure.
- MUST return bounded snippets, not full web pages.
- MUST expose source URLs in UI.
- MUST respect `maxResults`.
- MUST cap `maxResults` at `10`.
- MUST NOT modify Product content.
- MUST NOT finish Mission.
- MUST NOT ask Delegate to browse.
- MUST NOT expose provider secrets.
- MUST NOT expose raw provider logs in Lead context.

## Provider Interface

Backend SHOULD implement a provider boundary:

```text
WebSearchTool
  -> SearchProvider.search(request)
  -> SearchResult[]
```

Provider candidates:

- HTTP search API provider.
- Model-native search provider.
- Constrained Codex CLI search provider.
- Fake deterministic provider for tests and smoke.

Every provider MUST return the same normalized result shape.

## UI Requirements

Progress:

- Show `Search` row with query and result count.
- Expanded row shows source links and bounded snippets.
- Failed row shows stable error code and retryability.

Diagnostics:

- Show raw structured payload.

Product:

- Product content may cite URLs from search results.
- Research Artifact display is optional for first implementation.

## Acceptance

- Tool protocol accepts valid `web_search` and rejects invalid shape.
- Lead context lists `web_search` only when implementation is enabled.
- Executor persists `WEB_SEARCH_COMPLETED` with bounded results.
- Executor handles provider timeout/rate-limit/unavailable with stable failure codes.
- A loop smoke proves the Lead can call `web_search`, observe results, then call `work_product`.
- Browser smoke shows the search row in Progress with source links.
- Target-machine smoke passes before public deployment.

## Follow-Up

- Add Research Artifacts if source trails need Product lineage.
- Keep provider fallback behavior aligned with `issue22-web-search-query-fallback.md`.
- Add source quality scoring only after result normalization is stable.
