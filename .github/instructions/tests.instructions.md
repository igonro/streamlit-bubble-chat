---
description: "Use when writing, editing, or reviewing tests in tests/**. Covers the two test patterns (unit vs e2e), when to use each, naming, fixtures, and DOM selectors."
applyTo: "tests/**"
---

# Test Conventions

## Two Patterns — Choose the Right One

### Unit tests (`test_component_api.py` and similar)
- **What**: Python-only, no browser, no running Streamlit
- **When**: Testing `bubble_chat()` argument handling, config merging, state management, return values
- **Framework**: `pytest` with `monkeypatch`; mock `st.components.v2.component` to capture args
- **Run**: `make test` (fast, no setup needed)

```python
# Pattern: monkeypatch the v2 component, reload the module, assert on captured args
@pytest.fixture
def component_module(monkeypatch):
    monkeypatch.setattr(st.components.v2, "component", lambda *a, **kw: lambda **c: c)
    return importlib.reload(importlib.import_module("streamlit_bubble_chat"))
```

### E2E browser tests (`test_e2e_*.py`)
- **What**: Real Chromium via Playwright against a live Streamlit app
- **When**: Testing rendered DOM, UI interactions (typing, clicking), window open/close, badge state, message ordering, CSS selectors
- **Framework**: `pytest` + `conftest.py` fixtures; mark every test `@pytest.mark.e2e`
- **Run**: `make test-e2e` (requires Playwright chromium: `uv run playwright install chromium`)

```python
# Pattern: use streamlit_app_factory fixture to launch the example, use page_with_errors for error capture
@pytest.fixture(scope="module")
def my_app(streamlit_app_factory):
    return streamlit_app_factory("my_example.py", 8505)  # choose a free port

@pytest.mark.e2e
def test_something(my_app, page_with_errors):
    page, errors = page_with_errors
    page.goto(my_app)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(4000)  # Streamlit takes ~4 s to fully render
    ...
    assert not errors  # always check at the end
```

## File Naming

| Pattern | Purpose |
|---------|---------|
| `test_component_api.py` | Unit tests for the Python API |
| `test_e2e_<mode>.py` | E2E tests scoped to one example (`simple`, `avatar`) |

One pytest file per example app for e2e tests; group related assertions within a single test function.

## DOM Selectors

Always use the `.stbc-*` CSS classes — they are stable identifiers:

| Selector | Element |
|----------|---------|
| `.stbc-bubble-btn` | Floating bubble button |
| `.stbc-badge` | Unread count badge |
| `.stbc-window` | Chat window panel |
| `.stbc-msg` | Any message row |
| `.stbc-msg-user` / `.stbc-msg-assistant` / `.stbc-msg-system` | By role |
| `.stbc-avatar` | Avatar circle |
| `.stbc-msg-name` | Agent name label |
| `.stbc-unread-divider` | "New messages" divider |
| `.stbc-input` | Text input field |
| `.stbc-send-btn` | Send button |

Prefer `page.locator(".stbc-*")` over `page.query_selector` — locators are lazy and auto-retry.

## Fixtures (from `conftest.py`)

- `streamlit_app_factory(example_name, port)` — launches `examples/<example_name>` on `port`, returns `base_url`; session-scoped, cleans up automatically
- `browser` — session-scoped Chromium instance
- `page_with_errors(browser)` — returns `(page, errors_list)`; `errors` collects JS console errors

## Timing

- `page.wait_for_load_state("networkidle")` + `page.wait_for_timeout(4000)` after `page.goto()` — Streamlit needs ~4 s to hydrate
- After clicking a button that triggers a Streamlit rerun, wait `1500`–`2000` ms before asserting
- Playwright locators auto-retry; prefer them over immediate `count()` checks after interactions

## What Goes Where

| What you want to test | Use |
|-----------------------|-----|
| `bubble_chat()` argument validation | Unit test |
| `assistant_config` merging / defaults | Unit test |
| `unread_count` passed correctly to component | Unit test |
| Invalid roles / missing content / bad hex colors | Unit test |
| `key=None` skips session state | Unit test |
| Bubble renders in the page | E2E |
| Message appears after user types + sends | E2E |
| Unread divider skips system messages | E2E |
| Badge count resets on open | E2E |
| Avatar colors / contrast | E2E |
| CSS class applied for role | E2E |
| ARIA attributes (`aria-label`, `aria-expanded`, `role`) | E2E |
| Escape key closes window / exits maximized | E2E |
