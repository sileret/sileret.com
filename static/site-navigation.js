/* Reserve the sticky header's actual height for native fragment navigation. */
(() => {
  const header = document.querySelector(".site-header");
  if (!header) return;
  let refreshTocObserver = () => {};
  let headerOffset = 0;
  const updateOffset = () => {
    const offset = Math.ceil(header.getBoundingClientRect().height) + 16;
    if (offset === headerOffset) return;
    headerOffset = offset;
    document.documentElement.style.setProperty(
      "--header-offset", `${headerOffset}px`
    );
    refreshTocObserver();
  };
  updateOffset();
  if (typeof ResizeObserver !== "undefined") new ResizeObserver(updateOffset).observe(header);
  else window.addEventListener("resize", updateOffset);

  const mainToc = document.querySelector(".post-toc");
  const sidebarToc = document.querySelector(".sidebar-toc");
  const tocLinks = mainToc?.querySelector("nav");
  if (tocLinks && sidebarToc) {
    const clonedLinks = tocLinks.cloneNode(true);
    // Keep section destinations, but avoid duplicate IDs in the document.
    clonedLinks.removeAttribute("id");
    clonedLinks.querySelectorAll("[id]").forEach(element => element.removeAttribute("id"));
    clonedLinks.setAttribute("aria-labelledby", "sidebar-toc-heading");
    sidebarToc.querySelector("[data-sidebar-toc]").append(clonedLinks);
    const sidebar = sidebarToc.closest(".post-version-sidebar");
    const sections = [...clonedLinks.querySelectorAll('a[href^="#"]')].flatMap(link => {
      let id;
      try { id = decodeURIComponent(link.getAttribute("href").slice(1)); }
      catch { return []; }
      const heading = document.getElementById(id);
      return heading ? [{ link, heading }] : [];
    });
    let currentLink = null;
    const updateCurrentSection = () => {
      let nextLink = null;
      for (const { link, heading } of sections) {
        if (heading.getBoundingClientRect().top <= headerOffset + 1) nextLink = link;
        else break;
      }
      if (nextLink !== currentLink) {
        currentLink?.removeAttribute("aria-current");
        currentLink = nextLink;
        currentLink?.setAttribute("aria-current", "location");
      }
      // Scroll only the desktop sidebar, never the post, to keep its marker visible.
      if (currentLink && !sidebarToc.hidden && window.matchMedia("(min-width: 1100px)").matches) {
        const linkBounds = currentLink.getBoundingClientRect();
        const sidebarBounds = sidebar.getBoundingClientRect();
        if (linkBounds.top < sidebarBounds.top) sidebar.scrollTop += linkBounds.top - sidebarBounds.top;
        else if (linkBounds.bottom > sidebarBounds.bottom) sidebar.scrollTop += linkBounds.bottom - sidebarBounds.bottom;
      }
    };
    let sectionUpdatePending = false;
    const queueSectionUpdate = () => {
      if (sectionUpdatePending) return;
      sectionUpdatePending = true;
      window.requestAnimationFrame(() => {
        sectionUpdatePending = false;
        updateCurrentSection();
      });
    };
    window.addEventListener("scroll", queueSectionUpdate, { passive: true });
    const syncToc = () => {
      // A ToC below the viewport is not yet a reason to show its duplicate.
      sidebarToc.hidden = mainToc.getBoundingClientRect().bottom > headerOffset;
      if (sidebar.hasAttribute("data-toc-only")) sidebar.hidden = sidebarToc.hidden;
      updateCurrentSection();
    };
    if (typeof IntersectionObserver !== "undefined") {
      let observer;
      refreshTocObserver = () => {
        observer?.disconnect();
        observer = new IntersectionObserver(syncToc, {
          rootMargin: `-${headerOffset}px 0px 0px 0px`,
          threshold: 0,
        });
        observer.observe(mainToc);
        syncToc();
      };
      refreshTocObserver();
    } else {
      window.addEventListener("scroll", syncToc, { passive: true });
    }
    window.addEventListener("resize", syncToc, { passive: true });
    syncToc();
  }

  // Direct links must also account for the header after fonts and styles load.
  window.addEventListener("load", () => {
    updateOffset();
    if (!window.location.hash) return;
    let id;
    try { id = decodeURIComponent(window.location.hash.slice(1)); }
    catch { return; }
    const target = document.getElementById(id);
    if (target) target.scrollIntoView({ block: "start", behavior: "instant" });
  }, { once: true });
})();
