## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex

# Issue 22: Web Search Query Fallback And Effective Query Visibility

## Problem

Public target-machine runs showed `web_search` returning `search_no_results` for research tasks even though shorter searches for the same topic produced valid results.

Observed case:

- Long query with many scholarly terms returned no DuckDuckGo Lite results.
- Query with `site:` terms generated from `allowedDomains` also returned no results.
- Short query `Haitian Revolution historiography` returned valid sourced results on the same target machine.

This is a provider/query-shaping failure, not a model-provider failure.

## Decision

`web_search` provider implementations MUST perform bounded query fallback before returning `search_no_results`.

Fallback order:

1. Search the requested query with provider-native domain syntax when configured.
2. If no results, search the requested query without provider-native domain syntax and apply backend post-filtering.
3. If no results, search a compacted query without provider-native domain syntax and apply backend post-filtering.

Domain constraints remain hard constraints for returned results:

- `blockedDomains` MUST always be excluded.
- `allowedDomains`, when non-empty, MUST be respected by backend post-filtering.
- The provider MUST NOT return disallowed domains simply to avoid an empty result set.

The Lead context SHOULD still encourage concise queries. Provider fallback is a safety net, not a reason to pack many topics and domain restrictions into one search request.

## Product Contract

The Lead still calls one stable tool: `web_search`.

The backend may run multiple provider attempts internally, but this MUST be invisible as additional model turns. The UI and Lead observation should show the final effective query and whether fallback was applied.

Successful observations SHOULD include:

```json
{
  "query": "requested query",
  "effectiveQuery": "query that produced the returned results",
  "fallbackApplied": true,
  "fallbackReason": "no_results_after_primary_query",
  "attemptCount": 3
}
```

Failed observations SHOULD include the same bounded diagnostics when fallback was attempted.

## Acceptance

- Target-machine probe for a long Haitian Revolution query returns results through fallback.
- Target-machine probe for a domain-constrained Haitian Revolution query returns allowed-domain results through post-filtering.
- `blockedDomains` results are excluded after fallback.
- Existing `WEB_SEARCH_COMPLETED` and `WEB_SEARCH_FAILED` events remain stable.
- Work Mode tests cover parser, fallback, and executor payload fields.

## Follow-Up

- Add a paid or official search API provider if DuckDuckGo Lite becomes unstable.
- Add source quality scoring only after fallback behavior is stable in public smokes.
