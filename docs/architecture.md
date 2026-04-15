# Architecture

This document explains the non-obvious design decisions in `streamlit-bubble-chat` and how the frontend works under the hood.

## Overview

```
┌───────────────────────────────────────────────────┐
│  Python (bubble_chat)                             │
│  • validates inputs                               │
│  • merges assistant_config with defaults          │
│  • reads is_open / is_maximized from session_state│
│  • calls st.components.v2.component(data=…)       │
└──────────────────────┬────────────────────────────┘
                       │  serialized JSON
                       ▼
┌───────────────────────────────────────────────────┐
│  TypeScript (FrontendRenderer)                    │
│  • receives BubbleChatData                        │
│  • builds/updates body-level DOM singletons       │
│  • sends state back via setStateValue/Trigger     │
└──────────────────────┬────────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────────┐
│  DOM (document.body)                              │
│  • .stbc-root   (bubble button + badge)           │
│  • .stbc-window (chat panel)                      │
│  • .stbc-backdrop (maximized overlay)             │
└───────────────────────────────────────────────────┘
```

## Why `isolate_styles=False`

Streamlit's v2 component API supports `isolate_styles=True` (the default), which wraps the component in a shadow DOM or iframe. This prevents CSS leaks but also means the component is confined to a small inline area in the page layout.

`streamlit-bubble-chat` needs a **floating UI** — a bubble button pinned to the bottom-right corner and a chat window that overlays the page. This is incompatible with style isolation, so the component opts out with `isolate_styles=False` and `html=" "` (a space, not empty, to prevent iframe wrapping).

## Body-level DOM singletons

The visible chat UI (bubble button, chat window, backdrop) lives directly on `document.body`, **not** inside the component's `parentElement`.

**Why**: Streamlit destroys and recreates component containers during rapid fragment reruns. If the chat window lived inside `parentElement`, it would flicker or reset every time Streamlit reruns. By placing the UI on `document.body`, it survives these mount/unmount cycles.

**Consequences**:
- Only **one set** of DOM elements exists per page (`.stbc-root`, `.stbc-window`, `.stbc-backdrop`). This is why multiple `bubble_chat()` calls share the same visible UI.
- The component uses `parentElement` only as a read-only source for Streamlit theme CSS variables, which are then copied onto the body-level elements.
- Cleanup is a no-op — the elements persist intentionally.

## Persistent CSS injection

Streamlit removes the component's `<style>` tag when it briefly unmounts during reruns. Since the visible elements live on `document.body` (outside the component tree), they lose all styling when this happens.

To solve this, the component injects a persistent `<style id="stbc-persistent-css">` element into `<head>` on first render. This copy is never removed by Streamlit's lifecycle, ensuring the floating UI remains styled across all reruns.

## First-render gate (`data-stbc-init`)

Python sends `is_open` and `is_maximized` on every rerun, but after the first render, the **DOM is the source of truth** for visual state. If the user opens the chat and Streamlit reruns, the Python-side `is_open` might still be `False` (stale echo).

The component sets `data-stbc-init="true"` on the window element after the first render. On subsequent renders, it reads the open/maximized state from DOM classes (`stbc-open`, `stbc-maximized`) instead of from Python data.

## State synchronization

The component uses Streamlit's bidirectional state API:

| API | Used for | Behavior |
|-----|----------|----------|
| `setStateValue("is_open", bool)` | Open/close state | Persists across reruns. Triggers `on_is_open_change`. |
| `setStateValue("is_maximized", bool)` | Maximize state | Persists across reruns. Triggers `on_is_maximized_change`. |
| `setTriggerValue("new_message", text)` | User-submitted text | One-shot value. Triggers `on_new_message_change` (the `on_message` callback). Cleared after read. |

**State values** (`is_open`, `is_maximized`) persist in `st.session_state[key]` and survive reruns.

**Trigger values** (`new_message`) fire the callback once and are consumed. They don't accumulate.

## APCA contrast algorithm

Avatar circles need a text color (for the icon/emoji overlay) that is readable against the background color. Instead of a simple luminance threshold, the component uses **APCA 0.0.98G-4g** (Accessible Perceptual Contrast Algorithm), which accounts for the asymmetry between dark-on-light and light-on-dark text.

The algorithm:
1. Converts the background hex color to linear sRGB luminance (Y).
2. Computes `|Lc(white, bg)|` and `|Lc(black, bg)|` — the perceptual contrast of white and black text against the background.
3. Picks whichever has higher contrast.

This produces correct results across all themes without needing to detect dark/light mode.

Reference: [APCA W3](https://github.com/Myndex/apca-w3)

## Theme variable sync

Streamlit defines CSS custom properties (`--st-background-color`, `--st-text-color`, `--st-primary-color`, etc.) on the component's ancestor elements. Since the chat UI lives on `document.body` (outside the component tree), these variables aren't inherited.

The `syncThemeVars()` function reads the computed values from `parentElement` and copies them onto the body-level elements:

```
parentElement (Streamlit theme vars defined here)
    │
    └── reads via getComputedStyle()
            │
            ├── .stbc-root     (copies vars here)
            ├── .stbc-window   (copies vars here)
            └── .stbc-backdrop (copies vars here)
```

This runs on every render, so theme changes (e.g., switching dark/light mode) propagate immediately.

## Frontend modules

The TypeScript source is split into focused modules:

| Module | Responsibility |
|--------|---------------|
| `index.ts` | Slim entry point — wires modules together, handles events. |
| `types.ts` | TypeScript interfaces (`BubbleChatData`, `Message`, `AssistantConfig`). |
| `dom.ts` | Creates body-level singletons, sets ARIA attributes, manages window state. |
| `messages.ts` | Renders message bubbles, avatars, names, unread divider. |
| `contrast.ts` | APCA algorithm for auto-selecting white/black text on colored backgrounds. |
| `icons.ts` | SVG icon constants, Material Symbols font loader, icon renderer. |
| `theme.ts` | Copies Streamlit CSS variables onto body-level elements. |

Vite bundles everything into a single `index-[hash].js` and `styles-[hash].css`. The Python side globs for these files.

## Accessibility

The component includes:

- `role="dialog"` and `aria-labelledby` on the chat window.
- `aria-label` on all interactive elements (bubble button, close, maximize, send, input).
- `aria-expanded` on the bubble button, synced with open state.
- `aria-controls` linking the bubble button to the chat window.
- `aria-live="polite"` on the unread badge.
- `aria-modal="true"` when the window is maximized.
- Escape key closes the window (or exits maximized mode first).
- Focus moves to the input when opening, and back to the bubble button when closing.
