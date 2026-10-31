#!/usr/bin/python3
"""Probe private administration guards using trusted and untrusted loopback sources."""
import http.client
import socket


def status(path, source, method='GET'):
    connection = http.client.HTTPConnection('127.0.0.1', 80, timeout=5,
                                             source_address=(source, 0))
    try:
        connection.request(method, path, headers={'Host': 'localhost'})
        return connection.getresponse().status
    finally:
        connection.close()


def main():
    assert socket.gethostname() == 'prod-blog-01'
    assert status('/', '127.0.0.2') == 200
    assert status('/comments/api/v2/version', '127.0.0.2') == 200
    for path in ['/admin/', '/stats/', '/comments/sidebar/', '/comments/swagger/',
                 '/comments/api/v2/settings', '/comments/api/v2/user/access_token']:
        actual = status(path, '127.0.0.2')
        assert actual == 404, (path, actual)
        print('BLOCKED untrusted ' + path)
    assert status('/comments/api/v2/comments/0', '127.0.0.2', 'DELETE') == 404
    for path in ['/admin/', '/stats/', '/comments/sidebar/']:
        assert status(path, '127.0.0.1') == 200
        print('ALLOWED trusted ' + path)


if __name__ == '__main__':
    main()
