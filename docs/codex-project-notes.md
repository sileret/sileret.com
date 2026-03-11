# Codex Project Notes

This file is for future Codex sessions working in this repository. It records the current structure and behavior of the site as implemented, not just the intended workflow.

## Project snapshot

- Static site generator: Hugo
- Theme model: custom templates in `layouts/`; no external theme
- Main site stylesheet: `static/styles.css`
- Content model: page bundles under `content/posts/<slug>/index.md`
- Publish automation: `scripts/publish.py`

Current config in `hugo.toml` is minimal:

- site title: `sileret`
- taxonomy: `tag -> tags`
- home page does not use `params.heroTitle` or `params.tagline` anywhere in templates
- `params.contactEmail` is configured but currently unused in templates

## Repo map

- `hugo.toml`: site config
- `content/_index.md`: home page body content
- `content/about/index.md`: About page content
- `content/posts/<slug>/index.md`: blog posts
- `layouts/index.html`: home page post feed
- `layouts/_default/list.html`: section and taxonomy list pages
- `layouts/_default/single.html`: regular single content pages, including posts
- `layouts/about/single.html`: About page layout
- `layouts/_default/baseof.html`: shared HTML shell and navigation
- `static/styles.css`: user-owned site styling; do not edit unless explicitly asked
- `scripts/publish.py`: Apple Notes/Shortcut import, Hugo bundle generation, git publish
- `docs/shortcut-publish-workflow.md`: Shortcut export mode notes

## Rendering behavior

### Home page

- Uses `layouts/index.html`.
- Displays the 12 most recent pages in section `posts`.
- Does not use Hugo pagination despite `pagination.pagerSize = 10` in config.

### Post and list cards

- Both home and list pages try to find a thumbnail in this order:
  1. resource matching `title-image*`
  2. resource matching `cover*`
  3. first image resource in the bundle
- Card summary uses `.Summary` unless the summary contains an image, in which case it falls back to truncated plain text.

### Single posts

- Post layout shows title, `date`, optional `lastmod`, tags, and full content.
- There is no custom shortcode or special post rendering logic in this repo at the moment.

### About page

- Uses a dedicated layout, but the layout is minimal and just renders `.Content`.

### Tags

- Taxonomy is enabled via `tag = "tags"`.
- There is no custom tags template; Hugo will fall back to the default list template for tag pages.

## Content conventions

### Post bundles

- Posts are leaf bundles: `content/posts/<slug>/index.md`
- Images can live beside `index.md` and be referenced relatively
- Example already in repo: `content/posts/renaissance-technologies/rentec-aerial-view.png`

### Front matter used by generated posts

The publish script writes:

```yaml
---
title: "Post title"
date: 2026-03-01T12:00:00+01:00
lastmod: 2026-03-03T12:00:00+01:00
tags:
  - example
note_id: "p11419"
---
```

Notes:

- `note_id` is how the publish script matches an exported note to an existing post.
- Existing `date` is preserved on republish; `lastmod` is refreshed from the note modified time.
- Manual posts are valid without `note_id`, but the publish script only tracks posts that do have one.

## Publish script: actual behavior

`scripts/publish.py` is the operational core of this repo. Future changes should be based on the code below, not older assumptions.

### Export modes

Default mode:

- Recreates `.notes-export/`
- Uses AppleScript to export notes from Apple Notes folder `Blog` unless overridden by `NOTES_BLOG_FOLDER`
- Exports every note in that folder, not just notes containing a `Tags:` line
- Reads both `plaintext` and HTML `body` from Apple Notes during export
- Extracts embedded Notes images from HTML `data:image/...` sources into per-note export asset folders like `<note>.assets/`
- Rewrites inline Notes images into Markdown image links pointing at those exported asset files

Shortcut mode:

- `--skip-export` reads pre-exported markdown files from `NOTES_EXPORT_ROOT_DIR`
- Does not run AppleScript export
- Does not update Apple Notes bodies unless code is changed

Local preview mode:

- `--local-only` writes or updates post bundles locally
- Skips git staging, commit, and push
- Skips updating Apple Notes from `Status: publish` to `Status: published`

### What qualifies a note for publishing

After export, a note is considered publishable when:

- it has `Status: publish` or `Status: published`

Important detail:

- The parser understands `Tags:`, `Control:`, `Status:`, `Slug:`, `Note ID:`, `note_id:`, `Modified:`, and `Lastmod:`.
- Explicit hashtag tokens on the `Tags:` or `Control:` line are preferred when present.
- Control tags `blog`, `publish`, and `published` are stripped before writing Hugo `tags` front matter.

### Post writing behavior

For each qualifying note, the script:

- resolves slug from `Slug:` override, existing post slug, or slugified title
- preserves the old slug unless a new explicit slug override is supplied
- renames the bundle directory when an existing post gets a new slug override
- converts embedded Apple Notes images into local Markdown image links during export
- rewrites relative Markdown links to local files into `attachments/<filename>`
- recreates the `attachments/` folder on each write
- copies linked local files into the post bundle

### Republish behavior

- If note status is `published` and the exported note `mtime` is not newer than the post `lastmod`, the script skips rewriting that post.
- If note status is `publish`, the script writes the post and later attempts to update the Apple Note body from `Status: publish` to `Status: published` in default export mode.
- If an exported note maps to an existing generated post and no longer has `Status: publish` or `Status: published`, the script removes that post bundle.

### Git behavior

When at least one post is written or removed, the script:

- stages `content/posts`, including deletions
- commits only if the staged diff is non-empty
- pushes
- aborts Notes status updates if `git push` fails

The script does not stage templates, config, docs, or CSS.

## Known mismatches and footguns

These are the most important things to re-check before future edits:

1. `AGENTS.md` still describes publish selection in terms of `#blog` plus `#publish` or `#published`, but the live script now requires `Status: publish` / `Status: published`.
2. `docs/shortcut-publish-workflow.md` mentions `Control: blog publish` and `Tags:`-style exports, which is only part of the current picture.
3. `baseURL` in `hugo.toml` is still `https://example.com/`; if production behavior ever matters, verify whether deployment overrides it externally.
4. `pagination.pagerSize` is configured but unused because the home page template manually takes the first 12 posts.

## Safe working rules for future Codex sessions

- Treat `static/styles.css` as user-owned and off-limits unless the user explicitly asks for CSS edits.
- Preserve existing post content unless the user asks for editorial changes.
- Assume `content/posts/` may contain a mix of generated and manual posts.
- Before changing publish behavior, inspect both `scripts/publish.py` and the latest docs because repo instructions have already drifted once.
- If a task touches publishing, always check whether the user means Apple Notes export mode or Shortcut `--skip-export` mode.

## Recommended verification workflow

For routine site changes:

```bash
git status --short
hugo
```

For publish workflow changes:

```bash
git status --short
python3 scripts/publish.py --dry-run
hugo
```

For Shortcut export mode:

```bash
NOTES_EXPORT_ROOT_DIR="/absolute/path/to/export" python3 scripts/publish.py --skip-export --dry-run
hugo
```

Use `hugo server -D` only when a visual check is needed.

## When this file should be updated

Update this document whenever any of the following change:

- publish eligibility rules
- note export format
- front matter written by the script
- bundle/image conventions
- template selection logic
- verification or deploy workflow
