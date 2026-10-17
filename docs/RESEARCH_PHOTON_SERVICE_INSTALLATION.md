# Research Photon standalone service installation

2026-10-16. **PASS for owner installation review with Research intake disabled. Not installed or authorized to activate.** SDK import-only validation passed; no missing imported module/runtime dependency detected. Actual systemd sandbox startup under a new UID and real project/line authentication remain owner-side acceptance steps, not tested claims.

Reviewed all five requested evidence reports and exact source/inventory. Local service candidate: `staging/research-photon-service-v1/`. Three connector modules are byte-for-byte identical to the17-test Linux-accepted version. New units fix the inaccessible home-path runtime by binding it to /opt; no Personal permission changes. Candidate SHA256.json digest: `a23cff1d17e7ac9d4f917ae67656bf0ccc8f302a96b6c72e7b9458761c651bd1`.

## Exact files and service

| Candidate source | Proposed target | SHA256 |
|---|---|---|
| alfred-research-photon-canary.service | /etc/systemd/system/alfred-research-photon-canary.service | 90ac117c8b64c0d7afdbff9fd2335f3bee8a059569aad820f645dd2ff6a8defb |
| alfred-research-photon.service | /etc/systemd/system/alfred-research-photon.service | c56765b234a1986f817768d6a05960dcb5b8a5b9c27c433d3c4c155c45032032 |
| connector.mjs | /opt/alfred-research-photon/v1/connector.mjs | ad4c96df541dae51dcc0403cc13ffed1fe6f6596ce580cd34e830951ca77b9cf |
| main.mjs | /opt/alfred-research-photon/v1/main.mjs | 701effc123e997ac6b328921b51f89117aa4f4742ade6de23daa500f8db5aba9 |
| research-project.mjs | /opt/alfred-research-photon/v1/research-project.mjs | ea65df22546e19233bb79e976aaf366470fb3fb5d197c1c40c006a9aa9cb6e96 |

Owner also creates protected policy.json and credential references documented in RESEARCH_PHOTON_CREDENTIAL_SETUP.md. Optional protected canary.txt contains only the approved transport-test text. No Personal/Hermes/Development/Memory file is replaced. No second Hermes, inbound listener or shared /send consumer is created. Install paths/accounts are proposed new resources; stop if occupied.

Service name: **alfred-research-photon.service**. Separate proposed user/group **alfredresearchphoton**: getent confirmed user absent; existing alfredphoton/alfredmsg already own Personal credentials/state and must not be reused. No account or permissions changed. Native systemd255 verified.

Exact primary unit:

```ini
# PROPOSED ONLY. Requires owner-created isolated UID, frozen runtime/SDK mounts,
# approved nonsecret policy and separately provisioned systemd credentials.
[Unit]
Description=Research-only Photon connector (bounded initial session)
After=network-online.target
Wants=network-online.target
[Service]
Type=simple
User=alfredresearchphoton
Group=alfredresearchphoton
StateDirectory=alfredresearch-photon
StateDirectoryMode=0700
UMask=0077
WorkingDirectory=/opt/alfred-research-photon/v1
LoadCredential=research-project-id:/etc/alfred-research-photon/credentials/research-project-id
LoadCredential=research-project-secret:/etc/alfred-research-photon/credentials/research-project-secret
ExecStart=/usr/bin/flock -n /var/lib/alfredresearch-photon/connector.lock /opt/alfred-research-photon/runtime/bin/node /opt/alfred-research-photon/v1/main.mjs run /etc/alfred-research-photon/policy.json
Restart=no
RuntimeMaxSec=310
TimeoutStopSec=5
KillMode=control-group
MemoryMax=1G
CPUQuota=50%
TasksMax=64
LimitNOFILE=256
NoNewPrivileges=yes
ProtectSystem=strict
ProtectHome=tmpfs
PrivateTmp=yes
ProtectProc=invisible
RestrictAddressFamilies=AF_INET AF_INET6 AF_UNIX
BindReadOnlyPaths=/home/alfred/.hermes/tools/node-26.7.0-linux-x64:/opt/alfred-research-photon/runtime
# Future reviewed nonsecret SDK dependency closure mounted at local node_modules.
BindReadOnlyPaths=/home/alfred/.hermes/hermes-agent/plugins/platforms/photon/sidecar/node_modules:/opt/alfred-research-photon/v1/node_modules
ReadWritePaths=/var/lib/alfredresearch-photon
# SDK diagnostics may include identifiers. Health is an allowlisted file instead.
SyslogIdentifier=alfred-research-photon
StandardOutput=null
StandardError=null
[Install]
WantedBy=multi-user.target
```

Optional alfred-research-photon-canary.service is frozen alongside it: same identity, credentials, mounts, state lock and resource controls; Type=oneshot, TimeoutStartSec=30, main.mjs send policy.json first-research-canary-v1, stdin protected canary.txt. RuntimeMaxSec was removed from oneshot after systemd-analyze reported it ignored; TimeoutStartSec30 is the effective outer limit. Unit syntax now verifies cleanly. No automatic restart or boot enable. Runtime5min is a bounded initial transport session, not an indefinitely available deployment.

Independent log identity is SyslogIdentifier=alfred-research-photon plus unit-specific systemd lifecycle/status. Raw SDK stdout/stderr intentionally discarded because they may disclose identifiers. Allowlisted health.json in private state provides READY/UNAVAILABLE/STOPPED and timestamp. Health freshness plus service state needed; stale READY is not liveness/delivery proof.

## Actual validation

- Prior Linux17/17 fake tests PASS, no changes to source since.
- Fresh accepted Bubblewrap SDK import-only: Node26.7.0, Spectrum/core/imessage12.7.0, import Spectrum/text/imessage exports and imessage.config only; **no Spectrum factory call**. Exit0,1.059495s, remaining tracked processes[]. No network/loopback, credentials or production sockets. Accepted pinned individual libs including libffi, per-process limits15sCPU/64GiBAS/128NPROC/8MiBfile/128FD/core0,45swall,1MiBoutput. SDK module tree bound read-only; no broad home access.
- Enumerated11191 regular SDK dependency files, symlink targets all within SDK root. Closure digest05798781a55ceab12896f164a832078db353d39452bd5d3cd2c10a62823d59fc (SHA256 of sorted JSON relative-path:file-digest map). Import graph resolved; no missing packages detected. This is import dependency loading, not proof all optional lazy provider/auth paths execute.
- systemd-analyze verify --man=no on two temporary unit files: final exit0, empty stdout/stderr. Temporary files removed; no unit installed/started. Audit scripts/output: artifacts/audits/research-photon-service-20261016/.
-15 pinned host input hashes unchanged before/after SDK import. Personal source hashes remain original accepted baseline. No real secret/config/message read.

## Later owner-operated installation (not executed)

First approve this exact candidate/manifest, isolated UID/mounts/state, and only disabled installation. Transfer the five candidate files plus SHA256.json to an owner-selected nonsecret staging directory; set SRC to its actual absolute path. Do not use the old bridge installer. Authenticate administrator directly, never put passwords in chat/argv.

```sh
sudo -i
set -euo pipefail
umask 077
read -r -p 'Absolute received service-candidate directory: ' SRC
printf '%s  %s\n' a23cff1d17e7ac9d4f917ae67656bf0ccc8f302a96b6c72e7b9458761c651bd1 "$SRC/SHA256.json" | sha256sum -c -
python3 -I -S -B - "$SRC" <<'PYVERIFY'
import pathlib,sys,json,hashlib
r=pathlib.Path(sys.argv[1]);m=json.loads((r/'SHA256.json').read_text())
for n,d in m.items():
 p=r/n;assert p.is_file() and not p.is_symlink()
 assert hashlib.sha256(p.read_bytes()).hexdigest()==d,n
print('Candidate hashes PASS')
PYVERIFY
# Stop on any existing installation/account; do not overwrite or reuse it.
test ! -e /opt/alfred-research-photon
test ! -e /etc/alfred-research-photon
test ! -e /var/lib/alfredresearch-photon
test ! -e /etc/systemd/system/alfred-research-photon.service
test ! -e /etc/systemd/system/alfred-research-photon-canary.service
! getent passwd alfredresearchphoton
! getent group alfredresearchphoton
useradd --system --user-group --home-dir /var/lib/alfredresearch-photon --no-create-home --shell /usr/sbin/nologin alfredresearchphoton
install -d -o root -g root -m 0755 /opt/alfred-research-photon/v1 /opt/alfred-research-photon/runtime /opt/alfred-research-photon/v1/node_modules
for n in connector.mjs main.mjs research-project.mjs; do
 install -o root -g root -m 0644 "$SRC/$n" "/opt/alfred-research-photon/v1/$n"
done
install -d -o root -g alfredresearchphoton -m 0750 /etc/alfred-research-photon
install -d -o root -g root -m 0700 /etc/alfred-research-photon/credentials
install -d -o alfredresearchphoton -g alfredresearchphoton -m 0700 /var/lib/alfredresearch-photon
install -o root -g root -m 0644 "$SRC/alfred-research-photon.service" /etc/systemd/system/alfred-research-photon.service
install -o root -g root -m 0644 "$SRC/alfred-research-photon-canary.service" /etc/systemd/system/alfred-research-photon-canary.service
```

Owner supplies real protected nonsecret policy and credentials using companion document; neither is included in candidate. Policy must remain enabled=false,intake_enabled=false until separate bounded live transport approval. LoadCredential sources are required by systemd even in disabled mode: missing credentials make startup fail closed before code. Disabled code itself reads no secret or SDK. Verify installed files against manifest again by target mapping above; recheck Node/SDK closure immediately before activation. Stop on drift.

```sh
systemd-analyze verify --man=no /etc/systemd/system/alfred-research-photon.service /etc/systemd/system/alfred-research-photon-canary.service
systemctl daemon-reload
# Only after protected policy and required credential sources are owner-provisioned:
systemctl start alfred-research-photon.service
systemctl show alfred-research-photon.service -p Id -p ActiveState -p SubState -p Result -p ExecMainStatus
/home/alfred/.hermes/tools/node-26.7.0-linux-x64/bin/node /opt/alfred-research-photon/v1/main.mjs health /etc/alfred-research-photon/policy.json
```

Health invocation is root-owned operator shell, avoiding unprivileged traversal of /home/alfred; health mode does not import SDK or read credentials. Disabled service exits0 normally; expect inactive/success and DISABLED health. Do not enable boot startup. Live transport steps only in first-live-test document after separate authorization. No Personal/Hermes restart or daemon signal.

## Rollback and readiness limits

Stop only the new units:

```sh
sudo systemctl stop alfred-research-photon.service alfred-research-photon-canary.service
```

Owner sets protected policy enabled=false,intake_enabled=false. Preserve all private pending/accepted/UNKNOWN records, credentials and account until retention/security review; no recursive delete, ledger reset or resend. If uninstall is desired, separately approve removal of only these new unit/code files and daemon-reload; never restore/delete Personal state. No production rollback needed now.

Installation review PASS, contingent on owner-controlled new account/files and effective sandbox validation. Missing owner project/line/sender/conversation bindings or credentials blocks live start, not permission to fall back. Full Hermes dispatch remains blocked and intake disabled. No source changes, service installation/start, credentials or real messages in this task.
