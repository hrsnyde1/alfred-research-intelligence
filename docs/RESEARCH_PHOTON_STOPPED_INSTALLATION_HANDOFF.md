# Dedicated Research Photon stopped installation handoff

2026-10-16. **BLOCKED on interactive administrator authentication; nothing installed/transferred on Linux.** Owner authorizes installation only, stopped/disabled, no actual credentials or login. Fresh read-only preflight: sudo -n true requires password; new account/group and all four proposed destination roots/primary unit absent; Research unit not-found/inactive. Personal Photon PID140714, Hermes454732, Development intake439206 active/running. Four source baseline hashes and Node SHA match accepted pins. No service restarted/modified.

Connector source verified against original staging/research-photon-connector-v1/SHA256.json (digest69d81db5e6444455fab5c5f8ba6fded94227ffb2f58cff793e81c40b470afe06). Primary unit is the revised Linux syntax-verified unit in staging/research-photon-service-v1, fixing private-home runtime traversal. Its manifest digest is a23cff1d17e7ac9d4f917ae67656bf0ccc8f302a96b6c72e7b9458761c651bd1. No shared bridge or canary unit installation.

## Intended installed files (not yet installed)

| Path | SHA256 |
|---|---|
| /opt/alfred-research-photon/v1/connector.mjs | ad4c96df541dae51dcc0403cc13ffed1fe6f6596ce580cd34e830951ca77b9cf |
| /opt/alfred-research-photon/v1/main.mjs | 701effc123e997ac6b328921b51f89117aa4f4742ade6de23daa500f8db5aba9 |
| /opt/alfred-research-photon/v1/research-project.mjs | ea65df22546e19233bb79e976aaf366470fb3fb5d197c1c40c006a9aa9cb6e96 |
| /etc/systemd/system/alfred-research-photon.service | c56765b234a1986f817768d6a05960dcb5b8a5b9c27c433d3c4c155c45032032 |

Also create root:alfredresearchphoton0640 policy.json containing only enabled=false,intake_enabled=false; empty root0700 credential directory; private service state0700; root-owned0755 mount destinations runtime and v1/node_modules. No real credentials, identity mappings, copied runtime or SDK packages. Unit retains separate LoadCredential references; sources deliberately absent, so any accidental startup fails closed. Required actual bindings will be supplied only after separate credential/connection authorization.

## 1. Owner transfer from Mac (not executed)

```sh
cd /Users/haydensnyder/Git/alfred-research-intelligence
REMOTE_STAGE=$(ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 alfred@192.168.50.81 'umask 077; mktemp -d /home/alfred/research-staging/research-photon-install.XXXXXXXX')
scp -o BatchMode=yes -o StrictHostKeyChecking=yes  staging/research-photon-service-v1/connector.mjs  staging/research-photon-service-v1/main.mjs  staging/research-photon-service-v1/research-project.mjs  staging/research-photon-service-v1/alfred-research-photon.service  staging/research-photon-service-v1/SHA256.json  "alfred@192.168.50.81:$REMOTE_STAGE/"
printf 'Received directory: %s\n' "$REMOTE_STAGE"
```

The original service manifest also names the optional canary; that file is intentionally neither transferred nor installed. Pin the full manifest and verify only the exact four selected entries below. No source/test byte edits.

## 2. Owner authenticates in Linux terminal

```sh
sudo -i
set -euo pipefail
umask 077
read -r -p 'Received directory printed on Mac: ' SRC
ART=$(mktemp -d /var/tmp/research-photon-stopped-install.XXXXXXXX)
for n in connector.mjs main.mjs research-project.mjs alfred-research-photon.service SHA256.json; do
 install -o root -g root -m 0600 "$SRC/$n" "$ART/$n"
done
printf '%s  %s\n' a23cff1d17e7ac9d4f917ae67656bf0ccc8f302a96b6c72e7b9458761c651bd1 "$ART/SHA256.json" | sha256sum -c -

python3 -I -S -B - "$ART" <<'PYVERIFY'
import pathlib,json,hashlib,sys
r=pathlib.Path(sys.argv[1]);m=json.loads((r/'SHA256.json').read_text())
for n in ('connector.mjs','main.mjs','research-project.mjs','alfred-research-photon.service'):
 p=r/n;assert p.is_file() and not p.is_symlink()
 assert hashlib.sha256(p.read_bytes()).hexdigest()==m[n],n
print('Exact selected candidate PASS')
PYVERIFY
BEFORE=$(systemctl show alfred-photon.service alfred-hermes.service alfred-development-intake.service -p Id -p MainPID -p ActiveState -p SubState)
for s in alfred-photon.service alfred-hermes.service alfred-development-intake.service; do systemctl is-active --quiet "$s"; done
# Recheck the accepted Personal/Hermes/runtime baseline without importing code.
sha256sum -c - <<'BASELINE'
ef019d1d50e4ca680aede49276181f8eff8d396d9b7c22a73bb5da2b2d7bb8e4  /home/alfred/.hermes/hermes-agent/plugins/platforms/photon/sidecar/index.mjs
841ed6cb6e2d392fcec33f8983dd34fffe677c6a8d40e442bc449e66beeb16e5  /home/alfred/.hermes/hermes-agent/plugins/platforms/photon/adapter.py
6a1a40708075e3550a824eae5519e98db97f52ea7995154e8c7e941de4e02144  /home/alfred/.hermes/hermes-agent/gateway/run_inbound.py
827c6c0b3a7fd3b731365ecd17bb52d65b05c9a53e67795922ec2ebb79de58fe  /home/alfred/.hermes/hermes-agent/plugins/platforms/photon/sidecar/send-format.mjs
ad19784f7e90ba789a099eccba77ede8dc90a778c424f1c10a70fed3ff903fdc  /home/alfred/.hermes/tools/node-26.7.0-linux-x64/bin/node
BASELINE
# Refuse existing account, installation or active Research service.
! getent passwd alfredresearchphoton
! getent group alfredresearchphoton
for p in /opt/alfred-research-photon /etc/alfred-research-photon /var/lib/alfredresearch-photon /etc/systemd/system/alfred-research-photon.service; do
 test ! -e "$p"; test ! -L "$p"
done
test "$(systemctl show alfred-research-photon.service -p ActiveState --value)" = inactive
useradd --system --user-group --home-dir /var/lib/alfredresearch-photon --no-create-home --shell /usr/sbin/nologin alfredresearchphoton
install -d -o root -g root -m 0755 /opt/alfred-research-photon/v1 /opt/alfred-research-photon/runtime /opt/alfred-research-photon/v1/node_modules
for n in connector.mjs main.mjs research-project.mjs; do
 install -o root -g root -m 0644 "$ART/$n" "/opt/alfred-research-photon/v1/$n"
done
install -d -o root -g alfredresearchphoton -m 0750 /etc/alfred-research-photon
install -d -o root -g root -m 0700 /etc/alfred-research-photon/credentials
install -d -o alfredresearchphoton -g alfredresearchphoton -m 0700 /var/lib/alfredresearch-photon
printf '%s\n' '{"enabled":false,"intake_enabled":false}' > "$ART/policy.json"
install -o root -g alfredresearchphoton -m 0640 "$ART/policy.json" /etc/alfred-research-photon/policy.json
install -o root -g root -m 0644 "$ART/alfred-research-photon.service" /etc/systemd/system/alfred-research-photon.service
systemd-analyze verify --man=no /etc/systemd/system/alfred-research-photon.service
systemctl daemon-reload
systemctl disable alfred-research-photon.service
```

No start/enable/restart/stop command is part of installation. Daemon-reload refreshes unit metadata, not running Personal/Hermes processes. Partial errors stop execution; do not compensate with account/permission changes or deletion. Retain ART for administrator review.

## 3. Verify stopped installation

```sh
python3 -I -S -B - "$ART/SHA256.json" <<'PYVERIFY'
import pathlib,json,hashlib,sys,os,pwd,grp,stat
m=json.loads(pathlib.Path(sys.argv[1]).read_text())
for n in ('connector.mjs','main.mjs','research-project.mjs','alfred-research-photon.service'):
 p=pathlib.Path('/etc/systemd/system')/n if n.endswith('.service') else pathlib.Path('/opt/alfred-research-photon/v1')/n
 st=p.lstat();assert stat.S_ISREG(st.st_mode)
 assert hashlib.sha256(p.read_bytes()).hexdigest()==m[n]
 assert (st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode))==(0,0,0o644)
p=pathlib.Path('/etc/alfred-research-photon/policy.json');st=p.lstat()
assert json.loads(p.read_text())=={'enabled':False,'intake_enabled':False}
gid=grp.getgrnam('alfredresearchphoton').gr_gid
assert (st.st_uid,st.st_gid,stat.S_IMODE(st.st_mode))==(0,gid,0o640)
uid=pwd.getpwnam('alfredresearchphoton').pw_uid
for name,owner,group,mode in [('/etc/alfred-research-photon',0,gid,0o750),('/etc/alfred-research-photon/credentials',0,0,0o700),('/var/lib/alfredresearch-photon',uid,gid,0o700),('/opt/alfred-research-photon/v1',0,0,0o755),('/opt/alfred-research-photon/runtime',0,0,0o755),('/opt/alfred-research-photon/v1/node_modules',0,0,0o755)]:
 s=pathlib.Path(name).lstat();assert stat.S_ISDIR(s.st_mode)
 assert (s.st_uid,s.st_gid,stat.S_IMODE(s.st_mode))==(owner,group,mode),name
assert not list(pathlib.Path('/etc/alfred-research-photon/credentials').iterdir())
print('Installed source/unit hashes, metadata, disabled policy and empty credentials PASS')
PYVERIFY
test "$(systemctl show alfred-research-photon.service -p ActiveState --value)" = inactive
test "$(systemctl show alfred-research-photon.service -p UnitFileState --value)" = disabled
systemctl show alfred-research-photon.service -p Id -p LoadState -p ActiveState -p SubState -p UnitFileState -p MainPID -p User
AFTER=$(systemctl show alfred-photon.service alfred-hermes.service alfred-development-intake.service -p Id -p MainPID -p ActiveState -p SubState)
test "$BEFORE" = "$AFTER"
printf '%s\n' "$AFTER"
```

Require MainPID0/inactive/disabled for Research and same active/running PIDs for Personal/Hermes/Development. No health mode/login is needed; stopped service plus disabled policy and absent secrets establish no new connection. Installation alone does not validate effective live sandbox.

## Next credential / connection procedure

Stop here after verification. Later owner-authorized credential setup uses RESEARCH_PHOTON_CREDENTIAL_SETUP.md: direct hidden terminal entry into the two root-only Research source files, verified real project/line/space/sender/profile/connection policy, no Personal fallback. Keep enabled=false,intake_enabled=false during setup. Only after separate authorization and service-isolation acceptance should owner set enabled=true and use RESEARCH_PHOTON_FIRST_LIVE_TEST.md. Do not install/start optional canary unit as part of this handoff; its later installation needs explicit scope. Hermes task dispatch remains disabled/unimplemented.

No passwords requested; no sudo policy change. If owner runs these commands, retain output without credentials and reverify from Linux before claiming installation PASS. Current status remains BLOCKED/not installed.
