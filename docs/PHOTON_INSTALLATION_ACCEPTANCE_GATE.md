# Photon disabled installation acceptance gate

2026-10-16. **PASS for the reviewed disabled-installation procedure. Execution still requires explicit A.** Nothing was installed/restarted; Research remains inactive.

## Independent scope validation

All four active baseline source hashes match. Three services are active/running with known users/launchers and restart dependencies. Current proposed drop-ins are absent; existing Hermes10/20/30 drop-ins are preserved. The corrected product source is identical to the 41-test Linux-accepted revision.

Fresh local validation: original 41 bridge tests PASS, five disabled-composition tests PASS and nine disposable-filesystem operator tests PASS. Archive is a pinned 15-file regular-file package, decoded and compared against each staged input. Source/config old/new hashes and exact artifact SHA-256 are in PHOTON_DISABLED_INSTALLATION_REVIEW.md. Full operator/source manifest and logs are in staging/photon-disabled-installation-v1 and artifacts/audits/photon-disabled-review-20261016/.

The operator CLI was not run privileged and no Linux source filesystem/systemd action was exercised. Its real file transaction was executed against temporary root mirrors with hash/metadata/xattr restoration and unchanged synthetic sent/retry history. These tests do not establish upstream delivery guarantees, a live outage duration or safe current job counts. Those remain explicit execution gates, not inferred approvals.

## Separate approval boundaries

| Scope | Explicit approval needed | Exclusions |
|---|---|---|
| A — Research-disabled installation | Photon/Hermes administrators and Personal/Development owners approve the pinned eight-source/two-drop-in artifact, maintenance lock/window, outgoing quiescence, upstream catch-up/risk policy, coordinated two-service replacement, rollback deadline and Personal/Development health evidence | No new Research credential, connection, profile/grant activation or message |
| B — Protected Research credentials | Credential/Security owners approve separate project ID/secret and separate Research caller-token references, resolver/service UID scope, no company-agent exposure and redaction | Does not enable connection or routing; values never enter this repo/reports |
| C — Research connection | Photon/Personal owner approves explicit enable, correct project/line, worker lifecycle/resource limits, five-minute lease or reviewed renewal, retries/UNKNOWN reconciliation and disable path | Does not authorize Research task processing or test messages |
| D — Fail-closed Research routing | Hermes/Research owners approve exact trusted sender/conversation/connection/profile, served-profile/hook integration, genuine issuer/registration, durable pending intake and no fallback | Does not authorize a live message or source acquisition/model/Memory work |
| E — First live Research test | Owner approves one exact controlled sender/conversation/message/reply budget and nonsecret destination/From evidence, with C/D prerequisites satisfied | No broader Research/provider/Memory execution or automatic follow-ups |

Each authorization must name scope/artifact/config revision, owners, limits and rollback/disable conditions. A does not imply B–E; B does not imply C. C without D must stay unavailable for intake. D without C grants no connection. E is not permission to promote Memory, run models or send unbounded messages. Existing source body/text cannot allocate any authority.

## Mandatory A pre-execution gates

- Baseline/Node/SDK, metadata, target absence and all direct-client/source-consumer contracts freshly reverified. Any drift stops, not force-applied.
- Owner-approved archive transfer and root-private extraction verified by externally pinned archive/manifest/checksum/helper digests.
- Effective disabled launch contract reviewed: proposed later-sorted flag0 drop-ins, no new override or wrapper/env-file assignment. No Research credentials attached or resolved.
- Personal and Development outgoing work safely quiesced; no unresolved send treated as absent. Development must remain quiescent through dependency startup. If no owner-supported safe quiescence method is available, installation is **BLOCKED**.
- Owner supplies upstream buffering/catch-up/replay evidence or consciously accepts the bounded maintenance risk. Messages may arrive while stopped; completeness/zero downtime is not promised. Never delete or rewind accepted/sent/UNKNOWN records or automatically resend.
- A explicitly scopes postrestart Personal/Development evidence. Routine status alone is not end-to-end messaging proof. Any controlled message requires its own stated budget inside A; no Research message under A.
- Exclusive maintenance/admin authority and exact snapshot retention/rollback deadline agreed. No unidentified shared consumer, source security flag or filesystem condition left to improvise.

## Post-install acceptance, still Research disabled

1. Ten target hashes match the pinned manifest; unchanged guard/dependencies and existing config remain unchanged.
2. Photon and Hermes run with expected launchers/users and one existing listener/Personal consumer; Development remains healthy without source change. No Research worker, credential attachment/resolution, connection or competing consumer.
3. Flag0 precedence and no active Research route/hook/grant verified by approved nonsecret configuration/monitor evidence; do not dump credentials or private histories.
4. Approved Personal and Development health/control evidence confirms original route/From identity and legacy sends; duplicate/UNKNOWN outcomes are held for reconciliation, not republished.
5. Existing delivery/retry/dedupe stores and completed messages are preserved; no migration, reset or deletion. Backup contains only code/config and source metadata.
6. Owners sign the maintenance result before unquiescing. On failure, use guarded rollback only after quiescence/reconciliation and then verify baseline plus Personal/Development health again.

## Stop conditions and next owner action

Any digest/protocol/health/disabled-state discrepancy, unknown current version, ambiguous delivery, secret exposure, inability to quiesce or expired window stops execution/acceptance. Do not compensate by enabling Research, reading credentials, bypassing identity checks, installing packages or deleting delivery records.

**Minimum next step:** owner approval A with the exact artifact and positive maintenance/quiescence/recovery/health plan. No B–E action in this task. The reviewed procedure is PASS; installation remains unexecuted and no authorization is implied.
