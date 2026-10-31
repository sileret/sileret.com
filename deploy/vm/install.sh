#!/bin/sh
# Invoke as root INSIDE the new VM, from a complete source checkout/snapshot.
set -eu
test "$(hostname)" = prod-blog-01
test "$(id -u)" = 0
cd "$(dirname "$0")/../.."
root=$(pwd)
for account in artalk blogbuild bloganalytics; do
  id "$account" >/dev/null 2>&1 || useradd --system --create-home --home-dir "/var/lib/$account" --shell /usr/sbin/nologin "$account"
done
install -d -m 0755 /usr/local/lib/blog /etc/blog /srv/blog /srv/blog/releases
install -d -o root -g artalk -m 0750 /etc/artalk
install -d -m 0700 /var/backups/blog
install -d -o artalk -g artalk -m 0700 /var/lib/artalk
install -d -o blogbuild -g blogbuild -m 0750 /var/lib/blogbuild
install -d -o caddy -g caddy -m 0750 /var/log/caddy
install -d -o bloganalytics -g bloganalytics -m 0750 /var/lib/blog-analytics
usermod -aG caddy bloganalytics
usermod -aG bloganalytics caddy
chown blogbuild:blogbuild /srv/blog /srv/blog/releases
install -m 0644 deploy/vm/Caddyfile /etc/caddy/Caddyfile
install -o root -g artalk -m 0640 deploy/vm/artalk.yml /etc/artalk/artalk.yml
install -m 0600 deploy/vm/nftables.conf /etc/nftables.conf
install -m 0755 deploy/vm/analytics.py deploy/vm/publish.py deploy/vm/backup.sh /usr/local/lib/blog/
install -m 0644 deploy/vm/*.service deploy/vm/*.timer /etc/systemd/system/
python3 - <<'PY'
import hashlib,io,tarfile,urllib.request,pathlib,secrets,os,subprocess
u='https://github.com/ArtalkJS/Artalk/releases/download/v2.10.1/artalk_v2.10.1_linux_amd64.tar.gz'
data=urllib.request.urlopen(u,timeout=120).read()
if hashlib.sha256(data).hexdigest() != '4d2555de251a1dc56c9e3d14b70f347d4fd243af81fc33d4c5d26704c155d71f':
    raise SystemExit('Artalk checksum mismatch')
with tarfile.open(fileobj=io.BytesIO(data)) as tar:
    member=next(m for m in tar.getmembers() if pathlib.Path(m.name).name=='artalk' and m.isfile())
    out=pathlib.Path('/usr/local/bin/artalk'); out.write_bytes(tar.extractfile(member).read()); out.chmod(0o755)
env=pathlib.Path('/etc/artalk/secrets.env')
if not env.exists():
    env.write_text('ATK_APP_KEY='+secrets.token_hex(32)+'\n'); env.chmod(0o600)
credentials=pathlib.Path('/root/blog-admin-credentials')
if not credentials.exists():
    password=secrets.token_urlsafe(30)
    environment=os.environ.copy()
    for line in env.read_text().splitlines():
        key,value=line.split('=',1); environment[key]=value
    subprocess.run(['/usr/local/bin/artalk','admin','-c','/etc/artalk/artalk.yml',
                    '--name','admin','--email','root@sileret.com','--password',password],
                   env=environment,cwd='/var/lib/artalk',check=True,stdout=subprocess.DEVNULL)
    credentials.write_text('Name: admin\nEmail: root@sileret.com\nPassword: '+password+'\n')
    credentials.chmod(0o600)
    subprocess.run(['chown','-R','artalk:artalk','/var/lib/artalk'],check=True)
PY
install -d -m 0755 /etc/systemd/system/caddy.service.d
install -d -m 0755 /etc/systemd/resolved.conf.d
cat > /etc/systemd/resolved.conf.d/90-blog.conf <<'EOF'
[Resolve]
LLMNR=no
MulticastDNS=no
EOF
cat > /etc/apt/apt.conf.d/20auto-upgrades <<'EOF'
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
EOF
cat > /etc/apt/apt.conf.d/52blog <<'EOF'
Unattended-Upgrade::Automatic-Reboot "false";
EOF
cat > /etc/ssh/sshd_config.d/20-blog-listen.conf <<'EOF'
AddressFamily inet
ListenAddress 192.168.231.2
EOF
cat > /etc/systemd/system/caddy.service.d/resources.conf <<'EOF'
[Service]
Environment=GOMEMLIMIT=96MiB GOMAXPROCS=1
MemoryHigh=112M
MemoryMax=160M
TasksMax=128
EOF
nft -c -f /etc/nftables.conf
caddy validate --config /etc/caddy/Caddyfile --adapter caddyfile
systemctl daemon-reload
systemctl enable --now nftables artalk caddy blog-analytics.timer blog-backup.timer blog-publish.timer
systemctl restart caddy
systemctl restart systemd-resolved ssh
echo 'Services installed. Git publishing remains gated by /etc/blog/enable-git-publishing.'
