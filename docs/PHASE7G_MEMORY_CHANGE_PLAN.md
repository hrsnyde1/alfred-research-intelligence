# Phase 7G — Minimal Memory-owned change proposal

## Boundary and conclusion

Documentation only; no implementation, production probe or deployment approval. See PHASE7G_MEMORY_CONTRACT.md for observed source and exact proposed semantics. A Research adapter alone cannot safely translate current saved/approved responses into independently verified knowledge. The minimum necessary extension belongs **inside the existing Memory authority**, with separately scoped callers and a full structured record/read lifecycle. No second database service, vault writer or model verifier service is proposed.

## Exact existing files and conditional modifications

Remote base: `/opt/alfred-obsidian-v1/current/source/`. These are owner-review targets, not authorization to edit the installed release. Author in the Memory owner's approved development checkout later, then stage an immutable reviewed release.

| Existing file/interface | Required minimum change if no other approved port supplies it |
|---|---|
| `focused_v1/store.py:259–288` create duplicate response | Return actual stored review_state by selecting it instead of hardcoding approved. No row review mutation. Preserve existing response keys; test pending/rejected/approved plus pending-edit semantics. Kind-mismatch handling is a separately explicit compatibility decision, not an unannounced API change. |
| `focused_v1/store.py:68–125` persistence/version check | Add Memory-owned structured Research revisions, attestations, lifecycle state and operation receipts through an explicitly reviewed additive schema extension/migration. Logical entities are proposed, not existing table names/DDL. No automatic migration during open; existing schema checks must recognize only owner-approved compatible versions. |
| `focused_v1/store.py:145–190` authentication/assignments | Extend existing principal/task authorization with trusted Research submitter, independent attestation verifier, Memory promotion authority and scoped specialist read grants. Reuse existing identities/broker where sufficient; keep global Alfred/bridge authority out of Research. Tenant/purpose/classification/current grant checks on every read/write. Personal-only allowlist until companies are registered. |
| `focused_v1/server.py:14–26,46–67` and `obsidian_candidate/service_api.py:329–340` combined routing | Expose owner-versioned Research operations/receipt lookup via the same Memory service; allocate action names/route only after contract review. Keep existing routes unchanged except the truthful duplicate response. Strict independent action field allowlists, bounded JSON/error/authorization behavior; no synthetic production promotion. |
| `focused_v1/store.py:297–431` and `service_api.py:88–103,195–259` generic read/update/review/bridge paths | Prevent managed Research records from bypassing attestation/currentness through legacy create, review, update, search, get_current, snapshots or fixed-actor bridge operations. Provide full scoped Research retrieval; do not give specialists bridge/Alfred credentials. All outward projections must enforce current validity/policy. Generic text edit becomes a new Research candidate or is denied. |
| `focused_v1/store.py:192–212,319–389,433–511`; `service_api.py:26–86,166–193` deletion/recovery | Extend existing deletion/suppression/replay protection to structured evidence, immutable revisions, indexes, receipt retention and optional projection. Explicit hold/purge policy; no orphaned full citations after forget, no stale restoration after tombstones. Preserve fail-closed quarantine/version protections. |
| `obsidian_candidate/bridge.py:353–420,625–675,918–955,1022–1055`; `routing.py:14–58`; `cycle.py:68–102` | Preserve existing export/Sync implementation. No Research export selected for first canary. Modify only the Memory-owned read/projection adapter or managed-record mutation guard if current pipeline can expose/bypass new records. Later enablement requires explicit mappings/currentness and real request/export/Sync receipts; do not rewrite workers or activate offline adapters. |

Prefer a small Memory-owned Research module called by the existing store/dispatcher to isolate new validation and SQL; its filename is not allocated here. New logical records must be committed by the same Memory service/transaction boundary. Do not hide structured Research JSON in ordinary development_lesson/task_progress to inherit auto-approval, or use capture_create's fixed Alfred actor.

### Minimal persistence/projection decision

Proposed default: additive structured entities in Memory's existing authoritative persistence, with immutable Research versions and operation receipts; no new server/parallel authoritative Memory. Keep ordinary Memory unchanged. Candidate/committed Research data must be inaccessible to legacy trusted retrieval/export. Promoted data is visible only through the new authorized current-record port initially.

Avoid a generic approved text projection for the first canary: it creates legacy search/export/edit bypass risks and is unnecessary for specialist full retrieval. If Memory owner chooses to reuse generic memories rows, add a managed-record binding and enforce Research policy on **every** legacy read/write/review/bridge path before exposing any row; a research kind string alone is insufficient. Later Obsidian projections require the same guard and explicit existing bridge selection. The exact physical schema/version is a Memory-owner decision, not prescribed SQL.

## Compatibility and unresolved approvals

- VERIFIED: constructor initializes only an explicitly new database and otherwise expects source schema v3; existing Memory/Research schema versions are unrelated. Migration needs approved metadata, backup/restore and startup compatibility design; never initialize/reset production on validation failure.
- UNKNOWN: effective running HTTP action/version/auth configuration, existing service virtual environment, actual stored schema and alternate uninspected Research ports. Owner supplies redacted evidence before choosing modifications. No database or protected config read is needed for schema examples.
- REQUIRED DECISIONS: attestation issuer/verification mechanism and key rotation/revocation/restore; exact Personal tenant, submitter/promoter/specialist subjects/grants; approved verifier/model and evidence policy; payload/receipt/time/retention limits; conflict/validity rules; transport operation/error schema and lookup retention; migration and rollback plan.
- ASSUMPTION TO APPROVE: Memory can retain bounded structured source excerpts under its existing retention authority. If not, define an authenticated immutable Memory-owned evidence storage port; arbitrary Research paths/URLs are not durable citation storage.
- Compatibility must preserve existing personal approval behavior for ordinary records without translating it into Research trust. Truthful duplicate response intentionally corrects the reply; it does not alter stored decisions. Existing search/bridge formats remain compatible, with new managed Research data denied unless a reviewed policy-aware projection is selected.
- Legacy delete/forget/hold remains authoritative. Research immutable history is not an exemption from legal deletion. No new production dependencies are selected here.

## Proposed implementation and acceptance sequence

1. **Owner closure:** sign candidate/attestation/receipt/read/lifecycle schemas and grants; confirm whether an existing approved port meets them. Resolve duplicate response semantics independently of Research deployment. No change follows merely from this document.
2. **Memory development:** separately authorize the response fix and additive Research module/guards in the Memory development repository. Use synthetic fixtures and fake attestation authorities; do not modify Research's accepted fake types to enable production.
3. **Mac Research development:** after Memory contract approval, implement proposed genuine adapter types and canonical vectors/receipt reconciliation against fake Memory-owned service examples. Preserve 305 accepted regressions, synthetic rejection and the shared invocation/accounting logic. No network access implied.
4. **Isolated Linux staging:** separately approve artifact transfer/extraction/runtime, synthetic database/evidence roots, host grants, migration tooling and permitted endpoints. Prove Memory existing suite, PHASE7G_MEMORY_ACCEPTANCE_TESTS.md and Research regression/contract tests. No production database clone containing private records.
5. **Migration/rollback rehearsal:** stage schema upgrade and incompatible-open rejection on synthetic fixtures, verify operation ledger and tombstone restore ordering, measure actual rollback behavior. An old binary must not serve unguarded Research data from a new schema. Prove no export/Sync side effects.
6. **Personal production approval:** exact reviewed release/config diff, scoped Memory caller and independently verified attestation authority, repository/commit, real verifier/models/budgets, existing conversation, permitted specialist read and receipt retention. This is a separate live authorization; Phase 7G grants none.
7. **One canary:** candidate acceptance → durable commit → separate promotion → fresh Frontend/specified specialist retrieval with complete evidence → truthful completion. A successful Memory commit alone is incomplete. No export/Sync/HQ/Development execution claims.

## Rollback and recovery requirements

Before any authorized deployment, record code/config/schema hashes and current principal/attestation revocation generations, pending operation IDs and compatible backup/restore evidence. A timer/directory is not proof of a usable backup. Memory owner defines which existing services/actions actually need changing; no restart is assumed here.

On failure under later rollback approval: disable only new Research ingress/promotion permissions, preserve immutable operation receipts and current revocations/tombstones, reconcile ambiguous commits by original operation identity, and keep current retrieval fail closed. Revert code only with schema-compatible guarded behavior; do not run an older reader that exposes newly managed data as ordinary approved memories.

Do not blindly downgrade/delete tables, reset databases, restore stale deletion ledgers/keys/attestation grants, discard pending operations or reverse published Obsidian state. Already promoted misinformation needs a Memory-owned revocation/correction; any already-delivered notification needs a separate approved correction. Respect held content and deletion policy. Preserve existing EXDEV-safe publication repairs, quarantine and Sync process. Research never performs compensating direct database/vault writes.

Current authorization ends with these three local documents. Component development, migration, staging, credentials and production canary all require separate approval.
