#!/usr/bin/env python3
"""Install checksum-pinned build tools locally; never changes system packages."""
import hashlib
import io
import platform
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = {
    ("Linux", "x86_64"): [
        ("hugo", "https://github.com/gohugoio/hugo/releases/download/v0.164.0/hugo_0.164.0_linux-amd64.tar.gz", "d9c8b17285ea4ec004d9f814273ea910f2051ce02c284993fd1f91ba455ae50d"),
        ("pagefind", "https://github.com/Pagefind/pagefind/releases/download/v1.5.2/pagefind-v1.5.2-x86_64-unknown-linux-musl.tar.gz", "afb824a9e7f64905a934900481cea5be679c03975e527329e0e5e6cc70f5feda"),
    ],
    ("Darwin", "arm64"): [
        ("pagefind", "https://github.com/Pagefind/pagefind/releases/download/v1.5.2/pagefind-v1.5.2-aarch64-apple-darwin.tar.gz", "7286f394a349bd37677d44a65a20078a02b1747da0b0814d83403bf86be17abe"),
    ],
}


def main():
    selected = TOOLS.get((platform.system(), platform.machine()))
    if not selected:
        raise SystemExit("Unsupported platform; install Hugo 0.164.0 and Pagefind 1.5.2 manually")
    destination = ROOT / ".tools/bin"
    destination.mkdir(parents=True, exist_ok=True)
    for name, url, expected in selected:
        data = urllib.request.urlopen(url, timeout=120).read()
        if hashlib.sha256(data).hexdigest() != expected:
            raise SystemExit(f"Checksum mismatch for {name}")
        with tarfile.open(fileobj=io.BytesIO(data)) as archive:
            member = next(m for m in archive.getmembers() if Path(m.name).name == name and m.isfile())
            executable = archive.extractfile(member).read()
        output = destination / name
        output.write_bytes(executable)
        output.chmod(0o755)
        print(f"Installed {output}")


if __name__ == "__main__":
    main()
