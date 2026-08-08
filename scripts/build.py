#!/usr/bin/env python3
"""Build the production site, including Git-backed historical post versions."""

from __future__ import annotations

import subprocess
import sys
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
    ensure_full_git_history()
    run(sys.executable, "scripts/generate_history.py")
    run("hugo", "--gc", "--minify", *sys.argv[1:])


if __name__ == "__main__":
    main()
