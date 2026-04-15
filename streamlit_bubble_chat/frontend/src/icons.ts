/* ─── Icon Rendering ─── */

const MATERIAL_RE = /^:material\/([a-z0-9_]+):$/;

/** Render an icon string (emoji or :material/name:) into a target element. */
export function renderIcon(el: HTMLElement, icon: string): void {
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

/* ─── Ensure Material Symbols font is loaded ─── */

let _fontLoaded = false;
export function ensureMaterialFont(): void {
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

/* ─── SVG Icons (Feather-style, inline) ─── */

export const ICON_CHAT = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>`;

export const ICON_CLOSE = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>`;

export const ICON_MAXIMIZE = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="15 3 21 3 21 9"/><polyline points="9 21 3 21 3 15"/><line x1="21" y1="3" x2="14" y2="10"/><line x1="3" y1="21" x2="10" y2="14"/></svg>`;

export const ICON_MINIMIZE = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="4 14 10 14 10 20"/><polyline points="20 10 14 10 14 4"/><line x1="14" y1="10" x2="21" y2="3"/><line x1="3" y1="21" x2="10" y2="14"/></svg>`;

export const ICON_SEND = `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2"/></svg>`;
