# Phase 6 executed test results

All tests used synthetic temporary data, explicit test-only actors/adapters and deterministic clocks. No external networks, real company data, Linux services, live providers, Memory APIs, vault writes or actual messages.

## Full suite

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

**241 passed, 0 failures, 0 errors**, 21.916 seconds, exit 0. All 215 accepted prior tests remain unchanged; 26 new tests in `tests/test_workflow.py`.

Existing diagnostics remained successful:
- Each environment's large interrupted transaction: child exit 29, old SQLITE_READONLY_ROLLBACK reproduced, authorized recovery preserved two packet revisions/verdicts and retry state.
- Forged registration receipt diagnostic: child exit 30, no trusted registration or database/hot-journal mutation.
- Phase 4 validity conflict/negative expiration and Phase 5 bound export/Sync prerequisite regressions passed.

## Targeted suite

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_workflow.py' -v
```

**26 passed, 0 failures, 0 errors**, 9.065 seconds, exit 0. The full suite subsequently re-executed all these tests.

Coverage includes:
- GitHub Frontend → accountable lead/independent verifier → classification → submit/commit/promote/read → proposal-only CTO artifact → distinct ACK/FINAL fake delivery.
- All three companies' separate Memory/HQ partitions, authorized personal owner read, company owner denial and revocation/tombstone.
- Preserved partial HTML evidence and NMR gate; complete explicitly user-supplied article document. No raw HTML promotion is claimed.
- Inaccessible YouTube/Instagram/TikTok, rejected/NMR, budget/deadline exhaustion, memory commit/promotion failures and export request/export/Sync failures with honest short messages.
- Successful corrected export/Sync exact receipt link; generic Department proposal with no invented reader grant.
- All 12 ordered unequal environment pairs × 4 wrong caller/notice route/recipient attacks = 48 denials. Valid requester with forged environment claim and fabricated context also denied.
- Immutable message/fixture replay, one-source validation, 128,000-byte durable input limit and prompt injection containment.
- Justified supporting specialist and independent verifier identity; concurrent duplicate requests create one task/lifecycle and two logical notices.
- Accepted-but-undelivered transport remains pending even when workflow is complete; unavailable lookup never causes blind resend; three-send exhaustion creates no extra logical notice; forged final text/references or completion-bearing ACK rejected.

Crash-boundary subtests:
`intake_intent`, `intake_task`, `acknowledgment`, `source:effect`, `research:effect`, `verification:effect`, `intelligence:effect`, `memory_submit:effect`, `memory_commit:effect`, `memory_promote:effect`, `retrieval:effect`, `memory_hq_sync:effect`, `notification_prepare`, `notification_accept`, `notification_delivery`, `result`, `completion`.

Each restarts/reconstructs the coordinator and verifies one committed task, one six-operation company Memory/HQ lifecycle, two notifications and eventual fake delivery. Separate `transport_accept` and `transport_delivery` crashes reconcile durable receipts. An injected crash after a researcher output checkpoint proves restart does not call the researcher model again.

A fresh Python subprocess (exit 0, sockets blocked) restores synthetic registration only through trusted harness stdin, loads saved Intake/fixture bytes from the temporary project root, resumes after promotion, and confirms one lifecycle/two delivered notices. It receives no resupplied Research message/source fixture and creates no production trust.

## Development finding and preserved limitation

The first 19-test run had 18 passes and one failure: an integration test incorrectly expected ordinary HTML to complete. Inspection showed accepted WebsiteAdapter always records partial HTML extraction, and the accepted independent verifier deliberately returns NMR. The new test expectation was corrected to verify retained evidence and honest NMR; prior source/verification tests were not changed. A separate user_supplied article-document success test was added. Subsequent targeted runs passed 20, then 22, then 26 tests as coverage expanded. This records a capability limit rather than fabricating complete HTML investigation.

## Compilation and packaging

Executed standard-library in-memory compilation using `compile(path.read_bytes(), str(path), 'exec')` for all src/test Python files: **38 passed**, no bytecode emitted. `tomllib` assertions verified empty runtime dependencies, Python >=3.10, src discovery and workflow package initializer. Exit 0. No dependency installation or package build.

The proposed release inventory is SHA-256 review metadata only, unsigned and not deployed. Actual Linux identity, service, filesystem, provider, Memory and messaging acceptance remains pending.

## Targeted recovery correction — latest validation

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v`

**247 passed, 0 failures, 0 errors**, 26.448 seconds, exit 0. All 241 prior tests retained; six regression tests added.

Targeted command (with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests`):

```sh
python3 -m unittest -v test_workflow.WorkflowTests.test_recovered_sync_revalidates_before_and_after_checkpoint test_workflow.WorkflowTests.test_commit_outbox_gap_repaired_once_concurrent_restart test_workflow.WorkflowTests.test_missing_or_ambiguous_receipt_reconciliation_fails_closed test_workflow.WorkflowTests.test_noop_outbox_repair_is_not_completion test_workflow.WorkflowTests.test_revoked_sync_checkpoint_cannot_complete test_workflow.WorkflowTests.test_unchanged_sync_checkpoint_replays_idempotently test_workflow.WorkflowTests.test_successful_export_and_distinct_sync_receipts
```

**7 passed, 0 failures, 0 errors**, 2.514 seconds, exit 0. The original stale-Sync reproduction yields PARTIAL before and after checkpoint; no Sync-success text. The enqueue-crash reproduction preserves one original commit and repairs exactly one outbox event under concurrent recovery and duplicate restart. No-op or ambiguous reconciliation cannot complete. Revoked Sync is blocked; unchanged success remains idempotent.

Compilation using standard-library `compile()` over all source/test files: **38 passed**, no bytecode. `tomllib` assertions confirmed no runtime dependencies, Python >=3.10, and workflow package initializer; no build or install. Existing hot-journal diagnostics again reported child exit 29 and preserved committed history in all four environments; forged receipt diagnostic reported child exit 30 with no unauthorized mutation. All test data remained synthetic and temporary.

## Cached-result correction — latest final validation

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

**256 passed, 0 failures, 0 errors**, 36.449 seconds, exit 0. All 247 prior tests retained; nine new tests added.

Targeted execution: **12 passed, 0 failures, 0 errors**, 9.538 seconds, exit 0:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests python3 -m unittest -v \
  test_workflow.WorkflowTests.test_cached_result_failed_sync_all_environments \
  test_workflow.WorkflowTests.test_cached_result_revocation_and_supersession \
  test_workflow.WorkflowTests.test_cached_result_failed_hq_delivery \
  test_workflow.WorkflowTests.test_cached_result_promotion_invalid_without_export \
  test_workflow.WorkflowTests.test_cached_result_unchanged_concurrent_restart_one_final \
  test_workflow.WorkflowTests.test_delivered_final_is_not_rewritten_after_sync_failure \
  test_workflow.WorkflowTests.test_prepared_final_is_not_sent_after_sync_failure \
  test_workflow.WorkflowTests.test_cached_result_missing_ambiguous_reconciliation \
  test_workflow.WorkflowTests.test_completion_snapshots_deny_cross_environment_receipts \
  test_workflow.WorkflowTests.test_recovered_sync_revalidates_before_and_after_checkpoint \
  test_workflow.WorkflowTests.test_commit_outbox_gap_repaired_once_concurrent_restart \
  test_workflow.WorkflowTests.test_successful_export_and_distinct_sync_receipts
```

The new cached-result test exercises the exact failure in all four environments, checks that no FINAL exists before restart, appends a real FAILED Sync to the authorized attempt, verifies the new PARTIAL FINAL is actually delivered once, and compares the original checkpoint and full Memory transcript before/after. Revocation and genuine immutable correction/supersession invalidate current promotion, reads, export/Sync and HQ claims. A later failed HQ delivery is independently excluded. Concurrent unchanged restart forbids provider research/verification and Memory commit/promotion calls and still produces one FINAL. All 12 cross-environment receipt snapshots reveal no foreign data; a forged context is denied.

Already-delivered FINAL remains unchanged after later failure, while recovery returns a new immutable PARTIAL projection. A prepared but unsent obsolete FINAL is neither rewritten nor sent; even direct public replay is rejected. Missing, ambiguous or unresolved reconciliation gives PARTIAL with no claimed success receipts. No separate correction/update notification is claimed.

Exact independent diagnostic (temporary synthetic state, not the new test helper): before correction, a crash at `result` plus later FAILED Sync returned COMPLETED and a stale Sync claim. With the final correction it returns PARTIAL, delivers one corrected FINAL without Sync-success text, preserves historical COMPLETED and both receipts, leaves Memory history unchanged, and replays idempotently. Exit 0.

Compilation: 38 source/test Python files passed in-memory `compile()`, no bytecode. `tomllib` verified empty runtime dependencies, Python >=3.10 and src discovery. Exit 0; no installation/build. Original large-transaction diagnostics still report child exit 29 for all four environments, successful authorized recovery and preserved committed history; forged-registration diagnostic still reports child exit 30 and no unauthorized mutation.

Development-only validation exposed a missing notification bootstrap attribute after public replay validation was added (full run exit 1 with 65 reported errors). The wiring was corrected without weakening tests; subsequent full runs passed, including the final 256-test run above. All data remained synthetic and temporary; no live systems were contacted.
