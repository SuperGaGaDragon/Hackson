## header
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Lst Modified by: Codex

# Issue 9: Derived Worker Backlog And Memory Freshness

## 1. Self Grill

Q: Why did public smoke fail after the Me redesign?

A: The public database had thousands of old `pending` derived jobs. The smoke runner processed global FIFO batches, so the current smoke user's new summary, memory, diary, and relationship jobs stayed behind unrelated historical backlog.

Q: Why is this a product issue, not just a test issue?

A: The user expectation is cross-dialogue continuity: the product should learn from usage. If derived jobs accumulate without a reliable consumer, the UI can claim Memory exists while new conversations do not become more familiar.

Q: What is the risk in a naive fix?

A: A one-off script that only makes smoke pass would hide the real issue. The production runtime needs a bounded worker loop, and tests need a scoped way to process a current user/conversation without draining unrelated jobs.

Q: Should chat wait for this worker?

A: No. Derived work remains best-effort and must not block visible replies. The worker should process small batches in the background and mark failures without breaking chat.

## 2. Decision

- Add repository/service support for scoped pending job reads by `user_id` and optional `conversation_id`.
- Keep default worker processing FIFO for production fairness.
- Add a process-local background derived worker loop controlled by platform env.
- Enable that loop in production by default with conservative batch and interval settings.
- Each background loop pass should process both old FIFO jobs and a small latest-pending freshness lane so new users are not starved by historical backlog.
- Let smoke process only the current smoke user's jobs so historical backlog cannot invalidate current behavior.
- Keep worker failures recorded on jobs, not raised into chat paths.

## 3. Acceptance

- Worker tests cover scoped pending job processing.
- App startup can enable the process-local derived worker loop through settings.
- Background loop tests cover the freshness lane.
- Public smoke can create a fresh user, process that user's derived jobs, and observe summary, relationship memory, companion memory, and diary outputs.
- New relationship memory uses at least two Agent source messages and never writes generic filler.
- Old generic relationship memory is hidden from user-facing reads.
