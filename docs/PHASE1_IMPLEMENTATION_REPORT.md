# Phase 1 implementation report

Date: 2026-10-15. Status: offline foundation corrected after independent review and tested; awaiting owner review. No Phase 2 work or Linux integration was performed. All schemas are internal Research contracts, not production interface claims.

## Files changed in this phase

Created:

- `pyproject.toml` — src-layout packaging metadata, Python >=3.10, no runtime dependencies; setuptools build backend declaration only.
- `src/alfred_research/__init__.py` — package/version.
- `src/alfred_research/contracts.py` — immutable versioned contracts, strict decoding, canonicalization and digests.
- `src/alfred_research/tenancy.py` — trusted offline principal grants and issued-context authorization.
- `src/alfred_research/budgets.py` — fixed model configuration, production fail-closed behavior and escalation exception.
- `src/alfred_research/state.py` — environment-partitioned SQLite transactions, tasks, audits, immutable packet history and current heads, exact-revision decisions, replay-safe retries, outbox and resource reservations.
- `src/alfred_research/persistence.py` — schema v2, read-only existing-file validation, complete new-file initialization and explicit storage errors.
- `src/alfred_research/verification.py` — independent-principal and exact-content decision validation.
- `tests/test_foundation.py` — all 31 original offline acceptance cases retained; shared fixture extracted and retry calls supply stable IDs.
- `tests/test_corrections.py` — 20 regression cases covering the five correction requests.
- `docs/PHASE1_IMPLEMENTATION_REPORT.md` — this report.
- `docs/PHASE1_TEST_RESULTS.md` — executed results and acceptance mapping.
- `docs/PHASE1_CORRECTION_REPORT.md` — correction root causes, exact changed files, interfaces and regression results.

Updated: `docs/CONTRACT_GAPS.md`, with Phase 1 discoveries. Existing Phase 0 audit/plan, downloaded handoffs and `.gitignore` are unchanged. Python checks generate ignored `__pycache__` files locally. Test databases live only in temporary directories and are cleaned up by the tests.

## Implemented functionality

Contracts validate field types (including rejection of boolean-as-integer), supported schema/version, bounded strings/collections, known environments, source cardinality, nested tenant consistency, unique evidence identities, evidence references, classifications and verdicts. Frozen records use tuples for nested collections. JSON decoding rejects unknown/missing fields and duplicate keys. Source, task, packet, claim, evidence, assignment, budget, audit and outbox records carry environment ownership.

The synthetic environment keys are `personal`, `gabos`, `fintra`, `sc_products`; these are local aliases, not production tenant IDs. OfflineAuthority accepts trusted bootstrap grants and issues immutable in-process context capabilities. Reconstructed, altered or foreign-authority contexts are rejected. Store operations check issued context, environment and role; every environment uses its own `research.sqlite3` file. Company actors have no cross-environment read/write path or HQ exception in this phase.

Task creation, transitions, packet/verdict recording, audit writes, outbox changes and budget changes use `BEGIN IMMEDIATE` SQLite transactions with synchronous FULL. Request IDs are idempotency keys scoped to the environment; identical replay returns the task, changed content fails. Concurrent callers cannot duplicate creation or overspend the ceiling. Failed writes roll back their audit/state effects together.

Transitions follow the Phase 0 proposed local state model. Ordinary transition calls cannot directly approve a task. Packet recording moves eligible tasks into awaiting_verification; authenticated verifier decisions alone select approved/rejected/needs_more_research. Approved/rejected/failed/cancelled tasks are terminal. Rework from needs_more_research consumes the bounded retry allowance; cancellation remains available after exhaustion. Explicit retry calls consume the same allowance exactly once per durable retry ID. Replaying an ID returns its original committed task snapshot, even if the live task has since advanced; it does not repeat audit or outbox effects. Use get_task for current state. Recovery lists active committed work without incrementing retries or replaying state changes. Each recovery scan has its own audit event; recovery's work effects are idempotent, not its audit history.

Canonical packet serialization is compact sorted-key UTF-8 JSON, preserving array order and exact Unicode codepoints, excluding floats/NaN. SHA-256 includes all packet/nested schema versions, environment/scope/classification, source identity/version/digest, researcher/model/provider, claims, evidence, packet identity/version and limitations. A changed packet gets a new immutable version; all revisions retain canonical content and stored digest. A separate current-head pointer advances transactionally. Decisions have a composite foreign-key link to exact task/version/digest/environment. Duplicate historical writes return their digest without moving the head or changing task state; conflicting or skipped revisions fail. Historical packet and verdict reads are environment-authorized and audited. Decisions bind exact digest and environment to an authenticated verifier distinct from the researcher. Packet and decision provider/model labels are checked against fixed role assignments. No researcher or verifier model actually runs.

Outbox primitives store task-linked event identity, topic and payload digest with pending/delivered/exhausted states. Duplicate enqueue reconciles identity; delivery status is recorded by an authenticated director; failed attempts stop after three. Events survive restart. No dispatcher, payload transport or external delivery receipt is implemented.

Budget reservations use integer synthetic cost units (requested units multiplied by configured integer price). Per-environment ceilings are pinned persistently on first reservation. Pending reservations count fully against the ceiling; settlement consumes actual reported units and releases the remainder; cancellation releases an unconsumed reservation. Duplicate reservations/settlements reconcile idempotently; over-consumption, wrong actor, changed identifiers or budget exhaustion fail safely. Model/provider substitutions, ambiguous assignments and role escalation are rejected. Production configurations require approved assignments, and production execution remains disabled even with them until host integration.

## Validation and outcome

Required correction command: `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v`.

Final correction result: **51 tests passed, 0 failures, 0 errors**, Python 3.14.3 (31 original cases plus 20 correction cases). Additional `python3 -m compileall -q src tests` and package TOML/source AST validation passed. See PHASE1_TEST_RESULTS.md for requirement mapping and the unsupported Python 3.9 probe. No wheel build/install was attempted because it could require build dependencies.

Tests use synthetic data, temporary directories and a socket guard. Child Python processes deliberately exit with codes 23, 24 and 25 to exercise task rollback and retry replay both before and after commit, without returning a response. It also blocks socket creation. No network, real providers, services, Memory, vaults, credentials, CTO intake or production writes were used.

## Known limitations

- In-process authorization is a trusted-library boundary, not a sandbox against hostile Python code or direct SQLite access by the same OS account. Trusted root/grant/configuration injection must never be exposed to source content or LLM output. OS users, permissions, encryption and host authentication remain Linux work.
- Only Python 3.14.3 was positively validated. Metadata requires >=3.10; the installed Python 3.9.6 is unsupported. Linux Python/runtime/filesystem compatibility is unverified.
- SQLite contains only Research-local metadata and evidence packets. There is no trusted Memory promotion, specialist retrieval service, HQ synchronization or Obsidian write.
- Audit ordering is durable SQLite sequence order; events have unique IDs, tenant, actor, operation and subject. External timestamps, signing, retention and tamper-evident audit storage await the host audit contract. Denied attempts are raised to the caller rather than written to another tenant's audit.
- Offline model assignments are trusted configuration, not owner approval evidence. Resource consumption and local delivery outcomes are trusted caller reports; external usage/receipt reconciliation is deferred.
- Budgets are environment-wide synthetic cost ceilings, not provider billing or per-task deadlines. There are no provider calls, model agents, automatic budget adaptation, scheduler, worker leases or backoff timers.
- Outbox stores a payload digest rather than a transport-ready payload/receipt. Exactly-once external delivery is not claimed; future adapters need durable payload references, receipt lookup and transport idempotency.
- Initial source identities are synthetic already-pinned fixtures. A live intake-to-fetched-snapshot identity lifecycle must be specified in Phase 2; changing the submitted pinned source requires a new request in this implementation.
- Verification independence here is separate issued principals/roles, not independently deployed processes or cryptographically signed host attestations. Prior verdicts remain recorded but cannot approve a revised digest.
- No migrations are implemented. Corrected persistence uses schema v2, while existing public record schemas remain v1. Existing v1 files are rejected without modification; previously overwritten packet history cannot be reconstructed. Reusing an old local database requires a separately reviewed migration/import, not deletion or silent initialization. Unsupported or malformed databases and changed budget ceilings fail closed.
- New databases are fully initialized in a private same-directory temporary file and published with a no-overwrite hard link. This requires filesystem hard-link support; failures are explicit. Existing files (including empty files) are validated read-only first, then revalidated under the transaction lock. File bytes/schema/rows are tested unchanged on rejection. Linux filesystem, abrupt power loss and deployment permissions remain unverified.

## Corrected internal interfaces

- `retry(context, task_id, retry_id)` now requires a caller-persisted logical retry identity; generating a fresh ID on every replay is incorrect. IDs are environment-scoped and bound to task and requesting principal. Missing IDs fail rather than silently generate an unsafe identity.
- `get_retry(context, task_id, retry_id)` retrieves the immutable operation and original result.
- `get_packet(context, task_id, packet_version=None)` returns the current head or an explicit historical version.
- `packet_history(context, task_id)` returns immutable revisions in version order.
- `verification_history(context, task_id, packet_version=None)` returns decisions linked to all revisions or a selected revision. Historical verdict retrieval does not authorize current content.
- `PersistenceError` reports SQLite/filesystem errors; `UnsupportedSchemaError` identifies a non-mutating rejection. Authentication, contract and budget errors keep their existing exception types.

## Exact deferred Phase 2 work

Implement the common bounded source-adapter result with explicit SUPPORTED_FETCHED/PARTIAL/AUTH_REQUIRED/INACCESSIBLE/UNSUPPORTED/ERROR outcomes; intake locator versus immutable fetched snapshot contracts; fixture-backed GitHub inventory/manifest/skill parsing without execution; website/article extraction; PDF/local document extraction; authorized media metadata/transcript adapter interfaces for YouTube, Instagram, TikTok and X. Test malformed/oversize inputs, redirects, unsafe paths/symlinks/submodules, prompt injection, attribution/license metadata, source pins/digests and honest blocked/partial outcomes. Live fetching or authentication needs its own authorization and readiness checks. No source adapter was implemented in Phase 1.

Live agents remain Phase 3, taxonomy/distribution and CTO proposals Phase 4, Memory/HQ simulations Phase 5, messaging simulations/Mac acceptance Phase 6 and authorized Linux integration Phase 7. Full V1 operational acceptance still requires actual Linux end-to-end evidence.

Phase 1 stops here. No commit, push, dependency installation, service startup or deployment occurred.
