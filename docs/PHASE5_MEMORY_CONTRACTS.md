# Phase 5 proposed Memory integration ports

Status: VERIFIED LOCAL fake behavior; PROPOSED external contracts; UNKNOWN LINUX mappings. No production Memory endpoint, database schema, credentials or vault mapping is asserted. Existing Memory remains the intended authority. This package is a bounded test double and operation transcript inside Research, not a second authoritative Memory system.

## Existing contracts reused

ResearchStore owns authenticated task state, immutable packet revisions, exact-digest verification decisions, budget reservations, audits and durable outbox primitives. IntelligenceOrganizer owns immutable IntelligenceRecord/Batch history, exact duplicate and validity semantics, source snapshots, classification, specialist associations and currentness. OfflineAuthority issues exact in-process context capabilities. These components are unchanged.

KnowledgeCandidate embeds the exact IntelligenceRecord (including packet version/digest, claims, source/evidence, observed revision, limitations, ownership, access restrictions, validity and simulated status), independent VerificationDecision, Research catalog sequence as record_version, relationship/target references and stable idempotency ID. Company labels must exactly match the established local environment alias. Fake submit compares against authoritative local Research history; submitting a newly fabricated or altered candidate is insufficient.

Contract schemas use `.proposed.v1` names, except MemoryEvent's local test transcript schema. All use existing strict Contract type/schema/unknown-field validation and canonical SHA-256. MemoryCommand binds environment, exact record ID/digest, operation/idempotency ID, expected lifecycle sequence, related IDs and an explicit fixture outcome. It cannot supply authority or permission grants. MemoryReceipt has a distinct operation discriminator, receipt ID, record version/digest, actor, sequence, observation time, outcome, stage/state and SIMULATED / NON_PRODUCTION marking. KnowledgeCandidate, MemoryReceipt and RetrievalResult cannot be relabeled production.

## Logical ports and distinct receipts

MemoryPort is a Python Protocol, not a network client. FakeMemoryAdapter provides named ports that reject commands for the wrong operation.

| Port | Preconditions / effect in the test adapter |
|---|---|
| submit | Issued same-environment Director, current approved Research identity; durable CANDIDATE receipt |
| commit | Expected lifecycle sequence and CANDIDATE state; separately checked approval; COMMITTED receipt |
| promote | Expected sequence and COMMITTED state; separately checked current approval; PROMOTED receipt |
| retrieve | Independently granted specialist plus matching environment/category/classification, PROMOTED state and fresh Research validation; separate RETRIEVABLE receipt and complete provenance |
| supersede | Expected sequence; one same-environment promoted replacement with explicit verified Research CORRECTION/UPDATE/VALIDITY_UPDATE relationship; old item becomes SUPERSEDED |
| expire | Expected sequence and actual validity boundary reached; EXPIRED tombstone |
| delete / revoke | Expected sequence and nonterminal record; DELETED / REVOKED logical tombstone |
| request_export | Current promoted record; EXPORT_REQUESTED receipt only |
| export_status | Prior export request, current promoted record; simulated EXPORTED, PARTIAL or FAILED result |
| sync_status | Successful latest export-status receipt and current promoted record; separate simulated SYNCED, PARTIAL or FAILED result |
| hq_allow / hq_sync / hq_retrieve | Explicit eligibility, scoped company partition and separately granted owner retrieval; see PHASE5_HQ_SYNC_CONTRACT.md |

Commit does not confer promotion. Promotion is not proof of fresh retrieval. Export request is not export completion; export is not Obsidian Sync. No export writes a Markdown file. Receipt outcome and operation must both be checked; failed/partial fixtures do not advance lifecycle state. RETRIEVABLE is an observation receipt, not a persistent grant; the underlying state remains PROMOTED.

## Authorization and currentness

All non-retrieval operations require issued same-environment Director context. Specialist retrieval requires an independently configured exact-context TestMemoryAccess grant for both matched specialty and access classification. The association in a research item creates no grant. HQ owner grants are separate and personal-only. Trusted bootstrap supplies per-environment service Director contexts for receipt persistence on authorized reads; untrusted request/candidate data cannot select another service identity.

Submission, commit, promotion and retrieval confirm the exact current immutable packet and APPROVED independent decision through existing Research checks. Rejected, NEEDS_MORE_RESEARCH, changed, expired, disputed or superseded records fail currentness checks. Every retrieval checks currentness again, and reused retrieval operation IDs are rejected: request a new ID for a fresh retrieval receipt. Knowledge remains NON_PRODUCTION, Memory-ineligible, even after fake promotion. FakeMemoryAdapter rejects production=True or absent explicit test_only=True. There is no production-capable implementation.

## Durability, concurrency and ambiguity

The existing WorkflowJournal holds bounded immutable MemoryEvent fixtures under each environment's `phase5-memory-test-transcript-v1` namespace, using Director-only `packet:memory:<sequence>` keys. Maximum 500 events/environment and existing 2 MB envelopes apply. The test transcript reduces successful mutation receipts into lifecycle state; no semantic/vector Memory index, service or long-term production record store is implemented.

Lock order is Research catalog then environment test transcript. Thus Research supersession, fake lifecycle writes, revocations, retrieval and HQ sync are serialized within the relevant environment. Mutations use expected lifecycle receipt sequence; stale or out-of-order operations fail. Non-mutating export/retrieval/HQ observations do not change that sequence. One stable operation ID must retain exact command, candidate and actor; changed replay fails. Replays return the original historical receipt, never a fresh observation or a claim of current trust. A different submit ID for identical content does not duplicate the stored candidate; its own receipt may advance the expected lifecycle sequence. Callers must use returned mutation sequences.

Immutable event publication occurs before stable digest-bound insertion into the existing SQLite outbox. A lost response raises DeliveryAmbiguous; it does not return success to the caller. Replay or Director reconcile repairs the missing outbox event without repeating the committed effect. Local receipts describe only test-adapter results, not confirmed external Memory delivery. Existing outbox delivery state remains pending unless separately changed through its original test APIs; this phase implements no consumer or real delivery acknowledgement.

Restart reconstructs fixtures from journal events. Trusted tests explicitly restore the existing offline registration authority and reissue independently configured access grants; grants/owner contexts are not imported from candidate files. Fresh-process tests transfer synthetic authority state over trusted harness stdin only. Recovery is not a production registry/credential restoration protocol.

The transcript itself provides actor/environment/operation/outcome audit; existing SQLite reads and outbox commits retain their original audits. Authorization/validation failures raise and are not represented as successful receipts. Denied-attempt audit policy remains a Linux question. Logical delete/revoke preserves synthetic historical evidence for tests; real retention, legal holds and secure deletion require Memory-owner agreement.

## Unverified production boundaries

Real Memory contract versions, authentication, approved model/verifier attestations, production currentness policy, specialist grants, ownership/classification mappings, correction/revocation semantics, transport receipts, anti-replay keys, deletion/retention, storage encryption, backup and export/Sync acceptance are unresolved. No historical Obsidian bridge endpoint is repurposed as Research ingestion. Phase 6 messaging/completion work is not implemented.

## Export receipt correction — explicit attempt bindings

MemoryCommand and MemoryReceipt now use `.proposed.v2` schema identifiers. Other contracts and SQLite schema remain unchanged. Existing v1 command/receipt payloads (including nested old transcript receipts) fail closed rather than being silently upgraded or treated as export authorization. No automatic migration is provided; these are temporary offline fixtures, and any future import requires reviewed explicit mapping.

Export operations require explicit singleton `export_attempt`, `export_destination` and command `export_record_version`. Non-export operations require these fields empty. The test destination is the fixed label `test-obsidian:<authenticated-environment>`, not a path or actual vault. A request establishes its own operation ID as attempt identity. Its receipt records attempt/destination plus the authoritative record version/digest. Completion commands and receipts also bind an exact `prerequisite_receipt`: export completion references its successful EXPORT_REQUESTED receipt; Sync references its successful EXPORTED receipt.

The adapter checks the latest record-specific request, its SUCCESS outcome/stage, matching record digest/version, actor, attempt and destination before both new completions and replay. Sync additionally requires the matching successful export receipt referencing that exact request. A failed/partial request cannot authorize completion. A failed/partial completion requires a new explicitly authorized request to retry; old success replay cannot override that failure or a newer attempt. A revoked, superseded, disputed or expired record also fails before replay. Duplicate legitimate successes remain idempotent while the same attempt and latest applicable phase remain valid.

Lost responses remain DeliveryAmbiguous; no success is returned until authorized receipt lookup/replay/reconcile confirms the durable stage. Recovering a request receipt proves only EXPORT_REQUESTED, never EXPORTED or SYNCED. No actual export/Sync provider or independent external delivery attestation is implemented.
