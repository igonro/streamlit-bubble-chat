# Contributing

Thanks for contributing to Streamlit Bubble Chat.

## Prerequisites

- `uv`
- `npm`
- `git`

## Local setup

```bash
make setup
```

That command installs Python dependencies, installs the project in editable mode,
installs frontend dependencies with `npm ci`, and installs the git hooks defined
in `.pre-commit-config.yaml` via `prek`.

## Common commands

```bash
make check           # run the full hook suite (formatting, linting, lock check)
make test            # run all tests (unit + e2e)
make test-unit       # run unit tests only
make test-e2e        # run Playwright e2e tests only
make upgrade         # refresh uv dependencies and hook revisions with a 14-day cooldown
make build           # build frontend assets and Python distributions
```

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
