# Codex project notes

Private VM staging was added on October 31, 2026: Debian `prod-blog-01` on
`prod-vmh-03`, with Caddy, Artalk, GoAccess, Pagefind and Sveltia CMS. Production
Cloudflare/Hyvor configuration is still intact. Read `docs/vm-deployment.md` for
the isolation policy, private access, build overrides, backup boundaries and the
enabled Git publisher for `codex/private-blog`. Cloudflare builds for that
private branch are blocked in `scripts/build.py`; public `main` is unchanged. Do not expose the VM or change DNS as
part of routine implementation work.

This is the repository-specific briefing for future Codex sessions. It describes current implementation, not older intended workflows.

## Project snapshot

- Static site generator: Hugo, custom templates, no external theme.
- Production host: Cloudflare Pages.
- Production URL: `https://sileret.com/`.
- Primary authoring model: direct Markdown page bundles.
- Production build command: `python3 scripts/build.py`.
- Comments provider: Hyvor Talk, enabled after deployment supplies a Website ID.
- Analytics provider: Cloudflare Web Analytics, enabled externally in Cloudflare.
- Public historical versions: generated from Git at build time.
- Main stylesheet: `static/styles.css`, user-owned and off-limits without an explicit CSS request.

The private VM pins Hugo `0.164.0`; local verification on October 31 used Hugo
`0.169.0` extended. `hugo.toml` uses `locale = "en-US"`; the deprecated
`languageCode` key is no longer used.

## Repository map

- `hugo.toml`: site and provider-neutral comment configuration.
- `archetypes/posts.md`: standard article archetype.
- `archetypes/thought.md`: quick-thought archetype.
- `content/posts/<slug>/index.md`: current posts.
- `content/about/index.md`: About page.
- `layouts/partials/post-card.html`: shared home/list rendering for articles and thoughts.
- `layouts/partials/post-history.html`: resolves a post's history on current, historical, and comparison pages.
- `layouts/partials/post-history-sidebar.html`: shared version navigation.
- `layouts/partials/home-sidebar.html`: front-page Recently updated and Explore sections.
- `layouts/partials/recently-updated.html`: selects the five most recently updated published posts.
- `static/post-history.css`: responsive sidebar layout and fragment scroll offsets; keeps the main stylesheet untouched.
- `static/site-navigation.js`: measures sticky-header height for section links and sidebar positioning, and toggles the sidebar ToC.
- `layouts/partials/theme-toggle.html`: accessible System/Light/Dark icon button in the header.
- `static/theme.js`: applies saved theme choices before paint and handles the three-state control.
- `static/theme.css`: explicit palette overrides and responsive theme-button styles; keep its palettes synchronized with `static/styles.css` if colors change.
- `layouts/partials/image-viewer.html`: accessible browser-sized image dialog.
- `static/image-viewer.js`: original-image viewing, per-post galleries, keyboard controls, and optional native fullscreen.
- `static/image-viewer.css`: viewport-filling image-viewer styles, separate from the main stylesheet.
- `layouts/partials/comments.html`: comment-provider dispatcher.
- `layouts/partials/comments/hyvor.html`: Hyvor full-post embed.
- `layouts/partials/post-comment-id.html`: stable comment identity resolution.
- `layouts/partials/post-comments-link.html`: post-list comment link/count.
- `layouts/partials/comment-count-loader.html`: one Hyvor count loader per list page.
- `layouts/_default/single.html`: current post/page template and public history list.
- `layouts/_default/post-version.html`: read-only historical-version template.
- `layouts/_default/post-changes.html`: read-only word-level comparison template.
- `static/post-changes.js`: highlights changes in rendered comparison content.
- `scripts/generate_history.py`: generates history data, version pages, and historical assets.
- `scripts/build.py`: full-history check, history generation, and production Hugo build.
- `scripts/publish.py`: separate legacy Apple Notes sync; not the manual-post publisher.
- `docs/authoring-and-publishing.md`: canonical content and publishing workflow.
- `docs/services.md`: Hyvor and Cloudflare setup and migration notes.

## Content formats

Post bundles live at `content/posts/<slug>/index.md`; assets live beside `index.md`.

### Articles

Articles use:

```yaml
format: article
```

Post lists show an Article label, date, optional update date, reading time, thumbnail, summary, and “Continue reading” link. A `<!--more-->` divider controls the summary boundary. Posts without `format` default to articles.

### Thoughts

Thoughts use:

```yaml
format: thought
```

Post lists show the entire thought. Thoughts retain a permanent page for linking, comment discussion, and version history. Listing thumbnails are intentionally omitted for thoughts.

### Shared front matter

New archetypes include:

```yaml
draft: true
comments: true
comment_id: "stable-slug-like-id"
```

`comment_id` is permanent after comments exist. `comments: false` disables the link and embed for one post.

## Home and list rendering

- Home uses `layouts/index.html` and displays the 12 newest pages in `posts`.
- Home includes a sidebar with Recently updated and Explore. Recently updated lists up to five distinct published posts ordered by `lastmod`, requiring `lastmod` later than `date` and at least two committed versions. `update_summary` overrides the latest public commit subject; `show_update: false` suppresses an entry. Empty update lists are omitted. Explore lists up to five topics with published-post counts and links to all posts (and all topics when needed); draft-only topics are omitted.
- On pages with sidebars, the header spans both columns. At widths below 1100px the sidebar follows the main content; the original desktop reading width is retained.
- Header menu links use a bold weight of 700, including Search when enabled, through `static/theme.css`.
- The page and sticky header share the solid `--bg` background in both color schemes, overriding the original gradient through `static/post-history.css`.
- The header theme button cycles System → Light → Dark → System, using monitor, sun, and moon symbols. System is the default and keeps the existing `prefers-color-scheme` automatic switching, including live OS preference changes. Explicit choices are saved under `sileret-theme` in local storage; selecting System removes the override. Storage failures fall back safely, and changes synchronize across tabs. The small blocking `/theme.js` script runs before stylesheets to apply a saved override before first paint; the button is enabled on DOM ready. Without JavaScript the control is hidden and the existing automatic CSS behavior remains.
- The shared HTML head advertises the posts-only RSS feed at `/posts/index.xml`, and the main navigation includes a visible RSS link.
- Section/taxonomy lists use `layouts/_default/list.html`.
- Both delegate each item to `layouts/partials/post-card.html` so article/thought behavior cannot drift between templates.
- Article thumbnails are selected in this order: `title-image*`, `cover*`, then the first bundle image.
- Thumbnails use Hugo image processing with `.Fill "960x270 Top"`.
- Article summaries containing an image fall back to truncated plain text.
- Comment counts load only when the Hyvor Website ID is configured.

## Single posts

- Show Article/Thought, publication date, optional update date, and article reading time.
- Article table of contents is rendered when Hugo produces a non-empty TOC.
- After the original ToC scrolls above the usable viewport, the sidebar shows a copy of its section links, above version history when available. It hides again when the original returns. Articles with a ToC get the sidebar layout even without multiple committed versions; a ToC-only sidebar stays hidden until needed. `IntersectionObserver` accounts for the sticky header, with a scroll-event fallback. Cloned navigation has no duplicate element IDs and is excluded from search indexing.
- The sidebar ToC marks the latest heading that has reached the reading line below the sticky header with `aria-current="location"`, a bold label, a tinted background, and a left marker. A passive scroll listener batches section tracking with `requestAnimationFrame`. The desktop sidebar scrolls internally when needed to keep the current link visible, without moving the post.
- Native fragment navigation reserves the measured sticky-header height plus 16px, so ToC targets and direct section links remain visible. CSS provides a fallback offset without JavaScript.
- A fixed “Scroll to top” link is always visible on every page, including mobile. It uses the native `#page-top` target and works without JavaScript.
- Thoughts do not render a TOC.
- Markdown image behavior remains in `layouts/_markup/render-image.html`: titled images get figures and captions, and image links retain their original asset URLs as a no-JavaScript fallback. With JavaScript, an ordinary image click opens the original in a viewport-sized modal without cropping. The viewer has Close, Open original, and a fullscreen toggle when supported by the browser. Multiple images in the same post get previous/next arrows and left/right keyboard navigation, wrapping at the ends. Repeated asset URLs appear once. Escape closes the viewer; closing restores focus and unlocks page scrolling. Gallery keys use the source page's permalink, so separate posts and historical snapshots do not mix, including on lists and rendered comparisons. Article-list thumbnails retain their links to the article. Viewer UI is excluded from search indexing.
- Current post pages own the sole comment thread.

## Hyvor Talk

`hugo.toml` selects `provider = "hyvor"` and enables comments, but `websiteId` is deliberately empty. Production must provide:

```text
HUGO_PARAMS_COMMENTS_WEBSITEID=<numeric Hyvor Website ID>
```

Without the ID, Hugo emits no third-party embed. When configured, current posts lazy-load the full Hyvor component and list pages load comment counts.

Identity priority:

1. Explicit post `comment_id`.
2. Oldest Git revision-derived stable ID from generated history.
3. Hugo file UniqueID fallback.
4. Page permalink fallback for non-file pages.

Before importing WordPress comments, explicit IDs must be mapped to the WordPress identifier type chosen in Hyvor. See `docs/services.md`.

## Public version history

`scripts/generate_history.py` follows each post's `index.md` history, including renames. It generates ignored build inputs:

```text
content/post-versions/
data/generated_post_history.json
```

For every committed `index.md` revision it:

- Reads the old Markdown blob with `git show`.
- Copies the bundle assets that existed at that commit.
- Generates `/posts/<current-slug>/versions/<12-character-commit>/`.
- Records date, commit subject, URL, and current/past status.

Historical pages are read-only, `noindex, follow`, and point to the current post/comments. Current posts, historical pages, and comparison pages share version navigation when more than one committed version exists. At viewport widths of 1100px and above it appears as a sticky right sidebar, with the post retaining its original 652px reading width and the header spanning both columns. On narrower screens it follows the post in normal document order. It lists committed snapshots, dates and times, public commit subjects, and comparison links, with the active page indicated. Posts with neither multiple versions nor a ToC keep their existing single-column layout.

Each revision after the original also gets a comparison at `/posts/<current-slug>/versions/<12-character-commit>/changes/`, linked from the current post header, version-history list, and historical page. Both sides use Hugo-rendered `.Content` from exact committed snapshots (including the newest revision) and their corresponding assets. `static/post-changes.js` compares rendered text tokens using a bounded Myers diff, highlights added words in the complete updated post, and strikes through removed words in an expandable earlier version. It preserves the DOM structure and labels changed image descriptions and link destinations. Python's standard-library `difflib` handles title changes separately. Other front matter is excluded. No raw-HTML Markdown setting is enabled. Both formatted versions remain readable without JavaScript. Formatting-only revisions can be inspected in the two views; image pixels are not compared. Comparison pages are `noindex, follow` and contain no comments. An update remains an in-place Markdown edit plus a public-facing Git commit; see the authoring guide for update notes and `lastmod` conventions.

Known boundaries:

- Only commits touching `index.md` create versions; asset-only commits do not.
- Commit subjects are public site content.
- Generated history represents committed Git state, not uncommitted edits.
- A full clone is mandatory. `scripts/build.py` unshallows before generation.
- Generated directories are disposable and must never be committed or edited.

## Build and deployment

Required local verification:

```bash
python3 -m unittest discover -s tests
python3 scripts/build.py
```

For preview:

```bash
python3 scripts/generate_history.py
hugo server -D
```

Cloudflare Pages configuration:

```text
Production branch: main
Build command: python3 scripts/build.py
Output directory: public
```

Do not replace the production command with plain `hugo`; public history would disappear from a clean build.

Cloudflare Web Analytics is enabled using the Pages project Metrics dashboard. It is not represented by a tracked script or token in this repository.

## Apple Notes status

Apple Notes is not currently the primary publishing path. `scripts/publish.py` remains for possible future use and should not be invoked to publish direct Markdown posts.

The live Notes script selects `Status: publish` or `Status: published`, not the old `#blog` plus `#publish` rule still found in older commits. It can generate, update, rename, or remove Notes-managed bundles and stages all of `content/posts`, so future agents must keep it isolated from manual publishing.

## Known external setup still required

Repository code cannot complete these dashboard actions:

1. Create/configure the Hyvor Talk site and provide `HUGO_PARAMS_COMMENTS_WEBSITEID` in Cloudflare Pages.
2. Reconcile WordPress comment identifiers before importing comments.
3. Enable Cloudflare Web Analytics under the Pages project Metrics tab.
4. Confirm Cloudflare uses `python3 scripts/build.py`, output directory `public`, and a compatible Hugo version.
5. Replace or update the site's privacy notice with the operator's real Hyvor/Cloudflare practices before public launch.

## Safety and maintenance rules

- Read this file before work, plus the focused docs named in `AGENTS.md`.
- Preserve user content edits and unrelated dirty worktree files.
- Never stage all post bundles when publishing one manual post.
- Never edit generated history files.
- Never change a live `comment_id` without migrating the Hyvor thread.
- Treat `static/styles.css` as user-owned.
- Update this briefing whenever content formats, comment identity, history generation, external services, build commands, or deployment behavior change.
