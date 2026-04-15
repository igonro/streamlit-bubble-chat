# Contributing

Thanks for contributing to Streamlit Bubble Chat.

## Prerequisites

- [`uv`](https://docs.astral.sh/uv/) — Python package manager and build backend.
- [`npm`](https://nodejs.org/) — for frontend dependencies (TypeScript, Vite).
- `git`

## Local setup

```bash
make setup
```

That command installs Python dependencies, installs the project in editable mode,
installs frontend dependencies with `npm ci`, and installs the git hooks defined
in `.pre-commit-config.yaml` via [`prek`](https://github.com/j178/prek).

## Common commands

```bash
make check           # run the full hook suite (formatting, linting, lock check)
make test            # run all tests (unit + e2e)
make test-unit       # run unit tests only
make test-e2e        # run Playwright e2e tests only
make build-frontend  # clean → typecheck → Vite build
make build           # build frontend assets and Python distributions
make upgrade         # refresh uv dependencies and hook revisions with a 14-day cooldown
```

## Frontend workflow

The TypeScript source lives in `streamlit_bubble_chat/frontend/src/`. After
editing any `.ts` or `.css` file:

```bash
make build-frontend
```

Then **restart Streamlit** — Vite hashes the output filenames (`index-[hash].js`)
and the Python side globs for them. A running Streamlit process won't pick up new
hashes until restarted.

## Testing

**Unit tests** (`tests/test_component_api.py`) test Python API logic without a
browser. They monkeypatch `st.components.v2.component` and assert on the arguments
passed to the component.

**E2E tests** (`tests/test_e2e_*.py`) launch Streamlit + Chromium via Playwright.
They require `uv run playwright install chromium` once. Each test file targets one
example app.

```bash
make test-unit       # fast, no browser needed
make test-e2e        # real browser, ~50 s
```

If an E2E test fails, check:
- Frontend is built (`make build-frontend`).
- Ports 8501, 8503 are free (tests launch Streamlit on those ports).
- Playwright browsers are installed (`uv run playwright install chromium`).

## Commit style

This repository uses Conventional Commits via Commitizen.

Examples:

- `feat: add agent name color overrides`
- `fix: preserve unread state when chat is closed`
- `docs: clarify release workflow`

## Pull requests

- Keep changes focused.
- Update tests and docs when behavior changes.
- Run `make check` before opening a pull request.
