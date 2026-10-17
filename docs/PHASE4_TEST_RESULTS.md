# Phase 4 executed test results

Executed locally, 2026-10-15, using synthetic temporary data only. No dependencies installed, services started, production access, commits or deployments.

## Full regression command

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Original implementation run (before validity correction): **177 tests, 177 passed, 0 failures, 0 errors**, 6.951 seconds, exit 0. Includes all original 162 tests unchanged and 15 new intelligence tests. An earlier final-candidate run also passed 177 tests in 6.934 seconds; final run includes the added conservative impact metadata and preserved source risks.

Existing crash diagnostics ran successfully inside the suite:
- Each of personal, gabos, fintra and sc_products: child exit 29, old read-only preflight reproduced SQLITE_READONLY_ROLLBACK; authorized SQLite recovery succeeded, with two committed packet revisions/verdicts and retry state preserved.
- Forged-receipt diagnostic: child exit 30; legacy/edited/fabricated JSON denied, database/hot journal unchanged and no trusted registration created.

## Targeted development command

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_intelligence.py' -v
```

15 tests passed, 0 failures/errors, 1.465 seconds. Final full-suite run re-executed these after the final source changes.

Coverage:
- Eleven specialist mappings, primary/secondary routing, six named non-development category routes, custom category validation and ambiguous-capability escalation.
- One record serving multiple simulated views; exact evidence/packet/source references; Memory ineligibility and production-view rejection.
- Two independently matched skills in one GitHub fixture, preserving paths, evidence and exact commit.
- Replay and exact-duplicate handling vs explicitly related distinct findings; changed replay inputs rejected.
- Correction history, supersession, expiry, expected-head validation and concurrent corrections (one winner, one stale rejection).
- Explicit conflicts exclude both sides and require escalation.
- Fault injection between catalog and outbox commits; concurrent replay repairs one event and preserves one batch.
- Fresh Python subprocess reads committed catalog/proposal history (child exit 0).
- All twelve ordered environment pairs deny foreign history, simulated distribution/views, proposals, status, processing and relationship writes. Unauthorized Researcher/Verifier processing fails.
- NEEDS_MORE_RESEARCH, REJECTED and changed packet digest cannot enter catalog.
- Generic department/profile proposal contracts cannot grant deployment, execution or approval authority.

Socket construction is blocked in the shared synthetic setup. No imported code executes. Existing source and workforce regression tests additionally exercise injection, unsafe paths, provider substitution, bounded budgets/rework and environment isolation.

## Compilation and packaging

Executed a standard-library Python check that compiled each `src/**/*.py` and `tests/**/*.py` in memory using `compile(path.read_bytes(), str(path), 'exec')`: **28 files passed**, exit 0; no bytecode emitted. Parsed `pyproject.toml` with tomllib and asserted dependency list empty, Python requirement >=3.10 and src package discovery. Package metadata checks passed. No wheel build or installation performed.

These are Mac-local offline acceptance results. They do not establish Linux filesystem durability, production specialist authorization, semantic accuracy, real Department approval or Memory integration.

## Validity correction — latest executed results

Required command re-executed after the final correction:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

**185 tests passed, 0 failures, 0 errors, 7.578 seconds, exit 0.** All previous 177 tests remain, with eight new validity regressions. Existing hot-journal diagnostics (child exit 29 in all four environments) and forged-receipt diagnostic (child exit 30) remain successful.

Eight added tests cover invalid/type/range/past expiration, the exact 2000→1001 conflict, identical-validity duplicates and expired replay, immutable Director-authorized validity revisions with unchanged verification/evidence, unauthorized/stale/changed-packet revisions, eight concurrent conflicting duplicate submissions, all four environments with cross-company revision denials, and no catalog provisioning for an expired initial request. Snapshot comparisons read SQLite directly and close connections, proving rejected requests leave catalog batches, audit rows and outbox rows unchanged. No existing tests were weakened or removed.

Exact independent reproduction also executed separately with `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src:tests python3` and temporary synthetic setup:
- Original expiration 2000; new-operation duplicate expiration 1001: raises `ValidityConflict: VALIDITY_CONFLICT: duplicate expiration differs; explicit VALIDITY_UPDATE required`.
- Duplicate expiration -1: raises ContractError (`expected bounded integer`).
- At time 1002: original expiration remains 2000, and original CURRENT status reflects that unchanged record; the conflicting operation was explicitly rejected. Catalog/audit/outbox snapshots remain identical.
- Diagnostic exit 0. The exact reproduction is also retained as an automated regression.

Final in-memory compilation re-executed: 28 Python files passed; standard-library TOML checks verified no dependencies, Python >=3.10 and src package discovery. Exit 0; no installation/build/bytecode emission.

An intermediate targeted run passed 22 tests before the eighth regression was added. Its new SQLite snapshot helper initially emitted unclosed-connection ResourceWarnings; it was corrected to explicitly close connections. Final full-suite execution passed without those warnings. An intermediate full run passed 184 tests before the final no-provisioning regression; the authoritative latest count is 185.
