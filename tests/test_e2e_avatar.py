from __future__ import annotations

import pytest


@pytest.fixture(scope="module")
def avatar_app(streamlit_app_factory):
    return streamlit_app_factory("avatar_chat.py", 8503)


@pytest.mark.e2e
def test_avatar_mode_multi_agent_flow(avatar_app, page_with_errors):
    page, errors = page_with_errors

    page.goto(avatar_app)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(4000)

    bubble = page.locator(".stbc-bubble-btn")
    assert bubble.count() == 1

    bubble.click()
    page.wait_for_timeout(1500)

    messages = page.locator(".stbc-msg")
    assistant_messages = page.locator(".stbc-msg-assistant")
    assert messages.count() == 6
    assert assistant_messages.count() == 5

    system_message = messages.nth(0)
    assert (
        system_message.evaluate(
            "element => element.classList.contains('stbc-msg-system')"
        )
        is True
    )
    assert system_message.locator(".stbc-system-pill").count() == 1
    assert system_message.locator(".stbc-avatar").count() == 0

    for index in range(assistant_messages.count()):
        assert assistant_messages.nth(index).locator(".stbc-avatar").count() == 1

    names = page.locator(".stbc-msg-name").all_inner_texts()
    assert set(["Guide", "Designer", "Dev", "Tester"]).issubset(names)

    first_avatar = assistant_messages.nth(0).locator(".stbc-avatar")
    assert first_avatar.evaluate("element => element.style.background") != ""

    input_el = page.locator(".stbc-input")
    input_el.fill("Hello agents")
    input_el.press("Enter")
    page.wait_for_timeout(1500)
    assert page.locator(".stbc-msg").count() == 8
    assert page.locator(".stbc-msg-user").last.locator(".stbc-avatar").count() == 1

    guide_avatar = assistant_messages.nth(0).locator(".stbc-avatar")
    material_icon = guide_avatar.locator(".material-symbols-rounded")
    if material_icon.count() == 1:
        assert material_icon.inner_text() == "explore"

    bubble.click()
    page.wait_for_timeout(1000)

    for _ in range(2):
        page.locator("button", has_text="Add assistant message").click()
        page.wait_for_timeout(1500)

    for _ in range(2):
        page.locator("button", has_text="Add system message").click()
        page.wait_for_timeout(1500)

    badge = page.locator(".stbc-badge")
    assert badge.count() == 1
    assert badge.inner_text() == "2"

    bubble.click()
    page.wait_for_timeout(1500)

    divider = page.locator(".stbc-unread-divider")
    assert divider.count() == 1
    assert (
        page.evaluate(
            """() => {
                const dividerElement = document.querySelector('.stbc-unread-divider');
                const nextElement = dividerElement?.nextElementSibling;
                return nextElement?.classList.contains('stbc-msg-system') ?? null;
            }"""
        )
        is False
    )

    divider_info = page.evaluate(
        """() => {
            const container = document.querySelector('.stbc-messages');
            const allMessages = Array.from(container.querySelectorAll('.stbc-msg'));
            const dividerElement = container.querySelector('.stbc-unread-divider');
            const nextElement = dividerElement.nextElementSibling;
            const dividerBeforeIndex = allMessages.indexOf(nextElement);
            let nonSystemAfter = 0;

            for (
                let index = dividerBeforeIndex;
                index < allMessages.length;
                index += 1
            ) {
                if (!allMessages[index].classList.contains('stbc-msg-system')) {
                    nonSystemAfter += 1;
                }
            }

            return { dividerBeforeIndex, nonSystemAfter };
        }"""
    )
    assert divider_info["nonSystemAfter"] == 2
    assert errors == []
