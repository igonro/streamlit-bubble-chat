"""E2E regression test: bubble button survives rapid rerun cycles.

Reproduces the bug where the floating bubble button disappears after
interacting with the chat while a ``@st.fragment(run_every=0.4)`` is
running — the exact conditions found in ``examples/dashboard_agent``.

Root cause (fixed): all visible UI (root, window, backdrop) now lives
on ``document.body`` as persistent singletons with a persistent CSS
``<style>`` tag.  This makes them immune to Streamlit's component
mount/unmount cycles during rapid fragment reruns.
"""

from __future__ import annotations

import pytest


@pytest.fixture(scope="module")
def stress_app(streamlit_app_factory):
    return streamlit_app_factory("tests/apps/rerun_stress_app.py", 8505)


def _assert_bubble_present(page, *, msg: str = "") -> None:
    """Assert that exactly one bubble button and one window exist."""
    label = f" ({msg})" if msg else ""
    bubble = page.locator(".stbc-bubble-btn")
    assert bubble.count() == 1, f"Expected 1 bubble button{label}, got {bubble.count()}"
    window = page.locator(".stbc-window")
    assert window.count() == 1, f"Expected 1 window{label}, got {window.count()}"
    backdrop = page.locator(".stbc-backdrop")
    assert backdrop.count() == 1, f"Expected 1 backdrop{label}, got {backdrop.count()}"


@pytest.mark.e2e
def test_bubble_survives_rapid_reruns_and_no_orphans(stress_app, page_with_errors):
    """Open/close the bubble many times while fragment reruns are happening.

    Exercises the mount/unmount cycle that caused the bubble button to
    vanish in the dashboard_agent example (roughly 1 in 20 attempts).
    Also verifies that no duplicate DOM elements accumulate.
    """
    page, errors = page_with_errors

    page.goto(stress_app)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(4000)

    bubble = page.locator(".stbc-bubble-btn")
    window = page.locator(".stbc-window")

    # -- Sanity: component rendered correctly on load --
    _assert_bubble_present(page, msg="initial load")
    assert bubble.is_visible()

    # -- Rapid open/close cycles --
    # The fragment reruns every 0.4 s, so 20 cycles (~12 s) should
    # hit the race window reliably if the bug were present.
    for i in range(20):
        bubble.click()
        page.wait_for_timeout(300)  # fast -- overlaps with fragment reruns
        _assert_bubble_present(page, msg=f"after open click #{i}")
        assert window.is_visible(), f"Window should be open at cycle {i}"

        bubble.click()
        page.wait_for_timeout(300)
        _assert_bubble_present(page, msg=f"after close click #{i}")
        assert not window.is_visible(), f"Window should be closed at cycle {i}"

    # After all the cycles, one final check with a longer wait
    page.wait_for_timeout(2000)
    _assert_bubble_present(page, msg="after all cycles + wait")

    # -- Verify the chat still works: open, send a message, verify echo --
    bubble.click()
    page.wait_for_timeout(1000)
    assert window.is_visible()

    input_el = page.locator(".stbc-input")
    input_el.fill("stress test message")
    input_el.press("Enter")
    page.wait_for_timeout(2000)

    messages = page.locator(".stbc-msg")
    last_msg = messages.last
    assert "stress test message" in last_msg.inner_text()

    # -- Close via header button (different code path) --
    page.locator(".stbc-close-btn").click()
    page.wait_for_timeout(1500)
    _assert_bubble_present(page, msg="after close via header")
    assert not window.is_visible()

    # -- Maximize then close (yet another code path) --
    bubble.click()
    page.wait_for_timeout(500)
    page.locator(".stbc-maximize-btn").click()
    page.wait_for_timeout(500)
    page.locator(".stbc-close-btn").click()
    page.wait_for_timeout(1500)
    _assert_bubble_present(page, msg="after maximize+close")
    assert not window.is_visible()

    # -- Varied-timing cycles (checks no orphans accumulate) --
    for delay in [100, 200, 400, 150, 300, 500, 100, 250]:
        bubble.click()
        page.wait_for_timeout(delay)
        if page.locator(".stbc-window.stbc-open").count() > 0:
            bubble.click()
            page.wait_for_timeout(delay)

    page.wait_for_timeout(2000)
    _assert_bubble_present(page, msg="after varied-timing cycles")

    # The exact bug symptom was: root=0, bubble=0
    root = page.locator(".stbc-root")
    assert root.count() == 1, f"Expected 1 root, got {root.count()}"
    assert root.is_visible(), "Root should be visible"

    assert not errors
