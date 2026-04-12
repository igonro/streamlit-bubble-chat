from __future__ import annotations

import importlib

import pytest
import streamlit as st


@pytest.fixture
def component_module(monkeypatch):
    monkeypatch.setattr(
        st.components.v2,
        "component",
        lambda *args, **kwargs: lambda **call_kwargs: call_kwargs,
    )

    module = importlib.import_module("streamlit_bubble_chat")
    return importlib.reload(module)


def test_bubble_chat_merges_assistant_defaults(component_module, monkeypatch):
    captured: dict[str, object] = {}

    def fake_component(**kwargs):
        captured.update(kwargs)
        return {"ok": True}

    monkeypatch.setattr(component_module, "_component", fake_component)
    monkeypatch.setattr(component_module.st, "session_state", {}, raising=False)

    result = component_module.bubble_chat(
        messages=[{"role": "assistant", "content": "Hello"}],
        type="avatar",
        assistant_config={
            "_default": {"icon": "🤖"},
            "Planner": {"avatar_bg": "#123456"},
        },
        key="chat",
    )

    assert result == {"ok": True}
    assistant_config = captured["data"]["assistant_config"]
    assert assistant_config["_default"]["icon"] == "🤖"
    assert assistant_config["_default"]["avatar_bg"] == ""
    assert assistant_config["Planner"]["icon"] == ":material/robot_2:"
    assert assistant_config["Planner"]["avatar_bg"] == "#123456"


def test_bubble_chat_reads_existing_component_state(component_module, monkeypatch):
    captured: dict[str, object] = {}

    def fake_component(**kwargs):
        captured.update(kwargs)
        return {"ok": True}

    monkeypatch.setattr(component_module, "_component", fake_component)
    monkeypatch.setattr(
        component_module.st,
        "session_state",
        {"chat": {"is_open": True, "is_maximized": True}},
        raising=False,
    )

    component_module.bubble_chat(
        messages=[{"role": "assistant", "content": "Hello"}],
        key="chat",
    )

    assert captured["data"]["is_open"] is True
    assert captured["data"]["is_maximized"] is True


def test_bubble_chat_wires_callbacks_and_defaults(component_module, monkeypatch):
    captured: dict[str, object] = {}

    def fake_component(**kwargs):
        captured.update(kwargs)
        return {"ok": True}

    def on_message():
        return None

    monkeypatch.setattr(component_module, "_component", fake_component)
    monkeypatch.setattr(component_module.st, "session_state", {}, raising=False)

    component_module.bubble_chat(
        messages=[{"role": "assistant", "content": "Hello"}],
        theme_color="#007AFF",
        name_colors={"Helper": "#e67e22"},
        key="chat",
        on_message=on_message,
    )

    assert captured["default"] == {"is_open": False, "is_maximized": False}
    assert captured["data"]["theme_color"] == "#007AFF"
    assert captured["data"]["name_colors"] == {"Helper": "#e67e22"}
    assert captured["data"]["user_icon_bg"] == ""
    assert callable(captured["on_is_open_change"])
    assert callable(captured["on_is_maximized_change"])
    assert captured["on_new_message_change"] is on_message
