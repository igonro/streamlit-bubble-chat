/* ─── DOM Builder ─── */

import cssText from "./styles.css?inline";
import { ICON_CHAT, ICON_CLOSE, ICON_MAXIMIZE, ICON_MINIMIZE, ICON_SEND } from "./icons";

/**
 * Inject a persistent copy of the component's full CSS into <head>.
 * Streamlit removes the component's <style> tag when it briefly unmounts
 * during reruns.  Body-level singletons lose all styling (positioning,
 * visibility, decoration) when that happens.  This persistent copy
 * ensures styles survive across mount/unmount cycles.
 */
export function ensurePersistentStyles(): void {
  if (document.getElementById("stbc-persistent-css")) return;
  const s = document.createElement("style");
  s.id = "stbc-persistent-css";
  s.textContent = cssText;
  document.head.appendChild(s);
}

/**
 * Ensure ALL body-level singletons exist (root + window + backdrop).
 *
 * **Single-instance by design**: this component creates one global set of
 * DOM singletons (.stbc-root, .stbc-window, .stbc-backdrop) on document.body.
 * Multiple bubble_chat() mounts will share the same visible elements.
 *
 * Every visible element lives on document.body — escaping the component's
 * parentElement — so they survive Streamlit destroying/replacing the
 * component container during rapid fragment reruns.
 * These elements are NEVER removed by cleanup.
 */
export function ensureBodyElements(): {
  root: HTMLElement;
  win: HTMLElement;
  backdrop: HTMLElement;
} {
  let root = document.querySelector(".stbc-root") as HTMLElement | null;
  if (!root) {
    root = document.createElement("div");
    root.className = "stbc-root";

    const bubbleBtn = document.createElement("button");
    bubbleBtn.className = "stbc-bubble-btn";
    bubbleBtn.innerHTML = ICON_CHAT;
    bubbleBtn.title = "Open chat";
    bubbleBtn.setAttribute("aria-label", "Open chat");
    bubbleBtn.setAttribute("aria-expanded", "false");
    bubbleBtn.setAttribute("aria-controls", "stbc-chat-window");

    const badge = document.createElement("span");
    badge.className = "stbc-badge stbc-hidden";
    badge.setAttribute("aria-live", "polite");
    bubbleBtn.appendChild(badge);

    root.appendChild(bubbleBtn);
    document.body.appendChild(root);
  }

  let backdrop = document.querySelector(".stbc-backdrop") as HTMLElement | null;
  if (!backdrop) {
    backdrop = document.createElement("div");
    backdrop.className = "stbc-backdrop";
    backdrop.setAttribute("aria-hidden", "true");
    document.body.appendChild(backdrop);
  }

  let win = document.querySelector(".stbc-window") as HTMLElement | null;
  if (!win) {
    win = document.createElement("div");
    win.className = "stbc-window";
    win.id = "stbc-chat-window";
    win.setAttribute("role", "dialog");
    win.setAttribute("aria-labelledby", "stbc-header-title");

    // -- Header
    const header = document.createElement("div");
    header.className = "stbc-header";

    const title = document.createElement("span");
    title.className = "stbc-header-title";
    title.id = "stbc-header-title";
    header.appendChild(title);

    const actions = document.createElement("div");
    actions.className = "stbc-header-actions";

    const maximizeBtn = document.createElement("button");
    maximizeBtn.className = "stbc-header-btn stbc-maximize-btn";
    maximizeBtn.title = "Maximize";
    maximizeBtn.setAttribute("aria-label", "Maximize chat window");
    actions.appendChild(maximizeBtn);

    const closeBtn = document.createElement("button");
    closeBtn.className = "stbc-header-btn stbc-close-btn";
    closeBtn.title = "Close";
    closeBtn.setAttribute("aria-label", "Close chat window");
    closeBtn.innerHTML = ICON_CLOSE;
    actions.appendChild(closeBtn);

    header.appendChild(actions);
    win.appendChild(header);

    // -- Messages container
    const messages = document.createElement("div");
    messages.className = "stbc-messages";
    win.appendChild(messages);

    // -- Input area
    const inputArea = document.createElement("div");
    inputArea.className = "stbc-input-area";

    const input = document.createElement("input");
    input.className = "stbc-input";
    input.type = "text";
    input.placeholder = "Type a message…";
    input.autocomplete = "off";
    input.setAttribute("aria-label", "Chat message");
    inputArea.appendChild(input);

    const sendBtn = document.createElement("button");
    sendBtn.className = "stbc-send-btn";
    sendBtn.innerHTML = `Send ${ICON_SEND}`;
    sendBtn.setAttribute("aria-label", "Send message");
    inputArea.appendChild(sendBtn);

    win.appendChild(inputArea);
    document.body.appendChild(win);
  }

  return { root, win, backdrop };
}

/* ─── UI Sync ─── */

export function applyWindowState(
  win: HTMLElement,
  backdrop: HTMLElement,
  isOpen: boolean,
  isMaximized: boolean,
): void {
  const maxBtn = win.querySelector(".stbc-maximize-btn") as HTMLElement;
  const bubbleBtn = document.querySelector(".stbc-bubble-btn") as HTMLElement | null;

  if (isOpen) {
    win.classList.add("stbc-open");
  } else {
    win.classList.remove("stbc-open");
  }

  // Keep aria-expanded in sync with open state
  if (bubbleBtn) {
    bubbleBtn.setAttribute("aria-expanded", String(isOpen));
  }

  if (isMaximized && isOpen) {
    win.classList.add("stbc-maximized");
    win.classList.remove("stbc-minimized");
    backdrop.classList.add("stbc-visible");
    win.setAttribute("aria-modal", "true");
    maxBtn.innerHTML = ICON_MINIMIZE;
    maxBtn.title = "Minimize";
    maxBtn.setAttribute("aria-label", "Minimize chat window");
  } else {
    win.classList.remove("stbc-maximized");
    win.classList.add("stbc-minimized");
    backdrop.classList.remove("stbc-visible");
    win.removeAttribute("aria-modal");
    maxBtn.innerHTML = ICON_MAXIMIZE;
    maxBtn.title = "Maximize";
    maxBtn.setAttribute("aria-label", "Maximize chat window");
  }
}
