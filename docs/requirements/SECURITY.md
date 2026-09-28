# LifeKit — Security & Privacy

## Trust Boundary

| Boundary | Threat | Mitigation |
|----------|--------|-----------|
| Localhost only | Network exposure | Flask binds 127.0.0.1; Next.js binds 127.0.0.1 |
| No auth | Physical access | Single-user local trust; no secrets in config |
| LLM provider | Data leaves machine | Ollama = local; OpenRouter = API call (user's key) |

## Privacy Commitments

- **No user modeling beyond important facts.** No psychological profiling.
- **No cloud sync.** All data stays on the local machine.
- **No telemetry.** No usage data leaves the machine.
- **Secrets never stored in config.** API keys come from env vars only.

## Known Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|------------|
| OpenRouter key in shell history | Low | Key exposure | Document `export OPENROUTER_API_KEY` best practice |
| LLM sees book content | Certain | Content leaves machine (OpenRouter only) | Default to Ollama (local) |
| DB file corruption | Very low | Data loss | WAL mode; file-copy backup |
