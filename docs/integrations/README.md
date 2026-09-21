# Integrations

## Model providers

Pluggable via `lifekit.llm` (provider protocol): **Ollama** is the default; **OpenRouter** works via the `OPENROUTER_API_KEY` env var only. Config resolution: CLI flags > env vars (`LIFEKIT_PROVIDER`/`LIFEKIT_MODEL`) > `~/.lifekit/config.json` (provider/model only, never keys) > defaults (`ollama`/`qwen3.6:latest`).

- Spec archived: `../../openspec/archives/llm-provider-config/`
- Assumption A21 in [product/ASSUMPTIONS.md](../product/ASSUMPTIONS.md)
- Long-running evals run against the home workstation's Ollama over Tailscale (A22) — never on a shared VM, and OpenRouter is free-models-only when used

## What's deliberately not integrated

No messaging channels (WeChat/Telegram/Slack), no calendar or todo wiring for exercises, no cloud sync, no auth, no multi-tenant anything. Phone access today is the workstation's tailnet IP in a browser — no additional integration needed. See Step 0 in [the roadmap](../product/ROADMAP.md) and A24.

If an integration is ever proposed, it starts as an [`intent/`](../../intent/) like any other change.
