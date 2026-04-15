/* ─── Streamlit Theme Sync ─── */

/** Streamlit theme CSS custom properties used by the component. */
const ST_THEME_VARS = [
  "--st-background-color",
  "--st-text-color",
  "--st-primary-color",
  "--st-border-color",
  "--st-border-color-light",
  "--st-widget-border-color",
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
export function syncThemeVars(source: HTMLElement, ...targets: HTMLElement[]): void {
  const cs = getComputedStyle(source);
  for (const v of ST_THEME_VARS) {
    const val = cs.getPropertyValue(v).trim();
    if (val) {
      for (const t of targets) t.style.setProperty(v, val);
    }
  }
}
