import type {
  FrontendRenderer,
  FrontendRendererArgs,
} from "@streamlit/component-v2-lib";
import "./styles.css";

import type { BubbleChatData } from "./types";
import { contrastColor } from "./contrast";
import { ensureMaterialFont } from "./icons";
import { syncThemeVars } from "./theme";
import { ensurePersistentStyles, ensureBodyElements, applyWindowState } from "./dom";
import { renderMessages } from "./messages";

/* ─── Main Component ─── */

const BubbleChat: FrontendRenderer = (
  args: FrontendRendererArgs,
) => {
  const { parentElement, data, setStateValue, setTriggerValue } = args;
  const d = data as BubbleChatData;

  ensureMaterialFont();
  ensurePersistentStyles();

  // All visible UI lives in body-level singletons — immune to
  // parentElement destruction during rapid Streamlit fragment reruns.
  const { root, win, backdrop } = ensureBodyElements();

  // Use parentElement only for reading Streamlit theme variables.
  syncThemeVars(parentElement as HTMLElement, root, win, backdrop);

  // Apply custom theme color + auto-contrast foreground
  if (d.theme_color) {
    const fg = contrastColor(d.theme_color);
    root.style.setProperty("--stbc-theme-color", d.theme_color);
    root.style.setProperty("--stbc-theme-fg", fg);
    win.style.setProperty("--stbc-theme-color", d.theme_color);
    win.style.setProperty("--stbc-theme-fg", fg);
    backdrop.style.setProperty("--stbc-theme-color", d.theme_color);
  } else {
    root.style.removeProperty("--stbc-theme-color");
    root.style.removeProperty("--stbc-theme-fg");
  }

  // Apply Python state ONLY on the very first render (initial open/close).
  // After that, the DOM is the source of truth — user interactions set
  // classes directly, and we never let stale Python echoes override them.
  if (!win.hasAttribute("data-stbc-init")) {
    win.setAttribute("data-stbc-init", "true");
    applyWindowState(win, backdrop, d.is_open, d.is_maximized);
  }

  // Read visual state from DOM (immune to Python echo lag)
  const isOpen = win.classList.contains("stbc-open");

  // Detect "just opened" transition for scroll targeting
  const wasOpen = root.getAttribute("data-was-open") === "true";
  root.setAttribute("data-was-open", String(isOpen));
  const justOpened = isOpen && !wasOpen;

  // Title
  const titleEl = win.querySelector(".stbc-header-title") as HTMLElement;
  titleEl.textContent = d.window_title;

  // Badge: hide when chat window is open
  const badge = root.querySelector(".stbc-badge") as HTMLElement;
  if (d.unread_count > 0 && !isOpen) {
    badge.textContent = d.unread_count > 99 ? "99+" : String(d.unread_count);
    badge.classList.remove("stbc-hidden");
  } else {
    badge.classList.add("stbc-hidden");
  }

  // Messages (returns divider element if unread messages exist)
  const dividerEl = renderMessages(root, d.messages, d.unread_count, d);

  // Scroll: to divider on open, to bottom on new messages
  const messagesContainer = win.querySelector(".stbc-messages") as HTMLElement;
  requestAnimationFrame(() => {
    if (justOpened && dividerEl) {
      dividerEl.scrollIntoView({ behavior: "smooth", block: "start" });
    } else if (isOpen) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  });

  // ── Event handlers ──

  const bubbleBtn = root.querySelector(".stbc-bubble-btn") as HTMLElement;
  const closeBtn = win.querySelector(".stbc-close-btn") as HTMLElement;
  const maxBtn = win.querySelector(".stbc-maximize-btn") as HTMLElement;
  const input = win.querySelector(".stbc-input") as HTMLInputElement;
  const sendBtn = win.querySelector(".stbc-send-btn") as HTMLButtonElement;

  // Open/close bubble
  bubbleBtn.onclick = () => {
    const nowOpen = !win.classList.contains("stbc-open");
    applyWindowState(win, backdrop, nowOpen, false);
    setStateValue("is_open", nowOpen);
    if (!nowOpen && win.classList.contains("stbc-maximized")) {
      setStateValue("is_maximized", false);
    }
    if (nowOpen) {
      requestAnimationFrame(() => input.focus());
    }
  };

  // Close via header button
  closeBtn.onclick = () => {
    const wasMaximized = win.classList.contains("stbc-maximized");
    applyWindowState(win, backdrop, false, false);
    setStateValue("is_open", false);
    if (wasMaximized) {
      setStateValue("is_maximized", false);
    }
    // Restore focus to the bubble button after closing
    requestAnimationFrame(() => bubbleBtn.focus());
  };

  // Maximize toggle
  maxBtn.onclick = () => {
    const nowMaximized = !win.classList.contains("stbc-maximized");
    applyWindowState(win, backdrop, true, nowMaximized);
    setStateValue("is_maximized", nowMaximized);
  };

  // Backdrop click → close maximized (go to minimized)
  backdrop.onclick = () => {
    applyWindowState(win, backdrop, true, false);
    setStateValue("is_maximized", false);
  };

  // Escape key → close window (or exit maximized first)
  win.onkeydown = (e: KeyboardEvent) => {
    if (e.key === "Escape") {
      e.preventDefault();
      const isMaxed = win.classList.contains("stbc-maximized");
      if (isMaxed) {
        applyWindowState(win, backdrop, true, false);
        setStateValue("is_maximized", false);
      } else {
        applyWindowState(win, backdrop, false, false);
        setStateValue("is_open", false);
        requestAnimationFrame(() => bubbleBtn.focus());
      }
    }
  };

  // Send message
  const doSend = () => {
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    setTriggerValue("new_message", text);
  };

  sendBtn.onclick = doSend;

  input.onkeydown = (e: KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      doSend();
    }
  };

  // Focus input when opening
  if (isOpen) {
    requestAnimationFrame(() => input.focus());
  }

  // Cleanup: no-op — all visible UI lives in body-level singletons
  // that persist across Streamlit mount/unmount cycles.
  return () => {};
};

export default BubbleChat;
