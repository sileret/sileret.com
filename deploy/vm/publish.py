#!/usr/bin/python3
"""Build without root; replace current atomically only after all checks pass."""
import fcntl
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path('/srv/blog')
SOURCE = ROOT / 'source'
LOCK = Path('/var/lib/blogbuild/publish.lock')
BRANCH = os.environ.get('BLOG_GIT_BRANCH', 'codex/private-blog')


def run(*args, **kwargs):
    return subprocess.run(args, check=True, text=True, **kwargs)


def main():
    os.environ['PATH'] = str(SOURCE / '.tools/bin') + os.pathsep + os.environ.get('PATH', '/usr/bin:/bin')
    with LOCK.open('w') as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if not SOURCE.exists():
            run('git', 'clone', '--branch', BRANCH, '--single-branch',
                'https://github.com/sileret/sileret.com.git', str(SOURCE))
        dirty = run('git', 'status', '--porcelain', cwd=SOURCE, capture_output=True).stdout
        if dirty:
            raise SystemExit('Source has local changes; preserving them and refusing to deploy')
        run('git', 'fetch', '--prune', 'origin', BRANCH, cwd=SOURCE)
        remote = f'origin/{BRANCH}'
        revision = run('git', 'rev-parse', remote, cwd=SOURCE, capture_output=True).stdout.strip()
        marker = ROOT / 'current/.revision'
        if marker.exists() and marker.read_text().strip() == revision:
            return
        run('git', 'merge', '--ff-only', remote, cwd=SOURCE)
        run('python3', '-m', 'unittest', 'discover', '-s', 'tests', cwd=SOURCE)
        release = ROOT / 'releases' / (datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ') + '-' + revision[:12])
        release.mkdir(parents=True)
        try:
            run('python3', 'scripts/build.py', '--search', '--config', 'hugo.toml,deploy/vm/hugo.toml', '--destination', str(release), cwd=SOURCE)
            if not (release / 'index.html').exists() or not (release / 'pagefind/pagefind.js').exists():
                raise RuntimeError('Missing site or search index')
            (release / '.revision').write_text(revision + '\n')
            link = ROOT / 'current.next'
            link.unlink(missing_ok=True)
            link.symlink_to(release)
            os.replace(link, ROOT / 'current')
        except BaseException:
            if (ROOT / 'current').resolve() != release.resolve():
                shutil.rmtree(release)
            raise
        # Keep three complete releases for rollback, plus the pinned staging snapshot.
        releases = [p for p in (ROOT / 'releases').iterdir() if not p.name.endswith('working-tree')]
        for old in sorted(releases, reverse=True)[3:]:
            if old.resolve() != (ROOT / 'current').resolve():
                shutil.rmtree(old)


if __name__ == '__main__':
    main()
