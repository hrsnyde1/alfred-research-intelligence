# Personal Research route contract

2026-10-16. **BLOCKED — not ready for route installation review.** A disabled, versioned proposal is prepared; the actual conversation/account/profile identities, effective route configuration and production authentication/consumer contracts remain unverified or missing. No conversation ID is invented or registered. No host configuration, route, hook, service or transport was activated.

## Inputs and inspection boundary

Reviewed PERSONAL_HERMES_RESEARCH_INTAKE_IMPLEMENTATION.md, PERSONAL_HERMES_RESEARCH_INTAKE_APPROVALS.md, PHASE7C_ADAPTER_SPEC.md, current `integration/hermes_intake.py` and its 27 tests. The prior result remains 332 passing Mac tests, including all 305 existing tests; no tests were rerun here. No PHASE7F findings document or reference was found under docs/ or artifacts/audits/; no Phase 7F sign-off is inferred.

Fresh read-only SSH inspection used `alfred@192.168.50.81`: nonsecret installed code, systemd/account metadata, configuration-path permissions and visible hook-directory names. No runtime configuration values, environment, credentials, logs, messages/chat history, sessions, databases or vaults were opened. No HTTP, Photon SDK, inbound subscription or send call occurred. Host code was read as text, never imported or executed. Initial local SSH sandbox denial preceded the approved read-only retry; no server sudo was used.

Evidence is under `artifacts/audits/personal-research-route-20261016/`: SOURCE_EVIDENCE.json, HOST_METADATA.json and SCOPE.json. Source observations establish interfaces, not the running process's loaded version, active configuration, upstream account rights or successful delivery.

## Existing verified interfaces

All source references below are relative to `/home/alfred/.hermes/hermes-agent/`.

| Interface | Verified current source behavior | Limit for Research |
|---|---|---|
| `gateway/profile_routing.py:56–96,133–185` | Conjunctive route discriminators; user=16, thread=8, chat=4, guild=2 specificity; first match among sorted routes; exact Photon comparison; receiving bot_profile must match transport owner | Target profile must be served; matching precedence is not sender authentication or tenant permission. Equal-score overlaps require explicit rejection/review. |
| `gateway/run.py:4384–4434` | profile routes are effective only when multiplex_profiles is enabled; rejects a matched unserved profile | Effective multiplexing/served-profile set not inspected. Do not enable it globally as an assumed one-row fix. |
| `gateway/platforms/base.py:4813–4857` | build_source stamps routed source.profile and a wire-invisible weak reference to the actual receiving adapter | Routed profile differs from receiving transport owner; serialized source cannot prove that owner. |
| `gateway/hooks.py:43–111,142–190` | Per-active-profile hooks/NAME/HOOK.yaml + handler.py, handle(event_type, context); registries loaded/cached by profile home | Generic lifecycle hooks are not an authenticated intake port; errors are nonfatal. No hot reload is established. |
| `gateway/run_turn.py:2168–2177` | agent:start gets platform/user/chat/thread/chat_type/session_id and message[:500] | No complete original message, platform event ID, raw sender provenance or recipient binding; do not hash this preview as an original intake. |
| `gateway/run_inbound.py:73–107,232–255` | pre_gateway_dispatch sees full event/gateway before normal authorization; can skip/rewrite; exceptions fall through | Pre-auth observation is not authorization; later hooks may rewrite event text. Not a fail-closed Research gate. |
| `gateway/run_inbound_consumer.py:1–60`, `run_inbound.py:1359–1367` | Existing post_gateway_admission consumer receives session_key, platform, source.to_dict(), message_id and full normalized text under routed scope; handled=True can return an optional reply without running agent | Fail-open on missing handler/error/timeout/invalid result. Busy/running-session and command/pending-reply lanes occur before this consumer. Payload omits raw_message and receiving adapter ref. Cannot safely activate Research by registration alone. |
| `hermes_cli/plugins.py:933–934`, lifecycle.py | Existing PluginContext.register_hook and lifecycle invocation; no replacement gateway needed | Plugin registration/permissions and active profile installation remain unapproved; this is distinct from HOOK.yaml lifecycle manifests. |
| Photon `adapter.py:796–825,889–931` | One existing GET /inbound consumer; space.id -> chat_id, messageId -> event/message ID, sender.id -> user_id with fallback; raw event preserved on MessageEvent | Fallback is sender.id OR space.phone OR space.id. Research must reject fallback and missing event IDs, not equate a chat ID with an authenticated owner. |
| Photon `sidecar/index.mjs:654–675,719–741,951–965` | Existing SDK stream receives multiple spaces, ignores explicit outbound echoes, emits normalized events. A second /inbound connection supersedes the first | A second subscriber would displace Hermes. Reuse the existing adapter and SDK account; do not open /inbound as an inspection probe. |
| Photon `adapter.py:702–703,1329–1331`, sidecar `1054–1063,1099–1119` | Token-gated sidecar requests; send(chat_id, text) -> POST /send spaceId/text -> SDK space.send -> ok/messageId | Token authorizes local sidecar access, not a Research sender grant or per-event signature. SDK acceptance is not recipient delivery or authoritative idempotency lookup. send() does not forward its reply_to/metadata parameters into this simple send path. |

A dedicated Research conversation can structurally share the existing Photon instance and account: the SDK stream is already multi-space and send resolves an explicit spaceId. Actual account membership/rights for a selected conversation are unverified. No second Photon process, account, inbound subscriber or platform registration is proposed. The existing Development observer in the sidecar is Development-scoped; it grants no Research authority and must not be repurposed or redirected.

## Current configuration evidence and access gaps

`alfred-hermes.service` is active/running as `alfredmsg` UID 984, GID 975, cwd `/var/lib/alfredmsg/hermes`, CanReload=no. `alfred-photon.service` is active/running as `alfredphoton` UID 983, GID 974, cwd `/home/alfred/.hermes/hermes-agent/plugins/platforms/photon/sidecar`, CanReload=no. The Hermes executable metadata is /bin/sh with no explicit --profile argument discovered; this does not prove a default profile or effective HERMES_HOME because wrapper/environment/config precedence remains relevant.

`/var/lib/alfredmsg` is 0700 and unreadable to SSH user alfred. Active-home candidates beneath it refused metadata/directory access. Their profile_routes, multiplex_profiles, served profiles, hooks and plugin lists could not be inspected. Credential-bearing runtime files were not opened to work around the restriction. `/home/alfred/.hermes/config.yaml` is readable to alfred but was deliberately not opened: it can contain credentials and is not established as the system service's effective configuration.

The visible, nonservice `/home/alfred/.hermes/profiles` contains developlement, developmentcto and developmentdev; each hooks directory is empty. This is not a census of the active service's profiles/hooks. Do not route Research to a Development profile or infer the active Personal binding from these names. Hermes source resolves home through context override/environment/platform default and layers config; cwd/account HOME alone is insufficient.

## Dedicated conversation selection and missing identities

No suitable actual Research space ID was discoverable within authorized nonsecret metadata. The suitable *shape* is an owner-designated EXISTING Photon space, distinct from ordinary Personal Alfred's space, already reachable by the current account, with verified permitted participants and one explicit owner sender. A distinct title or prefix in the same Personal chat is insufficient. Do not assume that a second DM with identical participants is a distinct platform space; owner must provide authoritative space identity/membership. No chat is created by this proposal.

| Required value | Established / missing |
|---|---|
| Trusted host issuer binding | Candidate existing process boundary is alfred-hermes.service / alfredmsg UID 984; exact issued principal/issuer identifier, capability and revocation/restore contract UNALLOCATED. OS UID alone is not a Research grant. |
| Transport origin | Existing Photon sidecar process UID 983 and authenticated Hermes adapter seam known; current account identity, adapter owner_profile and approved provenance attestation UNALLOCATED. |
| Receiving Research runtime profile | Actual target profile name, effective home, served status and fail-closed consumer installation UNVERIFIED. |
| Receiving recipient/account | Actual Alfred account/recipient identity and binding to this adapter UNALLOCATED. Neither UID 983/984 nor space.phone supplies it. |
| Existing dedicated conversation | Exact space.id/chat_id and chat_type/member/recipient policy UNALLOCATED; ordinary Personal conversation ID also needed to prove disjointness. |
| Authenticated requester | Exact non-fallback sender.id plus owner allowlist and mapped Personal Research principal UNALLOCATED. Display names, free-text sender/company or paired generic gateway access do not confer Research permission. |
| Research Director/state authority | Production Personal principal/grant, protected durable registration/state instance and authorization lifecycle UNALLOCATED. |
| Route/policy references | Owner-approved immutable route_ref/policy_ref, version, revocation and migration semantics UNALLOCATED. |

Request a redacted owner-produced manifest containing ONLY these nonsecret fields, current gateway.profile_routes/multiplex_profiles/served-profile and hook/plugin metadata, and signed owner approval references. Do not request tokens, raw config/env dumps, chats, numbers unrelated to the chosen binding or broad filesystem access.

## Exact normalized-field mapping required at the trusted boundary

| Adapter field | Required host derivation |
|---|---|
| event.event_id | Original Photon messageId, equal to the admitted MessageEvent ID; never a session UUID or newly generated ID. Missing ID denies. |
| event.conversation_id | Original space.id, equal to admitted source.chat_id and the reserved Research space. |
| event.sender_id | Explicit original raw sender.id, equal to normalized source.user_id; absence/fallback denies even when generic Hermes admits the source. |
| event.profile / route.profile | Approved routed Research profile Q from trusted route resolution, not message text. Receiving transport owner T is separately checked against the existing adapter and gateway bot_profile; do not substitute Q for T. |
| event.recipient | Owner-approved receiving account/Alfred identity bound to the actual transport. Neither space.phone nor a body destination establishes it. |
| event.issuer / host_principal | Genuine host issuer/capability bound to the existing Hermes service and current grant. UID 984 is evidence about the process, not an allocated wire issuer label. |
| message_text / message_digest | Complete approved canonical original text representation before preview truncation/untrusted rewrites. Raw SDK text and normalized event.text can differ; owner must approve exact representation/provenance. No digest from the 500-character hook preview. |
| route.requester | Current authorized Personal Research principal mapped independently from the platform sender; not a principal supplied by the message. |
| route_ref / policy_ref | Immutable current owner-manifest revision references, with explicit revocation and retained-pending policy. |

The current post-admission snapshot cannot alone satisfy the raw sender/transport/original-text rows. These are closure requirements, not claims that the live issuer or callback already implements them.

## Versioned route proposal

The following is a local **proposal document schema**, not an implemented Hermes config or an instantiable adapter binding. Null means genuinely unknown; no placeholder is a valid account/conversation ID. All company configuration is absent.

```json
{
  "schema": "personal_research_route_proposal.v1",
  "status": "BLOCKED",
  "enabled": false,
  "environment": "personal",
  "platform": "photon",
  "issuer": null,
  "host_principal": null,
  "transport_owner_profile": null,
  "research_profile": null,
  "recipient": null,
  "conversation_id": null,
  "chat_type": null,
  "authenticated_sender_id": null,
  "research_requester_principal": null,
  "research_director_principal": null,
  "route_ref": null,
  "policy_ref": null,
  "existing_personal_route_revision": null,
  "consumer": {
    "candidate_existing_seam": "post_gateway_admission",
    "authenticated_provenance_contract": null,
    "reserved_conversation_fail_closed_contract": null
  }
}
```

The eventual minimal Hermes routing delta is one conjunctive Photon/chat_id/user_id/bot_profile row to an approved served Research profile, leaving every Personal route, ordering, account, credential and transport untouched. This is conditional: actual routes must first be reviewed for overlaps; a wrong sender in a reserved Research chat must deny rather than fall through to Personal. Current matcher alone provides no reservation/deny row and current hooks fail open. That boundary requires a separately reviewed existing-host consumer/guard change, not invented config keys or model instructions.

## Intake and return contract

A future authenticated host callback must preserve original non-fallback sender, original event ID, receiving adapter/profile/account, conversation and canonical message representation before rewriting/truncation. After independent current authorization, derive environment/requester/route from the owner manifest, never the body. Post-admission source dictionaries alone are not that provenance. Full text alone is also not proof of the raw upstream sender. The live callback/receipt and reserved-conversation fail-closed policy are unresolved.

Reuse the tested envelope/operation correlation and one-source contracts: one full-commit GitHubReference, immutable accepted envelope, existing PendingAcquisition, same operation on replay, conflict on changed payload. Pending is durable before any ACK; no ResearchRequest/task/source digest until genuine authenticated acquisition resolves. Unpinned/unsupported/multiple sources deny. Current fixture-only materialization is not an acquisition authority and must never be used for real messages. No source/model/Memory call is authorized by route acceptance.

ACK wording proposal: “Research request accepted; source acquisition is pending. Research is not complete.” This is acceptance-only and requires durable pending evidence; acceptance does not mean a Photon send was delivered. Return via existing Hermes-owned delivery obligation to the bound receiving adapter and exact original authorized space, using a stable intake/ACK correlation. Do not use a home/default chat, message-supplied destination, new sidecar subscriber or parallel resend engine. `{action: handled, reply: text}` is an existing consumer return shape, not proof its default delivery ledger meets Research idempotency/currentness requirements.

The inspected Photon send path targets the same space but ignores its reply_to/metadata arguments. No native-thread reply guarantee or caller operation-key propagation is established; keep logical intake/event correlation in the approved Hermes obligation, and require a reviewed transport contract before promising more.

FINAL is a separate asynchronous notification after independently authorized genuine Research completion. Bind intake operation ID, originating conversation/recipient/transport, actual task/packet/version/verifier references and only actually completed stages. Reauthorize route, sender/recipient and current result before send; no rerouting on missing mapping. No Memory promotion/export/Sync/CTO success wording without separate authoritative receipts and permissions. No live FINAL implementation or authoritative Photon operation lookup/delivery is established. On unknown transport outcome retain/reconcile the original operation; never blind resend or rewrite delivered history. A source URL hash, synthetic APPROVED or intake ACK cannot authorize FINAL.

The tested adapter still requires exact OfflineHermesAuthentication and rejects production=True; production registration/acquisition are disabled. Supplying real IDs, installing a route or flipping test flags does not turn it into a live adapter. Reviewed genuine host authorization/durable registration/consumer variants are prerequisites to connecting real traffic.

**Decision:** interfaces and a minimal disabled proposal are documented. Installation review is BLOCKED on concrete identity/configuration evidence plus genuine authentication and fail-closed consumer/return contracts. See [change plan](PERSONAL_RESEARCH_ROUTE_CHANGE_PLAN.md) and [acceptance tests](PERSONAL_RESEARCH_ROUTE_ACCEPTANCE_TESTS.md).
