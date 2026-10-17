# Research Photon identity binding

2026-10-16. **BLOCKED — binding proposal only.** PERSONAL_IDENTITY and RESEARCH_IDENTITY below are redacted logical labels, not allocated accounts or valid configuration values.

## Existing field correlation

| Field | Installed behavior | Authorization limitation |
|---|---|---|
| messageId | SDK message.id -> sidecar messageId -> Hermes event/source.message_id | Require nonempty original ID and connection-scoped deduplication; not globally unique by assumption. |
| spaceId | SDK space.id -> normalized space.id -> Hermes chat_id; sidecar knownSpaces is keyed by space ID | Conversation identity alone does not identify the receiving account; cross-line collisions must be handled. |
| senderId | message.sender.id -> sender.id -> source.user_id | Adapter fallback to space.phone or spaceId is inappropriate for Research; reject missing raw sender rather than authorize fallback. |
| receiving line | SDK RemoteClient.phone is attached through each stream; dedicated space.phone selects client | Configured line label is not proof of actual Apple destination/alias; shared mode sentinel identifies no receiving address. |
| recipient/account | No separate authoritative field emitted by normalizeEvent at sidecar:654–675 | Do not invent one from phone, conversation, bot_profile, profile, UID or message body. |
| outgoing account | SDK clientForPhone(space.phone); bridge resolves cached space or im.space.get(spaceId)/create(target) | Bridge does not accept or verify explicit approved sending binding; fallback/random selection is prohibited for Research. |

Sidecar:344–350 creates one Spectrum app with project credentials and imessage.config(), no explicit clients config. Cloud may return dedicated clients or shared mode. SDK index.js:185–205 preserves internal instance keys but static clients may repeat a phone; phone alone is insufficient as a durable unique connection key. Current normalized events omit instance keys. Linux service identity is transport process identity, not the signed-in Apple identity.

## Required registration manifest

Every value is **UNALLOCATED/UNVERIFIED** unless expressly noted. Owner must provide a versioned, nonsecret manifest with:

- Provider/project opaque reference, shared/dedicated mode and approved entitlement/capability revision.
- Stable account-connection/instance reference; host/device custody reference and health/revocation generation. Distinguish two Apple Accounts from two receiving aliases on one account.
- PERSONAL_IDENTITY binding and frozen existing Personal route revision; RESEARCH_IDENTITY independent account or approved alias semantics, verified local receiving addresses represented by opaque IDs, and exact approved sending identity.
- Provider-attested derivation of actual destination (including aliases/groups), authenticated explicit sender and immutable event ID. Unknown or shared-only recipient cannot satisfy the Research gate.
- Owner-authorized sender principal, exact dedicated conversation ID/type/member policy, target Research profile and transport owner profile; no invented conversation or Apple account ID.
- Genuine Hermes issuer/capability, current grant/revocation policy, route/policy revision and owner approvals. No credentials belong in this manifest.

Token/address/phone are SDK client configuration field **names**, not permission to request or expose their values. Apple registration, sign-in, trusted device/number and provider provisioning requirements are provider/owner questions; none was performed or assumed complete.

## Smallest conditional bridge change

Reuse one existing sidecar/app/consumer. Carry an immutable provider-attested connection/receiving-identity binding with each event; preserve actual sender and original message ID. Version the bridge event contract and authenticate its provenance at Hermes admission. Cache and resolve by (connection, receiving identity, spaceId), not spaceId alone. Reject duplicate/ambiguous line labels and cross-line conversation collisions.

Outbound requests must carry a protected originating connection/sending-identity binding from the accepted operation, validate it against current owner policy and resolve the exact dedicated client with explicit line parameters. Never use randomPhone, shared-mode ambiguity, default recipient, bare-number create fallback or another account on a missing binding. Verify send receipt binds the selected connection and retain unknown outcomes for reconciliation. Internal instance metadata may require a reviewed SDK seam if not exposed; do not patch around this with untrusted fields.

This change is not implemented. If provider shared mode cannot attest recipient/select sender, local extensions cannot manufacture those guarantees. Stop and obtain a provider-supported dedicated connection option. Multiple clients under one service are a possibility, not approval for extra accounts, processes or connections.

See [support evidence](RESEARCH_IMESSAGE_IDENTITY_SUPPORT.md), [routing guard](RESEARCH_HERMES_FAIL_CLOSED_ROUTE.md) and [activation gate](RESEARCH_IMESSAGE_ACTIVATION_PLAN.md).
