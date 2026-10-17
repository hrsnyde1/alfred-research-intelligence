# Photon Linux installation gates

2026-10-16. **BLOCKED. No installation, Research connection or service restart authorized.** Linux source baseline matches; 25 isolated local tests pass. Those results do not prove loaded Linux runtime compatibility.

## Exact potential production source changes

Under /home/alfred/.hermes/hermes-agent/:

| File | Proposed action |
|---|---|
| plugins/platforms/photon/sidecar/index.mjs | Modify: separate Research app attachment and explicit project dispatch |
| plugins/platforms/photon/sidecar/research-project.mjs | Add: dedicated Research connection/cache/transport ledger |
| plugins/platforms/photon/adapter.py | Modify: project-aware requests and terminal Research ingress lane |
| gateway/photon_research.py | Add: trusted ingress validation, reserved gate and scoped hook |
| gateway/run_inbound.py | Modify: early Research guard |

send-format.mjs and installed SDK packages remain unchanged. Exact original/modified hashes are in staging/photon-two-project-v1/SOURCE_INVENTORY.json; the Linux originals match. Reverify immediately before any separately approved installation and stop on drift. This is a partial patch workspace; never replace the entire installed Hermes directory with it.

Additional approved configuration would include protected Research project references, nonsecret binding metadata, one exact served Research profile/route and one research_project_intake plugin handler. Their effective installed file paths are unverified; do not invent or install guessed config. No production credential files were inspected or copied. No changes to Development observer/service, Memory, Obsidian, existing Personal credentials or line are proposed.

## Protected references and permission requirements

Preserve existing PHOTON_PROJECT_ID / PHOTON_PROJECT_SECRET, sidecar token and Personal launch behavior. Proposed Research names:

- PHOTON_RESEARCH_ENABLED — absent/not 1 remains disabled.
- PHOTON_RESEARCH_PROJECT_ID and PHOTON_RESEARCH_PROJECT_SECRET — separately scoped protected references; no Personal fallback or cross-project reuse.
- PHOTON_RESEARCH_CONNECTION_REF — opaque owner-approved connection binding, available consistently to sidecar and guard.
- PHOTON_RESEARCH_LINE / SPACE / SENDER / PROFILE — exact owner-approved nonsecret binding metadata, privately administered.
- PHOTON_PERSONAL_LINE — verified unchanged stable Personal line for enabled-mode validation; shared-mode compatibility is unresolved.
- PHOTON_RESEARCH_STATE_DIR — suggested /var/lib/alfredphoton/research-transport-v1, not created. Service owner must approve a 0700 alfredphoton-owned nonsymlink directory, single-process ownership, retention and quota policy. It fits the existing ReadWritePaths by metadata; filesystem creation/access remains to be tested.

Only the bridge needs project credentials; the Hermes guard needs binding metadata. Secret-store mapping, service-user read permissions, inheritance and redaction require owner review. Do not copy values into reports, fixtures, Memory or task logs. The patch adds only built-in Node/Python dependencies; no package installation is required or authorized. Installed transitive SDK loading remains a runtime validation gate.

## Required owner approvals and evidence

1. Service owner supplies sanitized active launch metadata: exact Photon Node executable/version, bridge script/wrapper path, supervision model and source revision. /proc executable access was denied; do not use sudo, raw environment/argv or credential-bearing unit dumps to work around it.
2. Authorize isolated Linux fake-transport execution under proven filesystem/network controls, with no Research credentials or live SDK initialization. Validate active Node and Python versions, systemd-user ledger permissions/fsync, SDK dependency imports and full Hermes routing/plugin integration. This task ran only local copied-source tests.
3. Review complete patch against the exact installed source and independently review early admission bypass: its explicit sender/conversation authorization must be approved and all ordinary-agent/command/busy paths excluded. No model privilege from message text.
4. Approve genuine host-issued intake/registration authority and durable ACK obligations. Current Research intake remains offline-only. Scope source acquisition, execution, Memory and FINAL separately.
5. Verify project/line-instance, authorized requester, exact conversation, transport owner and served Research profile manifest. Owner-confirmed project provisioning does not supply those concrete mappings.
6. Review provider identity/accepted/unknown/delivery reconciliation semantics. UNKNOWN transport ledger entries cannot be cleared or retried merely to restore service. Single bridge ownership is required because locks are process-local; preserve dedupe history when capacity is exhausted.
7. Approve coordinated source/config installation and rollback only after staging passes. Review full SDK telemetry/log lifecycle and Research failure/reconnect behavior. No rollout command is authorized here.
8. Separately approve controlled real Research message/ACK and Personal control evidence, proving actual receiving/sending identities and no Personal fallback. No messaging in this task.

## Restart and dependencies

Both services report CanReload=no. Loaded Python and Node code require runtime replacement unless a supported alternative is independently established. Hermes Requires/After alfred-photon.service; both also Want/After alfred-development-intake.service. Neither has PartOf/BindsTo. Do not infer restart propagation or stop semantics solely from this list.

Owner must approve coordinated replacement of the actual external Photon bridge and Hermes, with quiescence/reconciliation of in-flight Personal work, one consumer per project and no process overlap on the Research state directory. If the sanitized launch manifest reveals another supervision relationship, revise ordering first. Existing Development observer dependency and all Personal settings remain intact. No restart, stop or reload has occurred.

## Installation and rollback boundaries

A later installation must verify candidate/baseline hashes, install only the approved source/config set with Research disabled, preserve state/ownership, restart under approved ordering and validate Personal before separately enabling Research. No guessed paths, force-applied patch or new Hermes instance.

Rollback first disables/disconnects Research while retaining terminal reservation and reconciling unknown sends. Preserve all Personal and Research pending/dedupe/delivery records. Restore coordinated bridge/adapter/gateway versions only after Research is detached; incompatible old/new protocol combinations and dual consumers are prohibited. Do not remove the guard before ingress is blocked, reroute Research to Personal, delete UNKNOWN records to resend, rotate credentials or rewind Memory/Obsidian.

**Exact next owner action:** provide the sanitized active launch/binding manifest and authorize a bounded Linux-isolated fake-transport compatibility run. Until those gates close, the recommendation remains BLOCKED for Linux installation readiness; Research remains disabled.
