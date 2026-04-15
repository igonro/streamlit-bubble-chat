from __future__ import annotations

import pytest


@pytest.fixture(scope="module")
def sound_app(streamlit_app_factory):
    return streamlit_app_factory("base_chat.py", 8506)


@pytest.mark.e2e
def test_sound_plays_for_closed_chat_new_assistant_message(sound_app, page_with_errors):
    page, errors = page_with_errors

    page.add_init_script(
        """
window.__stbcSoundEvents = [];

class FakeOscillator {
    constructor() {
        this.frequency = {
            setValueAtTime() {},
            exponentialRampToValueAtTime() {},
        };
    }

    connect() {}

    start() {
        window.__stbcSoundEvents.push('osc-start');
    }

    stop() {}
}

class FakeGainNode {
    constructor() {
        this.gain = {
            setValueAtTime() {},
            linearRampToValueAtTime() {},
            exponentialRampToValueAtTime() {},
        };
    }

    connect() {
        window.__stbcSoundEvents.push('gain-connect');
    }
}

class FakeBiquadFilterNode {
    constructor() {
        this.frequency = {
            setValueAtTime() {},
        };
    }

    connect() {}
}

class FakeAudioContext {
    constructor() {
        this.state = 'suspended';
        this.currentTime = 0;
        this.destination = {};
    }

    resume() {
        this.state = 'running';
        window.__stbcSoundEvents.push('resume');
        return Promise.resolve();
    }

    createOscillator() {
        return new FakeOscillator();
    }

    createGain() {
        window.__stbcSoundEvents.push('gain-create');
        return new FakeGainNode();
    }

    createBiquadFilter() {
        return new FakeBiquadFilterNode();
    }
}

window.AudioContext = FakeAudioContext;
window.webkitAudioContext = FakeAudioContext;
"""
    )

    page.goto(sound_app)
    page.wait_for_load_state("networkidle")
    page.wait_for_timeout(4000)

    sound_events = page.evaluate("() => window.__stbcSoundEvents")
    assert sound_events.count("gain-create") == 0

    page.locator("button", has_text="Add assistant message").click()
    page.wait_for_timeout(1500)

    sound_events = page.evaluate("() => window.__stbcSoundEvents")
    assert sound_events.count("gain-create") == 1

    page.locator(".stbc-bubble-btn").click()
    page.wait_for_timeout(1500)

    page.locator("button", has_text="Add assistant message").click()
    page.wait_for_timeout(1500)

    sound_events = page.evaluate("() => window.__stbcSoundEvents")
    assert sound_events.count("gain-create") == 1

    page.locator(".stbc-close-btn").click()
    page.wait_for_timeout(1000)

    page.locator("button", has_text="Add system message").click()
    page.wait_for_timeout(1500)

    sound_events = page.evaluate("() => window.__stbcSoundEvents")
    assert sound_events.count("gain-create") == 1
    assert errors == []
