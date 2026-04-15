"""Streamlit Bubble Chat - A floating chat bubble widget for Streamlit apps.

.. warning::

    This component renders as a **single global instance** per page.
    Mounting multiple ``bubble_chat()`` calls in the same page will cause
    them to share the same visible DOM elements (bubble, window, backdrop).
    Only one ``bubble_chat()`` per page is supported.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from typing import Any, Literal, TypedDict

import streamlit as st
from streamlit.errors import StreamlitAPIException

_COMPONENT_NAME = "streamlit-bubble-chat.bubble_chat"
_COMPONENT_JS_GLOB = "index-*.js"
_COMPONENT_CSS_GLOB = "styles-*.css"

_component: Callable[..., Any] | None = None

# Default assistant config entry for unnamed assistants
_DEFAULT_ASSISTANT: dict[str, str] = {
    "icon": ":material/robot_2:",
    "avatar_bg": "",
}

_HEX_COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
_VALID_ROLES = {"user", "assistant", "system"}


# ── Public types ──


class MessageDict(TypedDict, total=False):
    """Schema for a single chat message.

    Required keys: ``role``, ``content``.
    Optional keys: ``name`` (agent name for multi-agent scenarios).
    """

    role: str  # "user" | "assistant" | "system"
    content: str
    name: str


class AssistantVisualConfig(TypedDict, total=False):
    """Visual configuration for an assistant in avatar mode.

    Required keys: ``icon``.
    Optional keys: ``avatar_bg``, ``bubble_bg``, ``bubble_color``.
    """

    icon: str
    avatar_bg: str
    bubble_bg: str
    bubble_color: str


# ── Validation helpers ──


def _validate_hex_color(value: str | None, param_name: str) -> None:
    """Raise ``ValueError`` if *value* is not a valid ``#RRGGBB`` hex color."""
    if value is not None and value != "" and not _HEX_COLOR_RE.match(value):
        raise ValueError(
            f"{param_name} must be a valid #RRGGBB hex color, got: {value!r}"
        )


def _validate_messages(messages: list[dict[str, str]]) -> None:
    """Raise ``ValueError`` for invalid message dicts."""
    for i, msg in enumerate(messages):
        if "role" not in msg:
            raise ValueError(f"messages[{i}] is missing required key 'role'")
        if msg["role"] not in _VALID_ROLES:
            raise ValueError(
                f"messages[{i}]['role'] must be one of {_VALID_ROLES}, "
                f"got: {msg['role']!r}"
            )
        if "content" not in msg:
            raise ValueError(f"messages[{i}] is missing required key 'content'")


def _create_component() -> Callable[..., Any]:
    return st.components.v2.component(
        _COMPONENT_NAME,
        js=_COMPONENT_JS_GLOB,
        css=_COMPONENT_CSS_GLOB,
        html=" ",
        isolate_styles=False,
    )


def _get_component() -> Callable[..., Any]:
    global _component

    if _component is not None:
        return _component

    try:
        _component = _create_component()
    except StreamlitAPIException as exc:
        if "must be declared in pyproject.toml with asset_dir" not in str(exc):
            raise

        # When registration happens before runtime bootstrap, explicitly scan
        # installed manifests and retry once.
        from streamlit.components.v2.get_bidi_component_manager import (
            get_bidi_component_manager,
        )

        manager = get_bidi_component_manager()
        manager.discover_and_register_components(start_file_watching=False)
        _component = _create_component()

    return _component


def bubble_chat(
    messages: list[dict[str, str]],
    *,
    type: Literal["simple", "avatar"] = "simple",
    unread_count: int = 0,
    window_title: str = "Chat",
    theme_color: str | None = None,
    show_names: bool = True,
    assistant_config: dict[str, dict[str, str]] | None = None,
    user_icon: str = ":material/person:",
    user_icon_bg: str | None = None,
    name_colors: dict[str, str] | None = None,
    key: str | None = None,
    on_message: Callable[[], Any] | None = None,
) -> Any:
    """Render a floating chat bubble widget.

    Args:
        messages: List of message dicts with ``role`` (``"user"`` /
            ``"assistant"`` / ``"system"``) and ``content`` keys.  For
            multi-agent scenarios, include an optional ``name`` key
            (e.g. ``{"role": "assistant", "name": "Planner", ...}``).
        type: Widget variant.

            - ``"simple"`` — no avatars, classic bubble layout.  Agent
              names (if present) are shown above the bubble.
            - ``"avatar"`` — each message shows a round avatar circle
              with an icon (emoji or Material Icon).
        unread_count: Number shown on the notification badge.  Hidden
            when 0.
        window_title: Title displayed in the chat window header.
        theme_color: Optional hex colour (e.g. ``"#6366f1"``).  Falls
            back to the Streamlit theme primary colour.
        show_names: Whether to display the agent ``name`` above
            assistant messages.  Defaults to ``True``.  Only visible
            when messages carry a ``name`` field.
        assistant_config: Only used when *type* is ``"avatar"``.  Dict
            mapping assistant **name** values to their visual config:

            - ``icon`` — emoji or ``:material/icon_name:`` string.
            - ``avatar_bg`` — background colour for the avatar circle (hex).
            - ``bubble_bg`` — *(optional)* bubble background colour.
            - ``bubble_color`` — *(optional)* bubble text colour.

            Use the key ``"_default"`` to customise the fallback for
            unnamed assistants.  The built-in default is ``🤖`` with
            the theme background.
        user_icon: Icon for the user avatar (``"avatar"`` mode only).
            Supports emoji or ``:material/…:`` strings.  Default ``👤``.
        user_icon_bg: Background colour for the user avatar circle.
            ``None`` inherits from ``theme_color``.
        name_colors: Optional dict mapping assistant ``name`` → CSS colour
            string for the name label above the message.  Works in both
            *simple* and *avatar* modes.  Names not in the dict keep
            their default colour.  In *avatar* mode the ``avatar_bg``
            from ``assistant_config`` is used as fallback when a name
            is not present in ``name_colors``.
        key: Unique key for this component instance.
        on_message: Callback invoked when the user submits a message.
            Read the submitted text from
            ``st.session_state[key].new_message``.

    Returns:
        Component result object with ``.is_open``, ``.is_maximized``,
        and ``.new_message`` attributes.

    Raises:
        ValueError: If *theme_color*, any color in *assistant_config*,
            *user_icon_bg*, or *name_colors* values are not valid
            ``#RRGGBB`` hex strings.
        ValueError: If any message dict is missing ``role`` or ``content``,
            or contains an invalid ``role``.
    """
    # ── Input validation ──
    _validate_messages(messages)
    _validate_hex_color(theme_color, "theme_color")
    _validate_hex_color(user_icon_bg, "user_icon_bg")

    for cfg_name, cfg in (assistant_config or {}).items():
        _validate_hex_color(
            cfg.get("avatar_bg"), f"assistant_config[{cfg_name!r}].avatar_bg"
        )
        _validate_hex_color(
            cfg.get("bubble_bg"), f"assistant_config[{cfg_name!r}].bubble_bg"
        )
        _validate_hex_color(
            cfg.get("bubble_color"), f"assistant_config[{cfg_name!r}].bubble_color"
        )

    for nc_name, nc_color in (name_colors or {}).items():
        _validate_hex_color(nc_color, f"name_colors[{nc_name!r}]")

    # Merge assistant configs with defaults
    merged_assistant: dict[str, dict[str, str]] = {
        "_default": {**_DEFAULT_ASSISTANT},
    }
    for name, cfg in (assistant_config or {}).items():
        if name == "_default":
            merged_assistant["_default"] = {**_DEFAULT_ASSISTANT, **cfg}
        else:
            merged_assistant[name] = {**_DEFAULT_ASSISTANT, **cfg}

    component_state = st.session_state.get(key, {}) if key else {}
    is_open = component_state.get("is_open", False)
    is_maximized = component_state.get("is_maximized", False)

    data = {
        "messages": messages,
        "type": type,
        "unread_count": unread_count,
        "window_title": window_title,
        "theme_color": theme_color,
        "show_names": show_names,
        "assistant_config": merged_assistant,
        "user_icon": user_icon,
        "user_icon_bg": user_icon_bg or "",
        "name_colors": name_colors or {},
        "is_open": is_open,
        "is_maximized": is_maximized,
    }

    component = _get_component()

    result = component(
        data=data,
        default={"is_open": False, "is_maximized": False},
        key=key,
        on_is_open_change=lambda: None,
        on_is_maximized_change=lambda: None,
        on_new_message_change=on_message or (lambda: None),
    )

    return result
