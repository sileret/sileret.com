/* Apply a saved override before CSS paints; System keeps the native media query. */
(() => {
  const storageKey = "sileret-theme";
  const modes = ["system", "light", "dark"];
  const labels = { system: "System", light: "Light", dark: "Dark" };
  const systemTheme = window.matchMedia("(prefers-color-scheme: dark)");
  const root = document.documentElement;
  const readPreference = () => {
    try {
      const stored = window.localStorage.getItem(storageKey);
      return modes.includes(stored) ? stored : "system";
    } catch {
      return "system";
    }
  };
  let preference = readPreference();
  let button;
  const applyTheme = () => {
    if (preference === "system") root.removeAttribute("data-theme");
    else root.setAttribute("data-theme", preference);
    if (!button) return;
    const next = modes[(modes.indexOf(preference) + 1) % modes.length];
    const resolved = systemTheme.matches ? "Dark" : "Light";
    const current = preference === "system" ? `System (${resolved})` : labels[preference];
    const description = `Theme: ${current}. Switch to ${labels[next]} mode.`;
    button.dataset.themeMode = preference;
    button.setAttribute("aria-label", description);
    button.title = description;
  };
  applyTheme();

  document.addEventListener("DOMContentLoaded", () => {
    button = document.querySelector("[data-theme-toggle]");
    if (!button) return;
    applyTheme();
    button.hidden = false;
    button.addEventListener("click", () => {
      preference = modes[(modes.indexOf(preference) + 1) % modes.length];
      try {
        if (preference === "system") window.localStorage.removeItem(storageKey);
        else window.localStorage.setItem(storageKey, preference);
      } catch {
        // The control still works for this page when storage is unavailable.
      }
      applyTheme();
    });
  });
  if (systemTheme.addEventListener) systemTheme.addEventListener("change", applyTheme);
  else systemTheme.addListener(applyTheme);
  window.addEventListener("storage", event => {
    if (event.key !== null && event.key !== storageKey) return;
    preference = readPreference();
    applyTheme();
  });
})();
