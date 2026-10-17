# Photon two-project compatibility corrections

2026-10-16. **Implemented and validated in Mac-local staging only.** Both identified blockers have targeted before/after passing reproductions. **41 staged tests and all 347 Research regressions pass.** No Linux files, services, credentials or messages were accessed/changed in this task.

## Exact implementation scope

Workspace: staging/photon-two-project-v1/. Pre-correction snapshot: staging/photon-two-project-v1-before-corrections/. Existing installed baseline remains unchanged. The previous Linux test stage is also unchanged. Only staged candidate source, tests, patch/inventories and requested reports were updated.

Relative to the previous candidate:

- Modified plugins/platforms/photon/sidecar/index.mjs: authenticated caller dispatch, nonawaited worker startup after Personal listen readiness, fixed role/project audit fields and cancellable bounded Research delivery.
- Modified plugins/platforms/photon/adapter.py: separate Research caller credential resolution/header, with no Personal token fallback.
- Added plugins/platforms/photon/sidecar/caller-bindings.mjs: private issued caller capabilities and exact project permissions.
- Added plugins/platforms/photon/sidecar/research-lifecycle.mjs: bounded worker lifecycle/RPC/session management.
- Added plugins/platforms/photon/sidecar/research-worker.mjs: independently initialized Research SDK and scoped ledger, no inherited environment or forwarded SDK logs.

Previously staged research-project.mjs, gateway/photon_research.py and gateway/run_inbound.py remain unchanged. Against installed production, the proposed complete patch is now eight changed/additive files; unchanged send-format.mjs remains comparison evidence. No change to /usr/local/lib/alfred-v1.1/trusted_intake.py is needed or made.

Tests: added compatibility-corrections.test.mjs and immutable tests/fixtures/pre-correction-index.mjs; added one token-boundary method to test_guard.py; copied the previously reviewed sdk-source.test.mjs and nine public SDK source/package/type files into this self-contained test workspace. Original Research module/guard cases remain. No package installed. SOURCE_INVENTORY.json and TEST_INVENTORY.json record exact hashes/lengths; PHOTON_TWO_PROJECT_BRIDGE_DIFF.md contains all original/result source hashes.

Current bridge.patch SHA-256: **be1b8c0b900210f691b67e2e77cebea954b17909a9295d5f4edcbcacb29d632e**. Applied to an isolated baseline copy; all nine result file digests match. No patch was applied to Linux production.

## Correction 1: legacy Personal authority, not payload fallback

The existing x-hermes-sidecar-token credential authenticates a fixed legacy-personal host caller class. An absent project on its existing /send body resolves only to Personal. Existing Development notifications therefore retain exactly their body and credential. Explicit personal is accepted; explicit research is denied regardless of message text or scope supplied by that caller.

Research uses a **different protected caller capability**, PHOTON_RESEARCH_SIDECAR_TOKEN, sent as x-hermes-research-token. It must differ from the existing Personal sidecar token. Research authority requires explicit project=research and a reserved Research target; missing project/personal target denies instead of using a default. Research authority cannot access the common inbound stream, Personal actions or service controls. A present invalid Research token never falls back to a valid Personal token. Missing/unknown credentials deny both authorities; copied descriptors have no issued object identity.

Caller class/project/action are fixed audit labels. No token, message text, actual phone/conversation or body-supplied identity is logged. Shared existing Personal token cannot distinguish Hermes from Development individually; it identifies the already-trusted legacy host caller class. This preserves its permissions, not a new grant to unknown callers. Any need for per-process attribution is a separate owner-reviewed credential change.

The adapter resolves Research authority from protected scoped host configuration only for an originating Research ACK obligation and sends only its Research header. Missing/equal secret rejects before HTTP; it does not borrow Personal. Body metadata alone cannot request or resolve the capability. The existing terminal guard still protects Research intake; company/source text cannot select project, profile or environment.

## Correction 2: authentication cannot gate Personal readiness

Personal initialization is unchanged. The existing server begins listening first. The callback then asks the Research lifecycle to start without awaiting it. Research SDK imports/authentication run in a disposable worker thread inside the existing Photon process, not a new service, instance or inbound subscriber.

Defaults and ceilings:

| Control | Bound |
|---|---|
| Research initialization attempts | 1 per lifecycle; no automatic restart |
| Authentication/import readiness | 10 seconds, then worker termination |
| Send RPC | 10 seconds, then UNKNOWN/unavailable and termination |
| Research session lifetime, including SDK internal/background retries | 5 minutes, then unavailable/termination |
| Pending Research RPCs | 16 |
| Research shared-stream write attempts | 3, also cancellable by session termination |
| Test-only simulated deadlines | Milliseconds, never above production ceilings |

A timeout Promise alone would leave underlying SDK work capable of completing late; worker termination removes that late-connection path. Research failure/error/exit/session expiry affects only its worker/pending requests. The Personal app, listener and retry state are untouched. Worker receives explicit Research configuration with an empty environment, not Personal/caller credential variables. SDK stdout/stderr are consumed without forwarding; errors return generic unavailability. Both projects still share OS-process memory, so this is not adversarial secret isolation.

Parent-side cancellation removes only the Research consumer waiter; abort during drain does not clear/close the healthy Personal consumer. Research UNKNOWN ledger records and no-blind-resend behavior remain intact. Shutdown terminates Research independently while preserving existing whole-bridge Personal stop semantics. A new lifecycle has independent state; a stopped/timed-out one cannot revive from a late-ready event.

The five-minute lease is a deliberate bounded validation/canary policy, not indefinite production availability. Owner must approve it or separately review bounded renewal before live operation. Main event-loop timers require a responsive host; worker isolation avoids blocking that loop with SDK authentication but does not promise hard real-time scheduling under arbitrary host failure.

## Actual validation

Full relevant staged suites: **30 Node + 11 Python = 41 passed**, 0 failed/skipped. Full existing Research suite: **347 passed**, 0 failed. Final command transcripts/logs are in artifacts/audits/photon-compatibility-corrections-20261016/. Exact test names, commands and runtimes are in PHOTON_TWO_PROJECT_BRIDGE_TEST_RESULTS.md.

The Development reproduction runs the archived exact HTTP handler with its original body: old status400, corrected status200 through Personal without a body change. The startup reproduction executes the old awaited initialization block and proves Personal-ready remains false until auth resolves. Corrected tests prove Personal sends remain available during Research stall/failure, timeout terminates an actual disposable worker, and late readiness cannot resurrect it. A second actual worker test exercises the production worker protocol with only its SDK imports substituted by fake code; concurrent Personal and Research traffic/identities remain separate.

Additional tests prove token elevation denial, no Research-to-Personal default, unknown/colliding/copied authority denial, missing credentials, independent request/session/restart behavior, cancellation without Personal disruption and protected Research-only HTTP headers. The original 23 staged bridge/SDK checks remain included and passing. All synthetic state is temporary and removed; real provider packages/factories are not initialized.

## Remaining production gates

The prior Linux 23-test PASS belongs to the pre-correction revision. New worker creation/termination, resource ceilings, all 41 staged tests and credential-to-header integration require a separately authorized frozen Linux isolated run. No Linux execution was attempted here. Do not silently increase address-space/thread limits if the worker cannot fit the previously approved sandbox.

Installation needs current baseline verification, complete eight-file manifest, ownership/permissions, shared-client inventory, protected caller/project reference mapping, disabled launch precedence, coordinated maintenance/restart/rollback and Personal regression approvals. Live operation additionally requires genuine intake issuer/registration, actual Research profile/hook loading, line/sender/conversation mapping, provider UNKNOWN reconciliation, lease/renewal policy and explicit controlled messaging permission.

Earlier PHOTON_HERMES_ACTIVATION_AND_ROLLBACK.md and PHOTON_PROTECTED_CREDENTIAL_BINDINGS.md describe the superseded five-file/Development-edit/shared-caller design. Do not execute those procedures as-is: remove the proposed Development edit, include the three new modules and separate Research caller reference, and review updated worker termination/rollback before any installation. The updated production-candidate document records these gates; no final installation procedure is authorized by this correction task.

**Outcome:** the two compatibility corrections PASS in isolated Mac validation. **Minimum next step:** owner-authorized Linux isolated validation of the corrected frozen candidate. Research remains disabled and production unchanged.
