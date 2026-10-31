# Project Instructions (Codex)

This repository is a Hugo blog deployed through Cloudflare Pages.

The active implementation also has a private Debian VM, `prod-blog-01`, on
`prod-vmh-03`. Git auto-publishing follows `codex/private-blog`. Keep that VM
private until the user explicitly requests public cutover; public `main` and
the existing Cloudflare deployment must remain unchanged during private work.

## Scope

- Make changes in place in this repository.
- Do not introduce tooling that changes the site output format unless explicitly requested.
- Preserve user-authored content and unrelated working-tree changes.

## Required read first

- Before any work, read `docs/codex-project-notes.md` and use it as the repository-specific briefing.
- For content or deployment work, also read `docs/authoring-and-publishing.md`.
- For VM deployment work, also read `docs/vm-deployment.md`.
- For comments or analytics work, also read `docs/services.md`.

## Important paths

- Site config: `hugo.toml`
- Content posts: `content/posts/<slug>/index.md`
- About page: `content/about/index.md`
- Templates: `layouts/`
- Site CSS: `static/styles.css`
- Production build: `scripts/build.py`
- Public history generator: `scripts/generate_history.py`
- Legacy Apple Notes sync: `scripts/publish.py`

## Styling guardrail

- Treat `static/styles.css` as user-owned.
- Do not change `static/styles.css` unless the user explicitly asks for CSS edits.

## Current authoring model

- Direct Markdown authoring is the primary workflow; Apple Notes is not currently the publishing source.
- Articles use `format: article`, show summaries in lists, and may use `<!--more-->` to set the summary boundary.
- Thoughts use `format: thought` and display their complete content in lists.
- New posts should have a permanent `comment_id`. Never change it after comments exist.
- Manual posts are leaf bundles under `content/posts/<slug>/` with assets stored beside `index.md`.

Create an article:

```bash
hugo new content posts/<slug>/index.md
```

Create a thought:

```bash
hugo new content --kind thought posts/<slug>/index.md
```

## Build and preview

Public version history is generated from Git and is not committed. Plain `hugo` produces an incomplete site if generated history is absent.

Local preview:

```bash
python3 scripts/generate_history.py
hugo server -D
```

Production build and required build check:

```bash
python3 -m unittest discover -s tests
python3 scripts/build.py
```

Cloudflare Pages must use:

```text
Build command:   python3 scripts/build.py
Output directory: public
```

`scripts/build.py` fetches full history for shallow clones, regenerates public versions, and runs Hugo. Generated paths `content/post-versions/` and `data/generated_post_history.json` are ignored and must not be edited or staged.

## Comments and analytics

- Hyvor Talk is the selected comment provider.
- The website ID comes from the deployment environment variable `HUGO_PARAMS_COMMENTS_WEBSITEID`; it is intentionally blank in `hugo.toml`.
- Comment embeds belong only to current post pages. Historical versions are read-only and link to the current discussion.
- Cloudflare Web Analytics is enabled in the Cloudflare dashboard, not in repository code.
- Read `docs/services.md` before changing providers or comment identifiers.

## Publishing workflow

For direct Markdown posts:

1. `git status --short`
2. `python3 -m unittest discover -s tests`
3. `python3 scripts/build.py`
4. Stage only the intended post bundle and related implementation files.
5. Inspect `git diff --cached` and confirm no unintended posts are staged.
6. Commit using a public-facing message; commit subjects appear in post version history.
7. During private VM staging, push `codex/private-blog` and verify the VM's
   publisher and deployed revision. Push the Cloudflare production branch only
   when the user explicitly requests that public deployment.

Do not use `scripts/publish.py` for a manual post. It is a separate Apple Notes synchronization workflow and can write or remove Notes-managed bundles.

## Legacy Apple Notes workflow

The live script uses `Status: publish` or `Status: published` to select notes. Older documentation and history may mention `#blog`/`#publish`; that description is obsolete.

- `python3 scripts/publish.py --dry-run`: inspect Notes sync.
- `python3 scripts/publish.py --local-only`: write Notes-derived bundles without Git publishing.
- `--skip-export`: read pre-exported Markdown from `NOTES_EXPORT_ROOT_DIR`.

Only work on this workflow when the user explicitly returns to Apple Notes publishing.

## Operational safety

- VM administration is limited to `prod-blog-01`. Leave the other VMs and the
  shared libvirt network unchanged. Do not open public ports or change DNS as
  part of routine Git publishing.

- Never use destructive Git commands such as `git reset --hard` unless explicitly requested.
- If unexpected local changes appear, stop and ask before overlapping or staging them.
- Preserve user content edits unless explicitly asked to rewrite them.
- Do not stage all of `content/posts/` when publishing one manual post.
