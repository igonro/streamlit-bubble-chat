# API Reference

## `bubble_chat()`

```python
from streamlit_bubble_chat import bubble_chat

result = bubble_chat(
    messages,
    *,
    type="simple",
    unread_count=0,
    window_title="Chat",
    theme_color=None,
    show_names=True,
    assistant_config=None,
    user_icon=":material/person:",
    user_icon_bg=None,
    name_colors=None,
    key=None,
    on_message=None,
)
```

### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `messages` | `list[dict]` | *required* | List of message dicts. See [Message schema](#message-schema). |
| `type` | `"simple"` \| `"avatar"` | `"simple"` | `"simple"` shows plain bubbles. `"avatar"` adds round icon circles. |
| `unread_count` | `int` | `0` | Badge number on the floating bubble. Hidden when `0`. |
| `window_title` | `str` | `"Chat"` | Text in the chat window header bar. |
| `theme_color` | `str \| None` | `None` | Primary color override (`#RRGGBB`). Falls back to the Streamlit theme primary. |
| `show_names` | `bool` | `True` | Show agent `name` labels above assistant messages. |
| `assistant_config` | `dict[str, dict] \| None` | `None` | Per-agent visual config for avatar mode. See [Assistant config](#assistant-config). |
| `user_icon` | `str` | `":material/person:"` | Icon for the user avatar (avatar mode only). Emoji or `:material/…:`. |
| `user_icon_bg` | `str \| None` | `None` | Background color for the user avatar (`#RRGGBB`). `None` inherits from `theme_color`. |
| `name_colors` | `dict[str, str] \| None` | `None` | Map of `name → color` for the name label above messages. Works in both modes. |
| `key` | `str \| None` | `None` | Streamlit widget key. Required for callbacks and state access. |
| `on_message` | `Callable[[], Any] \| None` | `None` | Callback when the user sends a message. Read text from `st.session_state[key].new_message`. |

### Return value

A component result object with:

- `is_open` (`bool`) — whether the chat window is open.
- `is_maximized` (`bool`) — whether the window is maximized.
- `new_message` (`str`) — the last message sent by the user (trigger value).

Access state at any time via `st.session_state[key]`:

```python
chat_state = st.session_state.get("my_chat", {})
if chat_state.get("is_open"):
    st.write("Chat is open")
```

### Message schema

Each message is a dict with required `role` and `content` keys, and an optional `name`:

```python
{"role": "user", "content": "Hello!"}
{"role": "assistant", "content": "Hi there!", "name": "Guide"}
{"role": "system", "content": "Guide has joined the chat"}
```

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `role` | `str` | Yes | One of `"user"`, `"assistant"`, or `"system"`. |
| `content` | `str` | Yes | Plain text content. HTML and markdown are **not** rendered. |
| `name` | `str` | No | Agent name for multi-agent scenarios. Shown above the bubble when `show_names=True`. |

**Validation**: `bubble_chat()` raises `ValueError` if any message is missing `role` or `content`, or if `role` is not one of the three valid values.

### Roles

| Role | Rendering |
|------|-----------|
| `user` | Right-aligned bubble. In avatar mode, shows user icon circle. |
| `assistant` | Left-aligned bubble. In avatar mode, shows agent icon from `assistant_config`. |
| `system` | Centered pill with reduced opacity. No avatar. Does not count toward `unread_count`. |

### Assistant config

Only used when `type="avatar"`. Maps agent names to their visual configuration:

```python
assistant_config={
    "_default": {
        "icon": "🤖",
        "avatar_bg": "#6366f1",
    },
    "Planner": {
        "icon": ":material/explore:",
        "avatar_bg": "#059669",
        "bubble_bg": "#ecfdf5",
        "bubble_color": "#064e3b",
    },
    "Coder": {
        "icon": ":material/code:",
        "avatar_bg": "#7c3aed",
    },
}
```

| Key | Type | Required | Description |
|-----|------|----------|-------------|
| `icon` | `str` | Yes | Emoji or `:material/icon_name:` string. Built-in default: `:material/robot_2:`. |
| `avatar_bg` | `str` | No | Avatar circle background color (`#RRGGBB`). Empty string inherits from theme. |
| `bubble_bg` | `str` | No | Bubble background color override. |
| `bubble_color` | `str` | No | Bubble text color override. |

Use `"_default"` as the key to customize the fallback for unnamed assistants. Any named assistant not in the config inherits from `"_default"`.

### Color format

All color parameters must be `#RRGGBB` hex strings (e.g., `"#ff5733"`). This applies to:

- `theme_color`
- `user_icon_bg`
- All values in `assistant_config` (`avatar_bg`, `bubble_bg`, `bubble_color`)
- All values in `name_colors`

`bubble_chat()` raises `ValueError` for invalid hex colors. Empty strings (`""`) and `None` are accepted as "no color" / "inherit".

### Callbacks

The `on_message` callback fires when the user sends a message (Enter key or Send button):

```python
def handle_message():
    text = st.session_state.my_chat.new_message
    if not text:
        return
    st.session_state.messages.append({"role": "user", "content": text})
    st.session_state.messages.append(
        {"role": "assistant", "content": f"Echo: {text}"}
    )

bubble_chat(
    messages=st.session_state.messages,
    key="my_chat",
    on_message=handle_message,
)
```

The component also stores `is_open` and `is_maximized` as state values that trigger a Streamlit rerun when they change. You can attach additional callbacks via the result object if needed.

## Limitations

- **Single instance per page**: Only one `bubble_chat()` call per Streamlit page is supported. Multiple calls share the same DOM elements.
- **Text only**: Message content is rendered as plain text via `textContent`. No markdown, HTML, or rich media.
- **Material Icons require CDN**: `:material/…:` icons load the Google Fonts Material Symbols font at runtime. Emoji icons work offline.
- **`key` is needed for state**: Without a `key`, `is_open` / `is_maximized` won't persist across reruns and `on_message` can't read the submitted text.
