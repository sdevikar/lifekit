SHELL := /bin/bash
.PHONY: bootstrap ingest forge serve test lint clean all

LIFECMD  := python -m lifekit
DB_PATH  ?= $(HOME)/.lifekit/lifekit.db
PDF_PATH ?=
INTENT   ?=

bootstrap:
	@echo "Bootstrapping LifeKit..."
	@python -c "from lifekit.db.schema import init_db; \
    db = init_db(); print('Bootstrap complete!')"

ingest:
	@if [ -z "$(PDF_PATH)" ]; then \
		echo "Error: PDF= is required. Usage: make ingest PDF=path/to/book.pdf"; \
		exit 1; \
	fi
	@python -m lifekit.store --pdf $(PDF_PATH)

forge:
	@if [ -z "$(INTENT)" ]; then \
		echo "Error: INTENT= required. Usage: make forge INTENT='read the book'"; \
		exit 1; \
	fi
	@echo "Forge plan with intent: $(INTENT)"
	@python -m lifekit.plan_forge.forge --intent "$(INTENT)"

serve:
	@python -m lifekit.mcp.server

test:
	@python -m pytest tests/ -v

lint:
	@python -m py_compile $(wildcard lifekit/db/*.py) \
                          $(wildcard lifekit/store/*.py) \
                          $(wildcard lifekit/plan_forge/*.py) \
                          $(wildcard lifekit/mcp/*.py) 2>&1
	@echo "All files compiled successfully"

clean:
	@echo "Cleaning up..."
	@python -m py_compile --help >/dev/null 2>&1 || true
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name '*.pyc' -delete 2>/dev/null || true
	@echo "Clean done."
