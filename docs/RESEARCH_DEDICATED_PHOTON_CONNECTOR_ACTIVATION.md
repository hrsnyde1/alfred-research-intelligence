# Research-only connector Linux gates and controlled connection plan

2026-10-16. **Preparation only; do not execute installation/activation now.** Personal Photon/Hermes/Development must remain unchanged/running. No shared two-project bridge installation is required. No new Hermes gateway or ordinary Personal consumer is permitted.

## Exact proposed boundaries

These are new proposed paths and units, not claims that resources already exist:

| Resource | Proposed binding |
|---|---|
| Connector code | /opt/alfred-research-photon/v1/{connector.mjs,main.mjs,research-project.mjs} |
| Nonsecret protected policy | /etc/alfred-research-photon/policy.json, owner-approved project/line/sender/space/profile/connection_ref; enabled=false and intake_enabled=false initially |
| Protected credential source references | /etc/alfred-research-photon/credentials/research-project-id and research-project-secret; security owner provisions separately, never copied/read by this task |
| Service credential filenames | CREDENTIALS_DIRECTORY/research-project-id and research-project-secret; no Personal fallback |
| Dedicated UID/GID | alfredresearchphoton, must be owner-created/approved; no Personal groups or queue access |
| Private state | /var/lib/alfredresearch-photon,0700; flock connector.lock, pending/transport records0600 and health.json |
| Service | alfred-research-photon.service, source research-photon.service.proposed |
| Optional controlled outbound | alfred-research-photon-canary.service, source research-photon-canary.service.proposed; one fixed operation first-research-canary-v1, stdin from protected /etc/alfred-research-photon/canary.txt |
| Runtime | existing Node26.7.0 under /home/alfred/.hermes/tools/node-26.7.0-linux-x64/bin/node, read-only runtime mount |
| SDK | installed Spectrum12.7.0 nonsecret node_modules closure read-only bound into isolated code directory; freeze all symlink targets/dependencies before approval |

No credential values enter policy, shell arguments, environment assignments, task data, Memory, company agents or Git. systemd LoadCredential supplies only these Research files. Private home view exposes only explicit runtime/SDK mounts, not Personal configuration, message stores or sockets. systemd sandbox support, paths/traversal permissions and dependency closure must be tested; the proposed unit is not independently Linux-accepted yet. Do not relax boundaries to make it launch.

## Minimum next authorization

Authorize isolated Linux synthetic validation of the frozen new connector/units using fake credentials, the installed Node/SDK source and no network/host-loopback or production paths. This is a new candidate, so old bridge41 acceptance does not authorize installation. Validate credentialReader semantics with fake systemd credentials, complete dependency mounts, dedicated UID permissions, state locking/replay, 10s auth/send process termination and5min lease. Produce transfer/hash inventory before any later real deployment. No new packages needed at application-source level; runtime closure still needs verification.

After this passes, obtain owner approval for the separate service/code/UID/state installation; security owner separately provisions credential references. Attest provisioned project is dedicated with exactly the approved receiving line and authorized sender/conversation. Unknown/different/multiple ambiguous identities must fail closed. This task did not read real identities.

## Later approved operator sequence

1. Pin SHA256.json and install only the three code modules plus reviewed policy/unit(s); no Personal/Hermes files. Provision isolated UID/state and protected credential references through owner procedure. Frozen installation package and final permissions must be reviewed first; do not invent an installer command from this document.
2. Keep enabled=false/intake_enabled=false; daemon-reload for the new units only. Test disabled launch and health without SDK authentication:

```sh
sudo systemctl daemon-reload
sudo systemctl start alfred-research-photon.service
sudo systemctl show alfred-research-photon.service -p Id -p ActiveState -p SubState -p Result
sudo -u alfredresearchphoton /home/alfred/.hermes/tools/node-26.7.0-linux-x64/bin/node /opt/alfred-research-photon/v1/main.mjs health /etc/alfred-research-photon/policy.json
```

Disabled run exits normally; inactive after successful exit is expected. Health outputs DISABLED. Do not enable boot startup. No live test is authorized by these preparation commands.

3. Separately authorize a bounded live Research connection, then owner sets enabled=true in protected policy while retaining intake_enabled=false. No changes to Personal. Start only the new service:

```sh
sudo systemctl start alfred-research-photon.service
sudo systemctl show alfred-research-photon.service -p Id -p MainPID -p User -p ActiveState -p SubState -p Result
sudo -u alfredresearchphoton /home/alfred/.hermes/tools/node-26.7.0-linux-x64/bin/node /opt/alfred-research-photon/v1/main.mjs health /etc/alfred-research-photon/policy.json
```

Require fresh READY and expected isolated process plus no Personal PID/source changes. Health is local, not end-to-end proof; session expires5min and no restart is automatic. SDK logs suppressed to avoid secret leakage; only allowlisted health retained. Service permissions/mount/resource limits and final Linux execution acceptance must precede this step.

4. One separately authorized controlled inbound iMessage: approved requester sends one synthetic pinned full-commit URL to the dedicated Research number/conversation during the bounded session. Verify actual destination on messaging device and a single PENDING_INTAKE correlation, productionTrusted=false, via an approved redacted status inspector. No task/model/acquisition/Memory execution. Replaying identical event must retain correlation. Owner-provided true sender/space bindings required before test; do not widen allowlists.
5. One separately authorized outbound test: owner prepares nonsecret synthetic canary.txt. Stop only the Research run service to release flock, then start the proposed canary oneshot using the same isolated constraints/credential refs:

```sh
sudo systemctl stop alfred-research-photon.service
sudo systemctl start alfred-research-photon-canary.service
sudo systemctl show alfred-research-photon-canary.service -p Id -p Result -p ExecMainStatus
```

Require accepted receipt and owner-observed Research From identity/destination. SDK acceptance is not delivery. Same fixed operation and text suppress duplicate send; changed text or UNKNOWN refuses. Never clear ledger to repeat test. No automatic Personal control send or Personal restart. The optional canary unit/source is new local preparation, not approved installed infrastructure.

## Hermes task integration remains a separate gate

Unchanged Hermes has no verified Research ingress. Keep intake disabled even if messaging canary succeeds. Approve narrowly scoped authenticated same-orchestrator extension/registration first: isolated connector UID/transport identity, bound project/receiving line/sender/space/event/profile, existing durable pending intake/acquisition contracts, scoped idempotency, reserved Research failure terminal before ordinary agent paths. No untrusted caller metadata grants authority, no Personal fallback and no second Hermes gateway. An extension requiring Hermes restart conflicts with this task's no-restart limit and needs separate authorization/window; do not silently activate it.

## Rollback / stop

On failed authentication, wrong destination/From, duplicate/UNKNOWN, unsafe state, wrong UID/mount or any Personal impact: stop only the Research service(s):

```sh
sudo systemctl stop alfred-research-photon.service alfred-research-photon-canary.service
```

Leave protected policy disabled and intake disabled via approved owner config procedure. Retain Research pending/delivery/UNKNOWN state and receipts; never resend, delete/rewind records or touch Personal credentials/services. Revert only newly installed Research units/code under final reviewed package manifest if necessary. No activation/installation has occurred in this task, so there is presently nothing to roll back.
