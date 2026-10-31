#!/usr/bin/env python3
"""Build the production site, including Git-backed historical post versions."""

from __future__ import annotations

import subprocess
import sys
import argparse
import shutil
import os
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def run(*args: str) -> None:
    subprocess.run(args, cwd=ROOT, check=True)


def ensure_full_git_history() -> None:
    result = subprocess.run(
        ["git", "rev-parse", "--is-shallow-repository"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    if result.stdout.strip() == "true":
        print("Fetching full Git history for public post versions...")
        run("git", "fetch", "--unshallow", "origin")


def main() -> None:
    # This branch is served only by the private VM, never by public Pages previews.
    if os.environ.get("CF_PAGES") == "1" and os.environ.get("CF_PAGES_BRANCH") == "codex/private-blog":
        raise SystemExit("Cloudflare deployment is disabled for the private blog branch.")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--search", action="store_true", help="Generate the Pagefind index")
    parser.add_argument("--destination", "-d", default="public")
    options, hugo_args = parser.parse_known_args()
    ensure_full_git_history()
    run(sys.executable, "scripts/generate_history.py")
    hugo = ROOT / ".tools/bin/hugo"
    run(str(hugo) if hugo.exists() else "hugo", "--gc", "--minify",
        "--destination", options.destination, *hugo_args)
    run(sys.executable, "scripts/prepare_admin.py", options.destination)
    if options.search:
        pagefind = ROOT / ".tools/bin/pagefind"
        executable = str(pagefind) if pagefind.exists() else shutil.which("pagefind")
        if not executable:
            raise SystemExit("Install Pagefind with python3 scripts/install_build_tools.py")
        run(executable, "--site", options.destination)


if __name__ == "__main__":
    main()
