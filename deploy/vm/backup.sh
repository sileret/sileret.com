#!/bin/sh
# Run only in the blog guest. The SQLite online backup is transactionally consistent.
set -eu
test "$(hostname)" = prod-blog-01
umask 077
stamp=$(date -u +%Y%m%dT%H%M%SZ)
work=$(mktemp -d /var/backups/blog/.work.XXXXXX)
trap 'rm -rf "$work"' EXIT
sqlite3 -readonly /var/lib/artalk/artalk.db ".backup '$work/artalk.db'"
sqlite3 "$work/artalk.db" 'PRAGMA integrity_check;' | /usr/bin/grep -qx ok
tar -czf "/var/backups/blog/$stamp.tgz" -C "$work" artalk.db -C / etc/artalk etc/caddy etc/blog etc/nftables.conf
ln -sfn "$stamp.tgz" /var/backups/blog/latest.tgz
find /var/backups/blog -maxdepth 1 -type f -name '*.tgz' -mtime +14 -delete
