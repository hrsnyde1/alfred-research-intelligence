# Phase 7U — Memory release decision

2026-10-16. Scope: static, Mac-local review; only the two requested reports were created. No code imports, tests, SSH operations, source edits, package changes, production reads/writes, credentials, service actions, transfers or installation were performed in this phase.

## Recommendation

**RELEASE CANDIDATE READY FOR OWNER INSTALLATION REVIEW — solely for the two-line duplicate-create correction in `focused_v1/store.py`.** This is a review recommendation, not installation authorization or confirmation that all installation gates are satisfied.

**Production Research integration: BLOCKED.** The existing Phase 7T archive combines the narrow fix with a synthetic Research staging module and tests. Do not install that archive wholesale as the bug fix. No separate narrow release package was assembled in this read-only phase. Owner-approved minimal packaging, current baseline verification, acceptance and exact installation/rollback actions remain prerequisites to installation.

## Reviewed evidence and limits

Reviewed [7T candidate](PHASE7T_MEMORY_RELEASE_CANDIDATE.md), [7T diff](PHASE7T_MEMORY_DIFF_REPORT.md), [7T gates](PHASE7T_MEMORY_INSTALLATION_GATES.md), [7G contract](PHASE7G_MEMORY_CONTRACT.md), and [7S Linux results](PHASE7S_MEMORY_LINUX_TEST_RESULTS.md), together with the exact local baseline/work store and candidate manifest. The local eight manifest-listed payload/evidence files were independently size/hash checked; the archive SHA-256 was recomputed and matched. This confirms local candidate identity, not current installed server state.

Phase 7T compared the installed 34-file baseline allowlist successfully before and after its work. Its installed target was `/opt/alfred-obsidian-v1/releases/4d5ba29bd3027e74c808a8feaf1b5dadfded22f0` via `/opt/alfred-obsidian-v1/current`; source is below `source/`. That was a point-in-time source comparison, not an entire installed-tree audit or database inspection. Service active/running observations were not a full application health test.

## Independently releasable correction

The duplicate branch currently selects the original memory's identity/provenance/content, then incorrectly returns literal `approved`. The candidate adds the existing `review_state` column to that SELECT and returns that row value. A duplicate of a pending or rejected memory therefore reports pending or rejected; an approved row still reports approved. There is no duplicate-branch UPDATE and no approval, promotion or edit acceptance.

Only `focused_v1/store.py` changes. Existing response keys (`id`, `review_state`, `saved`, `duplicate`) and provenance checks remain. Identity, assignment, deletion checks and nonduplicate creation are unchanged. No Research module, codec dependency, route, schema, grant, configuration or Obsidian source change is required. The existing duplicate branch's kind comparison policy is unchanged and outside this fix.

The changed response value is intentional observable behavior: clients must not treat duplicate success as approval. Returning an approved original row while its replacement edit is pending does not approve that edit. Unchanged Obsidian files support source compatibility; they do not prove all downstream consumers tolerate the corrected value.

**Database migration required for narrow fix: NO.** It reads an existing column; no DDL, backfill, review-state rewrite, new tables or `user_version` change is needed. The core source retains version 3. No live database was inspected, and no production database access is necessary for this release-decision analysis.

## Supporting acceptance evidence

Phase 7S's isolated Linux control `__main__.DuplicateStateComparison.test_duplicate_create_actual_pending_rejected_approved` failed on untouched baseline with exit 1 and the expected `approved != pending` assertion, then passed against modified MemoryStore with exit 0, completing pending/rejected/approved and unchanged-row assertions. The baseline stopped at the first assertion; it did not independently complete rejected/approved cases.

The corresponding extension method `test_research_memory_stage.MemoryResearchStageTests.test_duplicate_create_actual_pending_rejected_approved` also passed. All seven authorized synthetic extension methods passed with no failures/errors/skips on Python 3.12.3. These are bounded compatibility evidence, not production Research authorization. The separately defined pending-edit/authorization method was not one of the seven Linux methods.

The prior wider Mac comparison retained the same 17 failures, 3 errors and 3 skips on baseline and modified trees; it is not a clean full regression pass. Full Linux Memory regressions and the other 16 extension methods have not been established by these seven passes.

## Research material still test-only or disabled

`focused_v1/research_stage.py` is an added synthetic implementation, excluded from the narrow release. Both TestAuthority and ResearchStage require explicit `test_only=True`, `production=False`; authority uses in-memory issued actor/attestation/grant state, not an approved production signature or credential boundary. No production route is added to the existing server.

Real `promote` and `dispatch_research` always deny. `simulate_promotion` produces simulated, nonproduction states/receipts, not real authorization. Delete/export remain unavailable pending policy. Test schema initialization explicitly creates four research_stage tables with staging metadata version 1; this is not an approved production migration. Candidate, attestation and receipt contracts carry staging/test versions. Scoped retrieval, validity/revocation and digest/provenance behavior are demonstrated only within this boundary.

`tests/test_research_memory_stage.py`, its synthetic fixtures and TestAuthority are test-only. Research dependency records identify codec/fixture dependencies for staging; those dependencies are unnecessary for the one-file correction and are not a production runtime approval. Do not remove guards, expose simulated methods, or copy test grants into production.

## Production Research contracts requiring owner approval

- Memory component-owner approval of a newly reviewed production-capable implementation and integration into the existing service, with exact files, dependency layout, routes and service actions. This candidate has no enabled production entrypoint.
- Host-issued principal, tenant/company, task and purpose binding; explicit independent writer, verifier, Memory-owned promoter and scoped specialist-reader grants. Start Personal-only; unregistered companies deny. No default Research principal, Director, verifier, bridge token or category may inherit promotion authority.
- Genuine independent verification authority, issuer/signature or authenticated boundary, permitted provider/model/execution and factual-evidence policies, contributor separation, expiry, revocation, rotation and restore generations. Synthetic attestations remain permanently ineligible.
- Production candidate/receipt/schema versions, canonical digests, sizes/time semantics, evidence provenance, policy/classification binding, idempotency/CAS/reconciliation and distinct commit/promotion/fresh retrieval contracts.
- Production schema constraints/indexes/migrations and old-reader compatibility; lifecycle, retention/hold/delete/tombstone/export policies; currentness and invalidation ordering.
- Consistent database/WAL backup and recovery plus separately protected deletion/trust/grant generations; rehearsed migration, incompatible-open and rollback behavior. No migration utility is approved by this candidate.
- Broader Memory/Obsidian/client regressions, unresolved historical failures, exact live canary permissions/budgets and rollback. Obsidian export/Sync/HQ requires separate projection/receipt/trust approval; none follows from test success.

## Separate acceptance and rollback gates

| Requirement | Narrow existing-Memory fix | Eventual production Research integration |
|---|---|---|
| Owner acceptance | Approve only the exact store diff/hash and truthful response semantics; review duplicate-response consumers | Approve all production contracts above and a new production-capable version |
| Artifact | Separately versioned, integrity-checked minimal payload with only store.py as changed runtime source; preserve prior immutable release | Reviewed complete production dependency/file manifest; exclude synthetic trust and test fixtures from runtime authority |
| Regression | Accept 7S control evidence and an owner-defined bounded synthetic regression plan for create/duplicate states, no mutation, provenance/task scope, deletion/suppression/hold, pending edits and relevant clients/Obsidian; assess inherited failures explicitly | Expanded lifecycle, trust, grants, schema/migration, concurrency/recovery and existing-service regressions, plus separately permitted canary |
| Installation | Fresh exact baseline match; approved existing-service release/switch actions and health criteria; no added Research routes/grants/schema | Approved backup/migration, routes, grants/trust, live permission scope, service actions and fresh-read acceptance |
| Rollback trigger | Response/client regression, failed health or unexpected writes/behavior | Authorization boundary, receipt/currentness, lifecycle, migration or service regression |
| Rollback action | Owner-approved switch to preserved baseline-compatible code and health verification; no schema downgrade, DB restore, vault rewind or grant/key changes needed for this source-only fix | Disable new entrypoints/authority safely, preserve operation/receipt/evidence history and invalidations; restore only through rehearsed schema-compatible recovery that cannot resurrect revoked/deleted knowledge |
| Rollback limitation | Reintroduces known false-approved duplicate response; existing stored states remain unchanged | Cannot blindly restore old DB/trust snapshots or treat simulated receipts as production acceptance |

No installation, restart or rollback command is authorized by this report. Exact existing-service actions must be approved in the installation review; do not overwrite a live source file in place or create another Memory service.

## Fresh installed baseline recheck

**Required immediately before installation.** Re-resolve current, compare installed `source/focused_v1/store.py` to the expected baseline hash/size in the inventory, and verify relevant unchanged source plus the owner's complete release map. Verify the proposed narrow payload hash independently and assess consumers outside the historical 34-file allowlist. Stop on drift; do not overwrite, silently rebase or reuse stale 7T approval. Any changed baseline needs a new diff and applicable acceptance evidence.

The 7T report noted additional installed modules outside its allowlist (including focused_v1 backup/history/ops/stage and Hermes plugin/dependency files, and Obsidian Hermes integration files). Their presence does not add them to the minimal patch; owner review must cover relevant response consumers. No current installed-baseline check was performed in Phase 7U.

## Remaining decision

The narrow fix is separable and ready for owner installation review. Installation awaits owner sign-off, minimal immutable artifact assembly, fresh baseline verification, agreed consumer/regression acceptance and exact service/rollback actions. Production Research remains blocked by missing approved real authority, routes, schemas/receipts/migration and operational acceptance. No production system was changed.
