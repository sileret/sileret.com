# Codex project notes

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

The site currently uses Hugo `0.164.0` extended locally. `hugo.toml` uses `locale = "en-US"`; the deprecated `languageCode` key is no longer used.

## Repository map

- `hugo.toml`: site and provider-neutral comment configuration.
- `archetypes/posts.md`: standard article archetype.
- `archetypes/thought.md`: quick-thought archetype.
- `content/posts/<slug>/index.md`: current posts.
- `content/about/index.md`: About page.
- `layouts/partials/post-card.html`: shared home/list rendering for articles and thoughts.
- `layouts/partials/comments.html`: comment-provider dispatcher.
- `layouts/partials/comments/hyvor.html`: Hyvor full-post embed.
- `layouts/partials/post-comment-id.html`: stable comment identity resolution.
- `layouts/partials/post-comments-link.html`: post-list comment link/count.
- `layouts/partials/comment-count-loader.html`: one Hyvor count loader per list page.
- `layouts/_default/single.html`: current post/page template and public history list.
- `layouts/_default/post-version.html`: read-only historical-version template.
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
- Section/taxonomy lists use `layouts/_default/list.html`.
- Both delegate each item to `layouts/partials/post-card.html` so article/thought behavior cannot drift between templates.
- Article thumbnails are selected in this order: `title-image*`, `cover*`, then the first bundle image.
- Thumbnails use Hugo image processing with `.Fill "960x270 Top"`.
- Article summaries containing an image fall back to truncated plain text.
- Comment counts load only when the Hyvor Website ID is configured.

## Single posts

- Show Article/Thought, publication date, optional update date, and article reading time.
- Article table of contents is rendered when Hugo produces a non-empty TOC.
- Thoughts do not render a TOC.
- Markdown image behavior remains in `layouts/_markup/render-image.html`: images link to originals; titled images get figures and captions.
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

For every prior committed `index.md` revision it:

- Reads the old Markdown blob with `git show`.
- Copies the bundle assets that existed at that commit.
- Generates `/posts/<current-slug>/versions/<12-character-commit>/`.
- Records date, commit subject, URL, and current/past status.

Historical pages are read-only, `noindex, follow`, and point to the current post/comments. The current post contains a collapsible version list when more than one committed version exists.

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
