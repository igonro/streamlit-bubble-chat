"""Simple mode example — core features: notifications, system messages, names."""

import streamlit as st
from streamlit_bubble_chat import bubble_chat

st.set_page_config(page_title="Bubble Chat Demo", layout="wide")

st.title("🗨️ Streamlit Bubble Chat — Simple Mode")
st.write(
    "The default `type='simple'` mode — no avatars, clean bubble layout. "
    "Click the chat bubble in the bottom-right corner to explore."
)

# ── Session state setup ──
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": (
                "Welcome! This chat floats in the corner and stays open "
                "across re-renders."
            ),
        },
        {"role": "user", "content": "What about notifications?"},
        {
            "role": "assistant",
            "name": "Helper",
            "content": (
                "When the chat is closed, new messages show an unread "
                "badge on the bubble button."
            ),
        },
        {
            "role": "assistant",
            "name": "Bot",
            "content": (
                "Open the chat and the badge clears. You'll also see a "
                "'New messages' divider."
            ),
        },
        {
            "role": "assistant",
            "content": (
                "You can customise name label colours with name_colors "
                "— check Helper and Bot above!"
            ),
        },
    ]

if "unread" not in st.session_state:
    st.session_state.unread = 2


def handle_new_message():
    """Callback: user submitted a message via the chat widget."""
    text = st.session_state.chat_bubble.new_message
    if not text:
        return
    st.session_state.messages.append({"role": "user", "content": text})
    st.session_state.messages.append(
        {"role": "assistant", "content": f"You said: {text}"}
    )
    st.session_state.unread = 0


# ── Mount the bubble chat component (simple mode — no avatars) ──
result = bubble_chat(
    messages=st.session_state.messages,
    unread_count=st.session_state.unread,
    window_title="Support Chat",
    theme_color="#007AFF",
    name_colors={"Helper": "#e67e22", "Bot": "#2ecc71"},
    key="chat_bubble",
    on_message=handle_new_message,
)

# Reset unread when user has seen messages (chat was opened)
chat_state = st.session_state.get("chat_bubble", {})
if chat_state.get("is_open", False) and st.session_state.unread > 0:
    st.session_state.unread = 0

# ── Demo controls ──
st.divider()
st.subheader("Controls")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("Add assistant message"):
        st.session_state.messages.append(
            {"role": "assistant", "content": "Here is an update from the assistant."}
        )
        chat_state = st.session_state.get("chat_bubble", {})
        if not chat_state.get("is_open", False):
            st.session_state.unread += 1
        st.rerun()

with col2:
    if st.button("Add system message"):
        st.session_state.messages.append(
            {"role": "system", "content": "System: configuration updated."}
        )
        st.rerun()

with col3:
    if st.button("Clear messages"):
        st.session_state.messages = []
        st.session_state.unread = 0
        st.rerun()

with col4:
    if st.button("Set unread = 5"):
        st.session_state.unread = 5
        st.rerun()

st.divider()
st.subheader("Current State")
st.json(
    {
        "messages_count": len(st.session_state.messages),
        "unread": st.session_state.unread,
        "chat_open": st.session_state.get("chat_bubble", {}).get("is_open", False),
        "chat_maximized": st.session_state.get("chat_bubble", {}).get(
            "is_maximized", False
        ),
    }
)
