# Authoring and publishing

For the private Debian VM preview, also read `docs/vm-deployment.md`. It provides
Sveltia mobile editing and uses the same post bundles and permanent comment IDs.
VM builds add `--search --config hugo.toml,deploy/vm/hugo.toml`; Git auto-publishing
is enabled for `codex/private-blog`. Commit and push to that branch during
private staging; Sveltia targets it too. Cloudflare builds refuse this private
branch, and public `main` stays unchanged until a deliberate cutover.

This is the canonical workflow for posts written directly in the Hugo repository. Apple Notes is not part of the primary publishing path.

## Content model

Every post is a Hugo leaf bundle:

```text
content/posts/<slug>/
├── index.md
├── cover.jpg
└── another-image.png
```

Images and other post assets belong beside `index.md` and use relative links.

## Articles and thoughts

Create an article:

```bash
hugo new content posts/my-article/index.md
```

The `archetypes/posts.md` archetype sets:

```yaml
format: article
draft: true
comments: true
comment_id: "my-article"
```

Articles display a summary, estimated reading time, and an explicit “Continue reading” link in post lists. Put Hugo's manual summary divider on its own line to control the cutoff:

```markdown
This introduction appears in post lists.

<!--more-->

The rest appears only on the post page.
```

Create a thought:

```bash
hugo new content --kind thought posts/my-thought/index.md
```

Thoughts use `format: thought` and display their complete content in post lists. Their title and comments link still lead to a permanent post page.

Existing posts without `format` are treated as articles for backward compatibility. Any unknown format also falls back to article rendering.

Articles with a table of contents show its section links in the sidebar after the original ToC has scrolled out of view above the sticky header. Returning to the original ToC hides the sidebar copy. On narrower screens the sidebar continues to follow the post; the fixed “Scroll to top” link remains available on every page at every screen width. These navigation aids require no additional front matter.

The sidebar highlights the current section as the reader scrolls, including subsections. Following a ToC link updates the highlight automatically. The marker clears when returning above the first section.

The header's theme icon cycles through System (monitor), Light (sun), and Dark (moon). System follows the visitor's device setting automatically. An explicit choice is remembered in that browser and selecting System restores automatic switching. This is a reader preference and requires no front-matter changes.

## Comment identity

`comment_id` is the permanent Hyvor Talk thread identifier. Do not change it after a post receives comments, even if its title or URL changes.

New archetypes initially use the slug. Before importing existing WordPress comments, set each migrated post's `comment_id` to the identifier type selected in Hyvor's import screen—normally the old WordPress post ID or relative path. Complete the mapping before enabling comments publicly.

If `comment_id` is absent, the site uses a stable identifier derived from the post's oldest Git revision. That is safe for new comment threads but is not automatically compatible with WordPress import identifiers.

Set `comments: false` on a post to suppress both its comment link and embed.

## Public version history

`scripts/generate_history.py` reads the Git history of each `content/posts/<slug>/index.md`. It generates:

- Version navigation on the current post, historical snapshots, and comparison pages.
- Read-only historical pages under `/posts/<slug>/versions/<commit>/`.
- The assets present in each historical bundle revision.
- Word-level comparisons between each revision and its preceding committed revision.
- A stable fallback comment identifier based on the oldest revision.

Historical pages are marked `noindex, follow` and do not contain a separate comment thread. They link back to the current post and its comments.

The post header links to the latest comparison with “See what changed.” Each version-history entry except the original has a “What changed” link at `/posts/<slug>/versions/<commit>/changes/`. Comparisons show the complete formatted updated post with word additions highlighted. An expandable earlier version shows removals struck through in their original context. Headings, emphasis, links, lists, code, and images retain their normal Hugo rendering. Changed image descriptions and link destinations receive a short label. Title changes are shown separately; dates, tags, and other front matter are omitted. Metadata-only revisions explain that there is no title or text change. Comparisons are also `noindex, follow` and keep discussion on the current post.

When a post has multiple committed versions, version navigation appears beside it on wide screens (1100px and above) and below it on narrower screens, including phones. The same navigation is available while reading old versions or highlighted comparisons. It links to the current post, each committed snapshot, and its changes, showing the date, time, and public commit subject. No additional authoring fields are required.

The front page uses the same responsive layout, with Recently updated and Explore instead of a specific post's version history. Recently updated includes up to five published posts whose `lastmod` is later than `date` and which have multiple committed versions, sorted by `lastmod`. It shows one entry per post, with its title, date, latest public commit subject, and comparison link. Optionally set `update_summary: "Added the cost comparison and revised the conclusion."` to supply a clearer description, or `show_update: false` to omit a housekeeping update. Advance `lastmod` for meaningful updates; the feed does not infer editorial significance from Git changes. Explore includes populated topics with published-post counts and an all-posts link. Drafts are excluded from both sidebar sections, including draft-aware previews.

Both sides come from exact committed snapshots with their corresponding bundle assets, including the newest committed version. A small local JavaScript file adds highlights to the rendered text; without JavaScript, both formatted versions remain readable. Formatting-only changes can be inspected in the two versions. Image pixels are not compared, and asset-only commits still do not create a revision.

Generated source lives in `content/post-versions/` and `data/generated_post_history.json`. Both paths are ignored by Git, recreated on every build, and must never be edited manually.

Important consequences:

- Each committed change to `index.md` becomes a visible version.
- Commit subjects are shown publicly in the version list; write suitable commit messages.
- A complete Git clone is required. `scripts/build.py` automatically converts a shallow clone to a full clone before generating history.
- Asset-only changes do not create a new textual version unless `index.md` changes in the same commit.
- Historical pages reflect committed content only, never uncommitted working-tree edits.

## Updating an existing post

Edit the existing `content/posts/<slug>/index.md` in place. Git supplies the old text for readers automatically; you do not need to copy old paragraphs or create a separate post.

For a meaningful update, keep `date` as the original publication date and set `lastmod` to the update time. Add a short dated note near the top when readers need an explanation:

```markdown
> **Updated October 21, 2026:** Added the cost comparison and revised the conclusion.
```

Corrections that change the meaning should explicitly say what was wrong and what is now correct. Small typo fixes can be silent, although each committed edit still appears in version history.

Follow the publishing checklist below, committing each publishable update with a description readers can understand, such as “Add cost comparison and revise conclusion.” One commit produces one version per changed post. After committing, regenerate the local preview to see its comparison; after pushing, the production build does this automatically. The first committed version has no preceding version to compare.

## Local workflow

Generate history and start a draft-aware preview:

```bash
python3 scripts/generate_history.py
hugo server -D
```

After editing, run the production build:

```bash
python3 -m unittest discover -s tests
python3 scripts/build.py
```

## Publishing checklist

1. Set the post's `draft` field to `false`, or remove it.
2. Inspect `git status --short`.
3. Run `python3 -m unittest discover -s tests`.
4. Run `python3 scripts/build.py`.
5. Stage only the intended post bundle and related implementation files.
6. Inspect `git diff --cached`.
7. Commit with a public, descriptive message.
8. During private staging, push `codex/private-blog`. Use public `main` only for
   an explicitly requested legacy Cloudflare deployment or planned cutover.
9. Check the private VM publisher and served revision, or the Cloudflare result
   when that public deployment was explicitly requested.

Example:

```bash
git add content/posts/my-article
git diff --cached
git commit -m "Publish my article"
git push
```

Do not use `scripts/publish.py` for a manually authored post. That script is the separate Apple Notes synchronization workflow and may write or remove generated Notes posts.
