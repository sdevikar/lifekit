# LLM provider configuration — proposal

## Why

LifeKit's extraction pipeline (Steps 1–7) hardcodes Ollama as the only model
backend (`lifekit/extract/extractor.py` builds `ollama.Client()` directly, and
`lifekit/validate` and `lifekit/plan_forge` do the same). That blocks anyone
who wants to run the pipeline — notably the deferred full-book extraction eval
(A17/A20) — on a machine without a capable local model. Most open-source
projects in this space solve this with a small provider abstraction plus
layered configuration (CLI flags > env vars > config file > defaults); we
mirror that shape.

## What Changes

- **New**: `lifekit/llm/` package —
  - `base.py`: minimal `LLMProvider` protocol: `chat_json_schema(*, model,
    messages, json_schema, temperature) -> str` (returns the raw content string).
  - `ollama_provider.py`: wraps the existing `ollama.Client()` usage; default
    provider; behavior byte-identical (format=`<json schema>`, temp 0.1).
  - `openrouter_provider.py`: POSTs to `https://openrouter.ai/api/v1/chat/completions`
    (OpenAI-compatible, verified against OpenRouter docs) with
    `Authorization: Bearer $OPENROUTER_API_KEY`, `response_format` json_schema,
    and `HTTP-Referer`/`X-Title` attribution headers. Uses stdlib
    `urllib.request` — **no new dependencies**.
  - `config.py`: `resolve_config(cli_provider=None, cli_model=None)` →
    `LLMConfig`. Resolution order: CLI flags > env vars (`LIFEKIT_PROVIDER`,
    `LIFEKIT_MODEL`, legacy `OLLAMA_MODEL`, `OPENROUTER_API_KEY`) > config
    file (`~/.lifekit/config.json`, keys `provider`/`model`) > defaults
    (`ollama` / `qwen3.6:latest`; openrouter requires an explicit model — no
    invented default slug).
  - `__init__.py`: `get_provider(config) -> LLMProvider` factory.
- **Modified**: `lifekit/extract/extractor.py` — uses the provider abstraction;
  default path (no args) resolves config itself, so `extract_chapter(chapter)`
  behaves exactly as before (ollama, temp 0.1, 3-attempt retry). A legacy
  ollama-shaped `client` kwarg is still accepted and wrapped.
- **Modified**: `lifekit/extract/__main__.py` — gains `--provider` flag.
- **New**: `lifekit/config/__main__.py` — `lifekit config` CLI: `view` (shows
  resolved provider/model and the source of each; shows whether
  `OPENROUTER_API_KEY` is set, never its value), `set provider|model <value>`,
  `unset provider|model`. Keys are never stored in the config file and the
  setter refuses key-like names.
- **Modified**: `scripts/eval_step2_recall.py` — uses the provider abstraction
  (`--provider`, `--model` flags; local llama.cpp shim retained behind
  `--model-path` and adapted to the protocol), and fixes backlog item P1: the
  hardcoded `/home/hatch/workspace/lifekit-dev/.eval-step2/results.json` path
  becomes a `--results` flag defaulting to `./.eval-step2/results.json`
  (repo-relative CWD), with the ground-truth path also overridable via
  `--ground-truth`.
- **Security**: API keys travel only via `OPENROUTER_API_KEY` env var; never in
  config files, code, or git history.
- **Deferred**: provider-ifying `plan_forge` and the validate judge
  (they keep their existing Ollama calls; same pattern applies later).

## Capabilities

### New Capabilities

- `llm-provider-config`: choose the model backend (`ollama` default,
  `openrouter`) via CLI > env > `~/.lifekit/config.json` > defaults; inspect
  and persist it with `lifekit config`.

### Modified Capabilities

- `extraction-map`: unchanged default behavior; now routes through the
  provider abstraction and accepts `--provider`/`--model` overrides.

## Impact

- New: `lifekit/llm/{base,ollama_provider,openrouter_provider,config,__init__}.py`,
  `lifekit/config/__main__.py`, `tests/test_llm_config.py`,
  `tests/test_llm_providers.py`.
- Changed: `lifekit/extract/extractor.py` (internal only), `lifekit/extract/__main__.py`
  (`--provider`), `scripts/eval_step2_recall.py` (provider flags, portable paths).
- No new dependencies. `ASSUMPTIONS.md` gains A21; `ROADMAP.md` notes the infra feature.

## Done criterion (test before building anything else)

`pytest` fully green (existing 49 + new tests), including: config precedence
(CLI > env > file > defaults) asserted end-to-end; both providers exercised
with mocked HTTP/ollama client asserting request shape (Bearer auth, json
schema payload); extractor unchanged under a stub protocol provider; eval
script defaults to a portable results path. Results recorded in `tasks.md`.
