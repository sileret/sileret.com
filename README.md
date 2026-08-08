# sileret.com

A Hugo blog deployed from Git to Cloudflare Pages.

## Write

Create a long article:

```bash
hugo new content posts/my-article/index.md
```

Create a short thought, which is shown in full in post lists:

```bash
hugo new content --kind thought posts/my-thought/index.md
```

Put images beside `index.md` and reference them with relative Markdown paths.

## Preview and build

Generate Git-backed post history before previewing:

```bash
python3 scripts/generate_history.py
hugo server -D
```

Run the same production build used by Cloudflare Pages:

```bash
python3 scripts/build.py
```

The production output is written to `public/`.

## Publish

Set `draft: false`, commit the post bundle, and push the production branch. Cloudflare Pages deploys pushes automatically.

Read [docs/authoring-and-publishing.md](docs/authoring-and-publishing.md) for the complete workflow and [docs/services.md](docs/services.md) for Hyvor Talk and Cloudflare Web Analytics setup.
