# Personal Hermes Research intake adapter — implementation report

2026-10-16. **PASS for isolated implementation and regression validation; production/Linux attachment remains BLOCKED.** All **332 tests passed: 305 preserved existing tests plus 27 new intake tests**, with zero failures/errors/skips. No production activation, Linux access/deployment, real messages, live acquisition/provider calls, Memory API/writes, service restart, dependency installation, commit or push occurred. Existing fake-Memory regressions operate only on synthetic temporary fixtures; the new intake adapter has no Memory operation.

## Reviewed contracts and interface evidence

Read PHASE7C_CONTRACT_MATRIX.md, PHASE7C_ADAPTER_SPEC.md, PHASE7D_PERSONAL_CANARY_READINESS.md and PHASE7E_CORRECTION_REPORT.md, plus existing canary integration contracts, issued capabilities, ResearchStore/request/source contracts, immutable WorkflowJournal, source fixtures and canary tests. Reviewed local Phase 7B Hermes/Photon interface audit under `artifacts/audits/phase7b-20261015/PHASE7B_HERMES_PHOTON_CONTRACTS.md`. Its source observations are historical evidence, not a new Linux/runtime verification.

The existing Hermes seams are profile_routing.py and hooks.py. Photon already owns inbound NDJSON/message normalization; authenticated sender and receiver/profile mapping are separate host obligations. This library does not import the installed host application, create another orchestrator, listener, Photon platform adapter, `/inbound` consumer or outbound retry engine. No hook/profile/route was installed. Existing host evidence does not define a complete raw content/attachment parser, so the adapter consumes an explicitly authenticated normalized event rather than guessing one.

## Smallest supported input and authentication boundary

The implemented scope follows the existing first-canary contract: **Personal only, exactly one public GitHub tree URL at a full 40-hex commit**. Unpinned branches/URLs, other URL kinds, zero/multiple structured sources are rejected. General unpinned URL/file/media intake is not implemented; no placeholder digest is used to make those fit source.v1.

`OfflineHermesAuthentication` uses a separate injected OfflineAuthority and issued host context to attest an exact immutable ObservedHermesEvent. Only the exact issued event object is accepted: copied/deserialized JSON or a typed lookalike is not authentication. The host principal is stamped from its capability, never from message text, and must remain the same for later recovery. Identical observation payloads reuse the issued object; at most 256 distinct fixture observations are retained. The observe method is trusted synthetic host bootstrap, not a login or message-facing API. This is **not production Photon/host authentication**, a cryptographic signature or an existing Linux entitlement.

Default construction, production=True, missing authentication, missing routes and invalid grants all fail closed. A future genuine host issuer requires a separately reviewed authority/type; flipping flags, copying test snapshots or deserializing the offline event cannot enable it.

`research_hermes_intake.v1` preserves Personal environment, original issuer/host principal, platform, receiving profile and recipient identity, conversation, authenticated sender, platform event ID, exact message text/digest, original objective, one source reference and trusted route/policy references. `research_hermes_route.v1` can represent future known company aliases as schema data, but PersonalHermesIntake rejects all non-Personal configurations and registers/activates none.

## Routing, durable pending and replay

Routing uses the exact trusted tuple `(issuer, platform, profile, recipient, conversation_id)`, followed by exact sender authorization. Duplicate route keys, wildcards, unknown conversations/profiles/recipients and ambiguous sender mappings deny. Body/company strings and source instructions are inert data, including when they ask to change route, grant permissions or announce completion. Requester context is injected by the trusted route and must match its configured principal and Personal grant.

Operation ID is SHA-256 through existing canonical hashing of `(envelope schema, environment, issuer, platform, profile, recipient, conversation_id, event_id)`. Sender and submission contents are payload, not dedupe keys: rebinding a sender cannot evade the existing event conflict. The envelope digest binds all fields, including message text, objective, source and policy. Message digest is hash_content of the exact original text string; it is not source authenticity or a packet digest. Full tuple encoding avoids delimiter concatenation and includes receiving profile/recipient in existing pending-acquisition scope.

The adapter composes existing IntakeMapping, ResearchIntake, PendingAcquisition, PendingSources and WorkflowJournal, without changing their contracts or Research SQLite schema. A bounded Personal index (`hermes-personal-intake-v1`, maximum 128 envelope checkpoints) records the immutable envelope first, then creates the existing pending acquisition. ACK is returned only after both are durable. Duplicate events return the same ACK; changed text/objective/source/identity conflicts before another pending intake or task. The index uses existing Director provision/authorization, bounded file locks and fsynced immutable checkpoints. New intake over capacity denies without evicting replay history.

A crash between envelope and pending writes is repaired by recover. Recovery revalidates CURRENT issuer identity, route/policy, requester and Director grants, then restores pending acceptance without fetching, sending, executing Research or touching Memory. Host/route rebinding and revocation deny; stored observation JSON is not reissued as a new live event. Journal trust retains the existing offline boundary: trusted bootstrap and protected Research-local filesystem; hostile same-account checkpoint edits and production anti-rollback authority are not newly solved.

## Source and acknowledgment separation

Unfetched pinned sources have only a submitted URL/commit. They create no ResearchRequest, task or packet digest. `materialize_genuine_acquisition` always denies because an authenticated live acquisition authority/receipt contract does not yet exist. A caller-supplied hash or authenticated-looking JSON cannot resolve pending intake.

`materialize_fixture_for_test` is explicitly offline-only: it delegates existing complete matching fixture resolution to PendingSources and existing one-source ResearchStore.submit dedupe. The fixture digest hashes actual synthetic snapshot bytes, never a URL string. Wrong revision, substituted bytes and unknown intake deny. The same acquired fixture/replayed request creates one task, including after an actual crash immediately after task commit. The returned existing DurableTask has no new production-trust flag or schema change; the store remains production-disabled and existing downstream synthetic contracts remain intact.

`research_hermes_intake_ack.offline.v1` returns INTAKE_ACCEPTED and PENDING_ACQUISITION **at acceptance**, stable operation/envelope/pending digests, research_complete=False, production_trusted=False and SIMULATED / NON_PRODUCTION marking. These are intake/journal digests, not Research packet evidence. No send, delivery or final receipt is created. Replaying this historical ACK after a fixture task exists does not claim acquisition is still pending now; current acquisition status is a separate PendingSources reconciliation. Completion, factual verification, Memory commit/promotion and outbound delivery remain distinct and unimplemented by intake.

## Files and actual validation

Created only these application/test files; accepted source/tests and dependency metadata remain unchanged:

| File | Purpose | SHA-256 |
|---|---|---|
| `src/alfred_research/integration/hermes_intake.py` | Isolated attachment, typed envelope/route/ACK, offline host capability and existing pending/task composition | 90b3457416cf47e6cff5e126674dddcd49adae670f9c832044af88c14d246208 |
| `tests/test_hermes_intake.py` | 27 synthetic regressions | 8b458f21aa86730761276970f0dbbfa6f69311b4fc81d8db6d5f0b4f2bbda5b0 |

Documentation: this report and [exact pending Linux identity/route approvals](PERSONAL_HERMES_RESEARCH_INTAKE_APPROVALS.md). Evidence directory: `artifacts/reviews/personal-hermes-research-intake-20261016/`.

| Exact command/check | Final result |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_hermes_intake.py' -v` | 27 passed; zero failures/errors/skips; 0.719 s; exit 0 |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v` | 332 passed; zero failures/errors/skips; 41.101 s; exit 0 |
| In-memory source/test compilation | 45 Python files compiled; no bytecode writes |
| Frozen Phase 7E inventory | All 90 payload identities unchanged (89 original working-tree paths plus release-only RELEASE_README.md at its frozen location) |
| Frozen archive SHA-256 | unchanged `ec6dedd835e8c926d5e862a15d392c090e6831fbc84b41f1d5e6848d2c3fe63e` |

Validation used Mac Python 3.14.3. No claim of new Linux Python 3.12 compatibility is made; that requires separately authorized isolated staging. An initial new-test setup used the wrong existing registration snapshot helper name and was corrected to snapshot_for_tests; final runs above are clean. A prior full 332-test run passed before the final duplicate-observation capability reuse refinement; final reported results are from the refined code.

New test coverage includes valid pending intake with no task, identical replay and 300 duplicate host observations without consuming new capability slots, changed-payload rejection, forged/deserialized sender/company/environment/hash denial, unknown receiving identity, message/source injection, unpinned/multiple source refusal, unfetched/genuine-looking receipt refusal, missing/default/production authorization denial, duplicate/wildcard route refusal, future company schema without activation, requester mismatch, tuple scope uniqueness, concurrent duplicate acceptance, one-source fixture/task dedupe and substitution rejection, ACK trust/completion denial, current route/host revocation and rebinding, cross-environment recovery/materialization denial, interruptions on both sides of pending creation, and two real subprocess crashes with expected exits 37 and 38.

The crash children use current synthetic registration snapshots and temporary Research storage; sockets are prohibited in parent fixture and children. Fresh bootstrap recovery preserves pending and the exact ACK, and after task-effect crash preserves one task with the exact acquired synthetic digest. Full baseline hot-journal/forged-registration/Memory/workflow protections remain passing. No live key, credential, actual iMessage, provider, Memory endpoint or Linux system was accessed.

## Remaining approvals and next step

Production attachment requires a real host-authenticated callback, exact existing Personal profile/recipient/conversation/sender and policy/route references, approved Research principal/Director and durable registration authority, protected Linux state/runtime bounds, genuine source acquisition/receipt authority, and approved pending/ACK delivery semantics. Existing provider/independent verifier/Memory trust approvals remain separately required for later execution. Company identities remain unregistered and disabled.

The exact unallocated fields, digest/correlation mapping, revocation/recovery constraints and owner responsibilities are in PERSONAL_HERMES_RESEARCH_INTAKE_APPROVALS.md. No host IDs, profile, socket, token, Linux path or service actions are invented by tests. Next step is owner review of the local adapter plus redacted host identity/route and source-acquisition contracts, followed by a separately authorized staging plan. Stop after implementation/validation; no production activation is authorized.
