"""Avatar mode example — distinct agent avatars with Material Icons."""

import random

import streamlit as st
from streamlit_bubble_chat import bubble_chat

st.set_page_config(page_title="Avatar Chat", layout="wide")

st.title("🎨 Avatar Chat Mode")
st.write(
    "This example uses `type='avatar'` to show a round avatar circle "
    "next to each message. Agents are configured via `assistant_config` "
    "with Material Icons or emoji, each with a custom background colour."
)

# ── Assistant configuration (keyed by message `name`) ──
ASSISTANT_CONFIG = {
    "_default": {"icon": ":material/smart_toy:", "avatar_bg": "#6b7280"},
    "Guide": {"icon": ":material/explore:", "avatar_bg": "#ff6a00"},
    "Designer": {"icon": "🎨", "avatar_bg": "#7c3aed"},
    "Dev": {"icon": ":material/code:", "avatar_bg": "#059669"},
    "Tester": {"icon": ":material/bug_report:", "avatar_bg": "#dc2626"},
}

AGENT_NAMES = ["Guide", "Designer", "Dev", "Tester"]

# ── Session state ──
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Welcome to the avatar chat demo."},
        {
            "role": "assistant",
            "name": "Guide",
            "content": (
                "In avatar mode each assistant gets a round icon next to "
                "their messages."
            ),
        },
        {
            "role": "assistant",
            "name": "Designer",
            "content": (
                "You can use any emoji as the avatar icon — like this paint palette 🎨."
            ),
        },
        {
            "role": "assistant",
            "name": "Dev",
            "content": (
                "Or use Material Symbols with the :material/icon_name: "
                "syntax for a clean look."
            ),
        },
        {
            "role": "assistant",
            "name": "Tester",
            "content": (
                "Each agent has its own avatar_bg colour. The icon colour "
                "adapts automatically for contrast."
            ),
        },
        {
            "role": "assistant",
            "name": "Guide",
            "content": (
                "System messages appear as centered pills — no avatar, no "
                'name. Try the button "Add system message"!'
            ),
        },
    ]

if "unread" not in st.session_state:
    st.session_state.unread = 0


def handle_message():
    """User sent a message — simulate a random agent responding."""
    text = st.session_state.chat.new_message
    if not text:
        return
    st.session_state.messages.append({"role": "user", "content": text})

    # Pick a random agent to respond
    agent = random.choice(AGENT_NAMES)
    responses = {
        "Guide": f'Got it — I\'ll walk you through "{text}".',
        "Designer": f'Let me sketch something for "{text}".',
        "Dev": f'I can implement that. Working on "{text}"…',
        "Tester": f'I\'ll write tests for "{text}".',
    }
    st.session_state.messages.append(
        {"role": "assistant", "name": agent, "content": responses[agent]}
    )
    st.session_state.unread = 0


# ── Mount component (avatar mode) ──
result = bubble_chat(
    messages=st.session_state.messages,
    type="avatar",
    unread_count=st.session_state.unread,
    window_title="Agent Team",
    theme_color="#7c3aed",
    assistant_config=ASSISTANT_CONFIG,
    key="chat",
    on_message=handle_message,
)

# Reset unread when chat is open
chat_state = st.session_state.get("chat", {})
if chat_state.get("is_open", False) and st.session_state.unread > 0:
    st.session_state.unread = 0

# ── Demo controls ──
st.divider()
st.subheader("Simulate Agent Messages")

cols = st.columns(len(AGENT_NAMES))
for col, agent in zip(cols, AGENT_NAMES, strict=True):
    cfg = ASSISTANT_CONFIG[agent]
    with col:
        if st.button(f"{cfg['icon']} {agent}"):
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "name": agent,
                    "content": f"[{agent}] Here's an update from me.",
                }
            )
            if not chat_state.get("is_open", False):
                st.session_state.unread += 1
            st.rerun()

st.divider()
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Add assistant message"):
        st.session_state.messages.append(
            {"role": "assistant", "content": "Here is an update from the assistant."}
        )
        chat_state = st.session_state.get("chat", {})
        if not chat_state.get("is_open", False):
            st.session_state.unread += 1
        st.rerun()
with col2:
    if st.button("Add system message"):
        st.session_state.messages.append(
            {"role": "system", "content": "System: checkpoint saved."}
        )
        st.rerun()
with col3:
    if st.button("Clear all"):
        st.session_state.messages = []
        st.session_state.unread = 0
        st.rerun()

st.divider()
st.subheader("State")
st.json(
    {
        "messages_count": len(st.session_state.messages),
        "unread": st.session_state.unread,
        "chat_open": chat_state.get("is_open", False),
        "agents_in_chat": sorted(
            {m.get("name", "") for m in st.session_state.messages if m.get("name")}
        ),
    }
)
