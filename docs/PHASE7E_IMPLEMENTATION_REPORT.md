# Phase 7E — Integration contract harness implementation and validation

## Result and exact file inventory

Implemented the authorized Mac-only harness, followed by the three targeted execution corrections. The original harness passed 283 tests; the correction adds 22 regressions. See PHASE7E_CORRECTION_REPORT.md for current validation and exact recovery behavior. Production integration remains disabled. Proposed internal interfaces are designed around the reviewed Phase 7C/7D semantics; they are not claimed to be deployed Linux schemas or production-ready adapters.

Original harness files:

1. `src/alfred_research/integration/__init__.py`
2. `src/alfred_research/integration/canary_contracts.py`
3. `tests/test_canary_contracts.py`
4. `docs/PHASE7E_IMPLEMENTATION_REPORT.md` (this implementation/test report)

The targeted correction modifies `src/alfred_research/integration/canary_contracts.py`, `src/alfred_research/research/workflow.py` and this report; creates `src/alfred_research/research/execution.py`, `tests/test_execution_corrections.py` and `docs/PHASE7E_CORRECTION_REPORT.md`. Existing tests, dependency manifests and release artifacts remain unchanged. Of the 77 original Phase 7A payload paths, only the working copy of research/workflow.py now differs, as explicitly authorized; the frozen inventory and archive are untouched. Archive SHA-256 remains `99d4384e1d00592ce193bbcf91678dda62ffe6509a49b3c107e57cb17225ead8`. No transfer, extraction or execution of the archive occurred.

## Implemented contracts and interfaces

All contracts use the existing strict `Contract` serialization/validation, reject unknown JSON fields and unsupported schema versions, and preserve canonical digests. Proposed schema names include `.proposed.v1`; existing receipt versions remain unchanged.

| Boundary | Implemented interface / behavior |
|---|---|
| Authenticated intake | `GitHubReference`, `ResearchIntake`, `ConversationBinding`, `IntakeMapping`. Trusted bootstrap maps issued test context to issuer/conversation/requester/recipient/environment/policy. Exactly one public-GitHub-shaped full-commit tree reference; body text cannot create authority. Stable operation identity includes tenant, issuer, conversation and event. Unknown/ambiguous mapping and changed event payload fail closed. |
| Pending acquisition | `PendingAcquisition`, `AcquisitionResolution`, `SourceAcquisitionPort`, `PendingSources`. Director-provisioned existing WorkflowJournal stores pending intake before any ResearchRequest/task. Immutable ACQUIRED/FAILED/UNKNOWN resolution; only complete matching fixture snapshot permits materialization. Original URL/commit and actual fixture digest survive. Existing ResearchStore request identity makes crash after task commit and concurrent materialization idempotent. |
| Provider and verifier | `ProviderPort`, `IndependentVerifierPort`, `FakeExecutionPort`. Existing SyntheticModelProvider and draft/verifier-proposal schemas only. Shared research/execution.py validates exact response and trusted plan scope/assignment/deadline/call ceiling/task cost/retry revision bounds, preserves the Director reservation convention and reconciles usage once. Malformed outputs create rejection evidence, not successful checkpoints. The Director still controls packet preparation/rework; historical outputs can reconcile after expiry without new model execution. |
| Genuine-versus-synthetic | `GenuineExecution` is a separate proposed untrusted data envelope containing invocation/output digests and external issuer/operation/attestation references. Parsing it proves no authenticity. `require_production_authorization` always denies. No fake execution, Memory candidate/receipt or notification becomes genuine by changing a marker, approval flag or provider name. |
| Memory | `MemoryIntegrationPort`, `FakeMemoryPort` delegate to accepted FakeMemoryAdapter: candidate submission, commit, promotion, fresh authorized retrieval, exact receipt reconciliation/outbox repair and completion snapshot. Commit/promotion/retrieval remain distinct; citations and verification links remain attached. Historical receipt reconciliation is distinct from current completion authorization. |
| Photon | `PhotonPort`, `FakePhotonPort` reuse accepted Notifications and fake transport. ACK requires a durable task/authenticated origin; FINAL requires the existing durable reconciled result and current completion-bearing receipts. Acceptance and delivery remain different; replay uses existing logical notice identity and lookup. No live send or transport guarantee is invented. |
| CTO | `CTOProposal`, `CTOProposalPort`, `FakeCTOPort`. Local immutable proposal only, no external acceptance claimed. Requires Director context, current durable packet/version/digest, approved exact decision, matching source revision/digest and actual source evidence IDs. Explicit eleven-specialist identifier mapping; proposal cannot grant execution/publication/installation/deployment. Replay conflicts reject. |
| Production gate | Every executable harness constructor defaults to denial and requires explicit `test_only=True`; `production=True` always rejects. Test bootstrap remains independent of message/source/receipt content. The accepted production-disabled foundation is untouched. |

No new Memory, orchestrator, messaging gateway, provider service or authoritative registration system was built. Fake services delegate to existing components rather than duplicate their lifecycle logic. Protocols are Python integration seams, not network endpoint allocations. Missing local lookup may return None; that is not authoritative remote absence and must never justify blind live resend.

## Durability, isolation and authorization evidence

New tests cover all 12 ordered unequal environment pairs for pending reads/writes/resolution, a valid requester with forged environment, unissued context, forged issuer/conversation/recipient/policy, multiple sources and unsafe URLs. Trusted Director provisioning happens only after scope checks. These are synthetic configured contexts, not invented live company registrations.

Pending and resolution checkpoints survive a separately launched Python process (exit 0); task-effect interruption is injected after actual SQLite submit and replay returns the same task. Concurrent materialization returns one task identity. Changed payload, snapshot, commit or resolution cannot overwrite immutable history. Failed/ambiguous acquisition cannot create a task or acknowledgment.

Provider tests cover fixed-model substitution, deadline and environment budget exhaustion, forged specialist delegation, wrong verifier identity/self-verification and late responses. Synthetic outputs cannot disable their simulation flag. Genuine-shaped JSON does not authorize production.

Memory tests exercise distinct lifecycle receipts, full candidate provenance, forged receipt rejection, currentness after revocation and concurrent duplicate commits. Photon tests exercise separate ACK/FINAL and ACCEPTED states, idempotent replay, forbidden premature ACK, forged completion text/company and stale completion after revocation. Existing baseline tests additionally cover the previously corrected Sync effect/checkpoint/cached-result/prepared-notification and commit/outbox crash paths. CTO tests reject invented packet/version/decision/source/evidence and cross-company submission.

## Original harness validation (historical; correction results in separate report)

| Command/check | Actual final result |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v` | **283 passed, 0 failures, 0 errors**, 40.192 seconds, exit 0. |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_canary_contracts.py' -v` | **27 passed, 0 failures, 0 errors**, 1.802 seconds, exit 0. |
| In-memory `compile(source_text, path, 'exec')` across source and tests | 41 Python files compiled successfully; no bytecode written. |
| Standard-library `tomllib` package metadata check | Existing setuptools package discovery includes the new subpackage; `dependencies=[]`; metadata unchanged. No install/build/download performed. |
| Accepted payload/archive digest checks | 77 payload hashes unchanged; archive digest above unchanged. |

The first full development run had 281 cases with one new-test failure and one new-test error: the fresh-process network stub was installed before stdlib SSL imports, and an actor mismatch raised a generic contract error rather than AuthorizationError. Both were corrected without removing assertions or modifying baseline tests. An intermediate full run passed 281; two additional delegation/deadline regressions brought the final count to 283. Final optional-return type annotations were also exercised by the 27-test targeted rerun.

The full suite independently printed the existing large-transaction diagnostics for all four environments: child exit **29**, old read-only preflight `SQLITE_READONLY_ROLLBACK`, successful SQLite-managed recovery with two committed revisions/verdicts and retry state preserved. Forged-registration diagnostic: child exit **30**, fabricated/edited/legacy JSON denied, database and hot journal unchanged, no trusted registration created. Original validity reproduction remained fixed (2000 versus 1001 conflict; -1 rejected).

Tests use temporary synthetic state. New test setup forbids socket creation; the fresh-process reader installs the same prohibition after imports. No provider calls, Linux access, private company data, production writes, Photon sends or imported code execution occurred. Compilation and metadata checks were read-only.

## Limits and first real canary blockers

1. Host authentication is still the accepted in-process test authority. Production capabilities, protected durable database registration, credential storage/revocation/rotation/restore and OS boundaries remain unimplemented and unverified.
2. Source acquisition is fixture resolution, not fetching. Only the deliberately narrow `https://github.com/<owner>/<repo>/tree/<40-lowercase-hex>` grammar is supported here; this is not comprehensive GitHub URL parsing. Fixture bytes must be supplied again to materialize a recovered resolution and must match its durable digest. FAILED/UNKNOWN resolution is terminal for that event; there is no implicit retry or new success. Real acquisition/usage ambiguity still needs component-owned reconciliation.
3. Fake provider outputs and verifier proposals are not factual attestations or authoritative verification decisions. Shared execution now enforces the trusted task cost and invocation limits; packet/rework and per-claim approval remain Director/IndependentVerificationAgent responsibilities. Real usage/pricing, cancellation, hard resource enforcement and timeout lookup are unresolved. Synthetic model replay before an output checkpoint is not proof of exactly-once external execution. Rejected/ambiguous usage is held, never silently refunded.
4. GenuineExecution is data only. Production output verification and genuine candidate/receipt variants must be agreed with host/Memory owners; no current port can accept synthetic artifacts for real promotion. All existing NON_PRODUCTION/Memory-ineligible records remain unchanged.
5. Memory and Photon ports use concrete accepted fakes. Their complete external schemas, authentication, operation lookup/currentness/CAS and delivery semantics remain unresolved. Local snapshot locks do not establish remote atomic currentness during send. Already-delivered messages remain immutable; live correction/cancellation requires an independently approved event contract.
6. Fake CTO records are local proposals, never remote receipts or Development grants. Ambiguous/unmapped specialists require escalation; this harness accepts only the explicit eleven mappings. Actual proposal reception remains a CTO-owned missing interface.
7. This is boundary preparation, not a new live end-to-end coordinator or a production adapter. The existing coordinator remains fake-only. Full crash/power-loss, filesystem isolation and durable registration acceptance on Linux still require separate staging authorization.

The first real Personal canary remains blocked by C01–C11 in PHASE7D_PERSONAL_CANARY_READINESS.md: actual trusted conversation mapping, ingress/pending-source contract, protected identity/registration, authorized GitHub acquisition, approved fixed models/budgets and independent factual verifier, Memory-owned candidate/commit/promotion/full fresh retrieval/currentness, Photon authoritative delivery reconciliation and approved staging/rollback. Component owners must provide redacted signed-off evidence; owner policy acceptance alone cannot create these interfaces. No auto-approved Memory capture, global Alfred bearer or synthetic APPROVED verdict may bypass them.

Stop here for owner review. No production adapter, Linux staging, provider call, archive change, deployment, commit or push is authorized or performed.
