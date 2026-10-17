# One-time Research iMessage discovery — prepared, not executed

This standalone staging utility imports neither the existing connector nor Hermes. It creates one Spectrum client with only Research systemd credentials, reads `app.messages`, and stops after the first qualifying inbound text. No send/read/reply/typing API is called. No intake, ledger, task or Memory API exists here. Application writes are an exclusive, mode-0600 discovery report and, only with `--diagnostic`, an exclusive mode-0600 startup stage file. SDK stdout/stderr are discarded by systemd. Do not run this CLI directly outside the supplied service.

## Inspection and trust boundary

Inspected repository snapshots:
- `staging/research-photon-connector-v1/{connector,main,research-project}.mjs`: requires known line/space/sender; normal connector persists pending intake. Reusing it would unnecessarily retain content.
- `staging/research-photon-service-v1/alfred-research-photon.service`: dedicated UID, credentials `research-project-id` and `research-project-secret`, existing credential source paths, runtime and SDK mounts, connector lock.
- `staging/photon-linux-compatibility-v1/linux-sdk`: Spectrum 12.7.0. Core `resolveProjectCredentials` accepts explicit credentials; `Spectrum` calls authenticated `cloud.getProject`; messages iterator yields `[space,message]`. Provider cloud tokens map dedicated instance IDs to receiving phones. Built messages/spaces carry `platform`; message carries direction, sender, ID, content. The public tuple does not expose authenticated raw Fusor project metadata. Binding is therefore the explicitly authenticated client plus an independently pinned project digest and exact receiving-line digest. Explicit conflicting tuple projectId fields are rejected; arbitrary forged events without provenance cannot be authenticated by this utility alone. SDK transport/authentication remains the trust boundary.

No live Linux inspection or authentication was performed. Before operation, compare installed credential references, mounts, SDK version and API shapes against these inspected snapshots. If they differ, stop for review. Never inspect or print credential contents to perform this comparison.

The SDK can internally reconnect/refresh within the bounded session; this code makes no application retry. Deadline includes initialization and teardown and forcibly exits by 120 seconds; systemd adds a 125-second outer limit. A stalled SDK stop may prevent a report from being written, which fails closed. SDK lifecycle control frames/transport acknowledgments may occur; no user-facing response is sent.

## Owner qualification and output limitations

Independently identify the dedicated Research receiving line and nonsecret Research project ID from approved deployment metadata. Do not derive the expected project from whichever credentials happen to be installed: that would defeat the binding check. Missing/unknown receiving line is a blocker, not permission to learn it from any first message. Exactly one line digest is accepted; shared tokens, absent values, arrays and other ambiguous identity representations fail closed.

Use a fresh unpredictable challenge (at least 128 random bits) known only to the owner and operator. The owner sends exactly that challenge, with no newline, in the intended iMessage conversation during the bounded window. Only its SHA-256 is stored in policy. Do not reuse a challenge. It gates discovery; it is not independent proof of legal/owner identity. Review the resulting conversation and sender with the owner before registering an authorization. Discovery does not register anything or enable Research service/intake.

Identifiers resembling phone numbers or email handles are digested, including sender or conversation IDs. They cannot be recovered from this report. If downstream registration requires a raw phone-like sender ID, use the independently known owner handle through a separately reviewed registration process and compare its digest. Do not weaken report redaction. Receiving line is always a digest of the SDK `space.phone`, not a raw provider instance ID. Message correlation hashes project-scoped line/space/message identifiers; no content fingerprint is included.

## Synthetic validation (offline)

```sh
node --test staging/research-imessage-discovery-v1/discovery.test.mjs
node --check staging/research-imessage-discovery-v1/main.mjs
```

Tests use injected synthetic factories and no SDK imports or credentials. Seventeen tests cover Personal binding rejection, unknown/ambiguous line rejection, malformed/platform/outbound rejection, challenge mismatch, duplicate/conflicting replay handling, allowlisted output and handle redaction, one-event shutdown, no send/read/reply/intake/Memory calls and error teardown. Timeout is enforced by CLI process timer and systemd; actual systemd/installed SDK behavior requires later Linux review. No production source or Personal/Hermes files were changed.

## Linux installation — later, not executed

Run from the transferred staging directory on Linux. These commands install a separate utility; they do not change existing service definitions or credentials. Confirm Research remains inactive/disabled; do not stop or change Personal Photon or Hermes. If Research is active, stop here and arrange a separate approved maintenance window.

```sh
systemctl is-active alfred-research-photon.service
systemctl is-enabled alfred-research-photon.service
sudo test -d /var/lib/alfredresearch-photon
sudo test -x /opt/alfred-research-photon/runtime/bin/node
sudo install -d -m 0755 /opt/alfred-research-discovery/v1/node_modules
sudo install -m 0644 discovery.mjs main.mjs /opt/alfred-research-discovery/v1/
sudo install -d -m 0700 /etc/alfred-research-discovery
sudo install -m 0644 alfred-research-discovery.service /etc/systemd/system/
```

Create only hashed policy using hidden prompts. Use independently approved metadata, never read/copy the credential files. The challenge prompt accepts the exact owner-sent challenge; generate it securely outside shell command arguments/history. This writes no raw inputs:

```sh
sudo python3 - <<'PY'
import getpass, hashlib, json, os
h = lambda prompt: hashlib.sha256(getpass.getpass(prompt).encode()).hexdigest()
p = dict(role='research-discovery',
         project_sha256=h('Approved Research project ID: '),
         line_sha256=h('Approved Research receiving line (exact SDK format): '),
         challenge_sha256=h('Fresh owner challenge (exact text): '), timeout_ms=120000)
fd = os.open('/etc/alfred-research-discovery/policy.json', os.O_WRONLY|os.O_CREAT|os.O_EXCL, 0o600)
with os.fdopen(fd, 'w') as f: json.dump(p, f)
PY
sudo systemd-analyze verify /etc/systemd/system/alfred-research-discovery.service
sudo systemctl daemon-reload
```

The service uses the existing Research-only UID, credential source references and connector flock. It cannot run concurrently with the installed connector if that connector uses the inspected lock. No credential file is copied or modified. There is deliberately no `[Install]` section: never enable this unit.

## Operation — explicitly NOT authorized in this development task

After later live authorization and installed-runtime review:

```sh
sudo systemctl start --no-block alfred-research-discovery.service
systemctl show alfred-research-discovery.service -p ActiveState -p SubState -p ExecMainStatus
```

Owner sends the challenge once to the approved Research line from the intended conversation. Poll status after at most two minutes; do not start a second reader. Exit 0 means report written, 2 means generic configuration/SDK/report failure, 3 means timeout or stream ended without a match; flock may return 1 for contention. No raw diagnostics are captured. Existing report is never overwritten; do not repeatedly rerun to troubleshoot authentication.

```sh
sudo cat /var/lib/alfred-research-discovery/report.json
```

Example redacted shape (digest placeholders are illustrative):

```json
{
  "project_binding": {"role":"research", "sha256":"<Research project digest>"},
  "receiving_line": {"sha256":"<approved line digest>"},
  "conversation": {"id":"<opaque conversation ID, or sha256 field if handle-like>"},
  "sender": {"id":"<opaque sender ID, or sha256 field if handle-like>"},
  "correlation_sha256":"<message correlation digest>"
}
```

## Cleanup — later

Retain the protected report only as long as needed for owner review. Stopping/removing this separate unit does not affect Personal Photon or Hermes. After reviewing/retaining the allowlisted evidence in an approved protected location:

```sh
sudo systemctl stop alfred-research-discovery.service
sudo rm /etc/systemd/system/alfred-research-discovery.service
sudo systemctl daemon-reload
sudo rm /etc/alfred-research-discovery/policy.json
sudo rm /opt/alfred-research-discovery/v1/main.mjs /opt/alfred-research-discovery/v1/discovery.mjs
sudo rm /var/lib/alfred-research-discovery/report.json
```

If no report exists, omit its removal. Leave all existing credentials, connector lock, Research connector files, Personal services and Hermes configuration untouched. Do not activate routing or register identities as part of cleanup.

## Startup diagnostic — prepared only; no live run performed

The base unit is unchanged. Opt in with the temporary runtime drop-in below. Diagnostics contain only newline-separated fixed codes, each written at most once (seven lines maximum), synchronously flushed to `startup-stages.txt`. No SDK error, credential, identifier or message data is passed to the recorder. SDK stdout/stderr remain discarded. The diagnostic file is exclusively created: an existing file blocks a new run rather than overwriting evidence.

Codes mean:

| Code | Completed boundary |
| --- | --- |
| POLICY_OK | Policy parsed and validated; existing deadline armed |
| CREDENTIALS_OK | Research credential files read, project digest matched, secret shape validated |
| SDK_IMPORT_OK | Both SDK imports completed |
| PROVIDER_OK | `imessage.config()` returned |
| AUTHENTICATION_OK | `Spectrum()` returned after its internal authenticated project request and client initialization |
| STREAM_READY | Messages async iterator acquired and its `next` method validated |
| FAILED | Caught failure, timeout, or stream ended without a qualifying event |

The last successful code before FAILED identifies the last completed boundary. A failure after PROVIDER_OK can be authentication or another internal factory initialization failure: this public SDK API does not expose finer safe boundaries. STREAM_READY does not establish transport health or message delivery. A later FAILED can reflect iteration, teardown, qualification, or report persistence failure. No new code claims to resolve an unobserved live SDK failure.

No file means diagnostics were not enabled, the process never reached file creation (for example lock contention/runtime failure), or exclusive creation failed. If killed externally, the file can end at a successful stage without FAILED. An existing report also blocks report persistence. Review existing evidence before any separately authorized rerun; do not repeatedly authenticate to troubleshoot.

Exact update commands on Linux, from the transferred `staging/research-imessage-discovery-v1` directory, for the already installed discovery service and policy:

```sh
node --test discovery.test.mjs
node --check main.mjs
sudo install -m 0644 discovery.mjs main.mjs /opt/alfred-research-discovery/v1/
sudo systemd-analyze verify /etc/systemd/system/alfred-research-discovery.service
```

After separate live authorization, confirm the permanent Research connector is inactive and neither output exists. If any check fails, stop and review; these commands do not stop or modify any connector:

```sh
! systemctl is-active --quiet alfred-research-photon.service
sudo test ! -e /var/lib/alfred-research-discovery/startup-stages.txt
sudo test ! -e /var/lib/alfred-research-discovery/report.json
sudo install -d -m 0755 /run/systemd/system/alfred-research-discovery.service.d
sudo tee /run/systemd/system/alfred-research-discovery.service.d/diagnostic.conf >/dev/null <<'UNIT'
[Service]
ExecStart=
ExecStart=/usr/bin/flock -n /var/lib/alfredresearch-photon/connector.lock /opt/alfred-research-photon/runtime/bin/node /opt/alfred-research-discovery/v1/main.mjs --live-discovery /etc/alfred-research-discovery/policy.json --diagnostic
UNIT
sudo systemctl daemon-reload
sudo systemctl start --no-block alfred-research-discovery.service
```

Run each preflight check separately and require success before proceeding. During the unchanged 120-second window, the owner sends the previously agreed challenge once. Inspect only the safe diagnostic and service status:

```sh
systemctl show alfred-research-discovery.service -p ActiveState -p SubState -p ExecMainStatus
sudo cat /var/lib/alfred-research-discovery/startup-stages.txt
```

Exit codes remain 0 (report persisted), 2 (caught failure), 3 (timeout/no match); flock can return 1. Once the discovery unit is inactive, disable diagnostic mode without modifying the base unit:

```sh
sudo rm /run/systemd/system/alfred-research-discovery.service.d/diagnostic.conf
sudo systemctl daemon-reload
```

Keep the stage file for review; remove it only after retention/review and separate rerun authorization. Do not enable the unit. No commands in this section were executed during implementation.

## Credential reader correction — offline validated, deployment not executed

The credential reader accepts exact modes 0400/0600 when owned by root or the
service UID, and exact mode 0440 only when owned by root (systemd LoadCredential).
It rejects world permissions, group writes, other group-readable modes, special
mode bits, and unexpected owners. The existing regular-file, size, O_NOFOLLOW,
and policy checks remain in place. LoadCredential delivery and the unit are unchanged.
The metadata tests use synthetic UID 980 and root ownership without reading credentials.

Validation: 67 offline tests pass (the original 17 plus 50 credential metadata
cases); syntax checks pass for main.mjs, discovery.mjs, and discovery.test.mjs.

After transferring this corrected staging directory to Linux, run the following
from that directory. This replaces only the discovery CLI source. It does not
start a service, authenticate, alter credentials, or require daemon-reload.
The subshell stops if either Research service is active or transitioning.

```sh
(
set -eu
for unit in alfred-research-discovery.service alfred-research-photon.service; do
  state=$(systemctl show --property=ActiveState --value "$unit")
  case "$state" in inactive|failed) ;; *) exit 1 ;; esac
done
sudo test -f /opt/alfred-research-discovery/v1/main.mjs
/opt/alfred-research-photon/runtime/bin/node --check ./main.mjs
sudo install -o root -g root -m 0644 ./main.mjs /opt/alfred-research-discovery/v1/main.mjs
sudo cmp ./main.mjs /opt/alfred-research-discovery/v1/main.mjs
/opt/alfred-research-photon/runtime/bin/node --check /opt/alfred-research-discovery/v1/main.mjs
)
```

No live test, authentication, deployment, commit, or push was performed for this correction.
