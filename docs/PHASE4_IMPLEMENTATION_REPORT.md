# Phase 4 implementation report

Implemented the deterministic offline intelligence organization milestone only. Phase 5 is not started. Existing Phase 1–3 source and tests are unchanged.

## Files created or changed

Created:
- `src/alfred_research/intelligence/__init__.py`
- `src/alfred_research/intelligence/service.py`
- `tests/test_intelligence.py`
- `docs/PHASE4_IMPLEMENTATION_REPORT.md`
- `docs/PHASE4_TEST_RESULTS.md`
- `docs/PHASE4_INTELLIGENCE_CONTRACTS.md`

Updated `docs/CONTRACT_GAPS.md` with Phase 4 retrieval, taxonomy, catalog and handoff integration requirements.

## Implemented behavior

Versioned validated classification, intelligence, immutable batch, specialist-profile proposal and department proposal contracts. Eleven Development matches plus non-development categories and environment-specific category extensions. Separate per-capability evaluations for multi-skill repositories. Secondary matches and unresolved-capability CTO review proposals convey no authority.

Exact current approved packet/decision/source/review checks reuse Phase 3 and existing SQLite histories. No new research, model execution, budget spending or provider access is introduced. All records are explicitly NON_PRODUCTION / SIMULATED and Memory-ineligible; trusted production views fail closed.

Append-only environment-scoped journal batches reuse the Phase 3 durability primitives, with per-environment locking, idempotency and correction/update expected-head checks. Existing outbox is reconciled after an interrupted catalog-to-outbox boundary. Exact duplicate receipts preserve newly submitted packet provenance without new knowledge records/proposals. Related, corrected, updated, conflicting, superseded and expired/stale findings remain historically available. Conflicts conservatively exclude both sides and require further verification/human escalation.

Director-only simulated specialist views and proposal retrieval preserve private-company boundaries. Tests cover all 12 ordered environment pairs for history, distribution/views, proposal/status reads, processing and relationship writes. Test setup uses four synthetic environments and socket blocking. No live Memory, Hermes, Photon, Development, imported scripts or publication workflow is invoked.

## Validation and limitations

See PHASE4_TEST_RESULTS.md for executed commands/counts. New tests exercise all specialties, multi-skill capabilities, duplicate vs related content, historical corrections, concurrent head conflicts, expiry, disputed findings, approval exclusion, simulation-only views, proposal-only constraints, 12 cross-environment pairs, outbox fault repair and fresh-process history retrieval. Existing regression tests retain SQLite hot-journal/forged-receipt diagnostics and Phase 3 budget/deadline/rework checks.

Lexical routing is deterministic and deliberately not semantic verification. Contradictions and relationship targets require explicit Director input; no automatic semantic conflict detector is claimed. Generic benefits/dependencies are review requirements, not proof of utility or installation instructions. Actual dependency declarations remain in preserved evidence. Conflicts require subsequent authorized review; there is no automated winner selection. Validity is caller-specified and enforced offline, not checked against live sources. Catalog capacity is 500 batches/environment. This is a local append-only Research catalog, not a replacement Memory service. Individual specialist runtime access remains disabled; Director retrieval prepares proposed views only.

Linux registration credentials, filesystem guarantees, actual specialist identity mappings, Memory promotion policy, approved classification vocabulary, CTO/Department Director intake and real outbox delivery remain integration requirements. Synthetic verdicts cannot satisfy production approval. No Phase 5 integration has been implemented.

## Validity correction — owner-authorized follow-up

Corrected duplicate processing that previously skipped expiration validation and silently retained the original validity. ValidityConflict (a ContractError subtype) now explicitly reports VALIDITY_CONFLICT for duplicate content with a different expiration. Integer/type/range checks occur before any SQLite reads; future-expiration and duplicate consistency checks precede audited authoritative reads. Invalid/conflicting requests create no catalog batch, audit entry or outbox event. Existing immutable checkpoints provide read-only preflight identity; they never substitute for the authoritative approved SQLite packet/decision check on successful processing.

Added Director-only VALIDITY_UPDATE relationships for deliberate metadata-only revisions. They require the latest exact-content record, its expected digest, CURRENT status, a changed future expiration and the existing exact approved packet/source/review relationship. Changed evidence cannot use this path. History is retained and the original becomes SUPERSEDED. No duplicate proposal is emitted. A validity-only change reaffirms the original simulated evidence decision; it is not fresh factual investigation or production freshness authorization. Expired/disputed/superseded records cannot be revived using this path.

Correction files: `src/alfred_research/intelligence/service.py`, `src/alfred_research/intelligence/__init__.py`, `tests/test_intelligence.py`, this report, `docs/PHASE4_TEST_RESULTS.md`, `docs/PHASE4_INTELLIGENCE_CONTRACTS.md`, and new `docs/PHASE4_CORRECTION_REPORT.md`. No persistence schema, foundational API, production interface or dependency changes.
