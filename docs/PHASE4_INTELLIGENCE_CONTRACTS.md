# Phase 4 offline intelligence contracts

These are internal Research contracts, not Linux, Memory, or Department API claims. Schema names are versioned; existing Contract validation rejects unknown fields and malformed types. No production promotion API exists.

## Authority and storage

IntelligenceOrganizer accepts only OfflineAuthority-issued contexts. Processing/reconciliation require Director; reads check the original environment, and specialist views and proposals require Director. This conservative retrieval boundary grants no specialist agent additional access. Four catalog directories use the existing WorkflowJournal environment partition, no-follow files, bounded canonical envelopes, fsync, immutable hard-link commits and bounded exclusive flock. Catalog namespace is `phase4-intelligence-catalog-v1`; checkpoint keys are `packet:intelligence:<sequence>` (the existing Director-only namespace). No existing SQLite schema changes or migrations.

One Batch is the commit unit: record, relationship, proposals, actor, sequence, operation identity, submitted task/packet reference and canonical input digest. All history is append-only. Sequences must be contiguous; capacity is 500 batches per environment and 2 MB per envelope. This bounded offline implementation intentionally stops at capacity. It is not a production Memory index. The private filesystem and bootstrap authority retain the Phase 1–3 same-account trust boundary.

Commit the immutable batch first, then enqueue a stable digest-bound event in the existing SQLite outbox. An interruption between commits is repaired by replay or Director `reconcile`. This is recoverable intent, not a cross-file atomic transaction. No consumer or transport is implemented. SQLite outbox insertion audits the event once. Batch actor and operation preserve Research-local organization history. No background scheduling.

## Classification and matching

Classification has one primary category, related topics and zero or more specialists. Fixed ordered lexical rules recognize all 11 Development specialties and six named non-development categories; unmatched content is General Intelligence. Rules are routing hints, not factual research or semantic equivalence. Director may select a configured category, including environment-specific extensions. Source text cannot supply authority, trusted configuration, or role grants. Non-development SpecialistProfileProposal is an inert, versioned configuration proposal; deployment is forbidden.

Capabilities in multi-skill repositories are evaluated separately using only each capability's cited source evidence. Multiple matches are secondary responsibilities; no match generates a Central Development CTO classification-review proposal. Matching and proposals confer no installation, execution or publication permission. No new agents are created.

## Approval and identity

Processing loads the exact current immutable packet, one matching APPROVED SQLite decision, the Phase 3 SourceResult checkpoint and simulated per-claim review. Digest, verifier separation, source-result binding and review/decision identity must match. REJECTED and NEEDS_MORE_RESEARCH are denied. Packet/source content changes require fresh Phase 3 verification. Classification routing cannot change the packet's access classification or ownership.

Exact identity hashes environment, scope, access classification, complete SourceResult digest, ordered claim kind/text/evidence IDs and classification. Generated task IDs and decision IDs are excluded. This intentionally strict definition includes source provenance and revision, and does not assert semantic similarity. Same operation and input replays return the original batch. A different operation with exact content appends only a duplicate provenance receipt, referencing the existing record; it creates no new record or proposal. Receipt includes the newly submitted packet/task. Related findings require explicit Director-selected relationship targets; keyword overlap never merges records.

## Evolution and views

NEW, DUPLICATE, RELATED, CORRECTION, UPDATE and CONFLICT are explicit relationships. Corrections/updates require exactly one current target and its canonical record digest as expected head. Concurrent stale updates fail under the environment lock. Historical packets, decisions, records and proposals remain intact. Status is derived: DISPUTED takes precedence, then SUPERSEDED, then EXPIRED (the stale validity boundary), then CURRENT. Views return only CURRENT records and require explicit `simulated=True`; history and `status` expose excluded records. Validity uses integer epoch seconds and an injectable clock.

Contradiction recognition is explicit, not an unimplemented semantic detector: a Director declares CONFLICT with referenced findings. All conflicts are conservatively high-impact and exclude both sides from current views. Neither side wins; further verification or authorized human escalation is required. This milestone does not implement conflict resolution approval or live freshness checks.

Every IntelligenceRecord embeds the exact packet, source/evidence, decision reference, review digest, environment, access requirements and validity. All records are `NON_PRODUCTION / SIMULATED`, `memory_eligible=False`. There is no path to production-trusted views even for CURRENT items. Specialist identity is the authorized query selector and category association; real specialist credential mappings remain unconfigured.

## Proposal-only handoffs

Proposal includes capability, target specialist, exact source digest and available revision, source evidence IDs, expected evaluation benefit, dependency/license review, source risks/limitations, required implementation/testing work, environment and approval-required status. Its containing batch/record supplies original locator and packet/decision references. Status is immutable PROPOSAL_ONLY and approval_required must remain true. Generic departments may use the same versioned inert proposal contract with proposed specialist identifiers. No task submission, approval token, release permission, installation or GitHub publication is implemented.

## Validity correction addendum

Content identity intentionally remains separate from validity. NEW duplicate requests must have identical expiration; conflicting expiration raises exported ValidityConflict / VALIDITY_CONFLICT without a batch, audit entry or outbox event. Expiration must be a positive bounded integer (booleans, floats and strings rejected), and a new operation must expire in the future. An exact previously committed operation can replay after expiry, preserving the original record and never returning it through CURRENT views.

Read-only PacketPreparation/SourceResult checkpoints preflight identity and scope before audited SQLite calls. The authoritative exact approved packet/decision/review check remains mandatory for successful operations. Catalog locking serializes duplicate checks and revisions.

VALIDITY_UPDATE is an explicit Director-only metadata revision: one latest exact-content CURRENT target, its canonical expected-head digest, changed future expiration, unchanged packet/source/classification identity and an exact current approved verification relationship. It creates a new immutable record with preserved evidence/verification and supersedes its target. It creates no new proposal. Subsequent duplicates compare against the latest version. It does not authorize changed factual content, revive expired/disputed knowledge, or prove live freshness. No production promotion is enabled.
