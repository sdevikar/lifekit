# LLM provider configuration — tasks

Test-first: write each test, watch it fail, then implement. Do not start the
next task until the current one's tests pass.

- [x] 1.1 `tests/test_llm_config.py`: defaults → `ollama`/`qwen3.6:latest` with no env/file/flags
- [x] 1.2 Config file `~/.lifekit/config.json` (`provider`/`model` keys) overrides defaults
- [x] 1.3 Env vars (`LIFEKIT_PROVIDER`, `LIFEKIT_MODEL`, legacy `OLLAMA_MODEL`) override config file
- [x] 1.4 CLI args override env vars (full precedence: CLI > env > file > defaults)
- [x] 1.5 `openrouter` without `OPENROUTER_API_KEY` raises a clear error naming the env var
- [x] 1.6 `openrouter` without an explicit model raises a clear error (no invented default slug)
- [x] 1.7 Unknown provider name raises a clear error listing supported providers
- [x] 2.1 `tests/test_llm_providers.py`: `OllamaProvider` wraps an injected ollama-shaped client, passes `format=<json schema>` + `options={"temperature": …}`, returns `resp["message"]["content"]`
- [x] 2.2 `OpenRouterProvider` POSTs to `https://openrouter.ai/api/v1/chat/completions` with `Authorization: Bearer <key>`, `response_format` json_schema payload, parses `choices[0].message.content` (mock `urllib.request.urlopen`)
- [x] 2.3 `OpenRouterProvider` without a key raises before any HTTP
- [x] 2.4 `get_provider` factory returns the right class per resolved config
- [x] 3.1 `tests/test_extractor.py`: `extract_chapter` works unchanged with a stub protocol provider; legacy ollama-shaped `client=` kwarg still accepted (existing tests unmodified)
- [x] 3.2 Refactor `../../../lifekit/extract/extractor.py` internals to the provider protocol; default path (no args) resolves config itself and stays byte-identical (ollama, temp 0.1, 3-attempt retry)
- [x] 3.3 `../../../lifekit/extract/__main__.py` gains `--provider` passed through to `extract_chapter`
- [x] 4.1 `../../../lifekit/config/__main__.py`: `view` prints resolved provider/model + source of each, shows only whether `OPENROUTER_API_KEY` is set; `set`/`unset` round-trip through `~/.lifekit/config.json`; `set` refuses key-like names (key/api_key/token/secret)
- [x] 5.1 `../../../scripts/eval_step2_recall.py`: `--provider`/`--model` flags route through the provider abstraction; `--results` defaults to `./.eval-step2/results.json` (no hardcoded `/home/hatch` path — fixes backlog P1); `--ground-truth` overridable; llama.cpp shim kept behind `--model-path`, adapted to the provider protocol
- [x] 6.1 `../../../docs/product/ASSUMPTIONS.md`: add A21 (active) documenting provider config; `../../../docs/product/ROADMAP.md`: shipped-infra note (not a numbered MVP step)
- [x] 6.2 Full `pytest` run green; `py_compile` clean on all new/changed files
- [x] 6.3 Archive `../../changes/llm-provider-config/` → `../../archives/llm-provider-config/`; record test results below

## Test results (2026-09-16)

`pytest tests/` — **70/70 passed** (49 pre-existing + 21 new, 2.0s).

- `tests/test_llm_config.py` (9): full precedence chain CLI > env (`LIFEKIT_PROVIDER`/`LIFEKIT_MODEL`, legacy `OLLAMA_MODEL`) > `~/.lifekit/config.json` > defaults (`ollama`/`qwen3.6:latest`); openrouter without `OPENROUTER_API_KEY` or without explicit model raises a clear error; unknown provider rejected.
- `tests/test_llm_providers.py` (7): `OllamaProvider` passes `format=<json schema>` + `options={"temperature": …}` through to the wrapped client and returns `resp["message"]["content"]`; `OpenRouterProvider` POSTs to `https://openrouter.ai/api/v1/chat/completions` with `Authorization: Bearer <key>`, `response_format` json_schema payload, parses `choices[0].message.content`; both satisfy the `LLMProvider` protocol; factory returns the right class per config.
- `tests/test_config_cli.py` (5): `set`/`view`/`unset` round-trip through an isolated config file; `set api_key` refused; `view` never prints the key value, only whether `OPENROUTER_API_KEY` is set.
- `tests/test_extractor.py` (+1): `extract_chapter` accepts a protocol provider; all 8 pre-existing tests (legacy ollama-shaped `client=` stub) unmodified and passing — default behavior byte-identical.
- `py_compile` clean on all new/changed files. `python -m lifekit.config view/set/unset` smoke-tested manually.

New files: `../../../lifekit/llm/{__init__,base,config,ollama_provider,openrouter_provider}.py`,
`../../../lifekit/config/{__init__,__main__}.py`,
`tests/test_llm_config.py`, `tests/test_llm_providers.py`, `tests/test_config_cli.py`.
Changed: `../../../lifekit/extract/extractor.py` (internals only; legacy `client=` kwarg still accepted),
`../../../lifekit/extract/__main__.py` (`--provider`), `../../../scripts/eval_step2_recall.py`
(provider flags, `--results`/`--ground-truth` portable paths — closes backlog P1),
`../../../docs/product/ASSUMPTIONS.md` (+A21), `../../../docs/product/ROADMAP.md` (shipped-infra note).
