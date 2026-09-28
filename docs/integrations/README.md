# Integrations

## Model providers

Pluggable via `lifekit.llm` (provider protocol): **Ollama** is the default;
**OpenRouter** works via the `OPENROUTER_API_KEY` env var only. Config
resolution order, defaults, and the `lifekit config` CLI are documented as
assumption [A21](../product/ASSUMPTIONS.md).

- Long-running evals run against the home workstation's Ollama over Tailscale
  (A22) — never on a shared VM, and OpenRouter is free-models-only when used.

## What's deliberately not integrated

See the never-build list in [`.agents/intent.md`](../../.agents/intent.md).
No messaging channels, no calendar or todo wiring for exercises, no cloud
sync, no auth, no multi-tenant anything. Phone access today is the
workstation's tailnet IP in a browser — no additional integration needed.

If an integration is ever proposed, it starts as an OpenSpec proposal like any
other change.
