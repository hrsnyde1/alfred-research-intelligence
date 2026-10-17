# Phase 1 correction report

## Latest correction: Director-only initial provisioning

This section supersedes the earlier Director/researcher provisioning exception and earlier 76-test counts. The first-use opening path previously let an issued researcher initialize a missing database and create an active recovery registration. Existing-file registration/replacement already required a Director.

The missing-file branch in `persistence.open_database` now requires an issued, same-environment Director context **before** `_initialize_new` can create a directory or file. `OfflineRegistrationAuthority._register_new` independently requires Director authorization before updating the ledger. No additional provisioning role is introduced. Existing-file registration and replacement retain their Director-only checks. Normal researchers and verifiers can open already provisioned, registered databases according to existing operation permissions. Receipts and request metadata cannot grant provisioning rights; production authorization remains disabled.

Exact files changed:

- `src/alfred_research/persistence.py`: Director-only missing-file provisioning.
- `src/alfred_research/registration.py`: Director-only initial ledger registration.
- `tests/test_foundation.py`: explicit Director provisioning helper and authorized foundation setup; the foreign/forged-context test retains a wholly empty root and its original assertion.
- `tests/test_corrections.py`: concurrent cold initialization uses Director provisioning, then retains concurrent researcher request/idempotency assertions.
- `tests/test_hot_recovery.py`: history fixtures explicitly provision through Directors.
- `tests/test_registration.py`: five added regressions covering all environments, Director provisioning/idempotence, researcher use after provisioning, researcher/verifier denial without filesystem or ledger effects, forged scope/context/registration rejection, and 32 concurrent unauthorized attempts. Existing researcher replacement, forged-receipt, isolation and recovery tests remain.
- `docs/PHASE1_CORRECTION_REPORT.md` and `docs/PHASE1_TEST_RESULTS.md`: authorization policy and actual results.

Validation executed:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -k large_packet -k forged_receipt -v
```

Full suite: **81 passed, 0 failures/errors**, 2.635 seconds. Targeted diagnostics: **2 passed, 0 failures/errors**, 0.475 seconds. Large-transaction children exit 29 in all four environments; committed history/verdicts/retry state survives and uncommitted changes roll back. Forged-receipt diagnostic child exits 30; recovery is denied with DB/journal/ledger unchanged. An initial adaptation run had one failure because newly authorized setup populated the root of an existing empty-root negative test; that test now retains unprovisioned setup and its original assertion. No assertions were removed or weakened.

Limitations remain unchanged: the injected registration authority is an in-memory test provider with trusted bootstrap/snapshot inputs, not production durable authorization. Linux credential storage, grants, permissions, authority durability and restoration are unverified. No schema migration, new service, dependency installation, production access, commit, push, deployment or Phase 2 work occurred.


Date: 2026-10-15. Status: recovery authorization corrected with an independent offline test authority; offline validation passed; awaiting owner review. Phase 2 has not begun.

## Current correction: independent recovery registration authority

This section supersedes all earlier receipt-only authorization descriptions and the 61-test results below. The earlier assumption that matching public JSON proved prior trusted registration was incorrect. Receipts are now untrusted references checked against a separately injected authority, not authorization evidence by themselves.

### Root cause and corrected trust boundary

The old receipt contained only predictable schema/environment/device/inode fields. A copied receipt edited to match a never-registered database could pass the equality check and authorize physical recovery before schema rejection.

`OfflineRegistrationAuthority` is an explicitly **in-memory test-only authority**, injected independently of database and receipt contents. Its private ledger records a random authority ID, per-environment epoch, random registration ID, registering principal, and complete identity: canonical database path, environment, schema version, device/inode and expected schema-manifest digest. Verification requires an exact match to the live ledger's current active registration. An edited or fabricated JSON file cannot add a ledger entry, replace its bound identity, activate a revoked entry, or change its epoch.

This implements the independently trusted registration-authority option; it does not use a cryptographic signing key. Random IDs are identifiers, not secrets or bearer authorization. No public-metadata-derived key, universal secret, real credential or external authority service was introduced.

The injected authority, issued contexts and bootstrap configuration are trusted. Untrusted source/model data must never construct the authority or supply its test snapshots. This remains a trusted-library boundary, not protection against arbitrary Python code able to mutate the injected authority object or against hostile OS-level file replacement. Production authorization is disabled; this is not a production security subsystem.

### Authorized creation, registration, replacement and opening

1. ResearchStore validates the issued environment/role context before disk access. Persistence additionally requires an explicitly injected OfflineRegistrationAuthority and a context accepted by that authority's identity provider. Its root permits only the intended `root/environment/research.sqlite3` path, rejecting database symlinks and paths outside that scope.
2. Authorized Director provisioning may initialize a genuinely absent Research database. Only the process that actually publishes the new file may register that newly initialized, fully validated identity. Initialization still uses schema v2 and no-overwrite publication. An authority lock serializes in-process creation and registration.
3. Existing databases are **never automatically registered**, even if read-only schema validation succeeds. `register_database(..., context=<issued director context>)` is the explicit registration entrypoint. It checks the director/environment/path authorization before reads, requires complete read-only schema validation and then records the registration in the independent ledger. Replacement requires the explicit `replace=True` flag and creates a new active registration ID. Old receipt replay is rejected.
4. Ordinary opens perform the existing read-only schema preflight. Unsupported cold files fail unchanged; the only read-only failure allowed to proceed toward recovery is SQLITE_READONLY_ROLLBACK. Both clean and hot files must present a receipt matching the live authority ledger before any writable opening. Missing, fabricated, edited, substituted, revoked or wrong-authority evidence fails closed with RecoveryRequiredError and `recovery_attempted=False`.
5. Once authorized, SQLite itself performs rollback-journal recovery under BEGIN IMMEDIATE. Full schema/environment validation and another authority check run under the write lock before returning a connection. ResearchStore then performs its application transaction and validation as before. No journal is manually replayed, ignored, removed or overwritten.
6. Post-recovery rejection remains explicit: RecoveryValidationError reports `recovery_attempted=True` and that the database may have changed. A previously registered file whose committed schema was changed in place can be physically recovered and then rejected. No claim of non-mutating rejection is made after writable recovery was permitted. No migration or application operation is authorized on failure.

Legacy receipt-only JSON cannot be adopted automatically. A clean compatible existing database needs explicit director registration; an already-hot unknown database cannot be registered by bypassing read-only validation. There is no unsafe recovery override.

### Loss, revocation, rotation and restoration policy

| Event | Offline behavior and production boundary |
|---|---|
| Authority/trust-state loss or replacement | Without the injected provider, or with a new empty/different authority, all old receipts fail closed. DB/receipt contents cannot reconstruct trust. Clean files may be explicitly re-registered by an issued director; unknown hot files need separate operator handling. |
| Registration revocation | A same-environment issued director removes the active mapping. Receipt replay remains rejected. Other company directors cannot revoke it. Revocation survives transfer of the current trusted test state. |
| Authority rotation | A same-environment director changes that environment's epoch and invalidates its active registrations. Other environments remain valid. Clean files need explicit new registration; hot files are not silently rebound. |
| Registration replacement | Explicit director authorization plus successful clean schema validation creates a new ID and invalidates the prior receipt. There is no automatic replacement from file contents. |
| Worker-process restart in tests | The parent harness sends its **current trusted authority snapshot via stdin** to the child and explicitly reconstructs the test provider. No registry or trust material is loaded from the DB directory, receipt, source content or model output. This tests surviving worker crashes while the authority remains available. |
| Backup restoration / entire authority-process loss | There is no production backup/import or durable authority implementation. Do not restore an old test snapshot as an authoritative production registry: that could roll back revocations. Production recovery eligibility after restore must require current independently trusted authority/revocation state, or a new epoch and explicit authorized registration. Missing/uncertain state must fail closed. |
| Cryptographic key loss/rotation | No cryptographic key is used by this test ledger. If Linux selects a keyed authority, key protection, loss, rotation and anti-rollback restoration must be separately verified before enabling it; no key can be derived from public identity fields. |

`test_only=True` is mandatory when constructing/reconstructing the fake authority. `ResearchStore(production=True)` and a production model configuration are rejected. Direct persistence/registration calls with `production=True` are also rejected. Missing trust does not fall back to receipt equality. Host grants, durable authority storage, credential protection, filesystem permissions and authoritative restore/revocation behavior remain Linux integration blockers.

### Exact files changed in this authorization fix

Created:

- `src/alfred_research/registration.py`: scoped independent in-memory test ledger, active registrations, revocation/epoch rotation, test-only trusted-state transfer.
- `tests/test_registration.py`: 15 focused authorization regressions, including the exact forged-receipt diagnostic.

Updated:

- `src/alfred_research/persistence.py`: mandatory independent authority checks; explicit director-only existing-file registration/replacement; no arbitrary existing-file auto-registration; untrusted receipt format 2 references; preserved SQLite-managed recovery and mutation reporting.
- `src/alfred_research/state.py`: injected registration authority/context on opening and explicit production disablement.
- `tests/test_foundation.py`, `tests/test_corrections.py`, `tests/test_hot_recovery.py`: inject test trust explicitly, transfer current trusted state to crash children over stdin, and assert explicit director registration for legacy clean files. The basic crash fixture now commits the initial task in the parent before crashing the child, so it does not pretend a child's lost in-memory authority survived. Existing durability, isolation, hash, budget and idempotency assertions remain.
- `docs/PHASE1_CORRECTION_REPORT.md`, `docs/PHASE1_TEST_RESULTS.md`, `docs/CONTRACT_GAPS.md`: current trust boundary, results and Linux blockers.

SQL persistence remains schema v2. Research packet/request/verdict schemas, model assignments, budget behavior and task transitions are unchanged. Only the local untrusted receipt format changes; receipt format 1 is not trusted or automatically migrated.

### Actual validation

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -k large_packet -k forged_receipt -v
python3 -m compileall -q src tests
```

Full result: **76 passed, 0 failures, 0 errors**, in **2.295 seconds**, Python 3.14.3 / SQLite 3.50.4. This is all prior 61 cases plus 15 new authorization regressions. The targeted diagnostics separately passed **2 tests**, 0 failures/errors, in **0.473 seconds**.

Large-packet crash children exit **29** in all four environments. The old read-only preflight still reproduces SQLITE_READONLY_ROLLBACK; independently authorized opening recovers through SQLite. Committed tasks, two revisions, exact historical verdict links and retry results survive; uncommitted revision/audit/retry changes roll back. The forged-receipt fixture exits **30** with a real hot journal; legacy matching JSON, an edited legitimate receipt, and fabricated format-2 JSON are all refused before writable recovery. Database/journal bytes and the independent ledger remain unchanged.

Compilation exited 0. TOML/AST checks passed for **12 Python files**; no runtime dependency was added. An initial harness adaptation run produced 8 errors because subprocess stdin was supplied as text without text mode. The harness was fixed to use `text=True`; assertions and socket guards were retained. The original 61 cases then passed, followed by all 76 and the targeted diagnostics. No unresolved failure remains.

### Remaining limitations

The authority is intentionally not durable across loss of its own process and is not a multi-process production registry. Test snapshots are trusted bootstrap fixtures, not authenticated backup files or untrusted import formats. Production restore, anti-rollback, cross-worker revocation and registry availability remain unimplemented and production mode remains disabled. Filesystem path/device/inode binding and epochs reject the demonstrated receipt substitution/replay cases, but hostile same-account modification, inode reuse, filesystem races, abrupt power loss and Linux storage guarantees are not claimed. No Phase 2 work, service, dependency installation, real credential access, vault access, Linux change, commit, push or deployment occurred.

## Historical correction: hot rollback-journal recovery

The following records the preceding implementation and its 61-test validation. Its receipt-only trust assumption and clean-file auto-registration policy are superseded by the independent authority above.


This section supersedes earlier descriptions of an unconditional read-only preflight and earlier 51-test results, including those in PHASE1_IMPLEMENTATION_REPORT.md. It is limited to the last blocking persistence defect.

### Confirmed root cause

SQLite SELECTs against a database with a hot rollback journal require SQLite to roll back the interrupted transaction first. Rollback needs a writable database connection. The old `mode=ro` schema SELECT failed with `SQLITE_READONLY_ROLLBACK` before the writable connection could be reached. Small crash fixtures did not force dirty-page spill; an accepted packet with 500 claims of 8,000 characters each does. The automated regression executes the original read-only sequence against the crashed fixture and observes the original failure, then successfully opens the same file through corrected code.

### Exact database-opening sequence and policy

1. ResearchStore authorizes the issued context, role and requested environment before calling persistence. The root and grants remain trusted bootstrap inputs.
2. If the database file is genuinely absent, initialize schema v2 transactionally in the existing same-directory staging path and publish without replacement. Existing files are never recreated, reset or migrated.
3. Attempt complete SELECT/PRAGMA-only validation on a `mode=ro` connection: schema metadata, expected environment and exact schema manifest. Unsupported cold files fail here without a writable open or identity receipt creation. Close the probe.
4. After successful read-only validation, create or verify `research.sqlite3.identity.json`. This receipt records receipt format 1, last-validated schema version 2, environment, filesystem device/inode and expected-manifest digest. It is written privately, fsynced and published without replacement. Existing receipts must match the exact generated JSON; malformed, duplicate-key, stale or mismatched receipts fail closed. This adds a local sidecar, not database DDL or a schema migration.
5. Only the specific SQLite exception name `SQLITE_READONLY_ROLLBACK` permits the recovery path when preflight could not complete. Require an already-existing matching identity receipt; never invent/register identity from a hot unreadable file. Missing/mismatched identity raises RecoveryRequiredError with `recovery_attempted=False`. Other SQLite errors do not authorize a recovery write.
6. For a verified clean file or a recognized hot file, open `mode=rw`, enable foreign keys/FULL synchronization, and execute BEGIN IMMEDIATE. Let SQLite perform its normal journal recovery and locking; do not read around the journal, use immutable/nolock URI options, remove/rename journals, parse/replay journal pages, or restore the main file manually.
7. Under the write lock, validate the complete recovered schema/environment again and verify file identity. Commit the validation-only transaction and return the connection. ResearchStore then starts/revalidates its application transaction as before. Application reads, writes and audit operations start only after compatibility/authorization succeeds.
8. Any validation/open error after a writable opening was permitted raises RecoveryValidationError with `recovery_attempted=True` and an explicit message that the database may have changed. Its original cause is retained. Rolling back this validation transaction cannot undo SQLite's already completed recovery. No application migration, repair or operation is authorized on failure.

### Explicit trade-off and fail-closed cases

The prior implementation incorrectly assumed that matching receipt JSON proved trusted code had validated that environment/schema/file identity; it does **not** prove the current recovered schema or protect against hostile OS-level modification. Recovery can be necessary before current compatibility is knowable. For a registered file, this policy authorizes SQLite recovery followed by mandatory validation. If an administrator changed the same registered file in place to an incompatible version, recovery may restore its committed incompatible state and remove the journal before rejection. The error explicitly reports possible mutation; **non-mutating rejection is not guaranteed on this path**. A regression demonstrates this with committed schema version 999: SQLite rolls back uncommitted changes, version 999 remains, no migration/application audit occurs, and RecoveryValidationError reports the recovery permission.

Unregistered or identity-mismatched hot files are ambiguous and are refused without recovery writes. Tests preserve the main file, journal and receipt byte-for-byte, including an incompatible hot database whose dirty metadata misleadingly claims version 2. A compatible v2 file created before receipts existed can register during a clean, fully validated open; an already-hot legacy file without a receipt needs separate operator review. This run implements no manual recovery/registration override. Schema v1 is still unsupported and never migrated.

### Exact files changed for this last defect

- `src/alfred_research/persistence.py`: local identity receipt and SQLite-managed, guarded recovery/opening sequence; explicit RecoveryRequiredError and RecoveryValidationError. The SQL schema, public state API, model assignments and budgets are unchanged.
- `tests/test_hot_recovery.py`: 10 new automated hot-journal, policy and concurrent-recovery regression methods.
- `tests/test_corrections.py`: cold-initialization inventory now requires exactly the database and identity receipt, with no leaked staging files. All original assertions for schema non-mutation/isolation remain.
- `docs/PHASE1_CORRECTION_REPORT.md`: this policy, results and limitations.
- `docs/PHASE1_TEST_RESULTS.md`: latest executed counts and requirement mapping.

### Executed final validation

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v`: **61 passed, 0 failures, 0 errors**, in **1.836 seconds**, on Python 3.14.3 / SQLite 3.50.4. This includes all prior 51 cases plus 10 new methods. The large-packet child exits **29** in every environment and in the concurrent-recovery test. Before corrected opening, the legacy read-only probe raises SQLITE_READONLY_ROLLBACK and leaves bytes unchanged. After corrected opening, SQLite recovers successfully; two committed revisions, their exact historical verdicts, task state and committed retry result survive. The uncommitted third revision, audit event and retry-counter increment do not survive. Eight concurrent openers also recover/read the same committed state safely.

Other policy fixtures exit **30** after large raw SQLite DML transactions. They prove ambiguous-hot non-mutation and explicitly disclosed recovery-then-rejection for a previously registered but now unsupported file. Child exit 29/30 is intentional fault injection, not a failing test.

`python3 -m compileall -q src tests` exited 0. Standard-library TOML/AST checks passed for 10 Python files; Python >=3.10 and zero runtime dependencies remain declared. An early new-fixture run had four failing environment subcases because importing the unittest fixture after the child socket guard attempted to define SSL classes. The child now imports only the package and obtains its committed packet through the authorized API; guards and assertions were preserved. No unresolved failure remains.

### Remaining recovery limitations

- Receipts are trusted local metadata, not credentials, signed attestations or a security boundary against an account able to rewrite both files. They do not extend company permissions or authorize application operations before full validation.
- Moving/copying/restoring the database changes filesystem identity. A copied/stale receipt is rejected; a missing receipt can be established only after a clean compatible read-only validation. Already-hot unregistered files need separately authorized operator handling. Do not remove journals to make registration succeed.
- Receipt publication uses the same hard-link-capable filesystem as existing initialization. File data is fsynced, but directory fsync/power-loss guarantees and Linux backup/restore procedures remain unverified. Losing a receipt fails closed.
- SQLite must expose the specific extended exception name for automatic recovery authorization. On a runtime without that diagnostic (including potentially Python 3.10), the error fails closed rather than relying on error-message guessing. Only Python 3.14.3 / SQLite 3.50.4 was executed here.
- Rollback-journal recovery is tested, including process death and concurrent reopen. WAL, multi-database/super-journal recovery, hostile concurrent file replacement and abrupt power loss are not validated. Do not infer production guarantees from these local tests.
- No Phase 2 adapters, credentials, external services, live databases, commits, pushes or deployments were involved.

## Original correction history: exact files changed

Updated:

- `src/alfred_research/contracts.py` — added immutable, validated `RetryOperation` record with original task result.
- `src/alfred_research/state.py` — immutable packet revisions and current-head operations; exact-revision verdict linkage and historical reads; replay-safe retry and result lookup; corrected schema-opening path and explicit storage-error handling.
- `tests/test_foundation.py` — extracted shared setup/helpers into `FoundationFixture`; retained all 31 original test methods and assertions; explicit retry calls now provide stable logical IDs.
- `docs/PHASE1_IMPLEMENTATION_REPORT.md` — corrected functionality, interfaces, validation and compatibility limits.
- `docs/PHASE1_TEST_RESULTS.md` — current results and correction coverage mapping.
- `docs/CONTRACT_GAPS.md` — schema-version, retry identity, history and filesystem integration notes.

Created:

- `src/alfred_research/persistence.py` — schema v2 initialization/validation, immutable-record triggers, exact decision foreign keys and storage exceptions.
- `tests/test_corrections.py` — 20 regression test methods.
- `docs/PHASE1_CORRECTION_REPORT.md` — this report.

No other source/configuration/handoff files were changed. Compilation generates ignored local Python caches. All test state uses temporary directories and synthetic principals/data; no production data is imported or migrated.

## Root causes and corrections

### 1. Historical packets

Root cause: task ID was the packets table's sole primary key, and revision writes used INSERT OR REPLACE. Old canonical content was destroyed while old verdict hashes remained.

Correction: packets are append-only rows keyed by task/version, storing packet ID, environment, canonical JSON and SHA-256 digest. A separate head table identifies current content. SQL triggers reject UPDATE/DELETE of packets and decisions. Verdicts use a composite foreign key to exact task/version/digest/environment. History access validates row/body/digest consistency and authorizes the caller's environment.

BEGIN IMMEDIATE serializes competing revisions; the next version and stable packet identity are checked, and head advancement uses the prior version as a condition. Identical revision replay returns its original digest, including after a newer revision or terminal approval, without changing the head/state/audit. Conflicting content for an existing version, skipped versions, or new content on terminal tasks is rejected. Packet insertion, head update, task-state update and audit commit atomically. An old verdict cannot approve the revised head.

Tests cover all four environments, historical retrieval/verdict links after restart, exact canonical stored content, concurrent duplicate/conflicting writes, stale updates, SQL immutability, invalid linkage and rollback.

### 2. Unsupported schemas

Root cause: CREATE TABLE and metadata insertion ran before schema validation and outside the application transaction.

Correction: persistence schema v2 separates initialization from opening. Existing databases undergo SELECT/PRAGMA-only read-only preflight, checking metadata version/tenant and the complete schema manifest. Unsupported, malformed, empty and corrupt files fail explicitly without schema repair or migration. Compatible databases are revalidated under BEGIN IMMEDIATE before application writes. Database/file failures raise PersistenceError with the original cause; unsupported layouts raise UnsupportedSchemaError. Authorization/budget/contract errors preserve their established types.

A genuinely missing database is initialized transactionally in private same-directory staging and published by a no-overwrite hard link. A concurrent winner is validated, never replaced. Existing v1 databases are left intact and rejected: the corrected v2 layout is intentionally incompatible, and no implicit migration is authorized. The tests demonstrate compatible v2 state remains intact.

Regression snapshots compare file bytes, SQL dumps, sqlite_master objects, schema_version, user_version and application_id before/after repeated opening attempts. Fixtures contain preserved rows, an index, a view and a trigger. Cold concurrent initialization, compatible-file reopen, corrupt/empty files and database-tenant mismatch also pass.

### 3. Retry replay

Root cause: retry had no logical operation identity; every invocation incremented the allowance and appended an audit event.

Correction: `retry(context, task_id, retry_id)` requires a caller-persisted ID. IDs are unique per environment and bound to task and requesting principal. The operation and its original DurableTask result are immutable durable records. Task increment, result insertion and audit append occur in one transaction. Sequential, concurrent and restarted replay returns the recorded result before checking current task state or remaining allowance; it produces no repeated audit/outbox effect and cannot roll back live task state. A genuinely new ID consumes one allowance. Conflicting IDs, missing/blank IDs and new retries after exhaustion fail closed. `get_retry` exposes the authenticated historical result.

Tests include concurrent duplicates, sequential replay across all environments, later state changes, exhaustion, conflicting principals/tasks, transaction rollback, and child-process crashes before commit and after commit/before response. Each crash scenario finishes with one operation, one increment and one retry audit event.

Automatic rework accounting remains bounded as before: packet revisions have durable version identity, and state transitions use expected-state validation. Those operations cannot double-spend the allowance through an identical replay.

### 4. Isolation coverage

Root cause: prior negative tests emphasized task get/transition; other operation boundaries lacked direct cross-environment assertions.

Correction: a matrix covers every unequal pair among Personal Alfred, Gabos, Fintra and SC Products (12 pairs). It attempts foreign task reads/transitions, packet writes/current/historical reads, decision writes/history, retries/results, outbox enqueue/delivery and budget settlement. Rewritten attacker-local payload scopes cannot make foreign task IDs local. Audit/outbox/recovery listings return only the authenticated environment. A reservation ID reused in another environment affects only that environment's ledger. Each matrix pair snapshots the target database and proves no mutation to its bytes, rows or schema.

### 5. Focused forgery test

Root cause: the previous payload-forgery case changed requester and environment simultaneously, allowing requester validation to hide the environment check.

Correction: a new test holds the valid issued principal/role and requester constant while claiming a different environment. All 12 unequal environment pairs are rejected by authorization; no database is created.

## Executed validation

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 -m compileall -q src tests
```

Historical pre-hot-journal-correction full-suite result: **51 tests passed, 0 failures, 0 errors**, in **0.914 seconds**, Python 3.14.3. This comprises all 31 original cases and 20 correction cases. Compilation exited 0. A standard-library TOML/AST check passed for 9 Python files and confirmed Python >=3.10, no runtime dependencies and the unchanged build backend.

During development, the first changed-source run had 1 failure and 8 errors: the broader storage-error wrapper intercepted PermissionError-derived authorization exceptions, and URI construction lazily imported networking classes under the socket guard. Those implementation issues were corrected without weakening tests; database connections were also explicitly closed. The original suite then passed, followed by the expanded 50-test suite and final 51-test suite. No unresolved test failure remains.

No wheel build, installation, Linux inspection, real-provider call or external service check was performed. No new dependency was installed.

## Remaining limitations and compatibility

- Schema v1 files are not automatically upgraded. They must remain untouched until a separately reviewed import/migration is authorized. Packet content already overwritten by the earlier implementation is not recoverable from its digest alone.
- Retry callers must adopt the new required ID argument and preserve that ID across retransmission. Replay returns a historical operation result; current task state requires a separate authorized read.
- Immutable history is logical/application and SQL-trigger protection, not a security boundary against a hostile OS account able to replace a database or drop triggers. Authority/grants/root/model configuration remain trusted offline bootstrap inputs.
- Atomic initial publication requires same-directory hard-link support. Linux filesystem locking, abrupt power loss, service users, encryption, backups and deployment permissions remain unverified. Existing-file schema validation performs no application repair; see the latest recovery policy above for explicitly permitted SQLite rollback writes.
- Internal wire contracts remain v1; no Linux API or production model assignment is inferred. Python >=3.10 is declared; only Python 3.14.3 has positive execution evidence here.
- Audit timestamps/signatures/retention, real usage billing, external delivery attempt reconciliation, Memory promotion, HQ synchronization, Photon/Hermes routing and CTO intake remain deferred. No external exactly-once delivery claim is made.
- Phase 2 source locators/fetched snapshots and bounded adapters remain unimplemented. Live agents and later integration milestones remain unchanged.

No credentials/vaults/existing Alfred systems were accessed; no service was started, and nothing was committed, pushed or deployed. Stop for owner review.
