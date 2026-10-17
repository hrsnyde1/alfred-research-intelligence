# First standalone Research transport test

2026-10-16. **Prepared, not executed.** Requires owner authorization for a five-minute Research-only authenticated session, one incoming controlled message and one outgoing response. No Personal/Hermes restart, route change, task processing, source acquisition, model or Memory work.

## Preconditions

Owner installs only reviewed standalone files/units and dedicated account; validates effective unit mount/credential/state permissions with synthetic credentials; provisions separate protected Research credentials and verified project/line/space/sender/profile policy. Current source passed17 Linux fake tests; fresh SDK import-only passed with no missing imported dependency; unit syntax passed systemd255. This is not actual authenticated service boot proof.

Preserve Personal/Hermes source hashes/PIDs and current health metadata before/after, without messages/credentials. Require Research's dedicated project mapping and actual receiving/sending number attestation. SDK space.phone labels configured dedicated stream, not independently certified Apple destination. Missing conversation/sender mapping blocks test; do not temporarily allow arbitrary senders or conversations.

## Owner-operated transport steps (future authorization only)

1. Keep intake_enabled=false. Owner changes only standalone protected policy enabled=true, preserving all fixed bindings, then:

```sh
sudo systemctl start alfred-research-photon.service
sudo systemctl show alfred-research-photon.service -p Id -p User -p MainPID -p ActiveState -p SubState -p Result
sudo /home/alfred/.hermes/tools/node-26.7.0-linux-x64/bin/node /opt/alfred-research-photon/v1/main.mjs health /etc/alfred-research-photon/policy.json
```

Require active/running isolated Research PID and fresh READY/intake DISABLED. Startup auth timeout10s; session ends5min; no restart/retry/renewal. Fresh READY means factory initialized, not proof the approved line receives. No credential or SDK raw logs; service lifecycle identity is alfred-research-photon, allowlisted health timestamp in its private state.

2. Authorized owner sends exactly one synthetic message to the dedicated Research number in the configured conversation (for example a public GitHub full40-character commit reference). Confirm actual destination on device/provider, not message text. No research action runs. Inspect only redacted aggregate state:

```sh
sudo python3 -I -S -B - <<'PY'
import pathlib,json,collections
root=pathlib.Path('/var/lib/alfredresearch-photon');counts=collections.Counter()
for p in root.glob('*.json'):
 if p.name=='health.json':continue
 r=json.loads(p.read_text())
 if r.get('schema')=='research.connector.pending/1':
  assert r.get('productionTrusted') is False
  counts['pending_intake']+=1
 elif r.get('state') in ('UNKNOWN','ACCEPTED'):counts[r['state']]+=1
print(dict(counts))
PY
```

Take baseline aggregate before the authorized message and require pending_intake increases exactly1. Replay tests were synthetic; do not send additional real messages to manufacture duplicate events. No arbitrary ledger reads, contents, identifiers or receipts printed. Pending intent is a stored message/correlation, **not a created/completed Research task**. Durable source acquisition and Hermes intake are still absent.

3. Owner prepares protected /etc/alfred-research-photon/canary.txt with exactly this nonsecret response:

> Transport test only: message received. Research processing has not started.

Authorize exactly one fixed outbound operation first-research-canary-v1 to the same configured Research conversation/line. Stop only the Research run unit to release exclusive state lock, then:

```sh
sudo systemctl stop alfred-research-photon.service
sudo systemctl start alfred-research-photon-canary.service
sudo systemctl show alfred-research-photon-canary.service -p Id -p Result -p ExecMainStatus
```

One-off send reauthenticates only Research with same explicit fixed line. Type=oneshot TimeoutStartSec30; CLI auth10s/send10s. Require success/exit0, ACCEPTED aggregate increment1, and owner-observed correct Research From identity and recipient. Receipt proves SDK acceptance only; actual device observation is needed. Same operation/text cannot resend; UNKNOWN/conflicting text denies. Do not change operation ID/reset state to force retry. No automatic acknowledgment is implemented on ingress; this manual connector-level reply is the smallest transport acknowledgment and does not claim Research completion.

4. Stop only Research units and owner sets enabled=false,intake_enabled=false at test end:

```sh
sudo systemctl stop alfred-research-photon.service alfred-research-photon-canary.service
```

Preserve pending/transport/UNKNOWN state; confirm Personal/Hermes continue with original PIDs/source hashes. Do not enable Research on boot, renew indefinitely or attach Hermes during this canary.

## Fail / rollback

On wrong destination/From, identity refusal, credential failure, stale/unavailable health, failed send, UNKNOWN or Personal impact: stop the Research units above, retain protected state, disable only standalone policy and reconcile with owner. Never retry uncertain operation blindly, delete messages, rewind receipts or stop Personal. Rollback is disabling the new connection; no Personal code rollback required.

## Remaining Hermes integration

No verified authenticated ingress in unchanged existing Hermes. Keep intake disabled even after successful transport test. Genuine connector-UID/project/line/sender/space/event/profile authentication and a terminal reserved Research hook using existing pending-acquisition contracts require separate implementation/review. No second Hermes gateway or ordinary Personal fallback. If attachment needs Hermes restart, that is outside this task and requires its own authorization.

Outcome required for transport PASS: dedicated receiving evidence, one pending correlation, one Research-only accepted/observed reply, no Personal change, no task execution. No live test occurred while preparing this document.
