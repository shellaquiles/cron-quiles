.PHONY: help install install-dev sync test test-file test-filter lint format format-check run run-all serve clean update check
.PHONY: tools-deduplicate tools-populate-cache tools-scan-feeds tools-scrape-meetup requirements-freeze deploy-gh-pages

UV := uv
OUTPUT_DIR := gh-pages/data

help:  ## Muestra este mensaje de ayuda
	@echo "Comandos disponibles para Cron-Quiles:"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'

install:  ## Instala dependencias de producción
	$(UV) sync --frozen

install-dev:  ## Instala todas las dependencias (prod + dev)
	$(UV) sync --frozen --all-extras

sync:  ## Sincroniza entorno con lockfile
	$(UV) sync --frozen

test:  ## Ejecuta todos los tests
	$(UV) run pytest tests/ -v

test-file:  ## Ejecuta archivo específico (uso: make test-file FILE=test_ics_aggregator.py)
	$(UV) run pytest tests/$(FILE) -v

test-filter:  ## Ejecuta tests filtrados (uso: make test-filter FILTER="normalize_title")
	$(UV) run pytest tests/ -v -k "$(FILTER)"

lint:  ## Verifica código con flake8
	$(UV) run flake8 src/ --max-line-length=127 --count --statistics

format:  ## Formatea código con black
	$(UV) run black src/ tests/

format-check:  ## Verifica formato sin modificar
	$(UV) run black --check src/ tests/

run:  ## Ejecuta pipeline (uso: make run ARGS="--city cdmx --json")
	$(UV) run python -m cronquiles.main $(ARGS)

run-all:  ## Ejecuta pipeline completo para todas las ciudades
	$(UV) run python -m cronquiles.main --all-cities --json --output-dir $(OUTPUT_DIR)/

run-fast:  ## Ejecuta pipeline en modo rápido (--fast: sin enrich ni geocoding de historial)
	$(UV) run python -m cronquiles.main --all-cities --json --output-dir $(OUTPUT_DIR)/ --fast

serve:  ## Inicia servidor local en gh-pages/
	cd gh-pages && $(UV) run python serve.py

clean:  ## Limpia archivos generados
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true

update:  ## Actualiza dependencias (regenera lockfile)
	$(UV) lock --upgrade

check:  ## Verifica integridad del entorno
	$(UV) run python -c "import cronquiles; print('✓ Paquete importado correctamente')"
	@echo "✓ Entorno configurado correctamente"

# Herramientas de mantenimiento
tools-deduplicate:  ## Deduplica eventos
	$(UV) run python tools/deduplicate_events.py

tools-populate-cache:  ## Puebla cache desde historial
	$(UV) run python tools/populate_cache_from_history.py

tools-scan-feeds:  ## Escanea feeds
	$(UV) run python tools/scan_feeds_and_cache.py

tools-scrape-meetup:  ## Scraping histórico
	$(UV) run python tools/scrape_meetup_history.py

requirements-freeze:  ## Genera requirements.txt (compatibilidad temporal)
	$(UV) pip freeze > requirements.txt
	@echo "⚠️  requirements.txt generado para compatibilidad"

# Despliegue a rama orphan gh-pages
deploy-gh-pages:  ## Publica gh-pages/ y data/ en la rama orphan gh-pages
	@echo "Publicando en rama orphan gh-pages..."
	$(eval TMPDIR := $(shell mktemp -d))
	cp -r gh-pages/* $(TMPDIR)/
	mkdir -p $(TMPDIR)/data
	cp data/history.json $(TMPDIR)/data/ 2>/dev/null || true
	cp data/geocoding_cache.json $(TMPDIR)/data/ 2>/dev/null || true
	cp docs/COMMUNITIES.md $(TMPDIR)/ 2>/dev/null || true
	git config --local user.email "action@github.com"
	git config --local user.name "GitHub Action"
	git stash --include-untracked || true
	if git fetch origin gh-pages 2>/dev/null; then \
		git checkout gh-pages; \
	else \
		git checkout --orphan gh-pages; \
		git rm -rf . 2>/dev/null || true; \
	fi
	git rm -rf . 2>/dev/null || true
	cp -r $(TMPDIR)/* .
	rm -rf $(TMPDIR)
	git add -A
	git commit -m "🤖 Auto-update: Refresh events calendar & persist data" || true
	git push origin gh-pages --force
	git checkout main
	git stash pop || true
	@echo "✓ Publicado en rama gh-pages"
