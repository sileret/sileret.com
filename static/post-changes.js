/* Compare rendered text while leaving Hugo's links, images, and formatting intact. */
(() => {
  "use strict";

  function changedTokens(old, updated) {
    const removed = new Set();
    const added = new Set();
    const trace = [];
    let frontier = new Map([[1, 0]]);
    let stored = 0;
    for (let distance = 0; distance <= old.length + updated.length; distance++) {
      // Bound memory for wholesale rewrites; retain common opening/closing text.
      stored += frontier.size;
      if (stored > 1000000) {
        let start = 0, endOld = old.length, endNew = updated.length;
        while (start < endOld && start < endNew && old[start] === updated[start]) start++;
        while (endOld > start && endNew > start && old[endOld - 1] === updated[endNew - 1]) {
          endOld--; endNew--;
        }
        for (let i = start; i < endOld; i++) removed.add(i);
        for (let i = start; i < endNew; i++) added.add(i);
        return { removed, added };
      }
      trace.push(new Map(frontier));
      for (let diagonal = -distance; diagonal <= distance; diagonal += 2) {
        let x;
        if (diagonal === -distance || (diagonal !== distance &&
            (frontier.get(diagonal - 1) ?? -Infinity) < (frontier.get(diagonal + 1) ?? -Infinity))) {
          x = frontier.get(diagonal + 1) ?? 0;
        } else {
          x = (frontier.get(diagonal - 1) ?? 0) + 1;
        }
        let y = x - diagonal;
        while (x < old.length && y < updated.length && old[x] === updated[y]) { x++; y++; }
        frontier.set(diagonal, x);
        if (x >= old.length && y >= updated.length) {
          for (let depth = distance; depth > 0; depth--) {
            const previous = trace[depth];
            const k = x - y;
            const previousK = k === -depth || (k !== depth &&
              (previous.get(k - 1) ?? -Infinity) < (previous.get(k + 1) ?? -Infinity)) ? k + 1 : k - 1;
            const previousX = previous.get(previousK) ?? 0;
            const previousY = previousX - previousK;
            while (x > previousX && y > previousY) { x--; y--; }
            if (x === previousX) added.add(--y);
            else removed.add(--x);
          }
          return { removed, added };
        }
      }
    }
    return { removed, added };
  }

  function textTokens(root) {
    const tokens = [];
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT);
    while (walker.nextNode()) {
      const node = walker.currentNode;
      if (node.parentElement.closest("script, style")) continue;
      for (const match of node.textContent.matchAll(/\s+|[\p{L}\p{N}_]+|[^\s\p{L}\p{N}_]/gu)) {
        tokens.push({ node, text: match[0], key: /^\s+$/u.test(match[0]) ? " " : match[0] });
      }
    }
    return tokens;
  }

  function highlight(tokens, changed, kind) {
    const byNode = new Map();
    tokens.forEach((token, index) => {
      if (!byNode.has(token.node)) byNode.set(token.node, []);
      byNode.get(token.node).push({ ...token, changed: changed.has(index) });
    });
    for (const [node, parts] of byNode) {
      if (!parts.some(part => part.changed && part.text.trim())) continue;
      const fragment = document.createDocumentFragment();
      let wrapper = null;
      for (const part of parts) {
        if (part.changed) {
          if (!wrapper) {
            wrapper = document.createElement(kind === "insert" ? "mark" : "del");
            if (kind === "insert") wrapper.append(document.createElement("ins"));
            fragment.append(wrapper);
          }
          (kind === "insert" ? wrapper.firstChild : wrapper).append(document.createTextNode(part.text));
        } else {
          wrapper = null;
          fragment.append(document.createTextNode(part.text));
        }
      }
      node.replaceWith(fragment);
    }
  }

  function resourceKey(element, attribute, root) {
    const value = (element.getAttribute(attribute) || "").replace(/^#earlier-/, "#");
    const base = root.dataset.baseUrl;
    return base && value.startsWith(base) ? value.slice(base.length) : value;
  }

  function annotateResources(before, after) {
    let count = 0;
    for (const [selector, attribute, label] of [["img", "src", "Image"], ["a:not(:has(img))", "href", "Link"]]) {
      const old = [...before.querySelectorAll(selector)];
      const updated = [...after.querySelectorAll(selector)];
      const keys = (elements, root) => elements.map(element => JSON.stringify([
        resourceKey(element, attribute, root), element.getAttribute("alt"), element.getAttribute("title"),
      ]));
      const changes = changedTokens(keys(old, before), keys(updated, after));
      for (const [elements, indices, inserted] of [[old, changes.removed, false], [updated, changes.added, true]]) {
        for (const index of indices) {
          const element = elements[index];
          const note = document.createElement(inserted ? "mark" : "del");
          note.textContent = ` (${label} ${inserted ? "added or updated" : "removed or updated"})`;
          // Keep the label outside the link and the site's figure/caption structure.
          (element.closest("figure") || (element.tagName === "IMG" ? element.closest("a") : null) || element).after(note);
          count++;
        }
      }
    }
    return count;
  }

  if (typeof module !== "undefined" && module.exports) module.exports = { changedTokens };
  if (typeof document === "undefined") return;
  const before = document.getElementById("comparison-before");
  const after = document.getElementById("comparison-after");
  if (!before || !after) return;
  const oldTokens = textTokens(before);
  const newTokens = textTokens(after);
  const changes = changedTokens(oldTokens.map(token => token.key), newTokens.map(token => token.key));
  highlight(oldTokens, changes.removed, "delete");
  highlight(newTokens, changes.added, "insert");
  const resources = annotateResources(before, after);
  if (!resources && ![...changes.removed].some(i => oldTokens[i].text.trim()) &&
      ![...changes.added].some(i => newTokens[i].text.trim())) {
    document.getElementById("comparison-status").textContent =
      "No words were added or removed. This update changed formatting or spacing.";
  }
})();
