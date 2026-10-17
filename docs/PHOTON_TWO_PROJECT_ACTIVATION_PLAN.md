# Photon two-project bridge activation plan

2026-10-16. **Disabled staged candidate only. Do not install or connect.** Separate Personal and Research projects/dedicated Research number are owner-confirmed. No further registration is proposed.

## Configuration references

Preserve existing PHOTON_PROJECT_ID / PHOTON_PROJECT_SECRET resolution, sidecar token and all Personal route/feature settings. Research uses separate protected environment references; no values appear in staging reports:

| Proposed runtime name | Meaning / gate |
|---|---|
| PHOTON_RESEARCH_ENABLED | Absent or not exactly 1 means disabled; no Research initialization |
| PHOTON_RESEARCH_PROJECT_ID | Separate provisioned Research project identity |
| PHOTON_RESEARCH_PROJECT_SECRET | Research-only protected connection secret |
| PHOTON_RESEARCH_CONNECTION_REF | Owner-approved opaque project/connection binding, consistent between Hermes and sidecar |
| PHOTON_RESEARCH_LINE | Verified Research dedicated receiving/sending line |
| PHOTON_RESEARCH_SPACE | One approved exact conversation |
| PHOTON_RESEARCH_SENDER | One explicitly authenticated authorized requester |
| PHOTON_RESEARCH_PROFILE | One approved served Research profile |
| PHOTON_RESEARCH_STATE_DIR | Separate protected Research transport ledger directory; precreated 0700, service-user-owned, no symlink |
| PHOTON_PERSONAL_LINE | Verified original Personal line used to validate its stream when Research is active |

These are implemented proposed environment names, not proof of installed configuration. The installation owner must map protected secret-store references to them, preserving scope, preventing ambient Personal fallback and redacting all logs. Research credentials belong only in the bridge process, not Research Memory, fixtures, source, docs, GitHub or task logs. The Python guard needs only enable/connection/line/space/sender/profile metadata, not project credentials. Do not grant the intake plugin credential access unnecessarily. Environment inheritance and supervisor launch behavior must be verified in staging; no active environment was inspected here.

Missing/incomplete/reused Research bindings prevent its app from starting and leave Personal operational. The enabled-mode Personal line must be verified as a stable dedicated binding before activation. If Personal is shared mode, do not invent a number or weaken the check; return for a compatible owner-reviewed design. One process with two credentials prevents accidental routing errors, not credential isolation against a compromised process; stronger process separation needs explicit owner review.

## Hermes attachment

Install only the reviewed five-file delta from the exact baseline after independent source review. Unmodified dependencies and SDK patches remain existing components; do not replace the whole Hermes tree with this partial staging tree.

Use the existing profile routing schema for an exact conjunctive route: platform=photon, chat_id equal to the scoped Research route emitted by the connection, user_id equal to the approved sender, bot_profile equal to the actual transport owner, profile equal to the approved served Research profile, enabled only after approval. Preserve Personal rows/order. Route ID derives from project identity, line and space; obtain/verify it inside the protected staged connection, never from source text. Actual values and effective config path are unavailable, so no runnable YAML installation command is proposed.

Register exactly one `research_project_intake` handler through existing PluginContext.register_hook in that Research profile. Handler must use the trusted envelope passed by the guard, independently current Research issuer/requester grants and durable pending intake; return handled/reply only after durable acceptance. Missing/invalid/multiple handlers return unavailable. Existing post_gateway_admission is not a security boundary and is not used for Research. Current repository intake is offline-only: a genuine reviewed host issuer/registration implementation is a prerequisite, not a flag change. No acquisition/provider/Memory/final notification is enabled by this candidate.

## Required staging gates before installation approval

1. Recheck all installed baseline and dependency hashes against SOURCE_INVENTORY.json, plus exact SDK build/patch and effective config. Stop on drift; do not force-apply. Review the entire bridge.patch.
2. Obtain owner-attested project/line/instance, requester/conversation/profile and original Personal route manifest. No credentials or histories in review artifacts.
3. Authorize isolated Linux fake-SDK and Hermes integration tests. Validate two-app lifecycle, plugin discovery/profile scope, authenticated token boundary, state ownership under the actual service user, reconnect behavior and complete Personal features. Current Mac tests do not cover the full installed server.
4. Review provider/API guarantees for project-specific line provenance, outbound identity and authoritative reconciliation. UNKNOWN records must remain held; no manual deletion or retry until absence/delivery is established. Set an owner retention/capacity policy for the bounded 1,024-record ledger without evicting unresolved dedupe history.
5. Confirm single bridge ownership of Research state. File operations are fsynced/atomic but locking is process-local; overlapping old/new bridge processes must never share that directory. Supervisor replacement ordering must enforce this.
6. Review malformed-event, handler-timeout, missing-profile and unavailable-connection behavior, including no ordinary Personal fallback. Stage anti-forgery tests at the actual normalized ingress and verify no competing Personal consumer.
7. Approve installation source/config/state manifest and rollback compatibility before any production files are written. This task supplies no installation authorization.

## Service ordering and restart requirements

Changes to loaded Python adapter/gateway and the running Node script require replacing those runtimes; no supported hot reload is established (prior units report CanReload=no). Plan an owner-approved coordinated Hermes and Photon restart, with no overlap of consumers. If Hermes actually supervises its sidecar, determine that relationship first and use the existing supervisor rather than starting another process. If alfred-photon.service is the external sidecar, both alfred-hermes.service and alfred-photon.service need coordinated replacement. Effective ownership/launch config remains a gate; do not assume restarting one is sufficient.

First stage the reviewed code with Research disabled, verify original Personal behavior through separately approved controls, then separately approve enabling the Research connection and hook. Quiesce/reconcile existing Personal sends before replacement; preserve its credentials, line, caches' durable records and outbox. Do not stop/restart anything under this task.

## Controlled acceptance after separate authorization

Approve one controlled Research request and acceptance-only reply plus Personal control evidence. Prove actual Research project/receiving line, explicit sender/scope, correct served profile, no agent fallback and correct Research sending identity. Replay through an authorized harness must reuse one pending intake/ACK obligation. Test unknown outcomes without real duplicate sends. No task digest, genuine acquisition, provider execution, Memory promotion or FINAL is authorized by an ACK. SDK accepted messageId alone is not recipient delivery.

## Rollback boundaries

Disable Research ingress and outbound work while keeping its reservation guard terminal; stop/reconcile its app through owner-approved runtime replacement. Preserve Personal connection settings and all state. Keep UNKNOWN/accepted records and pending intake history; do not delete them to force retry or reroute to Personal.

Restore old bridge/adapter/gateway code only after Research is definitely disconnected and the updated adapter is no longer sending explicit-project payloads to an incompatible old bridge. Revert the coordinated source/config set atomically where supported, with separately reviewed service ordering and no dual consumer. Research events retained anywhere must remain quarantined; removing the guard first is unsafe. No phone deprovisioning, credential rotation, Memory/Obsidian rollback, second Hermes or second Personal subscriber belongs in rollback.

**Next owner action:** review the staged diff and synthetic evidence, provide the nonsecret binding/active-launch manifest, then authorize isolated Linux compatibility validation. Research remains disabled. No installation, restart or live connection is approved yet.
