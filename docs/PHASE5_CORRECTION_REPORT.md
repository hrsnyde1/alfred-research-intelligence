# Phase 5 export receipt correction

## Root cause

Export completion checked only that an export-request receipt existed, without requiring SUCCESS. Thus FAILED request → successful EXPORTED → successful SYNCED was accepted. Requests/completions also lacked explicit attempt, destination/version and prerequisite-receipt references; a check only for request success would still allow delayed events from unrelated or superseded attempts. Replay returned historical success before checking current export prerequisites.

## Exact changed files

- `src/alfred_research/memory/fake.py`
- `src/alfred_research/memory/contracts.py`
- `tests/test_memory.py`
- `docs/PHASE5_IMPLEMENTATION_REPORT.md`
- `docs/PHASE5_TEST_RESULTS.md`
- `docs/PHASE5_MEMORY_CONTRACTS.md`
- `docs/PHASE5_CORRECTION_REPORT.md` (new)

No other component, SQLite schema, credential, dependency, live service or vault changes. No Phase 6 work.

## Correction

Commands and receipts use proposed v2 schemas. Export operations bind an explicit attempt and fixed environment-specific test destination; commands supply the authoritative Research record version. Export completion must reference the exact successful EXPORT_REQUESTED receipt; Sync must reference the exact successful EXPORTED receipt, itself linked to the same request. The receipt retains record digest/version and attempt/destination/prerequisite references. Request attempt ID must equal its operation ID.

The adapter requires the latest record-specific request to have succeeded and checks record digest/version, destination, attempt and authenticated actor before accepting completion. It applies these checks and current Research validity before replay as well as new event creation. Wrong or stale references fail closed. A failed/partial phase cannot be revived by replaying old success; recovery requires a new authorized export request. Successful exact replay remains idempotent while the attempt and phase remain valid. Revoked/expired/disputed/superseded records cannot replay a completion as success.

All checks run under existing catalog/transcript locks. Rejections create no completed-export/Sync event. Failed/partial receipts remain visible in audit history. Test request response loss raises DeliveryAmbiguous; authorized lookup/replay/reconcile may establish the recorded request result, but request recovery never fabricates export completion or Sync. Destinations are labels `test-obsidian:<environment>`, never real vault paths.

Existing export test setup now supplies explicit references. Recovery after partial export/failed Sync creates a new request instead of silently promoting the failed attempt. All prior assertions and test cases remain.

## Compatibility

KnowledgeCandidate, other contracts and the existing SQLite schema are unchanged. The changed command/receipt schemas are explicit `.proposed.v2`; old v1 payloads and old nested transcript receipts are rejected. No automatic schema migration or unbound receipt import is attempted. Temporary simulation data may be regenerated; any future retained-data import requires a separately reviewed mapping. This fail-closed compatibility policy prevents old receipts from acquiring authorization bindings they never possessed.

## Executed validation

Required full suite: **215 passed, 0 failures/errors, 13.240 seconds, exit 0**. All original 208 cases plus seven new regressions.

Targeted Memory suite: **30 passed, 0 failures/errors, 5.644 seconds, exit 0**. Compilation: 33 Python files passed in memory; package metadata checks passed without installation or build.

Exact independent reproduction: promoted synthetic knowledge, FAILED request, SUCCESS export-status and Sync attempts. Both raise `successful export request required`, and transcript remains unchanged after denial. Separately, authorized successful request → export → Sync works with distinct exact linked receipts. Diagnostic exit 0.

New regressions cover failure/partial/rejected requests, valid and duplicate success, stale events after newer failure, failed same-attempt phases, wrong record/version/company/destination/attempt/prerequisite, out-of-order Sync, lost response/restart, revocation and supersession. Existing company isolation, owner/HQ, lifecycle, approval, source, budget, validity and SQLite crash diagnostics remain passing. See PHASE5_TEST_RESULTS.md for commands and results.

## Remaining limitations

Everything is SIMULATED / NON_PRODUCTION. No actual export, Obsidian Sync, Memory API or external acknowledgement is implemented. Explicit successful fake receipts are local test attestations, not independent production provider evidence. The fixed test destination is not a Linux vault mapping. Trusted local bootstrap/filesystem assumptions and production Memory/owner/credential/retention gaps remain unchanged. Failed/partial attempts require a new authorized request; no external same-attempt reconciliation transport is invented. No commits, pushes, deployments, real credentials or company data were used.
