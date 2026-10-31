/* Enhance links to original post images; keep those links as the no-JS fallback. */
(() => {
  const dialog = document.getElementById("image-viewer");
  if (!dialog || typeof dialog.showModal !== "function") return;
  const shell = dialog.querySelector(".image-viewer-shell");
  const image = dialog.querySelector("[data-viewer-image]");
  const caption = dialog.querySelector("[data-viewer-caption]");
  const counter = dialog.querySelector("[data-viewer-count]");
  const status = dialog.querySelector("[data-viewer-status]");
  const original = dialog.querySelector("[data-viewer-original]");
  const previous = dialog.querySelector("[data-viewer-previous]");
  const next = dialog.querySelector("[data-viewer-next]");
  const fullscreen = dialog.querySelector("[data-viewer-fullscreen]");
  let items = [];
  let index = 0;
  let opener;
  let closing = false;

  const displayImage = position => {
    index = (position + items.length) % items.length;
    const item = items[index];
    status.textContent = "Loading image…";
    image.alt = item.alt;
    image.src = item.url;
    original.href = item.url;
    caption.textContent = item.caption;
    caption.hidden = !item.caption;
    counter.textContent = `Image ${index + 1} of ${items.length}`;
    previous.hidden = next.hidden = items.length < 2;
  };

  document.addEventListener("click", event => {
    if (event.defaultPrevented || event.button !== 0 || event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) return;
    const link = event.target.closest?.("a[data-image-viewer]");
    if (!link || !link.querySelector("img")) return;
    const group = link.dataset.imageGallery;
    const links = group ? [...document.querySelectorAll("a[data-image-viewer]")].filter(candidate => candidate.dataset.imageGallery === group) : [link];
    const unique = new Map();
    for (const candidate of links) {
      const thumbnail = candidate.querySelector("img");
      if (!thumbnail || unique.has(candidate.href)) continue;
      unique.set(candidate.href, {
        url: candidate.href,
        alt: thumbnail.alt,
        caption: candidate.dataset.imageCaption || thumbnail.alt,
      });
    }
    items = [...unique.values()];
    if (!items.length) return;
    event.preventDefault();
    opener = link;
    displayImage(items.findIndex(item => item.url === link.href));
    document.documentElement.classList.add("image-viewer-open");
    dialog.showModal();
  });

  image.addEventListener("load", () => { status.textContent = ""; });
  image.addEventListener("error", () => {
    if (dialog.open) status.textContent = "This image could not be loaded. Try opening the original.";
  });
  previous.addEventListener("click", () => displayImage(index - 1));
  next.addEventListener("click", () => displayImage(index + 1));
  dialog.addEventListener("keydown", event => {
    if (event.altKey || event.ctrlKey || event.metaKey || event.shiftKey) return;
    if (event.key === "ArrowLeft" || event.key === "ArrowRight") {
      event.preventDefault();
      if (items.length > 1) displayImage(index + (event.key === "ArrowRight" ? 1 : -1));
    }
  });

  // Fullscreen belongs to the shell: browsers do not fullscreen dialog elements.
  fullscreen.hidden = !document.fullscreenEnabled || typeof shell.requestFullscreen !== "function";
  fullscreen.addEventListener("click", async () => {
    try {
      if (document.fullscreenElement === shell) await document.exitFullscreen();
      else await shell.requestFullscreen();
    } catch {
      status.textContent = "Fullscreen is unavailable. You can still view the image here or open the original.";
    }
  });
  document.addEventListener("fullscreenchange", () => {
    const enabled = document.fullscreenElement === shell;
    fullscreen.setAttribute("aria-pressed", String(enabled));
    const label = enabled ? "Exit fullscreen" : "Enter fullscreen";
    fullscreen.setAttribute("aria-label", label);
    fullscreen.title = label;
  });
  const closeViewer = async () => {
    if (closing) return;
    closing = true;
    if (document.fullscreenElement === shell) {
      try { await document.exitFullscreen(); } catch { /* Closing still works. */ }
    }
    dialog.close();
    closing = false;
  };
  dialog.querySelector("[data-viewer-close]").addEventListener("click", closeViewer);
  dialog.addEventListener("cancel", event => {
    if (document.fullscreenElement !== shell) return;
    event.preventDefault();
    document.exitFullscreen().catch(() => dialog.close());
  });
  dialog.addEventListener("close", () => {
    document.documentElement.classList.remove("image-viewer-open");
    image.removeAttribute("src");
    if (opener?.isConnected) opener.focus({ preventScroll: true });
  });
})();
