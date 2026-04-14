import type {
  FrontendRenderer,
  FrontendRendererArgs,
} from "@streamlit/component-v2-lib";
import "./styles.css";

/* ─── Types ─── */

interface Message {
  role: "user" | "assistant" | "system";
  name?: string;
  content: string;
}

interface AssistantConfig {
  icon: string;
  avatar_bg: string;
  bubble_bg?: string;
  bubble_color?: string;
}

interface BubbleChatData {
  messages: Message[];
  type: "simple" | "avatar";
  unread_count: number;
  window_title: string;
  theme_color: string | null;
  show_names: boolean;
  assistant_config: Record<string, AssistantConfig>;
  user_icon: string;
  user_icon_bg: string;
  name_colors: Record<string, string>;
  is_open: boolean;
  is_maximized: boolean;
}

const FALLBACK_ASSISTANT: AssistantConfig = {
  icon: "🤖",
  avatar_bg: "",
};

/* ─── Icon Rendering ─── */

const MATERIAL_RE = /^:material\/([a-z0-9_]+):$/;

/** Render an icon string (emoji or :material/name:) into a target element. */
function renderIcon(el: HTMLElement, icon: string): void {
  const m = MATERIAL_RE.exec(icon);
  if (m) {
    const span = document.createElement("span");
    span.className = "material-symbols-rounded";
    span.textContent = m[1];
    span.style.fontSize = "16px";
    el.textContent = "";
    el.appendChild(span);
  } else {
    el.textContent = icon;
  }
}

/* ─── Auto-contrast (APCA — Accessible Perceptual Contrast Algorithm) ─── */
/*
 * Inline implementation of APCA 0.0.98G-4g (W3 Licensed).
 * APCA is a perceptual contrast algorithm that accounts for the
 * asymmetry between dark-on-light and light-on-dark text, producing
 * correct contrast values across any theme without theme detection.
 *
 * Reference: https://github.com/Myndex/apca-w3
 * Constants: SA98G group "G-4g", monitor exponent 2.4
 */

/** Linearize an sRGB 0-255 channel and compute luminance Y. */
function sRGBtoY(r: number, g: number, b: number): number {
  const f = (c: number) => Math.pow(c / 255, 2.4);
  return 0.2126729 * f(r) + 0.7151522 * f(g) + 0.0721750 * f(b);
}

/** APCA contrast (Lc) — text Y vs background Y.  Returns signed float. */
function apcaLc(txtY: number, bgY: number): number {
  const blkThrs = 0.022, blkClmp = 1.414;

  // Soft-clamp near-black
  txtY = txtY > blkThrs ? txtY : txtY + Math.pow(blkThrs - txtY, blkClmp);
  bgY  = bgY  > blkThrs ? bgY  : bgY  + Math.pow(blkThrs - bgY,  blkClmp);

  if (Math.abs(bgY - txtY) < 0.0005) return 0;

  let sapc: number;
  if (bgY > txtY) {
    // Normal polarity: dark text on light bg (BoW) → positive
    sapc = (Math.pow(bgY, 0.56) - Math.pow(txtY, 0.57)) * 1.14;
    return sapc < 0.1 ? 0 : (sapc - 0.027) * 100;
  } else {
    // Reverse polarity: light text on dark bg (WoB) → negative
    sapc = (Math.pow(bgY, 0.65) - Math.pow(txtY, 0.62)) * 1.14;
    return sapc > -0.1 ? 0 : (sapc + 0.027) * 100;
  }
}

/**
 * Choose "#fff" or "#000" for best perceptual contrast against `hex`.
 * Compares |Lc(white, bg)| vs |Lc(black, bg)| and picks the winner.
 */
function contrastColor(hex: string): string {
  const h = hex.replace("#", "");
  const r = parseInt(h.substring(0, 2), 16);
  const g = parseInt(h.substring(2, 4), 16);
  const b = parseInt(h.substring(4, 6), 16);
  const bgY = sRGBtoY(r, g, b);

  const lcWhite = Math.abs(apcaLc(1.0, bgY));  // white text on bg
  const lcBlack = Math.abs(apcaLc(0.0, bgY));  // black text on bg
  return lcWhite >= lcBlack ? "#fff" : "#000";
}

/* ─── SVG Icons (Feather-style, inline) ─── */

const ICON_CHAT = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`;

const ICON_CLOSE = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`;

const ICON_MAXIMIZE = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg>`;

const ICON_MINIMIZE = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 14 10 14 10 20"/><polyline points="20 10 14 10 14 4"/><line x1="14" y1="10" x2="21" y2="3"/><line x1="3" y1="21" x2="10" y2="14"/></svg>`;

const ICON_SEND = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>`;

/* ─── DOM Builder ─── */

function buildDOM(): HTMLDivElement {
  const root = document.createElement("div");
  root.className = "stbc-root";

  // Backdrop (on document.body to escape the component stacking context)
  const backdrop = document.createElement("div");
  backdrop.className = "stbc-backdrop";
  document.body.appendChild(backdrop);

  // Chat window (on document.body — same reason as backdrop)
  const win = document.createElement("div");
  win.className = "stbc-window";

  // -- Header
  const header = document.createElement("div");
  header.className = "stbc-header";

  const title = document.createElement("span");
  title.className = "stbc-header-title";
  header.appendChild(title);

  const actions = document.createElement("div");
  actions.className = "stbc-header-actions";

  const maximizeBtn = document.createElement("button");
  maximizeBtn.className = "stbc-header-btn stbc-maximize-btn";
  maximizeBtn.title = "Maximize";
  maximizeBtn.innerHTML = ICON_MAXIMIZE;
  actions.appendChild(maximizeBtn);

  const closeBtn = document.createElement("button");
  closeBtn.className = "stbc-header-btn stbc-close-btn";
  closeBtn.title = "Close";
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
  inputArea.appendChild(input);

  const sendBtn = document.createElement("button");
  sendBtn.className = "stbc-send-btn";
  sendBtn.innerHTML = `Send ${ICON_SEND}`;
  inputArea.appendChild(sendBtn);

  win.appendChild(inputArea);
  document.body.appendChild(win);

  // Bubble button
  const bubbleBtn = document.createElement("button");
  bubbleBtn.className = "stbc-bubble-btn";
  bubbleBtn.innerHTML = ICON_CHAT;
  bubbleBtn.title = "Open chat";

  const badge = document.createElement("span");
  badge.className = "stbc-badge stbc-hidden";
  bubbleBtn.appendChild(badge);

  root.appendChild(bubbleBtn);

  return root;
}

/* ─── UI Sync ─── */

function applyWindowState(
  _root: HTMLElement,
  isOpen: boolean,
  isMaximized: boolean,
) {
  const win = document.querySelector(".stbc-window") as HTMLElement;
  const backdrop = document.querySelector(".stbc-backdrop") as HTMLElement;
  const maxBtn = win.querySelector(".stbc-maximize-btn") as HTMLElement;

  if (isOpen) {
    win.classList.add("stbc-open");
  } else {
    win.classList.remove("stbc-open");
  }

  if (isMaximized && isOpen) {
    win.classList.add("stbc-maximized");
    win.classList.remove("stbc-minimized");
    backdrop.classList.add("stbc-visible");
    maxBtn.innerHTML = ICON_MINIMIZE;
    maxBtn.title = "Minimize";
  } else {
    win.classList.remove("stbc-maximized");
    win.classList.add("stbc-minimized");
    backdrop.classList.remove("stbc-visible");
    maxBtn.innerHTML = ICON_MAXIMIZE;
    maxBtn.title = "Maximize";
  }
}

/* ─── Message Rendering ─── */

function renderMessages(
  _root: HTMLElement,
  messages: Message[],
  unreadCount: number,
  d: BubbleChatData,
): HTMLElement | null {
  const container = document.querySelector(".stbc-messages") as HTMLElement;

  // Remove existing divider (will re-insert at correct position)
  const oldDivider = container.querySelector(".stbc-unread-divider");
  if (oldDivider) oldDivider.remove();

  // Count actual message elements (exclude empty state and divider)
  const msgEls = container.querySelectorAll(".stbc-msg");
  const actualCount = msgEls.length;
  const isEmptyState =
    container.children.length === 1 &&
    container.firstElementChild?.classList.contains("stbc-empty");

  if (messages.length === 0) {
    if (!isEmptyState) {
      container.innerHTML = "";
      const empty = document.createElement("div");
      empty.className = "stbc-empty";
      empty.textContent = "No messages yet";
      container.appendChild(empty);
    }
    return null;
  }

  // Full rebuild if counts diverged (messages removed, or was empty state)
  const needsRebuild = isEmptyState || messages.length < actualCount;

  if (needsRebuild) {
    container.innerHTML = "";
    for (const msg of messages) {
      container.appendChild(createMsgEl(msg, d));
    }
  } else if (messages.length > actualCount) {
    // Append only new messages
    for (let i = actualCount; i < messages.length; i++) {
      container.appendChild(createMsgEl(messages[i], d));
    }
  }

  // Insert unread divider before the first unread non-system message.
  // Walk backwards, counting only non-system messages, to account for
  // system messages that don't contribute to the unread count.
  let dividerEl: HTMLElement | null = null;
  if (unreadCount > 0 && unreadCount < messages.length) {
    let nonSystemSeen = 0;
    let dividerIdx = -1;
    for (let i = messages.length - 1; i >= 0; i--) {
      if (messages[i].role !== "system") {
        nonSystemSeen++;
        if (nonSystemSeen === unreadCount) {
          dividerIdx = i;
          break;
        }
      }
    }
    if (dividerIdx > 0) {
      const allMsgs = container.querySelectorAll(".stbc-msg");
      if (allMsgs[dividerIdx]) {
        dividerEl = document.createElement("div");
        dividerEl.className = "stbc-unread-divider";
        dividerEl.textContent = "New messages";
        container.insertBefore(dividerEl, allMsgs[dividerIdx]);
      }
    }
  }

  return dividerEl;
}

/** Resolve assistant config for a message by name, with _default fallback. */
function resolveAssistantConfig(
  msg: Message,
  config: Record<string, AssistantConfig>,
): AssistantConfig {
  if (msg.name && config[msg.name]) return config[msg.name];
  return config["_default"] || FALLBACK_ASSISTANT;
}

function createMsgEl(msg: Message, d: BubbleChatData): HTMLElement {
  // ── System messages: centered pill, no avatar ──
  if (msg.role === "system") {
    const pill = document.createElement("div");
    pill.className = "stbc-msg stbc-msg-system";
    const pillInner = document.createElement("span");
    pillInner.className = "stbc-system-pill";
    pillInner.textContent = msg.content;
    pill.appendChild(pillInner);
    return pill;
  }

  const isUser = msg.role === "user";
  const isAvatar = d.type === "avatar";

  const row = document.createElement("div");
  row.className = `stbc-msg stbc-msg-${isUser ? "user" : "assistant"}`;

  // ── Avatar (only in avatar mode) ──
  if (isAvatar) {
    const avatar = document.createElement("span");
    avatar.className = "stbc-avatar";

    if (isUser) {
      renderIcon(avatar, d.user_icon || "👤");
      const bg = d.user_icon_bg || d.theme_color || "";
      if (d.user_icon_bg) {
        avatar.style.background = d.user_icon_bg;
      }
      if (bg) avatar.style.color = contrastColor(bg);
    } else {
      const cfg = resolveAssistantConfig(msg, d.assistant_config);
      renderIcon(avatar, cfg.icon);
      if (cfg.avatar_bg) {
        avatar.style.background = cfg.avatar_bg;
        avatar.style.color = contrastColor(cfg.avatar_bg);
      }
    }

    row.appendChild(avatar);
  }

  // ── Content wrapper (name label + bubble) ──
  const contentWrap = document.createElement("div");
  contentWrap.className = "stbc-msg-content";

  // Agent name label (for assistant messages with a name)
  if (!isUser && msg.name && d.show_names) {
    const nameEl = document.createElement("span");
    nameEl.className = "stbc-msg-name";
    nameEl.textContent = msg.name;

    // Tint the name label: name_colors takes priority, then avatar_bg
    if (d.name_colors[msg.name]) {
      nameEl.style.color = d.name_colors[msg.name];
    } else if (isAvatar) {
      const cfg = resolveAssistantConfig(msg, d.assistant_config);
      if (cfg.avatar_bg) {
        nameEl.style.color = cfg.avatar_bg;
      }
    }

    contentWrap.appendChild(nameEl);
  }

  // Message bubble
  const bubble = document.createElement("div");
  bubble.className = "stbc-msg-bubble";
  bubble.textContent = msg.content;

  // Apply custom bubble colours from assistant_config (avatar mode only)
  if (isAvatar && !isUser) {
    const cfg = resolveAssistantConfig(msg, d.assistant_config);
    if (cfg.bubble_bg) {
      bubble.style.background = cfg.bubble_bg;
    }
    if (cfg.bubble_color) {
      bubble.style.color = cfg.bubble_color;
    }
  }

  contentWrap.appendChild(bubble);
  row.appendChild(contentWrap);
  return row;
}

/* ─── Ensure Material Symbols font is loaded ─── */

let _fontLoaded = false;
function ensureMaterialFont(): void {
  if (_fontLoaded) return;
  _fontLoaded = true;
  const id = "stbc-material-symbols-link";
  if (document.getElementById(id)) return;
  const link = document.createElement("link");
  link.id = id;
  link.rel = "stylesheet";
  link.href =
    "https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200";
  document.head.appendChild(link);
}

/* ─── Main Component ─── */

/** Streamlit theme CSS custom properties used by the component. */
const ST_THEME_VARS = [
  "--st-background-color",
  "--st-text-color",
  "--st-primary-color",
  "--st-border-color",
  "--st-red-color",
  "--st-secondary-background-color",
  "--st-base-font-size",
  "--st-font",
];

/**
 * Copy Streamlit theme variables from the component's ancestor (where
 * Streamlit defines them) onto body-level elements that live outside the
 * component tree.  This keeps the chat window and backdrop themed.
 */
function syncThemeVars(source: HTMLElement, ...targets: HTMLElement[]): void {
  const cs = getComputedStyle(source);
  for (const v of ST_THEME_VARS) {
    const val = cs.getPropertyValue(v).trim();
    if (val) {
      for (const t of targets) t.style.setProperty(v, val);
    }
  }
}

const BubbleChat: FrontendRenderer = (
  args: FrontendRendererArgs,
) => {
  const { parentElement, data, setStateValue, setTriggerValue } = args;
  const d = data as BubbleChatData;

  ensureMaterialFont();

  // Ensure our root element exists inside parentElement
  let root = parentElement.querySelector(".stbc-root") as HTMLElement | null;
  if (!root) {
    root = buildDOM();
    parentElement.appendChild(root);
  }

  // Apply custom theme color + auto-contrast foreground
  if (d.theme_color) {
    const fg = contrastColor(d.theme_color);
    root.style.setProperty("--stbc-theme-color", d.theme_color);
    root.style.setProperty("--stbc-theme-fg", fg);
    const win = document.querySelector(".stbc-window") as HTMLElement;
    if (win) {
      win.style.setProperty("--stbc-theme-color", d.theme_color);
      win.style.setProperty("--stbc-theme-fg", fg);
    }
    const backdrop = document.querySelector(".stbc-backdrop") as HTMLElement;
    if (backdrop)
      backdrop.style.setProperty("--stbc-theme-color", d.theme_color);
  } else {
    root.style.removeProperty("--stbc-theme-color");
    root.style.removeProperty("--stbc-theme-fg");
  }

  // Propagate Streamlit theme variables to body-level window/backdrop.
  {
    const bodyWin = document.querySelector(".stbc-window") as HTMLElement;
    const bodyBackdrop = document.querySelector(".stbc-backdrop") as HTMLElement;
    if (bodyWin && bodyBackdrop) {
      syncThemeVars(parentElement as HTMLElement, bodyWin, bodyBackdrop);
    }
  }

  // Read visual state from data (Python is source of truth)
  const isOpen = d.is_open;
  const isMaximized = d.is_maximized;

  // Detect "just opened" transition for scroll targeting
  const wasOpen = root.getAttribute("data-was-open") === "true";
  root.setAttribute("data-was-open", String(isOpen));
  const justOpened = isOpen && !wasOpen;

  // Sync window state
  applyWindowState(root, isOpen, isMaximized);

  // Title
  const titleEl = document.querySelector(".stbc-header-title") as HTMLElement;
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
  const messagesContainer = document.querySelector(".stbc-messages") as HTMLElement;
  requestAnimationFrame(() => {
    if (justOpened && dividerEl) {
      dividerEl.scrollIntoView({ behavior: "smooth", block: "start" });
    } else if (isOpen) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  });

  // ── Event handlers ──

  const bubbleBtn = root.querySelector(".stbc-bubble-btn") as HTMLElement;
  const closeBtn = document.querySelector(".stbc-close-btn") as HTMLElement;
  const maxBtn = document.querySelector(".stbc-maximize-btn") as HTMLElement;
  const backdrop = document.querySelector(".stbc-backdrop") as HTMLElement;
  const input = document.querySelector(".stbc-input") as HTMLInputElement;
  const sendBtn = document.querySelector(".stbc-send-btn") as HTMLButtonElement;

  // Open/close bubble
  bubbleBtn.onclick = () => {
    const nowOpen = !document.querySelector(".stbc-window")!.classList.contains("stbc-open");
    applyWindowState(root!, nowOpen, false);
    setStateValue("is_open", nowOpen);
    if (!nowOpen) {
      setStateValue("is_maximized", false);
    }
    if (nowOpen) {
      requestAnimationFrame(() => input.focus());
    }
  };

  // Close via header button
  closeBtn.onclick = () => {
    applyWindowState(root!, false, false);
    setStateValue("is_open", false);
    setStateValue("is_maximized", false);
  };

  // Maximize toggle
  maxBtn.onclick = () => {
    const win = document.querySelector(".stbc-window") as HTMLElement;
    const nowMaximized = !win.classList.contains("stbc-maximized");
    applyWindowState(root!, true, nowMaximized);
    setStateValue("is_maximized", nowMaximized);
  };

  // Backdrop click → close maximized (go to minimized)
  backdrop.onclick = () => {
    applyWindowState(root!, true, false);
    setStateValue("is_maximized", false);
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

  // Cleanup on unmount
  return () => {
    root?.remove();
  };
};

export default BubbleChat;
