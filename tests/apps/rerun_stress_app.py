"""Stress-test example: rapid reruns that exercise component mount/unmount cycles.

This example simulates the conditions in the dashboard_agent app where
``@st.fragment(run_every=0.4)`` combined with ``st.rerun()`` can cause
the bubble chat component to be rapidly unmounted and remounted.

Used by ``tests/test_e2e_rerun_stress.py`` to verify the bubble button
survives rapid rerun cycles.
"""

from __future__ import annotations

import streamlit as st
from streamlit_bubble_chat import bubble_chat

st.set_page_config(page_title="Rerun Stress Test", layout="wide")

# ── Session state setup ──
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Session started"},
        {"role": "assistant", "content": "Hello! This is a rerun stress test."},
    ]

if "unread" not in st.session_state:
    st.session_state.unread = 1

if "rerun_counter" not in st.session_state:
    st.session_state.rerun_counter = 0


def handle_message():
    text = st.session_state.stress_chat.new_message
    if not text:
        return
    st.session_state.messages.append({"role": "user", "content": text})
    st.session_state.messages.append({"role": "assistant", "content": f"Echo: {text}"})
    st.session_state.unread = 0


# ── A rapidly-rerunning fragment (like dashboard_agent's _await_agent_response) ──
@st.fragment(run_every=0.4)
def tick_fragment():
    """Simulates the polling fragment that triggers frequent partial reruns."""
    st.session_state.rerun_counter += 1
    st.caption(f"Fragment tick: {st.session_state.rerun_counter}")


st.title("Rerun Stress Test")

# Render the fragment (causes partial reruns every 0.4s)
tick_fragment()

# Render the bubble chat widget
bubble_chat(
    messages=st.session_state.messages,
    unread_count=st.session_state.unread,
    key="stress_chat",
    window_title="Stress Test Chat",
    theme_color="#007AFF",
    on_message=handle_message,
)

# Reset unread when user opens the chat
chat_state = st.session_state.get("stress_chat", {})
if chat_state.get("is_open", False) and st.session_state.unread > 0:
    st.session_state.unread = 0
