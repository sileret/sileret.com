# Authoring and publishing

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

## Comment identity

`comment_id` is the permanent Hyvor Talk thread identifier. Do not change it after a post receives comments, even if its title or URL changes.

New archetypes initially use the slug. Before importing existing WordPress comments, set each migrated post's `comment_id` to the identifier type selected in Hyvor's import screen—normally the old WordPress post ID or relative path. Complete the mapping before enabling comments publicly.

If `comment_id` is absent, the site uses a stable identifier derived from the post's oldest Git revision. That is safe for new comment threads but is not automatically compatible with WordPress import identifiers.

Set `comments: false` on a post to suppress both its comment link and embed.

## Public version history

`scripts/generate_history.py` reads the Git history of each `content/posts/<slug>/index.md`. It generates:

- A version list on the current post.
- Read-only historical pages under `/posts/<slug>/versions/<commit>/`.
- The assets present in each historical bundle revision.
- A stable fallback comment identifier based on the oldest revision.

Historical pages are marked `noindex, follow` and do not contain a separate comment thread. They link back to the current post and its comments.

Generated source lives in `content/post-versions/` and `data/generated_post_history.json`. Both paths are ignored by Git, recreated on every build, and must never be edited manually.

Important consequences:

- Each committed change to `index.md` becomes a visible version.
- Commit subjects are shown publicly in the version list; write suitable commit messages.
- A complete Git clone is required. `scripts/build.py` automatically converts a shallow clone to a full clone before generating history.
- Asset-only changes do not create a new textual version unless `index.md` changes in the same commit.
- Historical pages reflect committed content only, never uncommitted working-tree edits.

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
8. Push the Cloudflare Pages production branch, normally `main`.
9. Check the Cloudflare deployment result and the live post.

Example:

```bash
git add content/posts/my-article
git diff --cached
git commit -m "Publish my article"
git push
```

Do not use `scripts/publish.py` for a manually authored post. That script is the separate Apple Notes synchronization workflow and may write or remove generated Notes posts.
