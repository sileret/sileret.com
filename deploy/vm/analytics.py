#!/usr/bin/python3
"""Refresh private log analytics and record coarse, bot-filtered traffic spikes."""
import collections
import datetime as dt
import gzip
import ipaddress
import json
import os
import re
import statistics
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlsplit

OUTPUT = Path('/var/lib/blog-analytics')
BOT = re.compile(r'bot|crawler|spider|slurp|headless|uptime|monitor|curl|wget', re.I)


def main():
    OUTPUT.mkdir(parents=True, exist_ok=True)
    files = sorted(Path('/var/log/caddy').glob('blog-access*.json*'))
    now = dt.datetime.now(dt.timezone.utc).timestamp()
    # Completed hours avoid comparing a partial hour against complete hours.
    hour = int(now // 3600) - 1
    counts = collections.Counter()
    referrers = collections.defaultdict(collections.Counter)
    report = OUTPUT / 'index.next.html'
    args = ['goaccess', '--no-global-config', '--log-format=CADDY', '--ignore-crawlers',
            '--no-query-string', '--anonymize-ip', '--keep-last=14', '--no-progress',
            '--html-report-title=Blog traffic (approximate)', '-o', str(report)]
    with tempfile.NamedTemporaryFile(mode='w+', suffix='.json') as normalized:
        records = 0
        for file in files:
            opener = gzip.open if file.suffix == '.gz' else open
            with opener(file, 'rt', errors='replace') as stream:
                for line in stream:
                    try:
                        event = json.loads(line)
                        request = event.get('request', {})
                        path = urlsplit(request.get('uri', '')).path
                        if path.startswith(('/comments/', '/admin/', '/stats/', '/avatar-disabled/')):
                            continue
                        if float(event.get('ts', 0)) < now - 14 * 86400:
                            continue
                        headers = request.get('headers', {})
                        ua = ' '.join(headers.get('User-Agent', []))
                        if BOT.search(ua):
                            continue
                        # Debian's Caddy 2.6 logs remote_ip; newer versions add client_ip.
                        ip = request.get('client_ip') or request.get('remote_ip')
                        ipaddress.ip_address(ip)
                        request['client_ip'] = ip
                        normalized.write(json.dumps(event) + '\n')
                        records += 1
                        if not (request.get('method') == 'GET' and event.get('status') == 200
                                and path.startswith('/posts/') and '/versions/' not in path
                                and path.count('/') == 3):
                            continue
                        # Count only known current post URLs; cap attacker-controlled cardinality.
                        if not (Path('/srv/blog/current') / path.lstrip('/') / 'index.html').is_file():
                            continue
                        bucket = int(float(event['ts']) // 3600)
                        counts[(path, bucket)] += 1
                        if bucket == hour:
                            ref = urlsplit((headers.get('Referer') or [''])[0]).hostname or 'direct / unknown'
                            referrers[path][ref] += 1
                    except (ValueError, TypeError, KeyError):
                        continue
        normalized.flush()
        status = subprocess.run(args + ['-f', normalized.name], stdout=subprocess.DEVNULL).returncode if records else 0
    if records and status == 0:
        os.replace(report, OUTPUT / 'index.html')
    elif not records:
        (OUTPUT / 'index.html').write_text('<!doctype html><title>Blog traffic</title><h1>No blog traffic yet</h1>')
        report.unlink(missing_ok=True)
    else:
        raise SystemExit(f'GoAccess failed: {status}')
    state_path = OUTPUT / 'spikes.json'
    state = json.loads(state_path.read_text()) if state_path.exists() else {'alerts': []}
    existing = {(a['path'], a['hour']) for a in state['alerts']}
    for path in referrers:
        baseline = statistics.median([counts[(path, hour - day * 24)] for day in range(1, 8)])
        observed = counts[(path, hour)]
        if observed >= max(100, 5 * max(10, baseline)) and (path, hour) not in existing:
            alert = {'path': path, 'hour': hour, 'requests': observed, 'usual': baseline,
                     'referrers': referrers[path].most_common(3)}
            state['alerts'].append(alert)
            print('Unusual blog traffic: ' + json.dumps(alert), flush=True)
    state['alerts'] = [a for a in state['alerts'] if a['hour'] >= hour - 14 * 24]
    state['updated_at'] = dt.datetime.now(dt.timezone.utc).isoformat()
    temp = OUTPUT / 'spikes.json.next'
    temp.write_text(json.dumps(state, indent=2) + '\n')
    os.replace(temp, state_path)


if __name__ == '__main__':
    main()
