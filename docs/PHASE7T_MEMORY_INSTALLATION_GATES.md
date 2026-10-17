# Phase 7T — Memory installation gates

2026-10-16 — **No Linux installation, migration, service action, credential provisioning, canary or Research activation authorized.** The Mac-local source review candidate is prepared; production installation remains BLOCKED. [Candidate/hash](PHASE7T_MEMORY_RELEASE_CANDIDATE.md) and [diff/schema analysis](PHASE7T_MEMORY_DIFF_REPORT.md).

## Required owner approvals before any installation

| Gate | Exact approval/evidence required | Current status |
| --- | --- | --- |
| Memory component-owner sign-off | Approve archive `77c8fa1487ccc4d42919ef38a334da4e98d5a29e5798bcb69429660bfd8eca00`, its two source changes and validation-only test; 34-path baseline/extra-consumer limits, truthful duplicate response semantics, compatibility and no new service | Pending |
| Installed-source / runtime pin | Recheck current release 4d5ba29bd3027e74c808a8feaf1b5dadfded22f0 and 34 hashes, added-path absence; owner supplies complete release/consumer map, effective handler/runtime/dependency evidence without exposing secrets | 34-path/current comparison passed; complete release/runtime acceptance pending |
| Real Research principals | Exact Personal-only subject/tenant/task/purpose binding and issuer; separate writer, verifier, Memory promoter and permitted specialist reader grants; companies deny until explicitly registered | No production Research subjects configured |
| Independent verifier authority | Approved issuer/signature or authenticated authority boundary, exact provider/model/execution policy, contributor independence, revocation/expiry/rotation/restore generations and audit; synthetic artifacts permanently ineligible | Unconfigured; TestAuthority is not acceptable production trust |
| Production candidate/receipt contract | Signed-off canonical schema/digest vectors, payload/time limits/encoding, candidate-sensitive metadata binding, operation/CAS/reconciliation semantics, separate commit/promotion/fresh retrieval and currentness failures | Staging contracts only; no wire action names/routes approved |
| Production schema / retention | Full DDL/constraints/index/version/migration/old-reader compatibility, deletion/hold/tombstone/evidence/receipt retention and invalidation ordering; explicit no-autoinit failure policy | Prototype test-only DDL; no migrator or live DB inspection |
| Consistent backup + rehearsal | Owner-approved consistent DB snapshot including WAL consistency, deletion ledger and separately secured key/trust/permission generations; synthetic upgrade/incompatible-open/restore/downgrade failure rehearsals | Not performed; no production DB/key access allowed here |
| Regression acceptance | Broader baseline/work/candidate comparisons, relevant untested 16 extension methods and unchanged Memory/Obsidian/client consumers; inherited Mac failure reproduction plan and explicit optional skips | Seven Linux extension methods + duplicate control only |
| Exact installation files / dependency layout | New immutable full Memory release assembly retaining all unchanged files; only source/focused_v1/store.py and source/focused_v1/research_stage.py from this overlay; tests not installed; pin Research codec/runtime dependency paths and hashes | Source payload known; full release/install paths and dependency policy not approved |
| Exact service actions | Named existing service alfred-memory-v1.service, exact version/path/symlink/config diff and restart/reload/health plan if needed; no second authoritative service, hot source overwrite or inferred restart | **None authorized**; no unit/config files in package |
| Rollback | Exact prior compatible release/hash, service actions/trigger conditions, data/trust/ledger ordering and reconciliation; preserve operational receipts/revocations/tombstones; demonstrate source-only versus migrated rollback separately | Not approved/rehearsed |
| Live canary permissions | Separate exact Personal conversation/task/source scope, synthetic exclusion, approved real models/verifier/issuer, budget/deadline, Memory writer/promoter and named specialist read; no export/Sync/HQ/Development action by default | No live canary authorized |

**No default Research principal may gain promotion authority.** The Research Director, researcher, support agent or verifier must not inherit promoter permission from a role/category/bridge token or client flag. Real promotion is an explicit Memory-owned current-policy authorization independent of submitting and verifying a packet. Existing test admin/promoter roles authorize only simulated states; they must not be copied to production grants.

## Approval must distinguish two installation decisions

1. **Dormant code/duplicate-response correction:** owner may review this limited source change independently; duplicate fix requires no DB migration. Even this needs full release/consumer regression and exact file/service rollback sign-off. No implementation import of ResearchStage into live handlers follows merely from placing its source file in a release.
2. **Production-capable Research integration:** this candidate cannot provide it. Genuine trust/auth/schema/receipt/retention/export policy and route implementations need new reviewed source changes and a newly versioned/tested candidate. Do not flip test_only/production flags, expose simulate_promotion via HTTP, auto-create TestAuthority grants or equate SIMULATED_SUCCESS receipts with real approval.

The current extension fails closed by design; installation of unchanged bytes would not create an enabled production Research endpoint. Packaging proof is not authorization to disable those guards.

## Proposed next installation step

First obtain Memory-owner review of this exact source-overlay archive and gate matrix. The next separately authorized action should be **isolated candidate-package transfer/verification and expanded regression/migration rehearsal on synthetic state**, with explicit test IDs, fixture scope, input hashes, runtime mounts/resources and cleanup. The present task transferred no candidate to Linux.

Before a real installation, the owner must provide a concrete immutable full-release destination (not current/source), dependency/config diff, exact existing-service actions, consistent backup/restore evidence and rollback commands. Recheck baseline hashes immediately before any later approved switch; mismatch stops the process. No installation/restart command is proposed for execution while these inputs remain unknown.

## Rollback contract for later owner review

- Before an approved switch, record old/new source/config/schema/trust/grant/ledger identities and pending operation IDs; validate a usable consistent backup/restore, not just a dated directory. Do not copy private production state into tests.
- Define disable/revert triggers: baseline mismatch, unsafe mount or runtime, regression, failed health/receipt/currentness checks, duplicate/conflicting mutation, revoked/expired trusted read or ambiguous outcome. Halt new ingress/promotion, reconcile by original operation identity and retain receipts.
- A dormant source-only rollback may restore the prior approved source release; it also restores the known incorrect duplicate reply and must be consciously accepted. No DB rollback follows from the duplicate fix.
- A migrated/published-state rollback needs compatibility-aware readers and current invalidation/tombstone/trust state. Never blindly drop Research tables, reset DB/schema, restore stale issuer grants/deletions, discard receipts or rewind Obsidian export/Sync. Published misinformation needs an owner-approved revoke/correct path.
- Approve exact service stop/switch/reload/restart/health actions and access independently. Do not invent automatic restart or emergency privilege escalation from this document.

## Current production and artifact boundary

Candidate archive and three requested documents are Mac-local. Read-only SSH comparisons show installed current target/34 source hashes unchanged and alfred-memory-v1 active/running at both observations. No production database, vault, credential/config content, application endpoint or live provider was accessed; no Linux write, service action, credential change, migration, Obsidian change, commit/push, deployment or Research activation occurred.

**Candidate preparation PASS; installation/activation BLOCKED. Stop and await owner approval.**
