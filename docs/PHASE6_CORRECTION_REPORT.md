# Phase 6 targeted recovery correction

## Scope and root causes

Only the two demonstrated Phase 6 recovery defects were corrected. No Phase 7, live integrations, dependencies, credentials, deployments or Git operations were introduced.

A: `ResearchWorkflow._memory_step` returned historical transcript receipts, or immutable flow checkpoints, without applying the Memory adapter's current export/Sync attempt checks. A later FAILED receipt could therefore leave an older SUCCESS in the completion message.

B: Memory transcript commit and SQLite outbox enqueue are separate durable writes. A crash between them left a real commit receipt without its required outbox event. The coordinator's receipt lookup bypassed the adapter's existing replay repair path.

## Corrections

`FakeMemoryAdapter.reconcile_receipt` authenticates the Director and receipt environment/actor, locks the intelligence catalog followed by the Memory transcript, requires an exact existing historical event and candidate identity, and reuses Phase 5 export/Sync binding and live-record checks for successful completions. Later failed/partial attempts, different attempts, revocation and supersession cannot authorize a cached current completion. Historical events remain unchanged.

The same operation repairs only the original event's deterministic outbox identity, then reads back and validates its task, environment, topic and event digest. Delivered-state/retry metadata may differ; the operation identity may not. It does not call commit again or manufacture a new receipt. Existing SQLite enqueue idempotency and transaction boundaries prevent concurrent duplicate effects.

The coordinator reconciles before writing a new Memory stage checkpoint and again whenever accepting a cached stage. Missing or mismatched reconciliation fails closed. Delivery ambiguity and persistence errors yield explicit incomplete PARTIAL/BLOCKED results. Invalid recovered Sync success is omitted from the current result, so the final notification cannot claim Sync completion.

## Exact files changed

- `src/alfred_research/memory/fake.py`
- `src/alfred_research/workflow/coordinator.py`
- `tests/test_workflow.py`
- `docs/PHASE6_IMPLEMENTATION_REPORT.md`
- `docs/PHASE6_TEST_RESULTS.md`
- `docs/PHASE6_MAC_ACCEPTANCE_MATRIX.md`
- `docs/PHASE6_CORRECTION_REPORT.md` (new)
- `docs/PHASE6_RELEASE_INVENTORY.json` (local review hashes refreshed; not transferred)

## Regression evidence

Six new tests cover later FAILED Sync before and after checkpoint; revocation after checkpoint; commit enqueue interruption followed by concurrent recovery and duplicate restart; missing/ambiguous reconciliation; a no-op outbox repair; and unchanged successful Sync replay. Existing successful request → export → Sync remains passing.

Original A reproduction: crash at `memory_sync_status:effect`, append FAILED Sync for the same attempt, restart. Result is PARTIAL with no Sync-success claim. Repeating at `memory_sync_status` after checkpoint gives the same safe result; old success and later failure remain in history.

Original B reproduction: crash in enqueue of `offline.memory.commit` after the Memory event is durable. Before restart there is one commit and zero matching outbox events. Two concurrent recovery callers plus repeated restart produce one commit, exactly one matching outbox event, and COMPLETED only after reconciliation succeeds.

Required full suite: **247 passed, 0 failures, 0 errors**, 26.448 seconds, exit 0; all 241 prior tests retained. Targeted diagnostics: **7 passed**, 0 failures/errors, 2.514 seconds, exit 0. In-memory compilation: **38 Python files passed**; package metadata checks passed. No installation or bytecode writes.

## Remaining limitations

All operations and receipts remain SIMULATED / NON_PRODUCTION. The two-store boundary is reconciled idempotently, not claimed to be one atomic transaction. A repair that cannot be confirmed produces an incomplete result; no automatic unbounded retry is introduced. Immutable already-finalized task notifications remain historical observations, not fresh knowledge retrieval. Actual Linux delivery/receipt reconciliation and credential boundaries remain unverified. Existing partial HTML/NMR and absent non-development retrieval grants remain unchanged. No Memory, Obsidian, Photon, Hermes, provider or Linux service was contacted.

## Cached final-result recovery correction

The later independent review reproduced a third bypass: `run()` loaded the immutable `packet:result` and sent FINAL without entering `_process` or receipt reconciliation. A crash at `result` left COMPLETED durable but no FINAL prepared. A later FAILED Sync for the same attempt was followed by a newly sent stale success message. This was reproduced before editing: COMPLETED with “Obsidian Sync receipt recorded.”

### Exact implementation changes

- `src/alfred_research/workflow/coordinator.py`: trusted bootstrap binds the notification Memory boundary. `_finalize` reconciles completion-bearing receipts even when the original result is cached. It records immutable `packet:final-result:<digest>` projections, retaining `packet:result` unchanged. Invalid or unresolved receipts produce PARTIAL/INCOMPLETE and are excluded from current completion claims. It never reruns research, verification, commits, promotions or retrieval operations. Stable notice identity is retained. If a previously prepared notice differs, it neither rewrites nor resends/confirms that notice.
- `src/alfred_research/memory/fake.py`: shares exact historical receipt/outbox validation through a private locked helper. Current promotion and granted specialist retrieval require live, promoted knowledge. HQ requires live promoted origin, current successful eligibility and the matching latest successful HQ delivery. Existing export/Sync prerequisite and latest-attempt checks remain intact. `completion_snapshot` holds catalog and Memory locks through fake FINAL preparation/delivery so concurrent invalidation cannot race that boundary. Only existing receipts are returned; no new success or fresh retrieval receipt is created.
- `src/alfred_research/workflow/notifications.py`: FINAL requires an immutable authorized reconciled projection with matching original task, conversation, requester, record, proposals and historical receipt references. Public FINAL replay also revalidates current receipts, including an obsolete prepared notice. Internal delivery from `_finalize` uses the already-held snapshot. ACK is unchanged.
- `tests/test_workflow.py`: nine new tests (no prior test removed or weakened).
- `docs/PHASE6_CORRECTION_REPORT.md`, `docs/PHASE6_TEST_RESULTS.md`, `docs/PHASE6_MAC_ACCEPTANCE_MATRIX.md`: current correction evidence.
- `docs/PHASE6_RELEASE_INVENTORY.json`: refreshed local integrity hashes/test counts only; no transfer or deployment.

### Regression scope and observed recovery

The new tests exercise all four environments for the exact cached COMPLETED → later FAILED Sync → restart path, preserve the original result and complete success/failure history, and verify one corrected PARTIAL FINAL is delivered. Other tests cover revoked and genuinely superseded records; failed later HQ delivery; invalid promotion without export; three concurrent unchanged recoveries with exactly one FINAL; an already delivered FINAL followed by failure; an obsolete prepared/unsent FINAL rejected even through public notification replay; missing, ambiguous and unresolved reconciliation; all 12 unequal-environment receipt snapshot pairs and a fabricated authenticated context.

The unchanged concurrent test forbids researcher/verifier provider calls and Memory commit/promotion calls during recovery. All remain uncalled. The earlier two crash-recovery reproductions remain enabled and passing.

Independent after-fix diagnostic recreated the exact original sequence without invoking the new regression helper: result is PARTIAL, no Sync-success claim, exactly one corrected FINAL delivered, original COMPLETED checkpoint intact and Memory history unchanged. Replaying the recovery remains idempotent.

### Remaining limitations

No separate correction/update notification contract is introduced. An already prepared, accepted/ambiguous or delivered FINAL remains immutable. If current reconciliation changes its content, recovery returns and durably records the corrected result but does not overwrite, resend or confirm the obsolete notice. An unsent obsolete outbox entry remains pending for explicit future reconciliation; the public simulation sender refuses stale receipts. Already delivered historical messages cannot be retracted. This is reported as a limitation, not claimed as correction delivery.

Currentness locking and receipts are test-adapter semantics only. Real transport cancellation, authoritative Linux Memory receipt lookup, credential/owner authorization and delivery/update contracts remain unverified. No production service, vault, provider or Linux host was accessed. No Phase 7 work occurred.

### Final executed validation for cached-result correction

- Required full suite: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v` — **256 passed, 0 failures, 0 errors**, 36.449 seconds, exit 0. All 247 prior tests remain passing; nine new tests added.
- Targeted diagnostics: **12 passed, 0 failures, 0 errors**, 9.538 seconds, exit 0. Command: `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests python3 -m unittest -v` followed by the twelve `test_workflow.WorkflowTests` methods listed in the latest test-results section.
- Exact independent before-fix reproduction: COMPLETED and stale Sync-success text. Exact after-fix reproduction: PARTIAL, no Sync-success text, one delivered corrected FINAL, historical COMPLETED retained, unchanged Memory history and idempotent replay.
- Standard-library in-memory `compile()` over all source/test Python files: **38 passed**. `tomllib` checks: no runtime dependencies, Python >=3.10 and src package discovery all passed. No bytecode, build or installation.
- Development validation history: the first correction version passed 256 tests. Adding public notification replay validation temporarily exposed a missing bootstrap attribute (full run exit 1, 65 reported errors; targeted run exit 1). Initializing that attribute corrected the wiring without changing test expectations. Subsequent full runs passed 256 tests; the final counts above refer to the exact final source.
