# Phase 7D — Smallest safe Mac implementation boundary

## Proposed first task: synthetic Personal canary contract harness

**Not implemented or authorized by this document.** The next requested authorization can be limited to local standard-library contract validation and synthetic tests, with no production adapter, network transport, credentials, Linux access or production enable flag. This advances reviewable integration semantics while component owners close live contracts.

The harness consumes synthetic equivalents of already reviewed Phase 7C logical fields and audit-established wire examples. Mark all harness events/results SIMULATED / NON_PRODUCTION. Any draft host schema must carry a separate proposed/test-only version; never label it an installed Hermes/Memory API. Missing production issuer/grant/assignment/receipt fails closed rather than receiving a default.

### Exact proposed file boundary

Create, after authorization, only `src/alfred_research/integration/__init__.py`, `src/alfred_research/integration/canary_contracts.py`, `tests/test_canary_contracts.py`, and a local implementation/test report. Names are proposed, not current files. The contract module should be pure validation/translation of supplied synthetic values with injected clocks and trusted test grants. It must not import HTTP/SSH/provider SDKs, start processes/services, create state outside temporary test roots, or deserialize untrusted data into an authority.

Keep accepted source/tests unchanged in this first task. Compose existing fixtures/contracts instead of changing the workflow to accept live data. If the proposed harness cannot use an existing interface unchanged, document the required seam for a later reviewed task; do not weaken a concrete fake-only check.

### Minimum behavior and test gates

| Boundary | What can be developed safely now after Mac approval | Required tests |
|---|---|---|
| Trusted Personal ingress | Proposed typed synthetic envelope binds issuer/event/conversation/requester/environment/objective/one pinned source and policy reference. Trusted test grant map establishes Personal scope; user text cannot supply it. Validate normalized Photon examples independently of any real transport. | Valid input; unknown/missing/forged subject/tenant/recipient; two sources; same event/same body replay; same event/changed body conflict; company text/injected instructions cannot alter scope. |
| Stable source/task identity | Pure operation identity and correlation from trusted issuer/event/conversation, original full-commit reference and actual supplied fixture digest; distinguish pending acquisition from materialized ResearchRequest. | Invalid commit/URL/digest, substituted snapshot, acquisition failed/missing, no placeholder pin; task ACK forbidden before materialization; repeat pins deterministic. No actual fetch. |
| Assignment/budget manifest | Test-only validation of required fields from PHASE7D_OWNER_DECISIONS.md using synthetic IDs/prices; fixed role binding, distinct verifier identity, finite ceilings/deadlines and missing-approval denial. | Substitution/missing fields, unbounded/negative limits, expired approval, same-principal/delegated self-verification, budget overrun/unknown billing remain blocked. No real price assumptions. |
| Memory semantic mapping | Synthetic examples retain source/evidence/packet version/digest/verifier/currentness/access and distinct candidate/commit/promotion/retrieval identities. Validate proposed semantics; do not generate real promotion tokens or pretend existing Memory create performs them. | Forged/mismatched/stale/synthetic-as-production receipt denied; commit not promotion; promotion not fresh retrieval; expired/disputed/revoked/superseded denied; correct citations survive. |
| Completion and recovery | Pure receipt projection models currentness, ambiguity and truthful notification intent using existing test fixtures; history stays immutable. | Later failure invalidates cached success; stale prepared notice withheld; already-delivered history not rewritten; missing outbox evidence blocks completion; replay/concurrent composition has one logical identity. No actual send. |
| Isolation | Test Personal allowlist with all other environment contexts explicitly denied; preserve existing four-environment suite. | All 12 unequal ordered pairs in boundary tests where applicable, copied grants/receipt/event metadata denied; no cross-environment identity deduplication. |

Harness success proves local contract semantics only. It cannot close active authentication, entitlements, remote transactionality, message delivery or factual verification. Do not fabricate durable external effects to satisfy a pure test.

## Existing code and tests to reuse

| Existing path/interface | Reuse / important constraint |
|---|---|
| `contracts.py`, `tenancy.py`, `state.py`, `persistence.py`, `registration.py`, `budgets.py` under `src/alfred_research/` | Strict canonical hashing, issued contexts, one-source durable task, immutable revisions/verdicts, retry/budget/outbox primitives, Director provisioning and trusted recovery. Production paths remain disabled; test registration is not a host authority. |
| `sources/contracts.py`, `processor.py`, `policy.py` | Fixture tree/evidence/digests, safe bounded extraction and permissions. Fixture/user_supplied origins cannot describe a real acquisition. Network policy validation is not an active SSRF-safe fetcher. |
| `research/contracts.py`, `provider.py`, `workflow.py`, `journal.py` | Existing role roster, one lead, synthetic execution and per-claim assessment/checkpoints. ModelProvider protocol alone does not bypass _Runtime's SyntheticModelProvider requirement. |
| `intelligence/service.py` | Approved exact packet linkage, duplicate validity conflict handling, immutable knowledge history, specialist matching/proposal-only records. Current records are NON_PRODUCTION and Memory-ineligible. |
| `memory/contracts.py`, `fake.py`, `access.py` | Separate test receipt lifecycle, currentness and repair behavior. MemoryPort is incomplete for live coordinator reconciliation and no receipt is production authorization. |
| `workflow/contracts.py`, `coordinator.py`, `notifications.py` | Authenticated synthetic conversations, immutable result projection, final receipt reconciliation and stable logical notices. Current concrete fake dependencies and local snapshot locks must remain untouched in the first task. |
| `tests/test_workflow.py`, `test_memory.py`, `test_research.py`, `test_registration.py`, `test_hot_recovery.py`, `test_intelligence.py`, `test_sources.py`, `test_source_corrections.py`, `test_foundation.py`, `test_corrections.py` | Preserve all baseline cases; compose synthetic setup only. Existing crash diagnostics do not establish remote exactly-once behavior. Never copy test bootstrap authority snapshots into production. |

Paths in the first six rows are relative to `src/alfred_research/`. The model roster currently keys model assignments by environment/role; differing per-specialty models are a separate versioned extension, not part of this task.

## Later code versus component-owned work

After contract closure and separate code approval, Mac work can add typed host envelope/receipt codecs, complete injectable ports, genuine-versus-synthetic variants, fixed assignment validation and acquisition/attestation provenance. Actual production transports/adapters remain outside this first task. A future live coordinator must avoid private fake state/services and cannot hold a local fake lock as proof that remote currentness remains valid during sending.

Hermes must supply authenticated dispatch and pending acquisition/ACK semantics; Photon/Hermes must supply message operation lookup, authoritative ambiguity/delivery handling and stale-message/correction policy. Extend existing components only if owners confirm sufficient interfaces do not already exist; do not add a gateway or second inbound stream/retry engine.

Memory must own candidate authority, exact independent attestation checks, separate durable commit/promotion and full authorized fresh retrieval/currentness with replay receipts. Extend its interface only under Memory-owner review; do not migrate its database, use auto-approved capture, pass an Alfred-kind global bearer or write vault Markdown. Security/Operations owns host capability/registration trust and protection. Research cannot self-issue any of these grants.

## Proposed subsequent sequence and reversibility

1. Obtain D01–D08 decisions and required redacted component evidence; authorize the first harness separately.
2. Implement/validate the harness with no accepted baseline edits. Review new files and actual results; unresolved live rows remain blocked.
3. Close production schemas and authorize minimal Mac port/live-contract development separately; preserve simulation protections and baseline hash vectors. Component owners review any unavoidable host extension diffs before staging.
4. Obtain exact Linux staging destination/user/state/egress/backup/rollback and artifact authorization. Transfer only a newly reviewed release under that approval, not the frozen Phase 7A archive by assumption. Run isolated synthetic Linux tests before attaching production services.
5. Authorize component staging and scoped accounts/costs; prove independent trust and durable receipt reconciliation. Then approve a concrete single-message Personal production canary and reversible routing diff. No company/HQ/export/CTO deployment is bundled.
6. On failure disable only the new approved Research route/attachment, reconcile accepted/unknown remote effects and preserve history, tombstones and revocations. Any shared-service restart, data correction or separate notification correction needs the approved procedure; no database reset or blind rollback of published Memory.

## Validation required for the next task (not run here)

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
```

All 256 accepted tests plus new harness cases must actually pass; report actual counts, not the expected baseline as a fresh result. Use temporary synthetic fixtures and injected time, no network. Perform compilation without writing accepted-tree bytecode (e.g. compile source strings in memory) and standard-library metadata checks without installing/build isolation downloads. Preserve the frozen release inventory and archive; new work requires its own reviewed inventory later.

This Phase 7D delivers documentation only. The minimum next development authorization is the four-file synthetic harness and its report, not production adapters, transfer, Linux staging or a live canary.
