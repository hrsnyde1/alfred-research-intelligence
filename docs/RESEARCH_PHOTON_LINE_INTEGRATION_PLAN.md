# Research Photon dedicated-line integration plan

2026-10-16. **Prepared conditional design; installation BLOCKED on project/binding metadata and reviewed source changes.** Owner states Alfred Research already has a provisioned dedicated number. No creation or registration is proposed. Personal line/account/routing must remain unchanged.

## What is established

Read prior identity support/binding/route/activation documents and account capability decision. Fresh SSH read-only source/metadata inspection reconfirmed sidecar and adapter digests; details and exact call sites are in RESEARCH_PHOTON_OUTBOUND_IDENTITY_AUDIT.md. No nonsecret manifest/metadata file was found among the sidecar directory's top-level regular files matching those names. This narrow search is not a project inventory or proof that none exists elsewhere. Active credential-bearing configuration was not opened. Source uses one Spectrum project and automatic cloud discovery, not a static explicit client list. Active same-project versus separate-project assignment is **not established**.

[Photon's official cloud provider documentation](https://photon.codes/docs/spectrum-ts/providers/imessage) describes discovery of project-owned lines and explicit client subsets. [Connection/routing documentation](https://photon.codes/docs/spectrum-ts/providers/imessage/connection-and-routing) describes dedicated line selection and runtime discovery changes. Neither identifies this installation's project. Only a nonsecret owner/provider manifest can close that binding without reading credentials.

| Question | Current decision |
|---|---|
| Same project? | Unknown. Require owner-attested comparison: active service project reference equals Research provisioned-line project reference, yes/no, with opaque project and instance labels. No raw identifiers needed in reports. |
| Can existing credentials discover Research? | Yes conditionally if Research belongs to the same dedicated project and is included in the provider's authorized inventory. No local credential change would then be expected, but bridge safety changes remain essential. No actual token issuance or inventory API called. |
| Separate project? | Existing single-project app cannot be assumed to discover another project's line. Requires separately scoped authorization/client connection; do not replace Personal project credentials. |
| New service? | Same-project dedicated SDK can merge line streams in one app. Separate-project case needs reviewed multi-connection support in the existing process or provider-supported explicit clients with approved credential renewal. No second Photon service/consumer is proposed. |
| Authoritative inbound field? | Dedicated SDK attaches routing line as space.phone from its authenticated client stream; normalized raw event retains space.phone. This is a routing-line label, not an independent Apple alias-recipient assertion. Require provider/owner attestation of line mapping and reject shared sentinel/ambiguous labels. |
| Survives Hermes? | Raw MessageEvent retains event; generic source.chat_id/user_id/profile serialization loses dedicated line identity. Explicit sender.id can fall back to line/chat in adapter; Research must reject that fallback. |

Provisioning may already cause automatic discovery at credential renewal if both lines share the active project. That could change existing get/create behavior even without a restart. This audit does not establish that it has happened or change anything to prevent it. Owner should verify current line inventory and impact through permitted nonsecret administration before any controlled traffic.

## Binding manifest proposal

Local design schema `research_photon_line_bindings.v1`, disabled by default; not an implemented config key. Null values deny activation. Keep actual phone and project values privately owner-managed; reports use opaque labels.

| Required binding | Personal | Research |
|---|---|---|
| project and connection reference | Existing value, owner verified; preserve | Same verified value or separate scoped reference; unresolved |
| dedicated provider instance/line | PERSONAL_LINE; exact existing identity | RESEARCH_LINE; already provisioned, actual binding unresolved |
| authenticated sender | Existing allowlist unchanged | Exact explicit authorized requester -> Personal Research principal |
| conversation ID/type/membership | Existing authorized scopes unchanged | Owner-approved exact Research scope; not invented from display title |
| transport owner profile | Existing adapter owner | Verified owner of same adapter/connection |
| target Hermes profile | Existing Personal profile/routes unchanged | Approved served Research profile; missing profile denies |
| issuer/grant/route revision | Existing policy preserved | Genuine current host capability, Research grant and immutable revision |

No concrete sender/conversation/profile/project bindings were supplied or found in authorized metadata. The precise configuration cannot be populated safely yet. Body text and a provisioned number alone do not authorize any requester.

## Minimal source/config delta

1. In plugins/platforms/photon/sidecar/index.mjs, add reviewed binding-loader and discovered-client validation, versioned inbound line/connection metadata, scoped caches, explicit line resolution for all actions and probe, and strict outgoing binding validation. Keep one /inbound consumer; prohibit default/random fallback. If SDK does not expose immutable instance provenance safely, review a narrow SDK seam instead of inventing it.
2. In plugins/platforms/photon/adapter.py, validate and carry protected line/connection/sender provenance, preserve it through outgoing helpers/fallbacks and deny absent binding. Do not use recipient phone as sender. Preserve all Personal messaging features and explicit original line selection.
3. In gateway source/admission/routing/delivery contracts, carry line metadata through session/outbox/recovery and enforce the fail-closed Research reservation before every agent/command/busy/pending-reply lane. Exact file responsibilities are in RESEARCH_HERMES_ROUTE_DIFF_PROPOSAL.md. A route-only edit is insufficient.
4. Add a disabled owner-approved manifest and one conjunctive Research route/reservation after actual active config/route collision review. Existing keys are insufficient for line matching; new keys require implementation, not an invented config-only installation. Keep Personal rows/order and profile unchanged.
5. Same project: retain credentials and discovery, enforce known-line allowlist. Separate project: add protected credential **references**, not values, only under later approved multi-connection design; retain Personal app/config. Explicit clients require a reviewed renewal mechanism because SDK does not renew explicit tokens. This is an additional scope gate, not an assumed small config change.

No code changes or production config were made. Exact deployable diffs require owner metadata and a separately authorized implementation task. Existing intake remains offline-only; genuine acquisition and production registration are disabled. Connecting a real line cannot make synthetic intake production-trusted.

## Validation and rollback plan

Stage with synthetic clients: prove pinned Personal sends before/after second-line discovery; Research sends use only Research; same conversation/message IDs across lines remain isolated; all endpoint/fallback/probe paths stay pinned; missing/forged/shared metadata, wrong requester/scope, line removal, duplicate phone, invalid profile, hook timeout and recovery fail closed. Replayed events create one pending operation; changed payload conflicts. Exercise ordinary agent, command, busy-session and pending-reply lanes. No live tests are authorized here.

Before installation review, record complete candidate/source/config digests, effective active route metadata, discovery inventory revision, preserved Personal baseline and retained-state compatibility. Service owner approves coordinated quiescence/restart if required; do not assume reload or Hermes-only restart. Reconcile active sends without duplicate publication. Separately approve controlled Research receipt/From verification and Personal control evidence, without provider/model/Memory work.

Rollback prerequisites: retain a compatible Research deny gate before removing its route; reconcile pending/unknown sends; ensure old unpinned bridge cannot discover Research. If the line remains in the active project, blindly restoring old code is unsafe. Owner must approve a tested Personal-only scoped connection/discovery restriction or keep the safe pinned bridge with Research disabled. Do not move/deprovision lines, replace credentials or create a second service as an implicit rollback. Restore only reviewed source/config revisions once safe; retain durable pending/dedupe and completed delivery evidence, never rewind Memory/Obsidian records. Stop on any wrong-line send, fallback, identity ambiguity or Personal regression.

**Next owner action:** provide a redacted mode/count and same-project comparison, opaque line/instance mapping, exact requester/conversation/profile scope and active route metadata. Then authorize isolated implementation/staging of the explicit-line bridge and Hermes guard. No production activation is ready.
