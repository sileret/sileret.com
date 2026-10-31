#!/usr/bin/python3
"""Test moderation in a temporary localhost-only Artalk instance and real CAPTCHA rejection."""
import json
import os
import secrets
import socket
import subprocess
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def request(url, data=None):
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, headers={'Content-Type': 'application/json',
                                                       'Origin': 'http://localhost:8088'})
    with urllib.request.urlopen(req, timeout=5) as result:
        return json.load(result)


def main():
    assert socket.gethostname() == 'prod-blog-01'
    comment = {'name': 'Deployment verification', 'email': 'test@example.invalid',
               'content': 'Temporary moderation verification', 'page_key': '__verification__',
               'site_name': 'sileret.com'}
    # The live service must refuse an unauthenticated comment without a CAPTCHA.
    try:
        request('http://127.0.0.1:23366/api/v2/comments', comment)
        raise RuntimeError('Live CAPTCHA did not block the request')
    except urllib.error.HTTPError as error:
        response = error.read().decode()
        assert 'captcha' in response.lower(), (error.code, response)
        print('PASS: live service requires CAPTCHA')
    with tempfile.TemporaryDirectory(prefix='artalk-verification-') as temporary:
        env = os.environ.copy()
        env.update(ATK_APP_KEY=secrets.token_hex(32), ATK_HOST='127.0.0.1', ATK_PORT='23367',
                   ATK_DB_FILE=temporary + '/test.db', ATK_CAPTCHA_ENABLED='false',
                   ATK_CAPTCHA_ALWAYS='false', ATK_EMAIL_ENABLED='false')
        process = subprocess.Popen(['/usr/local/bin/artalk', 'server', '-c', '/etc/artalk/artalk.yml'],
                                   env=env, cwd=temporary, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for attempt in range(30):
                try:
                    request('http://127.0.0.1:23367/api/v2/version')
                    break
                except OSError:
                    if process.poll() is not None:
                        raise RuntimeError('Temporary comment service failed to start')
                    time.sleep(0.1)
            result = request('http://127.0.0.1:23367/api/v2/comments', comment)
            assert result['is_pending'] is True, result
            query = urllib.parse.urlencode({'page_key': comment['page_key'], 'site_name': 'sileret.com'})
            anonymous = request('http://127.0.0.1:23367/api/v2/comments?' + query)
            assert anonymous['count'] == 0 and anonymous['comments'] == [], anonymous
            print('PASS: guest comment is pending and invisible to other visitors')
        finally:
            process.terminate()
            process.wait(timeout=10)


if __name__ == '__main__':
    main()
