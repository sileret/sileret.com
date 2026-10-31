#!/usr/bin/env python3
"""Generate visitor-facing historical post versions from the Git repository."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
POSTS_DIR = ROOT / "content" / "posts"
GENERATED_CONTENT_DIR = ROOT / "content" / "post-versions"
GENERATED_DATA_PATH = ROOT / "data" / "generated_post_history.json"
COMMIT_MARKER = "@@POST_HISTORY_COMMIT@@"


@dataclass(frozen=True)
class Revision:
    commit: str
    date: str
    subject: str
    path: str

    @property
    def short_commit(self) -> str:
        return self.commit[:12]


def git(*args: str, text: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=text,
    )


def is_git_repository() -> bool:
    result = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def reset_generated_output() -> None:
    if GENERATED_CONTENT_DIR.exists():
        shutil.rmtree(GENERATED_CONTENT_DIR)
    if GENERATED_DATA_PATH.exists():
        GENERATED_DATA_PATH.unlink()
    GENERATED_DATA_PATH.parent.mkdir(parents=True, exist_ok=True)
    GENERATED_CONTENT_DIR.mkdir(parents=True, exist_ok=True)
    (GENERATED_CONTENT_DIR / "_index.md").write_text(
        "---\n"
        'title: "Historical post versions"\n'
        "build:\n"
        "  list: never\n"
        "  render: never\n"
        "---\n",
        encoding="utf-8",
    )


def parse_revision_log(path: str) -> list[Revision]:
    result = git(
        "log",
        "--follow",
        "--diff-filter=AMR",
        "--name-status",
        f"--format={COMMIT_MARKER}%n%H%x1f%cI%x1f%s",
        "--",
        path,
    )
    revisions: list[Revision] = []
    for block in result.stdout.split(COMMIT_MARKER)[1:]:
        lines = [line for line in block.strip().splitlines() if line.strip()]
        if not lines:
            continue
        metadata = lines[0].split("\x1f", 2)
        if len(metadata) != 3:
            continue
        commit, date, subject = metadata
        revision_path = None
        for status_line in lines[1:]:
            fields = status_line.split("\t")
            if len(fields) >= 2:
                revision_path = fields[-1]
                break
        if not revision_path:
            continue
        exists = subprocess.run(
            ["git", "cat-file", "-e", f"{commit}:{revision_path}"],
            cwd=ROOT,
            capture_output=True,
        )
        if exists.returncode == 0:
            revisions.append(Revision(commit, date, subject, revision_path))
    return revisions


def split_front_matter(markdown: str) -> tuple[dict[str, str], str]:
    if not markdown.startswith("---\n"):
        return {}, markdown
    end = markdown.find("\n---\n", 4)
    if end == -1:
        return {}, markdown
    front_matter = markdown[4:end]
    body = markdown[end + 5 :]
    values: dict[str, str] = {}
    for line in front_matter.splitlines():
        match = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not match:
            continue
        key, value = match.groups()
        values[key] = value.strip().strip("'\"")
    return values, body


def show_file(commit: str, path: str, *, text: bool = True):
    return git("show", f"{commit}:{path}", text=text).stdout


def word_changes(before: str, after: str) -> list[dict[str, str]]:
    """Keep punctuation and spacing, without treating Markdown as trusted HTML."""
    old = re.findall(r"\w+|[^\w\s]|\s+", before)
    new = re.findall(r"\w+|[^\w\s]|\s+", after)
    segments = []
    for operation, a, b, c, d in SequenceMatcher(None, old, new, autojunk=False).get_opcodes():
        if operation == "equal":
            segments.append({"kind": "equal", "text": "".join(new[c:d])})
        else:
            if a != b:
                segments.append({"kind": "delete", "text": "".join(old[a:b])})
            if c != d:
                segments.append({"kind": "insert", "text": "".join(new[c:d])})
    return segments


def comparison_changes(before: str, after: str) -> dict:
    old_meta, old_body = split_front_matter(before)
    new_meta, new_body = split_front_matter(after)
    old_title, new_title = old_meta.get("title", ""), new_meta.get("title", "")
    return {
        "title_changes": word_changes(old_title, new_title) if old_title != new_title else [],
        "has_content_changes": old_body.strip() != new_body.strip(),
    }


def write_changes_page(
    revision: Revision,
    previous: Revision,
    stable_id: str,
    slug: str,
    current_url: str,
    previous_url: str,
    before: str,
    after: str,
) -> str:
    changes_url = f"/posts/{slug}/versions/{revision.short_commit}/changes/"
    destination = GENERATED_CONTENT_DIR / stable_id / f"{revision.short_commit}-changes.md"
    metadata = {
        "title": f"What changed — {split_front_matter(after)[0].get('title') or slug}",
        "url": changes_url,
        "type": "post-versions",
        "layout": "post-changes",
        "robots": "noindex, follow",
        "current_url": current_url,
        "version_url": f"/posts/{slug}/versions/{revision.short_commit}/",
        "previous_url": previous_url,
        "version_date": revision.date,
        "previous_date": previous.date,
        "subject": revision.subject,
        **comparison_changes(before, after),
        "before_page": f"/post-versions/{stable_id}/{previous.short_commit}",
        "after_page": f"/post-versions/{stable_id}/{revision.short_commit}",
        "build": {"list": "never", "render": "always"},
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changes_url


def copy_bundle_assets(revision: Revision, destination: Path) -> None:
    bundle_path = str(Path(revision.path).parent)
    tree = git("ls-tree", "-r", "--name-only", revision.commit, "--", bundle_path)
    for asset_path in tree.stdout.splitlines():
        if asset_path == revision.path:
            continue
        relative_path = Path(asset_path).relative_to(bundle_path)
        target = destination / relative_path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(show_file(revision.commit, asset_path, text=False))


def write_version_page(
    revision: Revision,
    stable_id: str,
    slug: str,
    current_url: str,
    changes_url: str = "",
) -> str:
    markdown = show_file(revision.commit, revision.path)
    front_matter, body = split_front_matter(markdown)
    title = front_matter.get("title") or slug.replace("-", " ").title()
    destination = GENERATED_CONTENT_DIR / stable_id / revision.short_commit
    destination.mkdir(parents=True, exist_ok=True)
    copy_bundle_assets(revision, destination)

    version_url = f"/posts/{slug}/versions/{revision.short_commit}/"
    generated_front_matter = {
        "title": f"{title} — historical version",
        "original_title": title,
        "version_date": revision.date,
        "commit": revision.commit,
        "current_url": current_url,
        "changes_url": changes_url,
        "url": version_url,
        "type": "post-versions",
        "layout": "post-version",
        "robots": "noindex, follow",
    }
    lines = ["---"]
    for key, value in generated_front_matter.items():
        lines.append(f"{key}: {json.dumps(value, ensure_ascii=False)}")
    lines.extend(["build:", "  list: never", "  render: always", "---", ""])
    (destination / "index.md").write_text(
        "\n".join(lines) + body.lstrip("\n"),
        encoding="utf-8",
    )
    return version_url


def generate() -> dict[str, dict]:
    reset_generated_output()
    history: dict[str, dict] = {}
    if not is_git_repository() or not POSTS_DIR.exists():
        GENERATED_DATA_PATH.write_text("{}\n", encoding="utf-8")
        return history

    for index_path in sorted(POSTS_DIR.glob("*/index.md")):
        relative_path = index_path.relative_to(ROOT).as_posix()
        hugo_path = index_path.relative_to(ROOT / "content").as_posix()
        slug = index_path.parent.name
        current_url = f"/posts/{slug}/"
        revisions = parse_revision_log(relative_path)
        if not revisions:
            continue

        oldest_revision = revisions[-1]
        stable_id = f"post-{oldest_revision.commit[:12]}"
        version_entries = []
        revision_sources = [show_file(revision.commit, revision.path) for revision in revisions]
        for position, revision in enumerate(revisions):
            is_current = position == 0
            url = current_url if is_current else f"/posts/{slug}/versions/{revision.short_commit}/"
            changes_url = ""
            if position + 1 < len(revisions):
                previous = revisions[position + 1]
                changes_url = write_changes_page(
                    revision, previous, stable_id, slug, current_url,
                    f"/posts/{slug}/versions/{previous.short_commit}/",
                    revision_sources[position + 1], revision_sources[position],
                )
            # Render both sides from exact committed snapshots, including the newest.
            snapshot_url = write_version_page(revision, stable_id, slug, current_url, changes_url)
            if not is_current:
                url = snapshot_url
            version_entries.append(
                {
                    "commit": revision.commit,
                    "short_commit": revision.short_commit,
                    "date": revision.date,
                    "subject": revision.subject,
                    "url": url,
                    "current": is_current,
                    "changes_url": changes_url,
                }
            )

        history[hugo_path] = {
            "stable_id": stable_id,
            "current_url": current_url,
            "versions": version_entries,
        }

    GENERATED_DATA_PATH.write_text(
        json.dumps(history, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return history


def main() -> None:
    history = generate()
    post_count = len(history)
    version_count = sum(max(0, len(item["versions"]) - 1) for item in history.values())
    print(f"Generated history for {post_count} posts ({version_count} historical versions).")


if __name__ == "__main__":
    main()
