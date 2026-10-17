# Phase 4 validity correction report

## Root cause

Exact content identity excludes validity metadata intentionally, but duplicate processing previously reused the existing record before validating expiration. Thus an expiration of -1 was accepted, and a request changing expiration from 2000 to 1001 silently reused 2000. Additionally, authoritative packet/verification reads audit themselves; simply checking expiration after those reads would still leave rejected-request audit effects.

## Exact changed files

- `src/alfred_research/intelligence/service.py`: early strict expiration checks, read-only checkpoint preflight, serialized duplicate-validity comparison, explicit ValidityConflict, and immutable VALIDITY_UPDATE relationships/status handling.
- `src/alfred_research/intelligence/__init__.py`: export ValidityConflict.
- `tests/test_intelligence.py`: eight added regressions and a non-auditing, explicitly closed SQLite snapshot helper.
- `docs/PHASE4_IMPLEMENTATION_REPORT.md`: correction behavior and limitations.
- `docs/PHASE4_TEST_RESULTS.md`: actual final results and reproduction evidence.
- `docs/PHASE4_INTELLIGENCE_CONTRACTS.md`: validity/replay/revision policy addendum.
- `docs/PHASE4_CORRECTION_REPORT.md`: this report.

No persistence schema or foundational API changes, dependencies, production writes or Phase 5 work.

## Correction and ordering

1. Check issued Director context and strict positive bounded integer expiration. Booleans, floats, strings, null, negative/zero and out-of-range values fail before audited reads or provisioning.
2. Load immutable PacketPreparation/SourceResult checkpoints for read-only identity preflight. These do not authorize a successful intelligence commit.
3. Expired new operations fail before catalog directory/lock creation; an exact previously committed operation may replay after expiry.
4. Under the existing environment catalog lock, validate operation replay, future expiration, relationship/expected-head and duplicate expiration. Conflicting duplicate validity raises exported ValidityConflict (ContractError subtype) with VALIDITY_CONFLICT. Rejected validity requests have no catalog batch, audit or outbox effects.
5. Only after validity succeeds, perform existing authoritative exact-current-packet, APPROVED decision and source/review linkage checks. Then commit immutable batch and reconcile the stable outbox event as before.

Content identity remains separate from validity: adding expiration to exact identity would incorrectly create unrelated records and duplicate proposals. Ordinary duplicates require matching expiration and preserve the original record. They never shorten or extend it.

An intentional change uses explicit Director-only VALIDITY_UPDATE with one latest exact-content CURRENT target, expected canonical record digest, changed future expiration and exact approved evidence/verification relationships. It creates a new immutable record, supersedes the old version, preserves source/packet/decision/environment, and emits no new proposal. Changed evidence cannot reuse that authorization. Concurrent stale revisions fail; later ordinary duplicates use the latest validity version. Expired or disputed records cannot be revived through this metadata-only path.

## Executed validation

`PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v`

**185 passed, 0 failures/errors, 7.578 seconds; exit 0.** All 177 previous tests preserved. Eight new tests cover all requested validity cases, replay, concurrency, history, authorization, expiry and tenant boundaries. Snapshot comparisons verify rejected operations do not alter catalog/audit/outbox state. Existing four-environment recovery and forged-receipt diagnostics remain passing.

The exact independent reproduction was rerun both directly and as an automated test: 2000→1001 explicitly conflicts, -1 is rejected, and at time 1002 the original record remains unchanged under its original expiration. Final compilation passed for 28 Python files in memory; metadata checks passed without builds or installation. See PHASE4_TEST_RESULTS.md for commands and intermediate-run details.

## Remaining limitations

Validity is Director-specified offline metadata, not live freshness proof. A metadata-only revision reaffirms the unchanged simulated packet decision, not fresh factual investigation; new evidence still requires independent verification. All records remain NON_PRODUCTION / SIMULATED and Memory-ineligible. Explicit conflict identification, local-account filesystem trust, bounded catalog capacity and deferred Linux/provider/Department contracts remain as documented. No live Memory, services, credentials, deployment, commits or pushes were used.
