# Personal Hermes Research intake — pending Linux approvals

2026-10-16. **Production and Linux attachment remain BLOCKED.** The implemented library is isolated development, not a registered Hermes hook, Photon consumer, authenticated live issuer, source fetcher or enabled Research service. No Linux destination, profile, principal, conversation, account, credential or provider has been allocated. `fixture-*` identifiers in tests are synthetic only.

## Required host identity and route manifest

Hermes/Photon and the Personal owner must approve these exact fields and their source of authority before a live implementation or route attachment:

| Field | Required approval/evidence | Current status |
|---|---|---|
| `issuer`, host principal and authorization reference | Existing Hermes process identity and actual authenticated dispatch/capability issuance; verify ingress provenance, current grants, expiry/revocation, rotation and restart/restore generations. No token value is requested. | Unallocated; OfflineHermesAuthentication is a test fixture only. |
| `platform` | Existing Photon adapter, not an additional `/inbound` subscriber. Preserve authenticated event provenance through existing Hermes normalization. | Source evidence identifies Photon; active Research entitlement unapproved. |
| `profile` | Exact existing receiving Hermes profile and hook lifecycle, effective service-home routing, event callback schema/version, supported attachment/reload/restart and disable path. | No Research profile/hook registered by this work. |
| `recipient` | Actual receiving Alfred identity/account binding, distinct from sender and chat ID; establish which host fields attest it. | Unallocated. |
| `conversation_id` | Exact existing Personal Research `space.id`/Hermes `chat_id`; unique trusted route. Group membership/recipient policy and ambiguity handling must be explicit. | Unallocated. No text-based company routing. |
| `sender_id` | Actual independently authenticated permitted owner/platform sender, not a body actor field, display name or Photon sender fallback. | Unallocated. Unknown/fallback/ambiguous identities must deny. |
| `environment` | Authoritative Personal tenant alias mapping to `personal`; no Personal-to-company wildcard. | Local alias only, not a Linux identity/grant. |
| `requester` and Director capability | Existing Research principal bound to Personal, role, authorized state instance and current task permissions; host principal is separate. | Test-only OfflineAuthority; no production registration authority. |
| `route_ref`, `policy_ref` | Immutable owner-approved mapping/policy revision, replacement/revocation and recovery policy. A route change must not silently adopt old pending events. | Unallocated. |

Match `(issuer, platform, profile, recipient, conversation_id)` exactly, then require the exact permitted sender. Duplicate route keys are rejected even if identical or associated with different senders; no wildcard or most-specific fallback is implemented. Company route schemas support existing environment vocabulary as future data, but all non-Personal routes are rejected by this adapter and confer no registration/grants.

## Event normalization and idempotency agreement

Phase 7B observes Photon `{messageId, space:{id,type,phone}, sender:{id}, content:{type,...}, timestamp}` normalized into Hermes MessageEvent, with missing space refused and a possible sender fallback. The library intentionally does not guess the complete raw content/attachment parser, import the host application or treat raw Photon JSON as authentication. Host integration must approve the exact normalized text/source selection and provide receiving profile/recipient plus authenticated sender independently. One typed full-commit GitHub tree reference is supported; arbitrary URL/file/media intake is not implemented.

Approve `research_hermes_intake.v1`, nested `research_hermes_event.offline.v1`/`research_hermes_route.v1` semantics or reviewed genuine variants, and the following fixed encoding rules before any live schema publication:

- Message digest is SHA-256 of existing canonical UTF-8 JSON encoding of the exact message text string, not raw HTTP bytes, a signature or an acquired-source digest. No whitespace normalization is applied. Original objective and the single structured source are bound by the complete envelope digest. Host interpretation of a submission is trusted bootstrap input, never an unverified model claim.
- Operation ID is `hash_content(("research_hermes_intake.v1", "personal", issuer, platform, profile, recipient, conversation_id, event_id))`. `hash_content` uses sorted-key compact UTF-8 canonical JSON and ordered arrays. Sender, message and structured source are payload, not dedupe keys: changed payload cannot evade conflict by changing sender. All identity fields are bounded to 128 characters and exact/non-wildcard.
- `ResearchIntake` reuses the existing acquisition dedupe with issuer `"hermes-" + hash_content((issuer, platform, profile, recipient, conversation_id))`, original event and conversation IDs. Existing `ResearchRequest.request_id` remains `"host-" + pending_intake.operation_id`. These are separate correlation IDs; preserve the envelope's original host identities in audit.
- Identical duplicate Photon events resume the same immutable pending intake and return the same logical acknowledgment; changed text, objective, source or identity for the same scoped event fails closed. Scope and grant checks apply again to recovery and materialization.
- Source text/instructions are data; they cannot select sender, environment, profile, Director, provider, Memory permission or completion status. Exactly one typed submitted source is enforced, without guessing URL ownership from free text.

Current bounds: 65,536 canonical bytes/event, 128 durable Personal intake envelopes/index and 256 distinct offline host observation payloads. Identical observations reuse their issued capability and do not exhaust the observation bound. WorkflowJournal uses existing 5-second bounded locks, immutable fsynced checkpoints and Director provisioning. Quota exhaustion denies new intake without deleting dedupe history. Production retention, backpressure/compaction, encrypted-at-rest needs, anti-rollback, process supervision and cleanup require owner approval; no unreviewed deletion/eviction is implemented.

## Pending acquisition and acknowledgment gates

1. Approve one owner-selected public GitHub repository/tree at a full 40-hex commit and exact same URL/commit grammar as existing GitHubReference. Unpinned URLs, branches, non-GitHub URLs, zero/multiple structured sources are rejected; this is the deliberately smallest Phase 7C/7D scope.
2. Source owner must provide a genuine authenticated acquisition authority/receipt contract: exact request/environment/submitted locator/pin, independently observed commit/tree/content digest, acquisition operation identity, access/redirect/peer/size/time policy, current grant and authoritative reconcile/failure semantics. A supplied digest or `authenticated:true` JSON is never sufficient. No fetch is implemented; source.v1 requires a resolved revision/digest before task creation.
3. Agree pending/failed/unknown lifecycle and recovery without fabricated task or packet identity. The library reuses PendingAcquisition/PendingSources; its only materialization seam is explicitly fixture-only. `materialize_genuine_acquisition` denies unconditionally until a separately reviewed genuine authority exists. Do not relabel fixture bytes, origins or receipts as real acquisition.
4. Approve acknowledgment wording/timing: `INTAKE_ACCEPTED` means durable acceptance and `PENDING_ACQUISITION` **at acceptance**, not Research/task completion. It contains no packet digest and is not a send/delivery receipt. Replay preserves this historical ACK even if a synthetic fixture task was later created; query acquisition through its separate current contract rather than infer current state from an old ACK.
5. Existing Hermes owns any eventual ACK delivery obligation/retry. Agree exact correlation, authoritative accepted/unknown/absent/delivered lookup and single retry ownership with Photon before sending. Existing POST /send response `{ok,messageId}` is not recipient delivery; no sidecar call or outbound ACK was made here.

## Linux attachment and eventual Research approvals

Security/Operations must approve the existing Hermes extension attachment, least-privilege Research-local storage/runtime identity, protected host capability and durable registration implementation, Personal grant/route manifest, bounded isolated Linux staging and tests, retention/backup/recovery and reversible disable procedure. No mount, account, service configuration, restart or deployment action is authorized by this task. Do not copy offline authority/registration snapshots into production or remove `SIMULATED / NON_PRODUCTION` checks.

Before genuine Research execution, the existing unresolved provider/model/price/budget and independent verifier authority contracts remain required. Memory candidate/commit/promotion/currentness and specialist grants require separate Memory-owned approval; intake success grants none. This adapter does not call Memory or providers, register agents, export to Obsidian, start Development work or create another orchestrator. Shared-service restart, if an approved attachment eventually needs it, is a separate explicit owner action.

**Next approval:** Hermes/Photon + Personal owner supply the redacted authenticated callback/route manifest above, and Source/Security owners supply a genuine acquisition authority contract. Then authorize a separate reviewed genuine adapter/staging change; do not activate this offline capability fixture.
