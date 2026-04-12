from __future__ import annotations

import pytest


@pytest.fixture(scope="module")
def simple_app(streamlit_app_factory):
    return streamlit_app_factory("base_chat.py", 8501)


@pytest.mark.e2e
def test_simple_mode_chat_flow(simple_app, page_with_errors):
    page, errors = page_with_errors

    page.goto(simple_app)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(4000)

    bubble = page.locator(".stbc-bubble-btn")
    window = page.locator(".stbc-window")
    badge = page.locator(".stbc-badge")

    assert bubble.count() == 1
    assert window.is_visible() is False
    assert badge.count() == 1
    assert (
        badge.evaluate("element => !element.classList.contains('stbc-hidden')") is True
    )

    bubble.click()
    page.wait_for_timeout(1500)
    assert window.is_visible() is True
    assert page.locator(".stbc-header-title").inner_text() == "Support Chat"

    assert page.locator(".stbc-msg").count() == 5
    assert page.locator(".stbc-avatar").count() == 0
    assert page.locator(".stbc-msg-name").all_inner_texts() == ["Helper", "Bot"]
    assert page.locator(".stbc-unread-divider").count() == 1

    input_el = page.locator(".stbc-input")
    input_el.fill("Test via Enter")
    input_el.press("Enter")
    page.wait_for_timeout(1500)
    assert page.locator(".stbc-msg").count() == 7

    input_el.fill("Test via button")
    page.locator(".stbc-send-btn").click()
    page.wait_for_timeout(1500)
    assert page.locator(".stbc-msg").count() == 9

    page.locator(".stbc-maximize-btn").click()
    page.wait_for_timeout(1000)
    assert (
        window.evaluate("element => element.classList.contains('stbc-maximized')")
        is True
    )
    assert page.locator(".stbc-backdrop.stbc-visible").count() == 1

    page.locator(".stbc-maximize-btn").click()
    page.wait_for_timeout(1000)
    assert (
        window.evaluate("element => element.classList.contains('stbc-maximized')")
        is False
    )

    page.locator(".stbc-close-btn").click()
    page.wait_for_timeout(1000)
    assert window.is_visible() is False

    bubble.click()
    page.wait_for_timeout(1000)
    assert page.locator(".stbc-msg").count() == 9
    assert errors == []
