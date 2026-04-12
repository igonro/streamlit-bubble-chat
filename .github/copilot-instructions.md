# Streamlit Bubble Chat — Project Guidelines

A Streamlit custom component (v2 API, no iframe) that renders a floating chat bubble. Single Python API function `bubble_chat()` in [`streamlit_bubble_chat/__init__.py`](../streamlit_bubble_chat/__init__.py). Frontend is vanilla TypeScript + CSS, built with Vite, in `streamlit_bubble_chat/frontend/`.

## Build & Test

```bash
make setup              # first-time: install Python deps + npm deps + git hooks
make build-frontend     # clean → typecheck → Vite build
make test               # unit tests (no browser)
make test-e2e           # Playwright e2e (requires running Streamlit app)
make format             # Ruff autofix
make check              # full pre-commit suite
```

Run examples manually:
```bash
uv run streamlit run examples/base_chat.py    # port 8501
uv run streamlit run examples/avatar_chat.py  # port 8503
```

E2E tests launch their own Streamlit process via `conftest.py` fixtures.

## Architecture

**Python → TypeScript:** `bubble_chat()` serializes messages and config as component args. The TypeScript `FrontendRenderer` receives them as `BubbleChatData`, builds the DOM imperatively (no framework), and sends state back via `setStateValue()` / `setTriggerValue()`.

**Two chat modes:** `type="simple"` (plain bubbles) and `type="avatar"` (per-agent round icons with APCA auto-contrast text). See examples.

**`isolate_styles=False`** — component injects directly into the host page DOM (no iframe). CSS uses `:host` selectors and inherits Streamlit theme variables.

## Conventions

- **Hashed build output** — Vite names bundles `index-[hash].js` / `styles-[hash].css`. Python globs for them (`js="index-*.js"`). After any `make build-frontend`, **restart Streamlit** to pick up new filenames.
- **`build/` is generated** — never edit files in `streamlit_bubble_chat/frontend/build/`.
- **DOM is imperative** — frontend builds the full widget in `buildDOM()` then updates it incrementally when props change. No framework dependency.
- **Text content only in bubbles** — messages use `textContent` for rendering. No markdown support.
- **APCA contrast** — avatar foreground color uses APCA 0.0.98G-4g to auto-select black or white text based on perceptual brightness.
- **`unread_count` counts non-system messages only** — system messages don't increment it; the unread divider skips them.
- **TypeScript strict mode** — changes to Python args require matching updates to the `BubbleChatData` interface in `index.ts`.
- **Conventional Commits** — `feat:`, `fix:`, `docs:`, etc. Enforced by git hooks via `prek`.

## Key Files

| File | Role |
|------|------|
| `streamlit_bubble_chat/__init__.py` | Public Python API |
| `streamlit_bubble_chat/frontend/src/index.ts` | All frontend logic (rendering, events, APCA) |
| `streamlit_bubble_chat/frontend/src/styles.css` | All styling |
| `examples/base_chat.py` | Simple mode reference |
| `examples/avatar_chat.py` | Avatar mode reference |
| `tests/conftest.py` | E2E fixtures (Streamlit launcher, Playwright) |
| `CONTRIBUTING.md` | Dev setup, commit style, PR workflow |

## Pitfalls

- After `make build-frontend`, always restart Streamlit — the hash changes.
- `html=" "` (space, not empty string) in `st.components.v2.component()` is required to prevent iframe wrapping.
- `theme_color` must be valid `#RRGGBB` — no validation in Python; invalid values silently break APCA.
- Material Symbols icons require Google Fonts CDN; emoji always work offline.
- E2E tests wait up to 30 s for Streamlit startup; slow machines may need `STREAMLIT_STARTUP_TIMEOUT` tuned in `conftest.py`.
