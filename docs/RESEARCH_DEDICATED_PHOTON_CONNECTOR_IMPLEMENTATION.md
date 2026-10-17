# Research-only Photon connector

2026-10-16. **Independent connection supported at installed SDK source level; local synthetic implementation PASS. Live installation/attachment not yet ready.** No Personal source, service, credential, conversation or history was accessed or changed except approved read-only source/hash inspection. No Linux writes, authentication, real messaging, Memory/Development changes or commits.

## Architecture evidence

Fresh SSH verified original Personal index SHA256 ef019d1d50e4ca680aede49276181f8eff8d396d9b7c22a73bb5da2b2d7bb8e4 and adapter841ed6cb6e2d392fcec33f8983dd34fffe677c6a8d40e442bc449e66beeb16e5. SDK package12.7.0 exports Spectrum through core. Installed @spectrum-ts/core/dist/index.js:4042 Spectrum(options) resolves per-call explicit projectId/projectSecret and creates platformStates/messageBroadcasters/lifecycle locally. Installed @spectrum-ts/imessage/dist/index.js:1883 clientForPhone selects dedicated client from space.phone; shared mode ignores line selector and is unsuitable. Separate processes isolate ambient SDK globals/lifecycle and create no competing Personal consumer. Existing unchanged sidecar is single-app; no shared bridge installation is used.

Line metadata is an authenticated project's configured dedicated stream label, not independently verified actual Apple receiving identity. Owner/provider attestation and controlled destination/From evidence remain necessary. Generic SDK support is not proof of provisioned project contents. We did not read active account metadata/credentials or initialize SDK.

## Exact local implementation

All new files are under staging/research-photon-connector-v1; existing application source remains unchanged.

- research-project.mjs: byte-for-byte reuse of reviewed ResearchProject/FileLedger, explicit project credentials, phone-pinned outbound lookup, scoped namespaces, UNKNOWN-before-send and no-blind-resend.
- connector.mjs: Research-only binding, injected independent factory, no Personal object/environment fallback, disabled default, durable pending envelope/message correlation, bounded text-only ingress, allowlisted health, separate protected credential file references. Intake is disabled by default and production attachment explicitly refused. Synthetic intake seam requires testOnly=true; this is not a production trust grant.
- main.mjs: separate process CLI run|health|send CONFIG [OPERATION_ID]. No SDK/credential access when disabled. 10s process authentication deadline; 10s send deadline; 5min initial run lease; no automatic reconnect/restart/renewal. Health snapshots every5s. Exceptions are generic; proposed service suppresses raw SDK logs. send reads text from stdin, never selects project from payload. Do not execute this CLI against real credentials yet.
- connector.test.mjs:17 fake-only tests; test-results.txt actual output.
- policy.synthetic.json: disabled, fake identifiers only; never suitable as live policy.
- research-photon.service.proposed: uninstalled candidate, separate UID/state and credential mounts, no Personal dependency/restart, no TCP/Unix listener. Requires Linux permission/mount/dependency validation before approval.
- SHA256.json: exact local inventory/digests, including reused module and proposed artifacts.

Each persisted inbound has project+line+space+message namespaced ID, fingerprint conflict detection, original authenticated stream sender/line/conversation, fixed profile/connection and stable research-pending correlation. Replay returns the same pending record; no duplicate task is created because no task is created at this boundary. Pending intake is neither task completion nor acquired source/packet digest. productionTrusted=false is retained. Full-commit URLs remain unacquired source text; no provider/model/Memory work.

Outgoing calls expose only operationId/text, use the fixed Research route/project and explicit phone. ACCEPTED denotes SDK acceptance, not delivery. UNKNOWN survives restart and denies resend. State cap1024 is inherited; exhaustion fails closed, no eviction/ledger reset. One process enforced by proposed flock. Pending/transport records include message text and private identifiers: private state must never enter source/logs/reports. No health output includes these fields.

## Hermes boundary

No existing unmodified Hermes authenticated Research endpoint is established. Existing adapter expects its existing single Personal sidecar stream; reusing it would risk replacing Personal's consumer. Do not open that /events stream or inject Research into the ordinary agent. Existing proposed research_project_intake hook/terminal guard is not installed and cannot be assumed available.

This implementation safely spools a versioned Research envelope instead. Future reviewed existing-Hermes attachment must authenticate connector UID via existing extension interface (or narrowly approved Unix socket extension), preserve exact project/line/space/sender/message/profile, register a genuine intake issuer and reuse PersonalHermesIntake/PendingSources contracts. Missing handler/profile returns UNAVAILABLE, never ordinary Personal. No socket or second gateway is implemented now. Until approved attachment exists, live connector can receive/store/send controlled Research messages but cannot execute Research tasks in Hermes. This is an explicit remaining integration blocker, not a working-end-to-end claim.

## Known limits

Linux execution of this new standalone entrypoint has not occurred. Service UID, config paths and mount destinations are proposals, not verified installed resources. Installed SDK dependency tree may contain symlinks or require libraries not covered by the proposed mounts; freeze/inspect closure and validate under an isolated Linux sandbox first. State ownership/symlink/ancestor security, service credential semantics and platform support require validation. Same trusted service UID can modify private ledger; this is not adversarial isolation from its own code. No promise of crash exactly-once delivery, infinite availability or complete upstream catch-up. Inbound malformed/unauthorized events quarantine without ordinary fallback; no private event diagnostics are emitted. Session expiry requires explicit restart after reconciliation.
