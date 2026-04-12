SHELL := /bin/bash

FRONTEND_DIR := streamlit_bubble_chat/frontend
E2E_MARKER := e2e
DEPENDENCY_COOLDOWN_DAYS := 14

.PHONY: setup sync frontend-install install-hooks check upgrade test test-unit test-e2e build-frontend build clean release-dry-run release-patch release-minor release-major

setup:
	uv sync --locked --all-groups
	npm --prefix $(FRONTEND_DIR) ci
	uv run prek install -f

sync:
	uv sync --locked --all-groups

frontend-install:
	npm --prefix $(FRONTEND_DIR) ci

install-hooks:
	uv run prek install -f

check:
	uv run prek run --all-files

upgrade:
	CUTOFF=$$(python3 -c "from datetime import datetime, timedelta, timezone; print((datetime.now(timezone.utc) - timedelta(days=$(DEPENDENCY_COOLDOWN_DAYS))).strftime('%Y-%m-%dT%H:%M:%SZ'))"); \
	uv lock --upgrade --exclude-newer "$$CUTOFF"
	uv sync --all-groups
	uv run prek auto-update --cooldown-days=$(DEPENDENCY_COOLDOWN_DAYS)

test: test-unit test-e2e

test-unit:
	uv run pytest -m "not $(E2E_MARKER)" --cov

test-e2e:
	uv run playwright install chromium
	uv run pytest -m "$(E2E_MARKER)"

build-frontend: frontend-install
	npm --prefix $(FRONTEND_DIR) run build

build: build-frontend
	uv build

clean:
	rm -rf .coverage .pytest_cache .ruff_cache build dist htmlcov
	find . -type d \( -name __pycache__ -o -name *.egg-info \) -prune -exec rm -rf {} +

release-dry-run:
	uv run cz bump --dry-run --yes

release-patch:
	uv run cz bump --increment PATCH --yes

release-minor:
	uv run cz bump --increment MINOR --yes

release-major:
	uv run cz bump --increment MAJOR --yes
