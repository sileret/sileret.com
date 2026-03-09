# Project Instructions (Codex)

This repository is a Hugo blog.

## Scope
- Make changes in-place in this repo.
- Do not introduce tooling that changes site output format unless explicitly requested.

## Important Paths
- Site config: `hugo.toml`
- Content posts: `content/posts/<slug>/index.md`
- About page content: `content/about/index.md`
- Templates: `layouts/`
- Site CSS: `static/styles.css`
- Publish script: `scripts/publish.py`

## Styling Guardrail
- Treat `static/styles.css` as user-owned.
- Do not change `static/styles.css` unless the user explicitly asks for CSS edits.

## Publishing Workflow
- Local preview: `hugo server -D`
- Build check: `hugo`
- Publish command: `python3 scripts/publish.py`

### What `scripts/publish.py` does
- Recreates `.notes-export/` on each run (temporary cache only).
- Exports notes from Apple Notes folder `Blog` by default (`NOTES_BLOG_FOLDER` can override).
- Parses tags from explicit text hashtags on the `Tags:` line.
- Publishes only notes that contain:
  - `#blog`
  - and either `#publish` or `#published`
- Writes/updates generated notes under `content/posts/`.
- Commits and pushes only when there are staged content changes.

## Manual Post Guidance
- Manual/non-Notes posts are valid if they live under `content/posts/<slug>/index.md`.
- Put post images in the same bundle folder (for example `content/posts/<slug>/image.png`) and reference by relative path in Markdown/front matter.

## Operational Safety
- Never use destructive git commands (for example `git reset --hard`) unless explicitly requested.
- If unexpected local changes appear, pause and ask before proceeding.
- Preserve user content edits unless explicitly asked to rewrite them.

## Quick Pre-Publish Checklist
- `git status --short`
- `hugo` (or `hugo server -D` and visually check key pages)
- Confirm no unintended posts are staged
- Then run `python3 scripts/publish.py`
