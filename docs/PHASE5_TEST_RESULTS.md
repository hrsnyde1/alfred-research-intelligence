# Phase 5 executed test results

All data and identities were synthetic and temporary. No dependencies installed, real Memory/vaults accessed, services contacted, commits/pushes or deployments performed. These are Mac-local offline test results, not Linux operational acceptance.

## Full required suite

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Original implementation run (before export correction): **208 tests passed, 0 failures, 0 errors**, 11.688 seconds, exit 0. All 185 accepted Phase 0–4 tests remain unchanged; 23 Phase 5 tests were added in `tests/test_memory.py`.

Existing diagnostics remained successful:
- All four environments: large-transaction crash child exit 29; original SQLITE_READONLY_ROLLBACK failure reproduced; authorized SQLite recovery preserved two committed revisions/verdicts and retry state.
- Forged-receipt diagnostic: child exit 30; forged/edited receipts denied without database/hot-journal mutation.
- Phase 4 validity reproduction: 2000→1001 explicitly conflicts, -1 denied, original history remains unchanged.

## New acceptance coverage

| Evidence | Executed coverage |
|---|---|
| Independent environments | Four complete fake lifecycles; 12 ordered unequal pairs × 14 foreign operations = 168 denials |
| Exact approval/provenance | Embedded Research source/packet/decision, canonical record digest, independent verifier, forged/changed candidate rejection; rejected/NEEDS_MORE_RESEARCH constructor rejection |
| Lifecycle separation | Candidate, commit and promotion receipts distinct; commit alone cannot retrieve; new independently authorized retrieval returns RETRIEVABLE with citations |
| Production boundary | Fake constructor rejects non-test/production mode; production relabeling/Memory eligibility rejected |
| Specialist access | Personal and Fintra specialists retrieve only explicitly granted matching categories/classifications; association-only and restricted classification grants denied |
| Protected owner | Explicit personal owner reads each permitted company partition; company Directors, reissued lookalikes, fabricated environment/company labels and absent owner grants denied |
| HQ eligibility | No default copy eligibility; disallowed record produces tombstone, not HQ_SYNCED; fresh owner retrieval denied |
| Evolution | Exact Research correction relationship and promoted replacement required; old current/HQ retrieval blocked, old tombstone applied, new separately authorized version retrievable, history preserved |
| Retraction/freshness | Delete, revoke, expiry and dispute block current specialist/HQ reads; revoked/sync race remains fail-closed |
| Concurrency/replay | Concurrent duplicate commits have one effect; stale/out-of-order operations denied; concurrent distinct delete/revoke updates have one winner |
| Ambiguity/restart | Timeout after immutable commit raises DeliveryAmbiguous; replay/reconcile repairs missing outbox insertion without duplicate; injected enqueue exception also recovers |
| Fresh process | Subprocess exit 0 restores synthetic registration through trusted harness stdin, replays COMMITTED receipt, promotes and freshly retrieves cited knowledge; sockets blocked in worker |
| Export versus Sync | Separate request/export/Sync receipts; missing prerequisites rejected; partial export and failed Sync recorded honestly; no Markdown files created |
| Audit/no real systems | Receipt transcript retains environment/actor/operation/outcome; setup blocks sockets; no live adapter or vault writer exists |

The 14 foreign operations per unequal pair are submit, history, specialist retrieval, commit, promote, revoke, delete, export request, export status, Sync status, HQ eligibility, HQ sync, expiration and supersession. Owner retrieval is tested separately because the explicitly authorized personal-owner exception is intentional.

## Targeted development runs and corrected harness error

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_memory.py' -v
```

An initial 17-test targeted run passed (3.406 seconds). After expanding coverage, a 22-test run had one harness AttributeError from calling `test_snapshot` instead of the existing `snapshot_for_tests`; this was corrected without removing or weakening tests. The following targeted run passed all 22 tests (3.946 seconds). Additional assertions, classification denial and fresh-process retrieval were then verified by the final 208-test full suite. Intermediate full runs passed 207 tests (11.506 and 11.573 seconds); the final count is 208.

## Compilation and package metadata

A standard-library Python command compiled every `src/**/*.py` and `tests/**/*.py` with `compile(path.read_bytes(), str(path), 'exec')` in memory: **33 files passed**, exit 0, no bytecode emitted. `tomllib` checks verified empty runtime dependencies, Python >=3.10, src package discovery and the new memory package initializer. No installation or wheel build performed.

Live Memory acceptance, production credential boundaries, real Obsidian export/Sync, durable external receipts and actual Linux HQ partition isolation remain unverified integration requirements.

## Export receipt correction — latest results

Executed the required full command again:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

**215 passed, 0 failures, 0 errors, 13.240 seconds; exit 0.** All 208 previous tests remain, with seven new export correction regressions. The existing partial-export/failed-Sync recovery test now explicitly creates new authorized requests; its original failure/separation assertions remain. No tests removed or weakened.

Targeted command `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_memory.py' -v` passed **30 tests**, 0 failures/errors, 5.644 seconds, exit 0. A preceding compatibility run passed all 23 previous Memory tests after updating explicit attempt bindings.

New tests prove:
- FAILED/PARTIAL request completion and Sync are denied; rejected outcome metadata is rejected. Denials append no completion events.
- Successful request/export/Sync link distinct exact receipts and replay without duplicate events.
- Old completion/sync replays cannot override a newer failed request, nor can old export success override a later failed completion in the same attempt.
- Wrong record, digest, version, destination, attempt, prerequisite receipt and company are rejected; Sync cannot reference the request receipt in place of EXPORTED.
- Lost request response followed by adapter restart/reconciliation establishes only EXPORT_REQUESTED; Sync remains denied until a valid export completion exists.
- Revoked and Research-superseded knowledge reject delayed completion/replay.

Independent reviewer reproduction rerun using temporary synthetic data through `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests python3`:

```text
export_status DENIED: successful export request required
sync_status DENIED: successful export request required
Authorized sequence: EXPORT_REQUESTED -> EXPORTED -> SYNCED ; all SIMULATED / NON_PRODUCTION
```

Diagnostic exit 0. It also asserted no new transcript events after the rejected completions, and checked exact request→export→Sync receipt references in the successful sequence.

Final source compilation/metadata command passed: 33 Python files compiled in memory, no bytecode; dependency-free src package and Python >=3.10 metadata verified; no build/install. Existing all-environment hot-journal diagnostics (child exit 29), forged-receipt diagnostic (child exit 30), 168 cross-environment denials, HQ/owner authorization and Phase 4 validity regressions remain passing in the full suite.
