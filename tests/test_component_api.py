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


# ── Validation tests ──


class TestValidation:
    """Tests for input validation in bubble_chat()."""

    def test_invalid_role_raises(self, component_module, monkeypatch):
        monkeypatch.setattr(component_module, "_component", lambda **kw: {"ok": True})
        monkeypatch.setattr(component_module.st, "session_state", {}, raising=False)

        with pytest.raises(ValueError, match=r"messages\[0\]\['role'\] must be one of"):
            component_module.bubble_chat(
                messages=[{"role": "bot", "content": "hi"}],
                key="chat",
            )

    def test_missing_content_raises(self, component_module, monkeypatch):
        monkeypatch.setattr(component_module, "_component", lambda **kw: {"ok": True})
        monkeypatch.setattr(component_module.st, "session_state", {}, raising=False)

        with pytest.raises(
            ValueError, match=r"messages\[0\] is missing required key 'content'"
        ):
            component_module.bubble_chat(
                messages=[{"role": "user"}],
                key="chat",
            )

    def test_missing_role_raises(self, component_module, monkeypatch):
        monkeypatch.setattr(component_module, "_component", lambda **kw: {"ok": True})
        monkeypatch.setattr(component_module.st, "session_state", {}, raising=False)

        with pytest.raises(
            ValueError, match=r"messages\[0\] is missing required key 'role'"
        ):
            component_module.bubble_chat(
                messages=[{"content": "hello"}],
                key="chat",
            )

    def test_invalid_theme_color_raises(self, component_module, monkeypatch):
        monkeypatch.setattr(component_module, "_component", lambda **kw: {"ok": True})
        monkeypatch.setattr(component_module.st, "session_state", {}, raising=False)

        with pytest.raises(ValueError, match="theme_color must be a valid #RRGGBB"):
            component_module.bubble_chat(
                messages=[{"role": "user", "content": "hi"}],
                theme_color="red",
                key="chat",
            )

    def test_invalid_user_icon_bg_raises(self, component_module, monkeypatch):
        monkeypatch.setattr(component_module, "_component", lambda **kw: {"ok": True})
        monkeypatch.setattr(component_module.st, "session_state", {}, raising=False)

        with pytest.raises(ValueError, match="user_icon_bg must be a valid #RRGGBB"):
            component_module.bubble_chat(
                messages=[{"role": "user", "content": "hi"}],
                user_icon_bg="rgb(0,0,0)",
                key="chat",
            )

    def test_invalid_assistant_config_color_raises(self, component_module, monkeypatch):
        monkeypatch.setattr(component_module, "_component", lambda **kw: {"ok": True})
        monkeypatch.setattr(component_module.st, "session_state", {}, raising=False)

        with pytest.raises(ValueError, match=r"assistant_config\['Agent'\]\.avatar_bg"):
            component_module.bubble_chat(
                messages=[{"role": "assistant", "content": "hi"}],
                assistant_config={"Agent": {"icon": "🤖", "avatar_bg": "bad"}},
                key="chat",
            )

    def test_invalid_name_colors_raises(self, component_module, monkeypatch):
        monkeypatch.setattr(component_module, "_component", lambda **kw: {"ok": True})
        monkeypatch.setattr(component_module.st, "session_state", {}, raising=False)

        with pytest.raises(ValueError, match=r"name_colors\['Bot'\]"):
            component_module.bubble_chat(
                messages=[{"role": "user", "content": "hi"}],
                name_colors={"Bot": "not-a-color"},
                key="chat",
            )

    def test_valid_hex_colors_pass(self, component_module, monkeypatch):
        captured: dict[str, object] = {}

        def fake_component(**kwargs):
            captured.update(kwargs)
            return {"ok": True}

        monkeypatch.setattr(component_module, "_component", fake_component)
        monkeypatch.setattr(component_module.st, "session_state", {}, raising=False)

        result = component_module.bubble_chat(
            messages=[{"role": "user", "content": "hi"}],
            theme_color="#AABBCC",
            user_icon_bg="#112233",
            name_colors={"Bot": "#ff00ff"},
            assistant_config={"_default": {"icon": "🤖", "avatar_bg": "#000000"}},
            key="chat",
        )
        assert result == {"ok": True}

    def test_empty_and_none_colors_pass(self, component_module, monkeypatch):
        captured: dict[str, object] = {}

        def fake_component(**kwargs):
            captured.update(kwargs)
            return {"ok": True}

        monkeypatch.setattr(component_module, "_component", fake_component)
        monkeypatch.setattr(component_module.st, "session_state", {}, raising=False)

        result = component_module.bubble_chat(
            messages=[{"role": "user", "content": "hi"}],
            theme_color=None,
            user_icon_bg=None,
            assistant_config={"_default": {"icon": "🤖", "avatar_bg": ""}},
            key="chat",
        )
        assert result == {"ok": True}

    def test_key_none_skips_session_state(self, component_module, monkeypatch):
        captured: dict[str, object] = {}

        def fake_component(**kwargs):
            captured.update(kwargs)
            return {"ok": True}

        monkeypatch.setattr(component_module, "_component", fake_component)
        monkeypatch.setattr(
            component_module.st,
            "session_state",
            {"chat": {"is_open": True}},
            raising=False,
        )

        component_module.bubble_chat(
            messages=[{"role": "user", "content": "hi"}],
            key=None,
        )

        # Without a key, is_open/is_maximized should use defaults
        assert captured["data"]["is_open"] is False
        assert captured["data"]["is_maximized"] is False
        assert captured["key"] is None

    def test_second_invalid_message_reports_correct_index(
        self, component_module, monkeypatch
    ):
        monkeypatch.setattr(component_module, "_component", lambda **kw: {"ok": True})
        monkeypatch.setattr(component_module.st, "session_state", {}, raising=False)

        with pytest.raises(ValueError, match=r"messages\[1\]\['role'\] must be one of"):
            component_module.bubble_chat(
                messages=[
                    {"role": "user", "content": "hi"},
                    {"role": "invalid", "content": "bad"},
                ],
                key="chat",
            )
