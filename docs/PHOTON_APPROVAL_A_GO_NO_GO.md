# Approval A operational GO / NO-GO

2026-10-16. **NO-GO for installation execution.** The 41-test Linux bridge and frozen Research-disabled artifact remain accepted; the source baseline still matches. Operational prerequisites are incomplete. No source/configuration changes, restarts, credential reads, messages or installation occurred.

## Blocking items

1. **No complete send barrier established.** Existing Gateway PAUSE is present and holds CTO/completion work, but intake previews and approval entrypoints are not covered; completion has a check/send race and CTO checks only at poll entry. Owners must identify/hold all launchers, drain in-flight work and positively attest idle preview/approval state. Keeping Development intake running preserves memory but does not permit unrestricted interactive intake during the hold.
2. **Unresolved delivery state is unknown.** Live ledgers were not read. Owners need content-free aggregate evidence of pending, accepted and ambiguous attempts. Completion uncertain/CTO attempted_uncertain must not be blindly retried. Hermes restart may automatically redeliver ambiguous replies with a duplicate-warning marker; its effective gate/current rows require owner reconciliation before restart.
3. **Provider recovery is unproven.** CatchUpEvents/reconnect support does not establish complete shutdown catch-up. Personal inbound dedup is memory-only. Obtain authoritative buffering/replay evidence or explicitly accept the scoped risk of lost/replayed inbound messages after draining known work.
4. **Maintenance and acceptance scope not yet fixed.** Approve actual window, rollback decision deadline, on-call operator, safe status/worker/consumer inspection, controlled Personal/Development message budgets and observation interval. Process-active alone is insufficient. Existing PAUSE must not be removed without its original owner's authorization.

## Exact approval A needed

Photon/Hermes administrators and Personal/Development owners must explicitly authorize:

- Only the pinned eight source changes plus two flag0 drop-ins, archive SHA256 `21a661d298fe33c7db012d812a27339d3812f442fda75c3bca994fc44ba17faa`, reviewed artifact transfer and root-private backup retention.
- Coordinated Hermes/Photon stop/start, downtime/reconnect impact, Development outgoing holds/drain, and preservation of existing PAUSE and all delivery/queue state. No Development service stop is implicit; if necessary, revise and approve its dependency ordering first.
- Resolution of ambiguous sends and the exact incoming recovery/risk policy; no ledger resets or automatic compensating sends.
- Effective Research flag0/no worker/no connection evidence and one Personal consumer. No additional /events subscriber for testing.
- Bounded Personal/Development health tests, correct original From identity, noncontent evidence, rollback triggers and deadline. Proposed budget is 30 minutes total with rollback decision by stop+10 minutes; approve or replace it before proceeding.

No approvals B–E are requested or implied. No Research credential population, connection activation, route activation, task processing or Research live test is part of A.

## Recommended next step

Owner supplies the complete quiescence/aggregate reconciliation/maintenance-health plan above. Once these gates are evidenced, reverify baseline and use PHOTON_INSTALLATION_OPERATOR_COMMANDS.md under the exclusive lock: stop Hermes then Photon; install/verify only ten targets; start Photon then Hermes; validate Personal and Development before releasing window-owned holds. Research remains disabled throughout. Preserve completed messages and retry history on installation and rollback.

Detailed evidence, exact hash checks, restart/retry semantics, acceptance limits and rollback criteria: [maintenance readiness](PHOTON_APPROVAL_A_MAINTENANCE_READINESS.md). This NO-GO narrows the earlier procedural PASS: code readiness does not establish operational readiness.
