/* ─── Message Rendering ─── */

import type { Message, AssistantConfig, BubbleChatData } from "./types";
import { FALLBACK_ASSISTANT } from "./types";
import { renderIcon } from "./icons";
import { contrastColor } from "./contrast";

export function renderMessages(
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
