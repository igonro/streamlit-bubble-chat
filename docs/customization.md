# Customization

## Theme color

Set `theme_color` to override the primary accent color used for the bubble button, header bar, and user bubbles:

```python
bubble_chat(
    messages=messages,
    theme_color="#6366f1",
    key="chat",
)
```

When `theme_color` is `None` (default), the component inherits the Streamlit theme's `--st-primary-color`.

The text color on themed elements (button icon, header text) is automatically selected as white or black based on the APCA perceptual contrast algorithm.

## Avatar mode

Set `type="avatar"` to show round icon circles next to each message:

```python
bubble_chat(
    messages=messages,
    type="avatar",
    assistant_config={
        "_default": {"icon": "🤖", "avatar_bg": "#6366f1"},
        "Guide": {
            "icon": ":material/explore:",
            "avatar_bg": "#059669",
        },
        "Coder": {
            "icon": ":material/code:",
            "avatar_bg": "#7c3aed",
            "bubble_bg": "#f5f3ff",
            "bubble_color": "#4c1d95",
        },
    },
    user_icon="😊",
    user_icon_bg="#3b82f6",
    key="chat",
)
```

### Icons

Two formats are supported:

| Format | Example | Requirement |
|--------|---------|-------------|
| Emoji | `"🤖"`, `"😊"`, `"🎨"` | Works offline, always available. |
| Material Symbols | `":material/explore:"`, `":material/code:"` | Requires Google Fonts CDN (loaded at runtime). |

Material Symbols use the same naming convention as Streamlit's icon support. Browse available icons at [fonts.google.com/icons](https://fonts.google.com/icons).

### Per-agent colors

Each named assistant can have its own avatar background and bubble colors:

```python
assistant_config={
    "Planner": {
        "icon": ":material/explore:",
        "avatar_bg": "#059669",      # green avatar circle
        "bubble_bg": "#ecfdf5",      # light green bubble
        "bubble_color": "#064e3b",   # dark green text
    },
}
```

Agents not listed in `assistant_config` inherit from `"_default"`. The built-in default uses `:material/robot_2:` with the theme background.

### User avatar

```python
bubble_chat(
    messages=messages,
    type="avatar",
    user_icon="😊",        # or ":material/person:"
    user_icon_bg="#3b82f6", # blue background
    key="chat",
)
```

When `user_icon_bg` is `None`, it inherits from `theme_color`.

## Name colors

Color the agent name label above messages. Works in both `"simple"` and `"avatar"` modes:

```python
bubble_chat(
    messages=messages,
    name_colors={
        "Guide": "#059669",
        "Coder": "#7c3aed",
    },
    key="chat",
)
```

In avatar mode, if a name is not in `name_colors`, the `avatar_bg` from `assistant_config` is used as fallback.

## Dark and light mode

The component inherits Streamlit's theme automatically. These CSS variables are synced from the Streamlit theme to the chat UI:

- `--st-background-color`
- `--st-text-color`
- `--st-primary-color`
- `--st-border-color`
- `--st-secondary-background-color`
- `--st-font`

Switching themes in Streamlit updates the chat UI immediately on the next rerun.

## Unread badge

Show a notification count on the floating bubble:

```python
bubble_chat(
    messages=messages,
    unread_count=3,
    key="chat",
)
```

The badge hides automatically when the chat window is open. System messages do not count toward the unread total — if you track unread count manually, skip messages with `role="system"`.

Values above 99 display as `"99+"`.

## CSS classes

The component uses `.stbc-*` prefixed CSS classes. These are stable and can be used for custom styling if needed:

| Class | Element |
|-------|---------|
| `.stbc-root` | Container for the bubble button |
| `.stbc-bubble-btn` | The floating bubble button |
| `.stbc-badge` | Unread count badge |
| `.stbc-window` | Chat window panel |
| `.stbc-header` | Window header bar |
| `.stbc-messages` | Messages scroll container |
| `.stbc-msg` | Any message row |
| `.stbc-msg-user` | User message |
| `.stbc-msg-assistant` | Assistant message |
| `.stbc-msg-system` | System message (centered pill) |
| `.stbc-avatar` | Avatar circle |
| `.stbc-msg-name` | Agent name label |
| `.stbc-unread-divider` | "New messages" divider line |
| `.stbc-input` | Text input field |
| `.stbc-send-btn` | Send button |

## Mobile

The chat window includes `safe-area-inset` padding for mobile devices with notches or rounded corners. On screens narrower than 480px, the window expands to full width.
