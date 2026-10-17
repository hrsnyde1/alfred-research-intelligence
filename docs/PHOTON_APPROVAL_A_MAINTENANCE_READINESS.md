# Approval A maintenance readiness

2026-10-16. **NO-GO for execution.** The frozen disabled bridge remains suitable for installation review, but complete operational quiescence and live recovery acceptance are not established. This report supplements the three disabled-installation documents; it does not authorize their commands.

## Evidence and inspection boundary

Reviewed PHOTON_DISABLED_INSTALLATION_REVIEW.md, PHOTON_INSTALLATION_OPERATOR_COMMANDS.md, PHOTON_INSTALLATION_ACCEPTANCE_GATE.md and PHOTON_CORRECTED_LINUX_ACCEPTANCE.md. Fresh read-only SSH used BatchMode=yes, StrictHostKeyChecking=yes and ConnectTimeout=8. Inspected installed Python source, bounded source filenames, selected systemd properties and source hashes. No imports, provider calls, credentials, message histories, delivery records, databases or configuration values were read. No host writes or service actions occurred. Linux lacks rg; bounded grep/find source inspection was used instead. Failed discovery paths were not evidence of absent functionality.

Photon, Hermes and Development intake are active/running. Fresh production hashes still match the accepted baseline:

| Source | SHA-256 |
|---|---|
| sidecar/index.mjs | ef019d1d50e4ca680aede49276181f8eff8d396d9b7c22a73bb5da2b2d7bb8e4 |
| photon/adapter.py | 841ed6cb6e2d392fcec33f8983dd34fffe677c6a8d40e442bc449e66beeb16e5 |
| gateway/run_inbound.py | 6a1a40708075e3550a824eae5519e98db97f52ea7995154e8c7e941de4e02144 |
| /usr/local/lib/alfred-v1.1/trusted_intake.py | d3e1677cb8d7ee17ab801448e85db48fee12d88bbf21a3561e9e755eef742168 |
| completion_integration/delivery.py | 62abc66a9608a54505e5fba9595ec4e53b97511ee8e2b2e0d482239b25ef7eb2 |
| completion_integration/runtime.py | 2feef45fdde9ed74e66c7c181a7a115fdee29c9b8afb19be5dc65b6f1e4d1bb6 |
| .dev/bin/cto.py | d60da3f6c230ef741c97f9689cd6fe85825b376c6e7029935165adb79b684ec1 |

## Development notification hold and resume

`/home/alfred/Alfred/gateway/PAUSE` is already present (existence only checked). Do not remove it at the end of maintenance: it predates this task and may hold unrelated work. Its owner and original purpose must be established.

| Path | Verified behavior | Maintenance implication |
|---|---|---|
| CTO `.dev/bin/cto.py:poll` | Under Gateway lock, checks PAUSE/STOP at entry; persisted plans retain `pending`, mark `attempted_uncertain` before external I/O, then `delivered` with receipt. Nonpending plans are skipped. | PAUSE holds new polls, not a poll already past its check. Drain existing poll/lock owner. Preserve plans. Resume only pending plans through existing poll; uncertain requires owner reconciliation. |
| Completion `runtime.py:run` | On-demand, no listener/scheduler of its own. Checks PAUSE before preparation and again immediately before transport. Existing /send body omits project and uses legacy authenticated Personal binding. | Hold all invocations and drain existing ones. PAUSE alone has a check/send race. Do not run notify during the window. |
| Completion `DeliveryTracker.deliver` | Private locked durable state; records `uncertain` before callback and `sent` after acceptance. Duplicate sent/uncertain suppress callback. Receipt means SDK acceptance, not receipt/read. | Preserve state directory, lock and receipts. No initialize/reset, no automatic resend of uncertain. No durable pending queue in this tracker; preserve publication inputs for never-attempted notifications. |
| Trusted intake | SO_PEERCRED-authenticated observe/submit/status and privileged approval operations. Preview send uses immediate 2-second /send. No PAUSE/quiescence operation appears in the inspected dispatcher. Preview/active state is in memory; confirmed inbox publish is fsynced/no-replace. | Completion/CTO PAUSE is not a global send barrier. Keep intake running to preserve its in-memory confirmations, but require all preview/approval issuers and Hermes submissions to be idle and held. |

Intake can remain running, but full interactive Development intake cannot be promised while notifications are paused: previews are part of its protocol and no independent outbound pause is established. During Photon outage it cannot observe new Photon events. Do not approve new preview/approval operations during the hold. Existing five-minute confirmations may expire; never synthesize or replay confirmation to compensate.

Active Development gateway/evidence timers were discovered; their services were inactive at inspection. These are not proof of no future sends or current in-flight work. No completion-specific systemd unit appeared in the loaded Alfred unit list; manual, external and unlisted launchers remain owner-inventory requirements.

Required owner-provided noncontent evidence before execution: all send entrypoints/issuers identified and held, active CTO/completion/preview/approval attempts drained, aggregate unresolved-state counts and whether a transport request is in flight. Do not dump plan text, destinations, tokens or ledger contents. Use an existing approved status interface or a separately reviewed content-free inspector; no such complete operational interface was established here. This task intentionally did not read live records.

Safe resume: preserve all protected inputs/plans/ledgers; compare approved aggregate counts before/after; resume only never-attempted pending work through its existing entrypoint. Sent/delivered is not permission to resend. Hold uncertain/attempted_uncertain until authoritative receipts or owner reconciliation resolve it. Restore only holds introduced under the approved window; preserve pre-existing PAUSE. Do not edit ledger states to force retries.

## Photon/Hermes restart and recovery

Hermes Requires/After Photon. Both Want/After Development intake and network-online; no PartOf/BindsTo. Users: Photon alfredphoton, Hermes alfredmsg, Development intake alfred. Stop Hermes then Photon; start Photon then Hermes, with Development intake kept running and quiescent. Both CanReload=no. Photon Restart=always/5s, stop timeout15s/KillMode control-group; Hermes Restart=always/5s, stop timeout70s/KillMode mixed. Explicit stop is needed; do not kill a PID and allow automatic restart during file replacement. Gateway/evidence services Restart=no, stop timeout90s/control-group; no stop of them is approved by the current procedure.

Installed Personal sidecar uses memory Maps for conversation/message caches and an in-memory consumer/waiter delivery loop. It waits for a reconnecting consumer while that process lives; this is not a disk-backed queue and does not survive bridge restart. It re-subscribes after stream errors/end with 1s exponential backoff capped30s plus jitter. SDK in-session reconnect and upstream CatchUpEvents exist, but completeness across shutdown is not established; upstream errors can prevent inbound delivery. A read acknowledgment follows local forwarding, not proof of durable completed agent handling.

Personal adapter MessageDeduplicator is bounded TTL memory. Same-process adapter replacement can inherit it; whole Hermes restart loses it. Replay can therefore be processed again. Do not translate source comments about reconnect into an exactly-once or restart-recovery guarantee.

Hermes final-response ledger (`gateway/delivery_ledger.py`) is best-effort SQLite state, default-enabled by source configuration gate, with pending/attempting/failed/delivered states. Actual effective gate/state was not read. Restart sweep may resend ambiguous attempting/failed replies with a visible recovered/possible-duplicate marker. MAX_ATTEMPTS=3, stale expiry24h, retention7days, cap500rows. Slash/ephemeral responses are excluded and ledger errors do not block sending. This differs from Development completion's uncertain-no-resend policy. Preserving files alone does not prevent Hermes automatic recovery sends on startup. Do not alter this policy as part of A.

Inbound loss, outbound uncertainty and duplicates remain possible. No authoritative provider retention/cursor evidence, current unresolved ledger counts, or full drain interface was established. Obtain proof or explicit bounded owner risk acceptance; unresolved ambiguous sends must be reconciled before planned restart. No zero-downtime promise or numerical recovery guarantee.

## Exact acceptance checks (future authorized window only)

Follow the frozen operator commands; this report does not execute them. Baseline drift, missing quiescence or unknown override is a stop condition.

1. Pin archive SHA256 `21a661d298fe33c7db012d812a27339d3812f442fda75c3bca994fc44ba17faa`, then manifest/helper/checksum hashes specified in PHOTON_INSTALLATION_OPERATOR_COMMANDS.md. Run its `operator.py verify` before stopping; it validates old bytes, metadata, target absence and unchanged send-format. Recheck Node/SDK pins from accepted Linux evidence.
2. After install, check every target against the exact manifest's `new` field (never run old-baseline verify after install). A content-free hash-only command, in the pinned root-private ART session:

```sh
python3 -I -S -B - "$ART/INSTALL_MANIFEST.json" <<'PY'
import hashlib,json,pathlib,sys
m=json.loads(pathlib.Path(sys.argv[1]).read_text())
for r in m['records']:
 p=pathlib.Path('/')/r['path']; assert not p.is_symlink()
 assert hashlib.sha256(p.read_bytes()).hexdigest()==r['new'], str(p)
for r in m['guards']:
 p=pathlib.Path('/')/r['path']; assert not p.is_symlink()
 assert hashlib.sha256(p.read_bytes()).hexdigest()==r['sha256'], str(p)
print('target and guard hashes PASS')
PY
```

3. Require exact flag0 drop-in digests on both services and reviewed DropInPaths/EnvironmentFiles/launcher precedence. Do not dump systemctl Environment or process environ. An owner-authorized privileged inspector can read each service MainPID's `/proc/PID/environ` internally and emit only the count/value-equals-zero result for PHOTON_RESEARCH_ENABLED; require exactly one `=0` for both. It must not print any other value. If effective environment cannot be checked safely, stop. No such privileged read occurred here.
4. `systemctl is-active --quiet` for Photon/Hermes/Development intake; `systemctl show` only Id/User/Group/MainPID/ActiveState/SubState/CanReload/DropInPaths. Confirm original launchers and expected process boundaries. No unreviewed restart loop, stream-degraded state or port change.
5. Verify one existing listener and exactly one Hermes Personal NDJSON consumer using an approved content-free transport monitor. Do not open /events as an extra test consumer: it replaces the existing subscriber. Workers are Node threads, so process counts alone cannot prove no Research worker. Require effective flag0, reviewed disabled code hash, and owner-approved worker/connection monitor evidence. Absence of a separate PID alone is insufficient. No new authenticated Research connection or credential attachment may exist.
6. Approved local /healthz stream summary can demonstrate local server/stream state; never print raw errors. /probe initiates provider I/O and requires explicit inclusion in A; neither proves successful Personal delivery. Do not create/send anything in this review.
7. A must scope a controlled Personal inbound/reply and one existing Development notification test, with fixed budget, correct original receiving/sending identity, acceptance receipt and owner-observed receipt. Use existing trusted caller credentials without exposing values. Legacy Development body omits project; explicit Research via Personal must remain denied (synthetic proof already exists). Capture only pass/fail and redacted correlation. This is no Research message permission.
8. Compare approved noncontent ledger/receipt summaries before/after. No extra logical message, unexpected recovery marker, UNKNOWN/uncertain growth or cross-route send. Finite observation cannot prove absence of all duplicates; owner must define observation interval and catch-up scope. Preserve receipts, never erase sent messages.

## Recommended window and stop policy

Before booking: resolve all NO-GO items in companion GO_NO_GO report. Owner supplies maintenance start/end, dedicated operator, rollback decision deadline and positive quiescence/health evidence. Recommended provisional budget: 30-minute window, rollback decision no later than 10 minutes after initial consumer stop, reserving 20 minutes for restore/recovery; these are proposed limits requiring owner acceptance, not measured runtime promises. Do not begin if available time cannot accommodate stop timeouts and owner recovery SLA. Expired deadline triggers stop/escalation, not a forced rollback through ambiguous sends.

At window: retain preexisting PAUSE; hold/drain all send paths and collect approved aggregate evidence. Acquire maintenance lock; reverify artifact/baseline; take helper's code-only snapshot under `/var/backups/alfred-photon-disabled-20261016-${BASHPID}`; stop Hermes/Photon; perform pinned ten-target transaction; verify disabled launch; start Photon/Hermes; perform scoped health/control evidence before releasing only window-owned holds. Do not restart Development intake by default. No Memory/HQ/Obsidian service is in scope.

Rollback on startup failure, digest/disabled-state drift, changed Personal sender/route, Development refusal, unexpected Research worker/auth, duplicate/recovered ambiguous delivery, unapproved consumer, or deadline failure. Quiesce/reconcile again first. Under same lock, use retained ART/BACKUP and exact operator rollback: stop Hermes then Photon, helper rollback, daemon-reload, start Photon then Hermes, recheck original hashes and health. Never restore databases/ledgers, rewind receipts or resend. Unknown current files/corrupt backup leave consumers stopped for administrator review. Operational recovery may outlast the proposed window.
