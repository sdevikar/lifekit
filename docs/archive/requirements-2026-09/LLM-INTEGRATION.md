# LifeKit — LLM Integration

## Provider Protocol

```python
class LLMProvider(Protocol):
    def chat(self, messages: list[dict], **kwargs) -> str: ...
    def chat_json(self, messages: list[dict], schema: type, **kwargs) -> dict: ...
```

## Providers

| Provider | Status | Auth |
|----------|--------|------|
| Ollama | Default | None (local) |
| OpenRouter | Available | `OPENROUTER_API_KEY` env var only |

## Config Resolution

```
CLI flags > env vars (LIFEKIT_PROVIDER/LIFEKIT_MODEL)
    > ~/.lifekit/config.json (provider/model only, never keys)
    > defaults (ollama/qwen3.6:latest)
```

## LLM Usage Boundaries

| Use | Allowed? | Notes |
|-----|---------|-------|
| Extraction (JSON schema) | Yes | temp 0.1, 3-attempt retry |
| Grounded chat replies | Yes | prose only |
| Briefing phrasing | Yes | LLM phrases, runtime decides |
| Scheduling decisions | **No** | Deterministic runtime owns |
| User modeling | **No** | Shallow facts only |
| Quiz/grading | **No** | Never |

## Dependencies

- Product code stays Ollama-native (`ollama.Client`, `format=<json_schema>`, temp 0.1).
- OpenRouter via stdlib `urllib` — no new dependencies.
- Long-running evals run against home Ollama over Tailscale (A22).
