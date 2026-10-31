#!/usr/bin/python3
"""Check guest connectivity; --host-filter also tests with the guest nft table removed.

Run only inside prod-blog-01. The host's libvirt filter stays active throughout.
"""
import argparse
import errno
import socket
import subprocess
import urllib.request


def blocked(address, port):
    try:
        with socket.create_connection((address, port), timeout=2):
            raise RuntimeError(f'ISOLATION FAILURE: reached {address}:{port}')
    except OSError as error:
        if error.errno not in (None, errno.ETIMEDOUT, errno.EHOSTUNREACH, errno.ENETUNREACH,
                               errno.ECONNREFUSED, errno.EACCES, errno.EPERM):
            raise
        print(f'BLOCKED {address}:{port} ({type(error).__name__})', flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--host-filter', action='store_true')
    args = parser.parse_args()
    assert socket.gethostname() == 'prod-blog-01', 'Run only in the blog guest'
    if args.host_filter:
        subprocess.run(['nft', 'delete', 'table', 'inet', 'blog'], check=True)
    try:
        for address, port in [('192.168.231.1', 22), ('192.168.122.1', 22),
                              ('192.168.122.50', 22), ('100.121.21.111', 22),
                              ('151.80.20.219', 22), ('169.254.169.254', 80)]:
            blocked(address, port)
        with urllib.request.urlopen('https://deb.debian.org/debian/README', timeout=15) as result:
            assert result.status == 200
        print('ALLOWED outbound HTTPS', flush=True)
        with socket.socket(socket.AF_INET6, socket.SOCK_STREAM) as test:
            test.settimeout(2)
            try:
                test.connect(('2001:41d0:c:bdb::1', 22))
                raise RuntimeError('ISOLATION FAILURE: reached host over IPv6')
            except OSError:
                print('BLOCKED IPv6', flush=True)
    finally:
        if args.host_filter:
            subprocess.run(['nft', '-f', '/etc/nftables.conf'], check=True)


if __name__ == '__main__':
    main()
