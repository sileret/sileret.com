# Shortcut + Publish Script Workflow

Use this workflow when Shortcut is responsible for selecting notes by Apple Notes tags, and `scripts/publish.py` handles Hugo post generation + git publish.

## Script mode

Run publish script in Shortcut-export mode:

```bash
NOTES_EXPORT_ROOT_DIR="/absolute/path/to/shortcut-export" python3 scripts/publish.py --skip-export --dry-run
```

Then publish for real:

```bash
NOTES_EXPORT_ROOT_DIR="/absolute/path/to/shortcut-export" python3 scripts/publish.py --skip-export
```

In `--skip-export` mode, the script:

- reads existing `.md` files from `NOTES_EXPORT_ROOT_DIR`
- does **not** run AppleScript Notes export
- does **not** rewrite Notes bodies from `#publish` to `#published`

## Required export file format

Each note should be one markdown file.

Recommended filename:

`<slug>-<stable-note-id>.md`

File content format:

```md
Note title
Control: blog publish
Note ID: p11458
Modified: 2026-03-03T16:45:00+01:00
Slug: optional-custom-slug

Actual note content starts here.
```

Notes:

- `Control:` can also be `Tags:`
- Control tokens can be plain text (`blog publish`) or hashtags (`#blog #publish`)
- `Note ID:` should be stable across runs so updates map to the same post
- `Modified:` should be ISO-8601 to avoid false updates from file write time

## Shortcut structure (high-level)

1. Find Notes with tags `blog` and `publish`.
2. Delete existing files in the export folder (avoid stale input).
3. Repeat each found note:
   - get title
   - get note body/plain text
   - get note identifier (preferred) and last modified date
   - build markdown text using the format above
   - save to export folder as `<slug>-<id>.md`
4. Optionally run on Mac:
   - `python3 scripts/publish.py --skip-export --dry-run`
   - then without `--dry-run` after review
