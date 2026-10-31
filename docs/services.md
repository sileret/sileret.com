# External services

There is also a private, self-hosted VM staging deployment using Artalk comments
and GoAccess log analytics. See `docs/vm-deployment.md` and `deploy/vm/` for its
configuration, isolation tests, access and operational limits. It uses
`deploy/vm/hugo.toml` as a build-time override; the main Hyvor/Cloudflare settings
below remain the production configuration until cutover. Permanent comment IDs
must be preserved through any eventual provider migration.

The site is prepared for Hyvor Talk comments and Cloudflare Pages Web Analytics. Both require one-time configuration in their respective dashboards.

## Hyvor Talk comments

The repository selects Hyvor in `hugo.toml`, but intentionally stores no account-specific website ID. Without an ID, the templates emit no Hyvor embed or comments links.

One-time setup:

1. Create the site in the Hyvor Talk Console.
2. Add the production and preview domains allowed by the Hyvor website configuration.
3. Copy the numeric Website ID from **Settings → Website**.
4. In Cloudflare Pages, add `HUGO_PARAMS_COMMENTS_WEBSITEID` to both production and preview environment variables.
5. Trigger a new deployment.
6. Confirm that a post renders the comment form and the home page renders comment counts.
7. Configure moderation, spam filtering, guest-comment policy, and notification recipients in Hyvor.

For local testing without changing tracked configuration:

```bash
HUGO_PARAMS_COMMENTS_WEBSITEID=1234 python3 scripts/build.py
```

Replace `1234` with the real Website ID. A Website ID is not a secret, but environment configuration keeps deployment-specific values out of the repository.

Implementation structure:

```text
layouts/partials/comments.html
layouts/partials/comments/hyvor.html
layouts/partials/post-comment-id.html
layouts/partials/post-comments-link.html
layouts/partials/comment-count-loader.html
```

`comments.html` is the provider switch. A future commenting provider should be added as a new provider partial and selected with `params.comments.provider`; do not mix two live providers on the same post.

The full Hyvor embed loads only on individual current posts. Lists load the lighter comment-count component and link to `#comments`. Historical versions have no embed.

### WordPress comment migration

Export WordPress comments before retiring WordPress. Hyvor can import a WordPress XML export using WordPress post IDs, relative paths, or absolute URLs. Choose the identifier type deliberately and make the Hugo `comment_id` values match before the public Hyvor deployment. Keep the original export as a backup.

## Cloudflare Pages

Connect the Git repository to Cloudflare Pages with these settings:

```text
Production branch: main
Build command:     python3 scripts/build.py
Build directory:   public
```

Pin a Hugo version compatible with the locally verified version when Cloudflare offers a `HUGO_VERSION` environment setting. The implementation was verified with Hugo `0.164.0` extended.

The build script:

1. Fetches full Git history if Cloudflare supplied a shallow clone.
2. Generates historical post versions.
3. Runs `hugo --gc --minify`.

Do not replace the build command with plain `hugo`; doing so silently removes visitor-facing version history.

## Cloudflare Web Analytics

Enable analytics through Cloudflare rather than adding another analytics script to the repository:

1. Open **Workers & Pages**.
2. Select the Pages project.
3. Open **Metrics**.
4. Select **Enable** under **Web Analytics**.
5. Deploy once so Cloudflare injects its beacon.

Cloudflare Web Analytics is external state: the repository cannot enable or verify the dashboard toggle. Record any future change to the analytics provider in this document and in `docs/codex-project-notes.md`.

Cloudflare's standard Web Analytics notification is a weekly summary. Immediate configurable post-level traffic-spike alerts are not part of the normal Pages setup. Add a separate alerting service or a scheduled Cloudflare Worker only if that requirement becomes important enough to justify it.

## Privacy and disclosure

Hyvor processes commenter information, while Cloudflare Web Analytics measures aggregate visits. Before public launch, update the site's privacy notice with the actual account, retention, moderation, and contact details. Do not fabricate legal identity or retention information in repository templates; it must reflect the operator's real configuration.
