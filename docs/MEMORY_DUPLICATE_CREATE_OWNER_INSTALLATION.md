# Minimal Memory correction — corrected owner installation review

2026-10-16, procedure revision 2. **BLOCKED FOR INSTALLATION: existing HQ Capture/worker/Sync pins reject a changed shared-current target.** No patch, service, timer, release switch or production change was performed. The checksum format is corrected and tested; the two-line bug fix remains validated. Read [shared impact review](MEMORY_SHARED_RELEASE_IMPACT_REVIEW.md) and [correction evidence](MEMORY_INSTALLATION_PROCEDURE_CORRECTION.md).

The original `owner_install.sh` and `owner_rollback.sh` under `artifacts/releases/alfred-memory-duplicate-create-0.1.0-rc1-20261016` are **superseded review artifacts; DO NOT RUN**. Their Memory-only restart sequence is unsafe for this shared deployment. They remain unchanged for audit/hash continuity. This document replaces their procedure; it does not authorize executing any future command below.

## Scope and immutable identities

Runtime delta: exactly two line substitutions in `source/focused_v1/store.py`; select existing review_state and return it instead of literal approved. No review-state write, approval/promotion policy, Research route/grant/source, schema, migration, dependency, Obsidian or Development code change is approved. No second Memory service or alternate production source path is proposed.

| Item | SHA-256 |
|---|---|
| Original store.py, 29,402 bytes | `5ca002bd93e486875191292c21ba782fb2df5eb3fa4d525654e80ad29069cf8c` |
| Patched store.py, 29,426 bytes | `0d84c9c12c0715f14be7729a5007073ebc99f55fa7820e6bed81a55834d969c1` |
| duplicate-create-review-state.patch | `0b25c3b80d2c5878ed6a1b9f76a9f638b58e17ade7717bdb08e4e8e2566a3a4a` |
| Original complete canonical inventory | `66d72779e1fa34f56245061344d0f935a0d962343b8d8677ac313e54151161ac` |
| Expected patched complete canonical inventory | `87227645b324a724f90d812dd4ceeb3665c4e7d179728e47b087f77094fe7bd2` |

OLD: `/opt/alfred-obsidian-v1/releases/4d5ba29bd3027e74c808a8feaf1b5dadfded22f0`.

NEW (proposed, not created): `/opt/alfred-obsidian-v1/releases/4d5ba29bd3027e74c808a8feaf1b5dadfded22f0-memory-duplicate-create-0.1.0-rc1`.

CURRENT: `/opt/alfred-obsidian-v1/current`. Both named releases must be real, root-owned immutable directories, not alternate symlinks. No overwrite of OLD or collision at NEW is allowed. Complete release verification covers 1,564 entries; every unchanged entry must remain byte-for-byte and metadata-identical. One file's size/digest alone may differ. The saved inventory is a point-in-time source/runtime baseline, not a database backup or a whole-server integrity assertion.

## Required approvals and hard preconditions

1. Memory owner accepts exact diff/digests, corrected duplicate semantics, six focused synthetic passes and known wider regression limits. Known caller trace found no code relying on unconditional approved; external callers require owner confirmation. saved=true remains persistence, not approval.
2. Shared-release owners approve a compatible binding for R42 Capture, R55 worker and R40 Sync, preserving their guard policy and exact source/runtime identity. Existing constants all pin OLD; both capture files also pin R40_SHA. Forward and rollback bindings must be reviewed/versioned together and have exact owner-approved hashes and installation actions. **No such approved bundle exists in this task. Stop here before transfer, quiescence or source switch.** A static constant match alone is insufficient; guard logic and dependencies must remain reviewed. No bypass, unit override, separate Memory path or hot-in-place patch is approved.
3. Approve all five service transitions and both timer transitions, their Requires ordering, ingress/client quiet window, in-flight request completion evidence, natural one-shot/child drain, queued-receipt reconciliation and normal scheduled publication permissions. Owners supply the existing authoritative drain/receipt status mechanism; do not invent a drain endpoint or read production state/credentials to infer it.
4. Approve complete release and external runtime manifests, current interpreter/import resolution, root-owned protected review payload, target paths and exclusive deployment lock. No outside symlink, new files, cache rewrite, permission drift or state/config/secret inclusion may be accepted as harmless. No environment, credential, API or database configuration change is part of this fix.
5. Approve exact health acceptance, bounded waits, rollback trigger/ordering and restoration of the known bug. Backups follow existing owner policy; this source-only fix requires no DB migration/restore. Observe any overlapping backup under that policy without restarting or replaying its job.

Until item 2 and drain evidence are supplied, this is a **gated procedure specification, not an executable installation approval**. No new compatible runtime guard files or service configuration have been created.

## Correct checksum command and protected review payload

The shell format must contain ONE backslash before n; printf emits actual newline bytes:

```sh
printf '%s  %s\n' '051bc9867010dd22882e4ac7982c071535208b2c566402958877468ecd20095c' OWNER_FILES.sha256 | sha256sum --strict --check -
```

This verifies only the historical manifest; it does not authorize the superseded scripts. For revision 2 use the following exact checksum command from an owner-approved root-owned, non-group/non-world-writable staging directory containing only the four allowlisted files and manifest:

```sh
printf '%s  %s\n' 'e95ba6391c3fbd91880b0f9dd1b37e39a4bbb928d15f472efe788d1ce94b2dbc' PROCEDURE_FILES.sha256 | sha256sum --strict --check -
sha256sum --strict --check PROCEDURE_FILES.sha256
```

The four files are `duplicate-create-review-state.patch`, `INSTALLED_RELEASE_INVENTORY.json`, `release_integrity_check.py`, `pin_preflight.py` in `artifacts/reviews/memory-installation-procedure-20261016`. Never transfer/execute the old owner scripts, full Research archive, test state or whole review-evidence directory as an install payload. Future owner transfer/root staging must pin these bytes before executing a helper and prevent unprivileged modification through the whole window. No transfer/staging directory was created by this phase. Stop on any failed verification; do not continue the next shell block manually.

The corrected printf payload was tested on isolated Mac synthetic files (good, old malformed, modified, missing, restored cases). GNU sha256sum on Linux additionally accepted corrected input and rejected the old malformed input using read-only `/dev/null`; no Linux synthetic file was created.

## Pre-mutation checks — future owner only

These commands are review specifications; none ran as an installation. Define variables in the owner-controlled shell and hold one deployment lock through acceptance or rollback. The cooperative lock is not protection from unrelated administrators; require an exclusive window.

```sh
set -euo pipefail
umask 077
OLD='/opt/alfred-obsidian-v1/releases/4d5ba29bd3027e74c808a8feaf1b5dadfded22f0'
NEW='/opt/alfred-obsidian-v1/releases/4d5ba29bd3027e74c808a8feaf1b5dadfded22f0-memory-duplicate-create-0.1.0-rc1'
CURRENT='/opt/alfred-obsidian-v1/current'
# cd to the owner-approved root-owned review staging directory first.
[ "$(id -u)" = 0 ]
exec 9>/run/lock/alfred-memory-release.lock
flock -n 9
[ -L "$CURRENT" ]
[ "$(readlink -f -- "$CURRENT")" = "$OLD" ]
[ ! -e "$NEW" ] && [ ! -L "$NEW" ]
printf '%s  %s\n' 'e95ba6391c3fbd91880b0f9dd1b37e39a4bbb928d15f472efe788d1ce94b2dbc' PROCEDURE_FILES.sha256 | sha256sum --strict --check -
sha256sum --strict --check PROCEDURE_FILES.sha256
python3 -I -S -B release_integrity_check.py INSTALLED_RELEASE_INVENTORY.json "$OLD" original
python3 -I -S -B pin_preflight.py "$NEW"
```

**The last command currently exits 75 for three exact pin mismatches. Do not execute further steps under the present installed pins.** The helper reads static AST constants only; it does not run a runtime's `inspect` action or read production configuration. A future owner-approved guard bundle needs its own exact verification/install/rollback commands and coordinated validation; those cannot be guessed or inserted into this two-line patch.

## Prepare and verify immutable release — only after all gates close

A future authorized owner may prepare a copy while old services continue, but must first satisfy the guard, full-release and payload approvals above. Preparation is not activation:

```sh
timeout --kill-after=5s 300s cp -a --reflink=auto -- "$OLD" "$NEW"
python3 -I -S -B release_integrity_check.py INSTALLED_RELEASE_INVENTORY.json "$NEW" original
patch --batch --forward --fuzz=0 -p1 --dry-run --directory="$NEW/source" --input="$PWD/duplicate-create-review-state.patch"
patch --batch --forward --fuzz=0 -p1 --directory="$NEW/source" --input="$PWD/duplicate-create-review-state.patch"
chmod --reference="$OLD/source/focused_v1/store.py" "$NEW/source/focused_v1/store.py"
chown --reference="$OLD/source/focused_v1/store.py" "$NEW/source/focused_v1/store.py"
python3 -I -S -B release_integrity_check.py INSTALLED_RELEASE_INVENTORY.json "$NEW" patched
python3 -I -S -B release_integrity_check.py INSTALLED_RELEASE_INVENTORY.json "$OLD" original
sha256sum --strict --check PROCEDURE_FILES.sha256
```

Dry-run/application must have no fuzz, offset, backup or reject file. Exact resulting hash and complete membership verification reject any unexpected patch result even if patch returns 0. The verifier checks complete types/modes/ownership/link targets/xattrs and file bytes before and after patch; it never follows the internal lib64 symlink. No database, vault, config or runtime state belongs in NEW. On timeout/failure retain incomplete NEW for owner inspection, do not overwrite/retry/delete automatically, and leave current/services unchanged.

## Service ordering and controlled activation specification

This section is conditional on approved compatible external pins AND owner-provided drain/receipt evidence. It is not permission to run stop/start commands now. Record initial states, PIDs, invocation identities, pending job identities and owner-approved nonsecret receipt/high-water summaries. Preserve the original states for restoration; do not start an originally inactive long-running service.

1. Owner pauses new direct Memory writes, capture submissions and editor/forced-command ingress through existing client maintenance controls. No Hermes, Photon or Development service/config change is proposed. All accepted requests must be durably acknowledged or held for same-ID reconciliation; no new-ID retry after an ambiguous result.
2. Stop only the two timers first. Do NOT stop their active services/children. Wait naturally for both one-shots, including any worker required by the Sync transaction, to become inactive/dead with no jobs, MainPID/ControlPID or cgroup descendants. Review Result/ExecMainStatus and authoritative receipt status. Permit at most 930 seconds for an already running Sync (command bound 900 seconds plus cleanup); if exceeded, abort the window without signaling/killing the job. The 90-second unit stop timeout is not a drain guarantee.

```sh
systemctl stop alfred-hq-v1-sync-cycle.timer alfred-obsidian-editor-hq-worker.timer
systemctl show alfred-hq-v1-sync-cycle.service alfred-obsidian-editor-hq-worker.service --property=Id,ActiveState,SubState,MainPID,ControlPID,ControlGroup,Result,ExecMainStatus --no-pager
systemctl list-jobs --no-pager
```

Owner polls these metadata checks at bounded intervals; inactive states alone do not prove receipt consistency or no child/manual exporter. Require owner confirmation that no manual export/Sync/forced-command process or in-flight ingress overlaps the switch. Never open/clear a vault lock, rerun process-once, or launch a manual Sync to manufacture quiescence. Durable pending work may remain; retain its identity/state.

3. With jobs drained and ingress idle, stop Capture and Editor first while Memory is still available, verify graceful exits/socket cleanup through existing owner health evidence, then stop Memory last. Do not stop editor while Sync still Requires it. If any stop times out, is forced, or leaves an ambiguous request, do not switch; reconcile first.

```sh
systemctl stop alfred-hq-capture.service
systemctl stop alfred-obsidian-editor-hq.service
systemctl stop alfred-memory-v1.service
systemctl show alfred-memory-v1.service alfred-hq-capture.service alfred-obsidian-editor-hq.service alfred-hq-v1-sync-cycle.service alfred-obsidian-editor-hq-worker.service --property=Id,ActiveState,SubState,MainPID,ControlPID,ControlGroup,Result,ExecMainStatus --no-pager
```

All five must be inactive with no control-group tasks/jobs. No killall/pkill, account-wide signaling, forced stop or stale-socket deletion is permitted. Capture's stop flag can finish the current receive; editor's SystemExit does not prove drain, hence the preceding idle gate.

4. Reverify old/new complete inventories, payload hashes, current target, the owner-approved external forward bindings and still-quiescent services. Perform the existing shared release switch as a same-directory rename, with no fallback to a different code path:

```sh
[ "$(readlink -f -- "$CURRENT")" = "$OLD" ]
python3 -I -S -B release_integrity_check.py INSTALLED_RELEASE_INVENTORY.json "$OLD" original
python3 -I -S -B release_integrity_check.py INSTALLED_RELEASE_INVENTORY.json "$NEW" patched
NEXT='/opt/alfred-obsidian-v1/.current-memory-duplicate-create-install'
[ ! -e "$NEXT" ] && [ ! -L "$NEXT" ]
ln -s -- "$NEW" "$NEXT"
mv -T -- "$NEXT" "$CURRENT"
python3 -I -S -B -c 'import os; fd=os.open("/opt/alfred-obsidian-v1",os.O_RDONLY|os.O_DIRECTORY); os.fsync(fd); os.close(fd)'
[ "$(readlink -f -- "$CURRENT")" = "$NEW" ]
python3 -I -S -B release_integrity_check.py INSTALLED_RELEASE_INVENTORY.json "$NEW" patched
```

The rename is atomic for path lookup; not for service state or publication. External pin bundle transition/rollback ordering must be separately supplied and verified while all consumers are stopped. No such bundle transition is authorized or implemented in this document. Any interruption after rename is an ambiguous code activation: keep timers/ingress closed, inspect target and follow approved rollback rather than resume blindly.

5. Start Memory first. Require the combined existing handler, correct cold-load source origin, service active/running, fresh process identity and owner-approved health `{status: ready}` before clients/workers resume. Read-only health GET at the existing endpoint may be authorized for the future owner; it was NOT called in this task. Do not send production create/review fixtures.

```sh
systemctl start alfred-memory-v1.service
systemctl is-active --quiet alfred-memory-v1.service
systemctl show alfred-memory-v1.service --property=ActiveState,SubState,MainPID,WorkingDirectory,Result --no-pager
python3 -I -S -B release_integrity_check.py INSTALLED_RELEASE_INVENTORY.json "$NEW" patched
```

The owner must approve exact effective endpoint/runtime health and cold-import evidence before installation. Unit active alone is not sufficient, and code verification does not prove the process loaded it. Normal service startup opens its existing configuration/keys/database and reapplies existing deletion recovery; this patch adds no such action. Do not claim a future restart performs no normal database I/O; no migration or record-state backfill is added.

6. Verify and start the originally active Capture and Editor with approved NEW-compatible pins. Capture startup can recover original capture IDs; accept only existing idempotent/reconciliation behavior and preserved receipts. Do not manually invoke worker-route or exports as a canary.

```sh
systemctl start alfred-hq-capture.service alfred-obsidian-editor-hq.service
systemctl is-active --quiet alfred-memory-v1.service alfred-hq-capture.service alfred-obsidian-editor-hq.service
systemctl show alfred-hq-capture.service alfred-obsidian-editor-hq.service --property=Id,ActiveState,SubState,MainPID,Result --no-pager
```

These start commands assume the observed three long-running services were active at the window's beginning; re-evaluate if initial state differs. Fail-closed pin errors, unresolved deletion recovery or missing owned sockets abort resumption. Do not disable checks or replace credentials.

7. Owner accepts receipt/currentness/health evidence, then restores only originally active timers and ingress. Worker/export/Sync publication resumes through the existing timers, not new manual launches; starting Sync can Require a worker, so do not separately run it to verify a job twice. Both timers observed Persistent=no, but a start can still schedule promptly.

```sh
systemctl start alfred-obsidian-editor-hq-worker.timer alfred-hq-v1-sync-cycle.timer
systemctl show alfred-obsidian-editor-hq-worker.timer alfred-hq-v1-sync-cycle.timer --property=Id,ActiveState,SubState,Triggers --no-pager
python3 -I -S -B release_integrity_check.py INSTALLED_RELEASE_INVENTORY.json "$NEW" patched
python3 -I -S -B release_integrity_check.py INSTALLED_RELEASE_INVENTORY.json "$OLD" original
sha256sum --strict --check PROCEDURE_FILES.sha256
```

Observe the first normal scheduled results and existing owner receipt/Sync acknowledgments. No new-ID republishing, duplicate manual activation, repeated publication canary, queue reset or export reversion is allowed. This owner observation would permit normal existing publication and requires separate explicit approval; none occurred here.

## Rollback prerequisites and sequence

Rollback is code-only and owner-controlled. Before installation, pin OLD full inventory, old/new external guard bundles and exact reverse binding actions, initial service/timer states and receipt high-water evidence. No DB snapshot restore, ledger/tombstone/grant/key rewind or vault/remote Sync rollback is part of this correction.

On health failure, keep/return ingress and the two timers paused. Let already running publications finish naturally; reconcile any ambiguous operation using its original ID and expected version. If safe drain cannot be established, stop and escalate to the owner, not forced termination or data rollback. Stop Capture/idle Editor, then Memory, in the same order; verify all consumers down. Reverify OLD unchanged and NEW exactly patched; any drift stops the scripted rollback for revised owner review.

While all consumers remain stopped, restore the approved OLD-compatible external guard binding through its separately approved exact commands, then atomically select OLD:

```sh
[ "$(readlink -f -- "$CURRENT")" = "$NEW" ]
python3 -I -S -B release_integrity_check.py INSTALLED_RELEASE_INVENTORY.json "$OLD" original
python3 -I -S -B release_integrity_check.py INSTALLED_RELEASE_INVENTORY.json "$NEW" patched
NEXT='/opt/alfred-obsidian-v1/.current-memory-duplicate-create-rollback'
[ ! -e "$NEXT" ] && [ ! -L "$NEXT" ]
ln -s -- "$OLD" "$NEXT"
mv -T -- "$NEXT" "$CURRENT"
python3 -I -S -B -c 'import os; fd=os.open("/opt/alfred-obsidian-v1",os.O_RDONLY|os.O_DIRECTORY); os.fsync(fd); os.close(fd)'
[ "$(readlink -f -- "$CURRENT")" = "$OLD" ]
python3 -I -S -B release_integrity_check.py INSTALLED_RELEASE_INVENTORY.json "$OLD" original
```

Start Memory first, validate health and OLD pin bindings; then restore originally active Capture/Editor, then originally active timers and ingress only after owner acceptance. Recheck complete inventories and payload digests after service recovery. Retain NEW and audit evidence; do not reverse-patch live source or delete publication stages. Reverting restores the known false-approved duplicate response; existing approved/pending/rejected records and completed publications must remain at their latest state.

If failure happens before any source switch, do not select OLD again blindly: establish current target and whether any service was stopped, then restore only initial states after owner drain/health review. Do not replay a failed deployment command over an existing NEW directory. No automatic trap is allowed to restart publication on uncertain health.

## Explicit stop conditions and current decision

Stop before mutations for unresolved owner approvals, incompatible pins, baseline/payload/membership/mode/link/xattr mismatch, target collision, unknown consumer, failure to secure exclusive window or incomplete rollback bundle. Stop before switching for active/ambiguous operations, jobs/children, forced stop, changed target or drift. Stop before resuming publication for startup/pin/health/cold-load failure, unresolved receipts/deletions, unexpected normal-cycle refusal or conflicting duplicate outcomes.

**Current decision: checksum correction PASS; full original release integrity PASS; installation BLOCKED by the three existing hard pins and unapproved coordinated drain/guard transition.** The exact next action is owner review of compatible shared-runtime pin rebinding and its paired rollback, followed by approval of this multi-service window. No install/stop/start/switch has been performed.
