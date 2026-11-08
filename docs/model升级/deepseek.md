## header
Created at: 2026-11-08
Created by: Codex
Last Modified at: 2026-11-08
Last Modified by: Codex

# DeepSeek Runtime Configuration

## brief intro
- goal for this file.
  - Define the production migration from a failed Codex CLI runtime to DeepSeek's OpenAI-compatible API.
- 架构思路
  - Keep `model_runtime/` provider-agnostic.
  - Store credentials only in the target machine's ignored private `.env`.
  - Verify the provider through an isolated runtime probe before changing the public service.
  - Preserve a rollback copy of the previous environment configuration.

## production contract
| Setting | Value |
| --- | --- |
| Provider | `openai_compatible` |
| Base URL | `https://api.deepseek.com` |
| API mode | `chat_completions` |
| Model | `deepseek-flash` |
| Token limit field | `max_tokens` |
| Credential | Target-only `HACKSON_MODEL_API_KEY`; never Git, logs, or command arguments |

`deepseek-flash` is the initial shared runtime for Idle, Companion, and Work because it is the current official low-latency OpenAI-compatible model. A later Work-specific model policy may use `deepseek-v4-pro` after separate quality, latency, and cost acceptance.

## compatibility rule
DeepSeek Chat Completions accepts `max_tokens`. Hackson's generic OpenAI path previously emitted `max_completion_tokens`, which is not part of the DeepSeek Chat Completions contract. The runtime client must choose the correct token field from the configured upstream.

## deployment sequence
1. Reproduce the public stable error through a temporary account.
2. Verify current target runtime configuration without printing credentials.
3. Add a regression test for the DeepSeek request payload.
4. Probe DeepSeek from an isolated process using the target-only credential.
5. Back up the public target `.env`.
6. Update only `HACKSON_MODEL_PROVIDER`, `HACKSON_MODEL_BASE_URL`, `HACKSON_MODEL_NAME`, `HACKSON_MODEL_API_MODE`, and `HACKSON_MODEL_API_KEY`.
7. Confirm no active Work Mission, Work Window, or model process is running.
8. Restart only `hackson-domain-8145.service`; never reboot or alter host networking.
9. Verify local target runtime, public Companion, Idle, Work regression, Pages proxy, and public health.

## failure mapping
- `401` / `403`: credential invalid or unauthorized; restore previous `.env` and inspect account state.
- `400`: request compatibility or model name error; keep public service on the previous config until the payload test is fixed.
- `402`: provider balance/billing problem; expose stable `model_unavailable`, do not retry-loop.
- `429`: expose stable `model_rate_limited` and stop frontend Auto.
- Network/timeout: preserve Work progress and use existing retryable pause semantics.

## release gate
- DeepSeek request unit test passes and proves `max_tokens` is used.
- Full backend suite passes.
- Isolated DeepSeek runtime probe returns expected content with provider/model metadata.
- Public model probe changes from `503 model_unavailable` to `200`.
- Idle, Companion, Work, Pages health, and Hackson health remain functional.
- No credential appears in Git diff, logs, process arguments, or assistant output.

## rollback
- Keep the timestamped pre-change `.env` backup on the target machine.
- If production verification fails, restore the backup and restart only `hackson-domain-8145.service` after the same active-work safety check.
- Do not restart the host, SSH, Tailscale, networking, or any power target.

## 代办
- Evaluate `deepseek-v4-pro` for Work-only long-form quality after the shared runtime is stable.
