# Research V1 — Phased implementation and Mac-to-Linux strategy

Status: Phase 0 planning only, 2026-10-15. Phase 1 requires explicit owner authorization. No source, test suite, dependency manifest, runtime data or services were created by this audit.

## Milestones and acceptance gates

| Phase | Bounded deliverable | Required acceptance evidence |
|---|---|---|
| 0 — Audit (this run) | Repository/tool inventory, architecture, gap register, staged plan | Three requested documents; facts/requirements/proposals/unknowns separated; no production modifications |
| 1 — Core contracts and isolated runtime | Versioned records; trusted environment context; durable per-environment task state/audit/outbox primitives; canonical packet hashing; fixed-model configuration validation and budget ledger | All four environments; forged tenant rejected; unknown scope denied; state/queue/budget isolation; duplicate request has one effect; crash/restart recovery; changed claim/evidence/scope invalidates digest; budget ceilings and cancellation; model substitution denied |
| 2 — Source adapters | Common bounded source result and offline fixtures for GitHub, web/articles, PDF/local documents, YouTube, Instagram, TikTok and X | Every category tests success/partial/auth-required/inaccessible/unsupported/error as applicable, malformed/oversize inputs and timeouts; pinned repository/file digests; traversal/symlink/submodule/redirect/SSRF flags; injection never executes; no invented media transcript |
| 3 — Research and independent verification | Director/lead/support workflow, model port, claim-evidence mapping, separate verifier and bounded rework | Self-approval denied; authenticated independent decision bound to exact tenant/packet; changed source requires new verification; unsupported claims cannot become trusted; rejected/needs-more-research remain unavailable; deadline/budget exhausted truthfully |
| 4 — Intelligence and proposals | Taxonomy, per-capability specialist matching, duplicate/version/conflict handling, scoped knowledge views and proposal-only CTO artifact | Multi-skill repository splits correctly; all 11 existing Development specialties covered; ambiguous match escalates; conflicting high-impact facts flagged; superseded facts excluded from current views; no proposal grants execution/install/publication |
| 5 — Memory/HQ simulations | Agreed logical ports plus explicitly fake candidate/commit/promotion/retrieval/HQ adapters; no vault access | Distinct commit/promote/read/export/Sync receipts; timeout reconciliation; replay has one effect; fresh authorized specialist sees approved citations; owner can query each HQ partition; company cross-read denied; revoked/deleted records absent from current retrieval |
| 6 — Communications and Mac acceptance | Fake dedicated conversation mappings, short ACK/final messages, durable notification delivery/recovery; complete offline pipeline | Crash at send/receipt boundaries; deduplicated final notifications; truthful partial/failure; all four environments end-to-end; synthetic/mock evidence clearly labeled; reproducible test report and digested staging inventory |
| 7 — Authorized Linux integration | Read-only discovery first, approved smallest adapters, staged rollout through existing infrastructure | Real ingress → research → independent verdict → confirmed Memory promotion → fresh specialist retrieval with citations → CTO proposal only → existing iMessage completion; company/HQ isolation, outage/restart and revocation tests; real receipts before operational PASS |

Dependencies: 1 precedes 2–3; 3 precedes trusted distribution in 4; 4 feeds 5; 5 feeds full 6. Linux discovery may later refine contracts, but live adapter activation and production changes are gated separately. Each phase produces test evidence and a gap update; a mock PASS cannot close a live contract gap.

## Recommended Phase 1 boundary

Implement only the standard-library offline core under the proposed package tree in ARCHITECTURE_AUDIT.md. Define records for later full scope now, while avoiding speculative external APIs. Use synthetic principals and separate temporary roots for Personal Alfred, Gabos Holdings Inc., Fintra AI and SC Products Group. Production identifiers remain configurable and unset until agreed.

Implement immutable authenticated context, version validation, one-source cardinality, explicit transitions, transactional task/idempotency/audit state, restart recovery, outbox primitives, canonical digest rules and fail-closed policy/budget checks. Budget tests use synthetic model IDs; no claim that a provider is configured. Production mode must reject missing approved role/model assignments. Preserve research/verifier actor separation in the contract even before model execution exists.

Do not implement live fetch, real model calls, platform authentication, Memory/HQ writes, specialist deployment, CTO submission, Photon sends or Linux services in Phase 1. No dependency installation is needed for the proposed core. Confirm target Linux Python compatibility later before selecting a packaging minimum; do not depend on Mac-only behavior or accidentally invoke Python 3.9.6 via `python`.

Proposed Phase 1 test command after tests exist:

```sh
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Required test groups: contract/cardinality validation; four-environment separation and tampered context; idempotency/retry races; transaction crash recovery; packet canonicalization and mutation; invalid transition and stale verdict rejection; independent actor checks; per-tenant budget reservation/exhaustion/release; missing or changed model assignments; outbox persistence. Use temporary directories, fake clocks and fault injection, with no network or real secrets. This command has not been run because no tests exist yet.

## Mac-to-Linux integration strategy

1. **Build portable offline evidence.** Keep fixtures synthetic and credentials absent. All Mac adapter receipts explicitly say simulated. Inventory source, configuration templates, schema versions and test output with digests at the later packaging stage. No transfer package is created in Phase 0.
2. **Authorize read-only Linux discovery.** Determine current availability and inspect only existing routing/runtime interfaces, redacted service configuration, Memory contracts, approved tenant mappings and CTO authorization boundary. Do not scan vault contents or assume historical paths are current. Record observed host versions and reconcile CONTRACT_GAPS.md with the owners.
3. **Map rather than replace.** Research attaches via the existing Hermes hook and Photon transport. Memory owns storage, promotion, retrieval authorization, Obsidian export and HQ sync. Development owns approvals, implementation, QA/review and releases. Missing host capability becomes an explicit owner-reviewed extension proposal, never an improvised parallel subsystem.
4. **Stage the smallest adapters.** Validate versioned request/response mappings and permission failures in a separately authorized isolated Linux staging context. Use allowlisted test principals and source fixtures. Verify Mac/Linux hashing and state compatibility, artifact digests and repeatable tests before changing host configuration.
5. **Review concrete rollout and rollback.** Provide exact files/config changes, approved service user and permissions, backup scope, migration compatibility, health checks and rollback steps. Installation, service changes and deployment require separate authorization. Preserve known-good Memory/Obsidian repair state and quarantines; never blindly restore old bridge or Sync snapshots after publication.
6. **Canary through real infrastructure.** Start with an owner-authorized low-risk public GitHub task in Personal Alfred. Confirm every stage through host receipts and fresh retrieval. CTO output remains a proposal; development execution and GitHub publication keep separate approvals. Add a public article and an accessible authorized media/document case, plus blocked-platform honesty.
7. **Validate all environments and HQ.** With separately approved test records, validate each company ingress, isolated execution/Memory and scoped specialist retrieval. Test partition-preserving owner HQ access and denied company-to-company reads. Exercise updates, conflicts, stale versions, deletion/revocation, retry and restart. A failed boundary leaves that integration disabled and V1 acceptance incomplete.
8. **Operational acceptance and handover.** Retain task IDs, source pins, packet digests, verifier identities/verdicts, Memory commit/promotion/read-back receipts, specialist authorization results, CTO proposal acceptance and actual message status. Record export/Sync evidence separately when selected. Supply operator recovery instructions and unresolved limitations. V1 is complete only when these real end-to-end tests pass.

## Failure and rollback principles

Research can resume from durable local task state without replaying committed effects. Ambiguous external timeouts require receipt lookup or idempotent reconciliation before retry. Host outages produce blocked/partial status rather than false success. Failures after promotion must not erase approved records by restoring an old database snapshot; use Memory-owned correction/retraction operations. Disable the Research route or new adapter if necessary while preserving existing Hermes/Photon/Memory/Development behavior.

## Phase 0 completion boundary

Created only `docs/ARCHITECTURE_AUDIT.md`, `docs/CONTRACT_GAPS.md`, and `docs/PHASED_IMPLEMENTATION_PLAN.md`. No commit/push, dependency installation, service startup, credentials change, vault access, third-party skill execution or Phase 1 implementation is authorized by these documents. Stop for owner review and explicit Phase 1 authorization.
