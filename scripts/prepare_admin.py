#!/usr/bin/env python3
"""Copy a checksum-pinned Sveltia bundle into a built site (no runtime CDN)."""
import base64
import hashlib
import io
import sys
import tarfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://registry.npmjs.org/@sveltia/cms/-/cms-0.256.1.tgz'
SHA512 = 'TvtXYC0RzCjWzTbA2kku8/x61g3sV2RvddV53vLkh2/C504GJA8zf3wEtatlyZES1eb0Lq8tQOfxeCHZi3Gnww=='


def main():
    cache = ROOT / '.tools/cache/cms-0.256.1.tgz'
    if not cache.exists():
        data = urllib.request.urlopen(URL, timeout=120).read()
        if base64.b64encode(hashlib.sha512(data).digest()).decode() != SHA512:
            raise SystemExit('Sveltia CMS checksum mismatch')
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_bytes(data)
    data = cache.read_bytes()
    if base64.b64encode(hashlib.sha512(data).digest()).decode() != SHA512:
        raise SystemExit('Cached Sveltia CMS checksum mismatch')
    with tarfile.open(fileobj=io.BytesIO(data)) as archive:
        member = next(m for m in archive.getmembers() if m.name.endswith('/dist/sveltia-cms.js'))
        target = Path(sys.argv[1]) / 'admin/sveltia-cms.js'
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(archive.extractfile(member).read())


if __name__ == '__main__':
    main()
