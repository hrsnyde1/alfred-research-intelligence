# Photon Research-disabled installation review

2026-10-16. **PASS for owner-controlled installation review, strictly with Research disabled.** This is a reviewed procedure and local artifact, not authorization to execute it. Approval A, an agreed maintenance window and positive quiescence/health gates below are still required. Approvals B–E remain separate. No production changes, restarts, credentials or messages in this task.

## Baseline and service evidence

Read all six requested reports, exact corrected patch and source/test inventories. Fresh read-only SSH used BatchMode=yes, StrictHostKeyChecking=yes, ConnectTimeout=8 and ConnectionAttempts=1. Initial sandbox denial preceded approved read-only retry. Sanitized launch paths/flags/dependencies and source hashes/metadata only; no raw environment, credentials, private messages, jobs or delivery history were accessed.

All four production baseline files still match accepted hashes; no drift. Exact Photon entrypoint is /home/alfred/.hermes/hermes-agent/plugins/platforms/photon/sidecar/index.mjs via Node /home/alfred/.hermes/tools/node-26.7.0-linux-x64/bin/node. Hermes launcher is /home/alfred/.hermes/hermes-agent/.hermes/bin/hermes. Photon runs as alfredphoton, Hermes as alfredmsg; Development intake runs as alfred from /usr/local/lib/alfred-v1.1/trusted_intake.py, cwd /home/alfred/Git/alfred. All three are active/running, PIDs140714/454732/439206, CanReload=no. These are process-health observations, not actual message-delivery proof.

Hermes Requires/After Photon; both Want/After Development intake. Neither Photon nor Hermes has PartOf/BindsTo. Personal and Development share the existing bridge: Hermes consumes inbound, Development observes intake and uses the legacy authenticated /send caller. No separate Personal consumer or new listener is installed. Development source remains unchanged.

Photon has no existing drop-ins. Hermes has 10-offline-pm.conf, 20-photon-credentials.conf and 30-photon-environment.conf. Proposed 60-research-disabled.conf targets are absent, including symlinks. EnvironmentFiles returned none. Sanitized ExecStart review shows no explicit Research name/assignment, source/eval or dotenv/env-file pattern. Combined with new later-sorted disabled Environment assignment this supports disabled launch; recheck this contract at execution and stop if new overrides/wrappers appear. No existing credential-bearing config was opened.

Existing index.mjs UID/GID1000:1000 mode0644, adapter.py0:0 mode0644, gateway/run_inbound.py1000:1000 mode0664. Native Linux source xattr counts are zero for these three. New modules proposed1000:1000/0644. Existing source tree traversal/ACL/service settings unchanged. Existing send-format.mjs remains byte-for-byte unchanged (guard digest in the artifact).

## Exact installation artifact and delta

Mac-local artifact: artifacts/candidates/photon-disabled-installation-20261016-v1.tar.gz

- Archive SHA-256: 21a661d298fe33c7db012d812a27339d3812f442fda75c3bca994fc44ba17faa.
- INSTALL_MANIFEST.json SHA-256: b43f6377bd41da64331795633844b5f8cf83d385aeb292769fe99efd85a0dee8.
- FILES.sha256 SHA-256: 6065a3ad987da2580ed4a6f772f7da5ef2b5d61577495e4e83250994b9d46ccf.
- operator.py SHA-256: 49e48ed60e0a3f541831cbe1bf53fbe06c2d31ebcc639de91dba5966323f8b74.

15 regular files, safe relative paths, no symlink/hardlink, verified against local bytes after packaging. Contains nine candidate source/evidence files, two nonsecret disabled drop-ins, manifest, corrected patch, owner transaction helper and checksum file. No SDK copy, tests, runtime binary, credentials or state is in the installation artifact. No transfer occurred in this task.

Eight source changes plus two new drop-ins; no Research credential/profile/hook changes:

| Exact target | Expected original SHA-256 | Result SHA-256 |
|---|---|---|
| /home/alfred/.hermes/hermes-agent/gateway/photon_research.py | ABSENT | 4aba0fdf6ed2b45ae5c401255e8d9d759e78e1bd2e4e38c7fbc4c63ccab5ee14 |
| /home/alfred/.hermes/hermes-agent/gateway/run_inbound.py | 6a1a40708075e3550a824eae5519e98db97f52ea7995154e8c7e941de4e02144 | 89c3cf4daa0a04473d6302bf53f20b6d3839bd4960f0bc70674c27b9c429b018 |
| /home/alfred/.hermes/hermes-agent/plugins/platforms/photon/adapter.py | 841ed6cb6e2d392fcec33f8983dd34fffe677c6a8d40e442bc449e66beeb16e5 | 540288fed36df43cb2e3049a1e46b94b1ddb0e94a4e8efad3f947e4f389e64c1 |
| /home/alfred/.hermes/hermes-agent/plugins/platforms/photon/sidecar/caller-bindings.mjs | ABSENT | 1bafa6bb31376fcdf5cf237003555fc7ba7d289711bcc192335ed565232075bf |
| /home/alfred/.hermes/hermes-agent/plugins/platforms/photon/sidecar/index.mjs | ef019d1d50e4ca680aede49276181f8eff8d396d9b7c22a73bb5da2b2d7bb8e4 | 2ac209c3864cf4165d55fbfff7ffa9e29d9a43b010d35937bc08ea51c73082ba |
| /home/alfred/.hermes/hermes-agent/plugins/platforms/photon/sidecar/research-lifecycle.mjs | ABSENT | 6ae5e27a677cc6df9c2065e73ce727ccf11174c8a915d29134792fbe3df089dc |
| /home/alfred/.hermes/hermes-agent/plugins/platforms/photon/sidecar/research-project.mjs | ABSENT | ea65df22546e19233bb79e976aaf366470fb3fb5d197c1c40c006a9aa9cb6e96 |
| /home/alfred/.hermes/hermes-agent/plugins/platforms/photon/sidecar/research-worker.mjs | ABSENT | 98ac1071ae1c06d0cba0e31bde819cec5288fe16cb577479c9862a6c8bf501a7 |
| /etc/systemd/system/alfred-photon.service.d/60-research-disabled.conf | ABSENT | 5125469d8fb27719838dd855a2665520f871da80aea4fb1ba254bbc8e19cf496 |
| /etc/systemd/system/alfred-hermes.service.d/60-research-disabled.conf | ABSENT | 5125469d8fb27719838dd855a2665520f871da80aea4fb1ba254bbc8e19cf496 |

Both drop-ins contain exactly `[Service]` and `Environment=PHOTON_RESEARCH_ENABLED=0` with real LF newlines. No LoadCredential, project/caller secret, line, sender, conversation or active route is added. No Development file is modified. Source bytes are exactly the corrected Linux-tested candidate, patch be1b8c0b900210f691b67e2e77cebea954b17909a9295d5f4edcbcacb29d632e. Operator/config files are administrative artifacts, not a second production messaging path.

## Independent validation

- Accepted corrected Linux bridge evidence: 41/41 passed, worker/namespace timeout cleanup and unchanged baseline, documented previously.
- Fresh Mac replay of the full relevant staged suite: 30 Node +11 Python, all pass (388.297 ms /0.084s).
- Five new disabled-composition tests: all pass (45.427 ms). Exact current HTTP/lifecycle code proves no secret lookup/worker when disabled, Research authentication/send denied, unchanged legacy Development body stays Personal, unknown caller denied, and exactly one listener/subscription retained.
- Nine independent disposable-filesystem operator tests: all pass (0.510 s). Install/result hashes, explicit disabled bytes, full restoration after success/partial failure, metadata/xattr preservation, baseline/artifact/new-target/symlink drift denial, corrupted-backup/unknown-current rollback denial, and untouched synthetic delivery/retry history.
- The archive's entire contents and hashes were independently decoded/compared. No privileged CLI, sudo/systemd action or production target was exercised. Operator tests use temporary root mirrors; Linux ACL/filesystem flags, real systemd precedence and actual outage behavior were not executed. Existing source xattrs are zero; nonempty synthetic xattr restoration was exercised using Mac-native xattr support.

Logs and artifact hashes: artifacts/audits/photon-disabled-review-20261016/. An initial Mac test harness hit unavailable os.listxattr; the helper gained a Mac-native xattr backend for local validation. Linux uses native os APIs, no package install. Final nine tests pass. The helper fsyncs backups/checkpoints/files/directories and retains the source baseline. No source tests or production candidate bytes were changed.

## Maintenance and message preservation

No zero-downtime claim. Stop Hermes, then Photon under a maintenance lock after Personal and Development owners quiesce outgoing work and reconcile ambiguous sends. Development remains running but must be positively quiesced through its existing owner workflow; if no safe quiescence method is available, **execution is BLOCKED**, not permission to kill it. Stopping/restarting Development itself requires explicit additional scope in A and an updated ordering/interlock; neither is implicit.

Messages may arrive upstream during the outage. Provider buffering, catch-up completeness and duplicate delivery across reconnect are not established by fake tests. Owner must obtain noncontent recovery evidence or explicitly accept the documented maintenance risk before A. Do not initiate discretionary messages during the window. Preserve all existing outboxes, dedupe, accepted/UNKNOWN and sent receipts; never rewind/delete delivery records or automatically republish to compensate. Any uncertain send requires existing owner reconciliation before retry.

The transaction writes only the ten manifest targets, backs up only original code/config metadata and refuses unknown versions. It never touches message stores, caches, retry ledgers, Memory, Obsidian or Development state. Per-file rename is atomic; the multi-file set is protected by stopped consumers and exclusive maintenance, not falsely described as a filesystem-wide atomic release. Existing ownership/modes/xattrs are retained; timestamps are not a rollback guarantee. Unknown immutable/security metadata or competing source consumer blocks execution pending owner review.

## Health and approval gate

After disabled restart, prove source/config hashes, disabled drop-in precedence, expected users/entrypoints/dependencies, one existing Personal listener/consumer and no Research worker/credential attachment. Use existing authorized noncontent monitors only. Process-active is insufficient for final acceptance: A must explicitly include owner-approved Personal/Development control evidence or a controlled Personal message/Development notification budget. This does not authorize first Research messaging (E).

Stop/rollback on Personal/Development refusal, changed route/From identity, duplicate/UNKNOWN delivery, unexpected Research worker, secret/log exposure, startup failure or digest drift. Retain receipts and investigate before any resend. Exact guarded operator sequence is PHOTON_INSTALLATION_OPERATOR_COMMANDS.md; approval scopes and acceptance criteria are PHOTON_INSTALLATION_ACCEPTANCE_GATE.md.

**Minimum next step:** owner grants A with maintenance/quiescence, recovery-risk and Personal/Development health scope, and approves source/config artifact above. No B–E permission is inferred. This task stops after review.
