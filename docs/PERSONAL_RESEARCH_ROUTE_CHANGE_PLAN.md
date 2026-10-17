# Personal Research route — minimal change and installation proposal

2026-10-16. **BLOCKED; local proposal only.** No configuration, profile, hook, account, conversation, consumer, service or Research runtime was created/activated. No Linux write, restart, live message, credential access, provider call or Memory write occurred.

## Required closure before an exact installable diff

Read [route contract](PERSONAL_RESEARCH_ROUTE_CONTRACT.md). The SSH account cannot inspect the active service home. No actual Research conversation/recipient/sender/profile is identified, and current effective Personal routes, multiplex setting and hooks/plugins are unknown. Therefore an exact installable file path/diff cannot honestly be supplied. Current local config at /home/alfred/.hermes is not proven to be the service config and may contain secrets; do not edit or copy it as a substitute.

Owners must provide a nonsecret redacted snapshot/version of active routing, served profiles, hook/plugin registrations, existing receiving adapter owner/account, ordinary Personal space and ONE selected existing distinct Research space with permitted members/sender. Supply the effective HERMES_HOME/config-layer location and approved schema, not environment/config dumps or secret values. PHASE7F findings are absent from the inspected documentation scope; no implicit approval is inherited.

## Smallest proposed configuration delta

After values and runtime support are approved, append exactly one route to the COMPLETE existing gateway.profile_routes list, without replacing/reordering any existing entry. This is a non-installable rendered template. All angle-bracket values are unallocated; leave disabled in preparation:

```yaml
# Proposed new row only; NOT a standalone replacement for gateway/profile_routes.
- name: "personal-research-intake-v1"  # proposed local rule label, not an allocated identity
  platform: "photon"
  profile: "<OWNER_APPROVED_SERVED_RESEARCH_PROFILE>"
  bot_profile: "<EXISTING_RECEIVING_ADAPTER_OWNER_PROFILE>"
  chat_id: "<EXISTING_DISTINCT_RESEARCH_SPACE_ID>"
  user_id: "<VERIFIED_NON_FALLBACK_OWNER_SENDER_ID>"
  enabled: false
```

bot_profile is the existing transport owner's profile, NOT automatically the Research target profile. Only if independently verified as the default owner may it be null/default under the current parser. Quote IDs exactly. user+chat specificity is 20; existing thread/user combinations can outrank it, and equal-score ties choose the first row. Reject overlaps/duplicates during installation review, rather than reorder Personal entries or rely on tie behavior. Profile must already be in the approved served set or be prepared under separate profile authorization.

Do not change gateway.multiplex_profiles by assumption. If it is not already effectively enabled, enabling it is a broader gateway change requiring separate review and regression acceptance. No second Photon platform configuration, instance, credential/account or inbound reader is proposed. Preserve Personal account/profile/default route and ordinary conversation exactly.

The adapter binding is the versioned route-contract proposal filled with actual approved values. `enabled`, host principal and transport owner are proposal/host policy fields; do not paste them as new fields into HermesResearchRoute, whose existing strict codec rejects unknown fields. Map research_profile to its profile, sender to sender_id and approved requester principal to requester. Record route_ref/policy_ref and Personal-only grants; no company rows.

## Minimal host attachment still required

A routing row is insufficient. Existing agent:start HOOK.yaml handlers see a 500-character preview with no platform event ID, and their returns cannot consume the turn. They must not implement intake by hashing the preview or run Research alongside an ordinary agent.

The candidate existing seam is PluginContext.register_hook("post_gateway_admission", callback). It carries full normalized text, message_id and source snapshot under routed profile scope and can return `{action: handled, reply: text}`. This is a plugin lifecycle registration, not a HOOK.yaml agent event. It is not a complete authenticated boundary:

- The callback lacks raw Photon sender and receiving transport reference; source.to_dict() cannot distinguish sender fallback or independently attest recipient/account.
- pre_gateway_dispatch can observe the full raw event earlier, but it runs BEFORE authorization, permits text rewrites and falls through on failure. An observation there cannot itself authorize Research.
- post_gateway_admission falls through to the ordinary agent on missing/failed/timed-out/invalid callbacks. Existing busy/running-session, slash-command and pending-reply lanes can bypass it. Merely returning a handled denial in the happy path does not close these failure paths.
- With a user+chat route, an unknown sender may miss the new row and fall through to an existing Personal/default route. The dedicated Research conversation needs an independently enforced reservation/deny policy, not body-text classification.

Before installing a route, separately approve a narrow existing-Hermes host change that supplies immutable authenticated provenance/current capability and enforces fail-closed handling of the RESERVED conversation across all lanes, including exceptions, timeouts, missing plugin, replay/queue/startup recovery and unauthorized sender. Outside that conversation it must leave Personal routing and processing unchanged. Determine whether an existing owner-supported guard already provides this under redacted runtime evidence; if not, authorize a specific minimal implementation/test diff. No such change or new public endpoint is implemented here. Do not create another orchestrator or Photon consumer as a workaround.

The tested Research adapter is offline-only and cannot be connected to real traffic unchanged. Authorize reviewed genuine host-capability/durable-registration variants while preserving test markers, and an authentic acquisition contract. Do not substitute OfflineAuthority, fixture snapshots or synthetic materialization for production authentication. Intake-only acceptance must not trigger models, Memory writes or Research execution.

## Proposed owner-controlled installation phases — not executed

| Phase | Exact required action/evidence | Stop condition |
|---|---|---|
| 0 — identity/config closure | Component owners supply filled manifest, active route/hook snapshot and distinct Research space membership/account evidence; pin source/config revisions | Any unknown ID, fallback sender, ambiguous route, unserved profile or wrong service-home path |
| 1 — local/staging boundary review | Authorize genuine host/registration and reserved-conversation guard changes at existing seams; run all existing 332 tests and new host-boundary cases on synthetic isolated input | Any fail-open agent/model path, source-digest fabrication, mixed Personal scope or synthetic trust |
| 2 — disabled preparation | Prepare versioned disabled row + bound identity policy + exact host attachment files, hashes, ownership/permissions and rollback diff in owner-approved staging; preserve every old Personal row and credential | Need for unrelated routing/config/account changes; unresolved global multiplex impact |
| 3 — isolated integration acceptance | Test copied/redacted config with existing Hermes matcher/loader and owner-supported profile runtime; no new inbound subscriber. Prove signed/capability event-to-pending, receiver return and exception/timeout handling | Plugin absence/failure falls through; raw sender/receiving identity not preserved; duplicate consumer/delivery ownership |
| 4 — installation review | Owners approve exact effective files/diffs/hashes, activation flag, current route revision, state path/registration authority, service action and stop/rollback criteria | No exact installable diff or approved reload method; live authority incomplete |
| 5 — separately authorized activation | Apply ONLY reviewed Research row/binding/attachment with compare-and-swap/current-revision checks and owner-supported atomic config publication. Verify unrelated config/Personal route hash projections unchanged | Concurrent config drift, broadened sender/company grants, change to Personal/default route |
| 6 — bounded live acceptance | One owner-approved existing-conversation request and acceptance-only ACK; no providers/Memory unless separately approved. Observe exact same authorized return conversation and current grants | Unknown send outcome, incorrect receiver, fallback identity, synthetic trust or any completion claim without genuine evidence |
| 7 — later FINAL | Separately approve genuine acquisition/execution/verifier and truthful notification contracts; prove current result-to-original-conversation link | Intake ACK alone or synthetic work cannot justify this phase |

No actual configuration target or installation/reload command is fabricated. Both relevant system units report CanReload=no. Profile hook registries cache loaded handlers; copying files is not proof of hot reload. Owner must identify an existing supported in-process reload/attachment mechanism and test its exact scope, or separately approve a precise alfred-hermes.service restart/window. No Photon restart should be necessary merely to add a conversation route; if one is found necessary, stop for a revised owner review. Do not call systemctl reload based on assumption or restart shared services during this task.

Only the existing Hermes consumer may own /inbound. A GET to that stream would supersede its connection, so even a read-only probe is prohibited. Outbound uses existing Hermes delivery/Photon send; define one retry owner, stable ACK/FINAL identities and authoritative reconciliation before enabling it. Do not let the gateway synthesize an extra normal-model response or a parallel final obligation for a handled Research event.

## Permissions and owner sign-offs

- **Personal owner:** exact existing dedicated space, distinction from Personal chat, sender/member/recipient scope, permitted source/repository and ACK wording; explicit bounded live test message budget.
- **Hermes owner:** effective profile/config revision, served target, receiving adapter owner, unchanged Personal routes, genuine admitted-event capability/provenance, reserved-conversation fail-closed policy across all lanes, plugin lifecycle and exact reversible reload/disable action.
- **Photon owner:** existing account's access to selected space, explicit non-fallback upstream sender, inbound/outbound normalization, one current consumer, allowed same-space send and lookup/ambiguity/delivery semantics. No credential values requested.
- **Security/Operations/Research:** production Personal requester/Director grants, protected durable state/registration, authentication expiry/revocation/recovery, quota/retention/anti-rollback, exact isolated staging and later installation/service window.
- **Source/Research/verifier owners:** genuine authenticated acquisition and later provider/evidence/verifier authority. No live acquisition/execution is authorized by installing a route.
- **Memory owner:** only if a future workflow selects Memory operations; no borrowed Alfred/bridge/Development grant, candidate promotion or vault/export permission follows from routing.

## Rollback specification — after a separately approved installation

Rollback must be available before activation and be limited to the new Research behavior:

1. Activate the reviewed RESERVED-conversation fail-closed disable state before turning off its consumer or routing row. Pause new Research submissions through that exact conversation; preserve ordinary Personal behavior and the existing Photon stream. Removing a user+chat row first could expose the default agent and is unsafe.
2. Freeze new acquisition/execution/send work for the Research binding only. Retain immutable accepted envelopes, pending acquisition, task IDs and delivery obligations. Reconcile accepted/unknown sends by ORIGINAL operation and transport identity; no blind retry, new task ID or second inbound connection.
3. Use the recorded expected revision/hash to disable/remove ONLY the new route row and detach ONLY the new Research registration/attachment through the owner-approved lifecycle. Preserve any required deny/reservation policy until the owner explicitly repurposes the conversation or approves safe fallback. Restore a whole config snapshot only when it has no unrelated intervening changes; otherwise apply a verified inverse diff. Do not erase other profiles/hooks or overwrite concurrent changes.
4. If supported reload is unavailable, obtain the separately approved precise Hermes restart/window; keep Photon and existing Personal settings untouched. No generic shutdown/reset of Hermes/Photon/Memory/Development is a rollback step.
5. Verify actual Personal routing/consumer count and old route-policy projections, Research disabled/denied behavior and retained pending/delivery identities. Delivered notices remain immutable history; corrections, if needed, are distinct owner-approved same-conversation messages. No database reset, stale authority restore, Memory/Obsidian rewind, queue purge or published-result rollback.

Stop and obtain revised owner review if source/config hashes drift, safe reservation disable is unavailable, an external effect is ambiguous, an unrelated route changed or an unexpected shared-service action is required. Do not equate an absent hook/file with safely disabled Research under this fail-open host.

**Next action:** owners provide the exact nonsecret active-routing and selected existing conversation identity manifest, and authorize/review the genuine provenance + fail-closed host attachment. Only then can an exact disabled installation diff be produced for review. Current proposal is not installable and is not production approval.
