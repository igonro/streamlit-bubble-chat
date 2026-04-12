"""Streamlit Bubble Chat - A floating chat bubble widget for Streamlit apps."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal

import streamlit as st

_component = st.components.v2.component(
    "streamlit-bubble-chat.bubble_chat",
    js="index-*.js",
    css="styles-*.css",
    html=" ",
    isolate_styles=False,
)

# Default assistant config entry for unnamed assistants
_DEFAULT_ASSISTANT: dict[str, str] = {
    "icon": ":material/robot_2:",
    "avatar_bg": "",
}


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
    """
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

    result = _component(
        data=data,
        default={"is_open": False, "is_maximized": False},
        key=key,
        on_is_open_change=lambda: None,
        on_is_maximized_change=lambda: None,
        on_new_message_change=on_message or (lambda: None),
    )

    return result
