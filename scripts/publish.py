#!/usr/bin/env python3
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
EXPORT_ROOT = Path(os.environ.get("NOTES_EXPORT_ROOT_DIR", ROOT / ".notes-export"))
CONTENT_DIR = ROOT / "content" / "posts"
TAG_LINE_PREFIX = "tags:"
SLUG_LINE_PREFIX = "slug:"
CONTROL_TAGS = {"blog", "publish", "published"}
PUBLISH_TAG = "publish"
PUBLISHED_TAG = "published"


@dataclass
class Note:
    note_id: str
    title: str
    tags: list
    slug_override: str | None
    body: str
    source_path: Path
    mtime: datetime
    has_publish: bool
    has_published: bool


def run(cmd, cwd=None, check=True):
    result = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    if check and result.returncode != 0:
        sys.stderr.write(result.stderr or result.stdout)
        raise SystemExit(result.returncode)
    return result


def slugify(text: str) -> str:
    value = unicodedata.normalize("NFKD", text)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value).strip("-")
    value = re.sub(r"-{2,}", "-", value)
    return value


def parse_note_id(path: Path) -> str:
    stem = path.stem
    match = re.match(r"(.+)-([A-Za-z0-9]+)$", stem)
    if match:
        return match.group(2)
    return slugify(stem) or stem


def clean_title(line: str) -> str:
    line = line.strip()
    if line.startswith("#"):
        line = line.lstrip("#").strip()
    return line


def parse_tags(line: str) -> list:
    tag_text = line.split(":", 1)[1] if ":" in line else ""
    tags = re.findall(r"#([A-Za-z0-9][A-Za-z0-9_-]*)", tag_text)
    return [t.lower() for t in tags]


def parse_slug(line: str) -> str | None:
    if ":" not in line:
        return None
    slug = line.split(":", 1)[1].strip()
    return slug or None


def parse_note_markdown(path: Path) -> Note | None:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    non_empty = [i for i, line in enumerate(lines) if line.strip() != ""]
    if not non_empty:
        return None
    title_idx = non_empty[0]
    title_line = clean_title(lines[title_idx])
    tag_idx = None
    slug_idx = None
    tags = []
    slug_override = None
    for i in range(title_idx + 1, min(title_idx + 8, len(lines))):
        stripped = lines[i].strip()
        lower = stripped.lower()
        if lower.startswith(TAG_LINE_PREFIX):
            tag_idx = i
            tags = parse_tags(stripped)
        if lower.startswith(SLUG_LINE_PREFIX):
            slug_idx = i
            slug_override = parse_slug(stripped)
    skip_indices = {title_idx}
    if tag_idx is not None:
        skip_indices.add(tag_idx)
    if slug_idx is not None:
        skip_indices.add(slug_idx)
    body_lines = [line for i, line in enumerate(lines) if i not in skip_indices]
    while body_lines and body_lines[0].strip() == "":
        body_lines.pop(0)
    body = "\n".join(body_lines).strip() + "\n" if body_lines else ""
    note_id = parse_note_id(path)
    mtime = datetime.fromtimestamp(path.stat().st_mtime).astimezone()
    has_publish = PUBLISH_TAG in tags
    has_published = PUBLISHED_TAG in tags
    return Note(
        note_id=note_id,
        title=title_line or path.stem,
        tags=tags,
        slug_override=slug_override,
        body=body,
        source_path=path,
        mtime=mtime,
        has_publish=has_publish,
        has_published=has_published,
    )


def parse_front_matter(text: str) -> tuple[dict, str]:
    if not text.startswith("---\n"):
        return {}, text
    lines = text.splitlines()
    end_idx = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            end_idx = i
            break
    if end_idx is None:
        return {}, text
    fm_lines = lines[1:end_idx]
    body = "\n".join(lines[end_idx + 1 :]).lstrip("\n")
    data = {}
    i = 0
    while i < len(fm_lines):
        line = fm_lines[i]
        if ":" not in line:
            i += 1
            continue
        key, value = line.split(":", 1)
        key = key.strip()
        value = value.strip()
        if key == "tags":
            tags = []
            if value:
                tags = [t.strip().strip("'\"") for t in value.strip("[]").split(",") if t.strip()]
            i += 1
            while i < len(fm_lines) and fm_lines[i].strip().startswith("-"):
                tag_val = fm_lines[i].strip().lstrip("-").strip().strip("'\"")
                if tag_val:
                    tags.append(tag_val)
                i += 1
            data["tags"] = tags
            continue
        data[key] = value.strip("'\"")
        i += 1
    return data, body


def load_existing_posts() -> dict:
    mapping = {}
    if not CONTENT_DIR.exists():
        return mapping
    for index in CONTENT_DIR.glob("*/index.md"):
        fm, _ = parse_front_matter(index.read_text(encoding="utf-8"))
        note_id = fm.get("note_id")
        if note_id:
            mapping[note_id] = {
                "slug": index.parent.name,
                "date": fm.get("date"),
                "lastmod": fm.get("lastmod"),
            }
    return mapping


def ensure_unique_slug(slug: str, note_id: str) -> str:
    index_path = CONTENT_DIR / slug / "index.md"
    if not index_path.exists():
        return slug
    fm, _ = parse_front_matter(index_path.read_text(encoding="utf-8"))
    existing_note_id = fm.get("note_id")
    if existing_note_id and existing_note_id != note_id:
        return f"{slug}-{note_id[:6]}"
    return slug


def format_dt(dt: datetime) -> str:
    return dt.isoformat(timespec="seconds")


def parse_dt(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        try:
            return datetime.strptime(value, "%Y-%m-%d")
        except ValueError:
            return None


def is_local_link(target: str) -> bool:
    target = target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1]
    lowered = target.lower()
    return not (
        lowered.startswith("http://")
        or lowered.startswith("https://")
        or lowered.startswith("mailto:")
        or lowered.startswith("data:")
        or lowered.startswith("#")
    )


def split_link_target(raw: str) -> tuple[str, str]:
    raw = raw.strip()
    if raw.startswith("<") and raw.endswith(">"):
        return raw[1:-1], ""
    if " " in raw:
        path, tail = raw.split(" ", 1)
        return path, " " + tail
    return raw, ""


def rewrite_links(body: str, md_dir: Path, bundle_dir: Path) -> tuple[str, list]:
    attachments = []
    attachments_dir = bundle_dir / "attachments"

    def replace(match):
        target = match.group(2)
        path, tail = split_link_target(target)
        if not is_local_link(path):
            return match.group(0)
        if path.startswith("/"):
            return match.group(0)
        source_path = (md_dir / path).resolve()
        if not source_path.exists():
            return match.group(0)
        new_name = source_path.name
        attachments.append((source_path, attachments_dir / new_name))
        new_target = f"attachments/{new_name}{tail}"
        return f"{match.group(1)}{new_target}{match.group(3)}"

    pattern = re.compile(r'(!?\[[^\]]*\]\()([^)]+)(\))')
    updated = pattern.sub(replace, body)
    return updated, attachments


def write_post(note: Note, slug: str, existing: dict | None) -> tuple[Path, bool]:
    bundle_dir = CONTENT_DIR / slug
    bundle_dir.mkdir(parents=True, exist_ok=True)
    attachments_dir = bundle_dir / "attachments"
    if attachments_dir.exists():
        shutil.rmtree(attachments_dir)
    body, attachments = rewrite_links(note.body, note.source_path.parent, bundle_dir)
    for source, dest in attachments:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)

    publish_date = existing.get("date") if existing else None
    if not publish_date:
        publish_date = format_dt(note.mtime)
    lastmod = format_dt(note.mtime)
    tags = [t for t in note.tags if t not in CONTROL_TAGS]

    front_matter = ["---"]
    front_matter.append(f'title: "{note.title}"')
    front_matter.append(f"date: {publish_date}")
    front_matter.append(f"lastmod: {lastmod}")
    if tags:
        front_matter.append("tags:")
        for tag in tags:
            front_matter.append(f"  - {tag}")
    front_matter.append(f'note_id: "{note.note_id}"')
    front_matter.append("---")
    content = "\n".join(front_matter) + "\n\n" + body.strip() + "\n"

    index_path = bundle_dir / "index.md"
    previous = index_path.read_text(encoding="utf-8") if index_path.exists() else None
    index_path.write_text(content, encoding="utf-8")
    changed = previous != content
    return index_path, changed


def ensure_export():
    exporter = shutil.which("exportnotes.zsh")
    cmd_prefix = None
    if exporter:
        cmd_prefix = [exporter]
    else:
        local_exporter = ROOT / "tools" / "notes-exporter" / "exportnotes.zsh"
        if local_exporter.exists():
            cmd_prefix = ["/bin/zsh", str(local_exporter)]
    if not cmd_prefix:
        sys.stderr.write(
            "exportnotes.zsh not found. Install notes-exporter or clone it into tools/notes-exporter.\n"
        )
        raise SystemExit(1)
    EXPORT_ROOT.mkdir(parents=True, exist_ok=True)
    run(
        cmd_prefix
        + [
            "--root-dir",
            str(EXPORT_ROOT),
            "--convert-markdown",
            "true",
            "--filename-format",
            "&title-&id",
            "--use-subdirs",
            "false",
        ]
    )


def update_notes_to_published(titles: list[str]):
    if not titles:
        return
    script = r"""
on run argv
  set targetTitles to argv
  set updatedCount to 0
  tell application "Notes"
    repeat with acc in accounts
      repeat with fold in folders of acc
        repeat with n in notes of fold
          set noteName to name of n
          if targetTitles contains noteName then
            set noteBody to body of n
            if noteBody contains "#publish" then
              set body of n to my replace_text(noteBody, "#publish", "#published")
              set updatedCount to updatedCount + 1
            end if
          end if
        end repeat
      end repeat
    end repeat
  end tell
  return updatedCount
end run

on replace_text(theText, searchString, replaceString)
  set AppleScript's text item delimiters to searchString
  set theItems to every text item of theText
  set AppleScript's text item delimiters to replaceString
  set theText to theItems as string
  set AppleScript's text item delimiters to ""
  return theText
end replace_text
"""
    with subprocess.Popen(
        ["osascript", "-"] + titles,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    ) as proc:
        stdout, stderr = proc.communicate(script)
        if proc.returncode != 0:
            sys.stderr.write(stderr or stdout)
            raise SystemExit(proc.returncode)


def git(cmd):
    return run(["git"] + cmd, cwd=ROOT, check=False)


def main():
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    ensure_export()

    existing = load_existing_posts()
    markdown_files = list(EXPORT_ROOT.rglob("*.md"))
    if not markdown_files:
        print("No exported markdown files found.")
        return

    updated_titles = []
    written = 0
    skipped = 0

    for md_path in markdown_files:
        note = parse_note_markdown(md_path)
        if not note:
            continue
        if "blog" not in note.tags:
            continue
        if not (note.has_publish or note.has_published):
            continue
        existing_info = existing.get(note.note_id)
        existing_lastmod = parse_dt(existing_info.get("lastmod")) if existing_info else None
        if note.has_published and not note.has_publish and existing_lastmod:
            if note.mtime <= existing_lastmod:
                skipped += 1
                continue

        slug = None
        if note.slug_override:
            slug = slugify(note.slug_override)
        elif existing_info:
            slug = existing_info.get("slug")
        else:
            slug = slugify(note.title)
        if not slug:
            slug = note.note_id
        slug = ensure_unique_slug(slug, note.note_id)

        if existing_info and note.slug_override and slug != existing_info.get("slug"):
            old_dir = CONTENT_DIR / existing_info.get("slug")
            new_dir = CONTENT_DIR / slug
            if old_dir.exists() and not new_dir.exists():
                old_dir.rename(new_dir)

        _, changed = write_post(note, slug, existing_info)
        written += 1
        if note.has_publish:
            updated_titles.append(note.title)

    if written == 0:
        print("No matching notes found with #blog and #publish/#published.")
        return

    git(["add", str(CONTENT_DIR)])
    diff_check = git(["diff", "--cached", "--quiet"])
    if diff_check.returncode != 0:
        git(["commit", "-m", f"Publish {written} posts"])
        push = git(["push"])
        if push.returncode != 0:
            sys.stderr.write("Git push failed. Notes not updated.\n")
            raise SystemExit(push.returncode)
    update_notes_to_published(updated_titles)
    print(f"Processed: {written}, skipped: {skipped}")


if __name__ == "__main__":
    main()
