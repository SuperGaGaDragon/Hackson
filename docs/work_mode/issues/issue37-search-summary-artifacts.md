## header
Created at: 2026-05-29
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex

# Issue 37: Search Summary Artifacts

## Problem

`web_search` currently leaves useful source evidence mostly inside Progress events. That is enough for an audit log,
but it is not enough for product-grade research work:

- Users should not have to scan Progress to understand what was searched.
- Later Lead turns can lose old search observations from the bounded event window.
- Evaluator Runtime needs durable research material, not only scattered event payloads.
- Search results should not be silently treated as final deliverable prose.

## Self Grill

Question: Should the Lead be required to call `work_product` after every search?

Decision: No. That makes source preservation depend on model discipline, adds another schema-failure point, and can
pollute the final Product with process notes. `work_product` remains the right tool for user-facing deliverable prose,
but source preservation should be backend-owned.

Question: Should Search Summary be attached to the active deliverable Product?

Decision: No by default. Attaching every search note to the main Product can move `latestArtifactId` and summary away
from the user's deliverable, making the Product reader feel noisy and making the Lead mistake research notes for the
answer. Search Summary should live in a separate Research Notes Product unless a later tool explicitly incorporates it.

Question: Is Search Summary a verified fact summary?

Decision: No. It is a bounded evidence note based on search metadata and snippets. It should include source links,
takeaways stated cautiously, and limitations. It is auditable source material, not truth certification.

Question: Should failed searches create artifacts?

Decision: No for V1.0.x. Failed searches already have visible Progress events. Creating failed-search artifacts would
add noise without durable evidence.

## Decision

On every successful `web_search`, backend MUST create a deterministic Search Summary Artifact.

Contract:

- If no Research Notes Product exists for the Mission, create one titled `Research Notes`.
- Append one non-deliverable Artifact per successful search.
- Use `kind=notes`.
- Set `metadata.artifactRole=search_summary`.
- Set `metadata.search.query`, `effectiveQuery`, `searchType`, provider, fallback flags, truncation, and bounded result metadata.
- Emit `SEARCH_SUMMARY_CREATED` after `WEB_SEARCH_COMPLETED`.
- Return `summaryArtifactId` and `summaryProductId` in the `web_search` observation.

Product semantics:

- Search Summary Artifacts are Product History, not authoritative Deliverables.
- Search Summary MUST NOT update `deliverableArtifactId`.
- Product reader may show the Research Notes Product, but the Deliverable surface should remain `No deliverable`.
- A later `work_product` call is still required to write final user-facing prose from search evidence.

Content shape:

```text
Search intent
Query
Effective query
Useful sources
Evidence takeaways from snippets
Limitations
Suggested next action
```

## Acceptance

- Successful `web_search` creates `WEB_SEARCH_COMPLETED` and `SEARCH_SUMMARY_CREATED`.
- Successful `web_search` creates or reuses a Research Notes Product.
- Search Summary Artifact content includes query, source URLs, snippet-based takeaways, and limitations.
- Search Summary Artifact is non-deliverable and does not set `deliverableArtifactId`.
- The Lead observation includes the summary Artifact id so later turns can inspect or cite it.
- Failed search behavior stays unchanged and creates no Search Summary Artifact.
- Target-machine isolated tests pass without stopping existing services.
