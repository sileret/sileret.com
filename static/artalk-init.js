"use strict";
document.addEventListener("DOMContentLoaded", () => {
  const element = document.getElementById("artalk-comments");
  if (!element || !window.Artalk) return;
  Artalk.init({
    el: element,
    server: new URL(element.dataset.server, window.location.origin).href,
    site: element.dataset.site,
    pageKey: element.dataset.pageKey,
    pageTitle: element.dataset.pageTitle,
    locale: "en",
    darkMode: "auto",
    pvEl: false,
    gravatar: { mirror: "/avatar-disabled/", params: "" },
    emoticons: false,
    versionCheck: false,
  });
});
