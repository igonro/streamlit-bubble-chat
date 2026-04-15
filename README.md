# Streamlit Bubble Chat

<p align="center">
  <strong>Floating chat bubble UI for Streamlit apps.</strong><br />
  Add a persistent chat window with unread badges, system messages, and optional agent avatars.
</p>

<p align="center">
  <a href="https://github.com/igonro/streamlit-bubble-chat/actions/workflows/ci.yml"><img alt="CI" src="https://github.com/igonro/streamlit-bubble-chat/actions/workflows/ci.yml/badge.svg"></a>
  <img alt="Python 3.10+" src="https://img.shields.io/badge/python-3.10%2B-3776AB?logo=python&logoColor=white">
  <img alt="Streamlit component" src="https://img.shields.io/badge/streamlit-component-FF4B4B?logo=streamlit&logoColor=white">
  <img alt="uv build backend" src="https://img.shields.io/badge/build-uv__build-4CC61E">
  <img alt="License: MIT" src="https://img.shields.io/badge/license-MIT-1F6FEB">
</p>

<p align="center">
  <a href="https://github.com/igonro/streamlit-bubble-chat">Source</a>
  ·
  <a href="https://github.com/igonro/streamlit-bubble-chat/blob/main/CONTRIBUTING.md">Contributing</a>
</p>

<p align="center">
  <img src="https://raw.githubusercontent.com/igonro/streamlit-bubble-chat/main/docs/images/demo.gif" alt="Bubble chat demo" width="800" />
</p>

`streamlit-bubble-chat` is a drop-in component for adding a floating chat window
to a Streamlit app. It works well for support flows, assistant side panels, and
multi-agent demos where you want the chat UI available without rearranging the
rest of the page.

## Installation

```bash
uv add streamlit-bubble-chat
```

Or with `pip`:

```bash
pip install streamlit-bubble-chat
```

## Quick start

```python
import streamlit as st

from streamlit_bubble_chat import bubble_chat


if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hello. How can I help?"},
    ]


def handle_message() -> None:
    text = st.session_state.support_chat.new_message
    if not text:
        return

    st.session_state.messages.append({"role": "user", "content": text})
    st.session_state.messages.append(
        {"role": "assistant", "content": f"Echo: {text}"}
    )


bubble_chat(
    messages=st.session_state.messages,
    key="support_chat",
    on_message=handle_message,
)
```

## Core arguments

```python
bubble_chat(
    messages,
    *,
    type="simple",
    unread_count=0,
    window_title="Chat",
    theme_color=None,
    assistant_config=None,
    name_colors=None,
    key=None,
    on_message=None,
)
```

Each message is a dictionary with `role`, `content`, and an optional `name`:

```python
{"role": "assistant", "content": "Hello", "name": "Guide"}
```

Inside `on_message`, read the submitted text from `st.session_state[key].new_message`.
The component also stores `is_open` and `is_maximized` in the same session-state entry.

All color parameters (`theme_color`, `user_icon_bg`, values in `assistant_config` and
`name_colors`) must be `#RRGGBB` hex strings — invalid values raise `ValueError`.

## Documentation

- [API Reference](https://github.com/igonro/streamlit-bubble-chat/blob/main/docs/api-reference.md) — full parameter docs, message schema, assistant config, limitations.
- [Architecture](https://github.com/igonro/streamlit-bubble-chat/blob/main/docs/architecture.md) — design decisions, state sync, frontend modules.
- [Customization](https://github.com/igonro/streamlit-bubble-chat/blob/main/docs/customization.md) — theming, avatars, colors, dark mode, CSS classes.

## What you get

- Floating chat bubble anchored to the bottom-right corner.
- `simple` mode for a clean message list.
- `avatar` mode for named assistants with emoji or `:material/...:` icons.
- Unread badges and an unread divider when new messages arrive.
- System messages rendered as centered pills.
- Theme-aware styling plus optional color overrides.
- User and assistant avatar customization.

## Examples

| Example | What it shows | Command |
| --- | --- | --- |
| `examples/base_chat.py` | Simple mode, unread badges, system messages, name colors | `uv run streamlit run examples/base_chat.py` |
| `examples/avatar_chat.py` | Avatar mode, multiple assistants, Material icons, custom avatar colors | `uv run streamlit run examples/avatar_chat.py` |

If you need fresh frontend assets first:

```bash
make build-frontend
```

## Limitations

- **Single instance per page** — only one `bubble_chat()` per Streamlit page. Multiple calls share the same DOM.
- **Text only** — message content is plain text. No markdown, HTML, or media rendering.
- **Material Icons need internet** — `:material/…:` icons load from Google Fonts CDN. Emoji icons work offline.

## Development

```bash
make setup
make check
make test
make build
```

`make setup` installs Python dependencies with `uv`, frontend dependencies with
`npm ci`, and the configured git hooks with `prek`.

## Contributing

Contribution guidelines live in [CONTRIBUTING.md](https://github.com/igonro/streamlit-bubble-chat/blob/main/CONTRIBUTING.md).

## Disclaimer

This project was built primarily with AI assistance. If you spot artifacts,
inconsistencies, or things that don't make sense, please open an issue.

## License

Released under the [MIT License](https://github.com/igonro/streamlit-bubble-chat/blob/main/LICENSE).
