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


@pytest.mark.e2e
def test_aria_attributes(simple_app, page_with_errors):
    """ARIA roles, labels, and aria-expanded are correctly set."""
    page, errors = page_with_errors

    page.goto(simple_app)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(4000)

    bubble = page.locator(".stbc-bubble-btn")
    window = page.locator(".stbc-window")

    # Bubble button should have aria-label and aria-expanded=false when closed
    assert bubble.get_attribute("aria-label") == "Open chat"
    assert bubble.get_attribute("aria-expanded") == "false"
    assert bubble.get_attribute("aria-controls") == "stbc-chat-window"

    # Window should be a dialog with aria-labelledby
    assert window.get_attribute("role") == "dialog"
    assert window.get_attribute("aria-labelledby") == "stbc-header-title"

    # Open the chat
    bubble.click()
    page.wait_for_timeout(1500)

    # After opening, aria-expanded should be true
    assert bubble.get_attribute("aria-expanded") == "true"

    # Input should have aria-label
    assert page.locator(".stbc-input").get_attribute("aria-label") == "Chat message"

    # Close/maximize buttons should have aria-labels
    assert (
        page.locator(".stbc-close-btn").get_attribute("aria-label")
        == "Close chat window"
    )
    assert page.locator(".stbc-maximize-btn").get_attribute("aria-label") is not None

    # Badge should have aria-live
    assert page.locator(".stbc-badge").get_attribute("aria-live") == "polite"

    # Send button should have aria-label
    assert page.locator(".stbc-send-btn").get_attribute("aria-label") == "Send message"

    # Close
    page.locator(".stbc-close-btn").click()
    page.wait_for_timeout(1000)
    assert bubble.get_attribute("aria-expanded") == "false"

    assert errors == []


@pytest.mark.e2e
def test_escape_key_closes_window(simple_app, page_with_errors):
    """Pressing Escape closes the chat window, or exits maximized first."""
    page, errors = page_with_errors

    page.goto(simple_app)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(4000)

    bubble = page.locator(".stbc-bubble-btn")
    window = page.locator(".stbc-window")

    # Open chat
    bubble.click()
    page.wait_for_timeout(1500)
    assert window.is_visible() is True

    # Maximize
    page.locator(".stbc-maximize-btn").click()
    page.wait_for_timeout(1000)
    assert window.evaluate("el => el.classList.contains('stbc-maximized')") is True

    # Escape should exit maximized first (still open)
    page.locator(".stbc-input").press("Escape")
    page.wait_for_timeout(1000)
    assert window.evaluate("el => el.classList.contains('stbc-maximized')") is False
    assert window.is_visible() is True

    # Escape again should close the window
    page.locator(".stbc-input").press("Escape")
    page.wait_for_timeout(1000)
    assert window.is_visible() is False

    assert errors == []
