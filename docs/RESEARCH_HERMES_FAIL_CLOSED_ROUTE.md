# Research Hermes fail-closed route

2026-10-16. **Design only; no route installed.** Exact trusted predicate:

`authenticated issuer + attested provider connection + actual Research receiving identity + explicit authorized sender + exact conversation scope + current route/grant revision -> approved served Research profile`

Each identity must derive from the protected host/provider boundary, never text, display names, URL content or caller-supplied recipient JSON. This is a proposed policy contract, not executable Hermes configuration. All live IDs and capability references remain unallocated.

## Existing seam and required extension

Installed-source evidence captured in the prior route audit: gateway/profile_routing.py uses conjunctive platform/chat/user/thread/bot_profile matching, not a receiving Apple account discriminator. bot_profile is transport ownership, not Apple identity. gateway/run.py rejects matched unserved profiles only when routing/multiplexing is effective. No-match can retain ordinary routing. Effective active routes remain unavailable in the authorized nonsecret inspection.

pre_gateway_dispatch runs before authorization and fails open. post_gateway_admission can return handled/reply, but missing hook, timeout, exception or malformed result falls through; busy-session, command and pending-reply lanes occur before this hook. Its serialized source omits raw sender provenance, transport reference and receiving account. agent:start only supplies a 500-character preview and cannot authenticate/dedupe the original event. The existing consumer hook alone cannot enforce the requirements.

The smallest conditional extension is a reviewed guard in the existing admission/dispatch path, with versioned trusted Photon provenance, before **all** ordinary-agent, busy-session, command and reply paths. Reuse the post-admission intake consumer only after the guard binds authorization and prevents fallback. Do not create another orchestrator, Photon subscriber or competing retry owner.

## Decision rules

| Input or fault | Required result |
|---|---|
| Explicit verified Personal binding | Preserve current Personal route and behavior under its existing policy. |
| Research connection/recipient + exact authorized sender/conversation + valid grant | Bind target Research profile and invoke only reviewed intake path. |
| Unknown/ambiguous receiving identity or connection | Reject/quarantine before ordinary agent; do not guess Personal. If current transport lacks verified destination metadata, do not activate the Research identity. |
| Research recipient with wrong/missing sender or conversation | Deny; no lower-specificity route or Personal fallback. |
| Missing/unserved Research profile, absent consumer, hook error/timeout, bad signature, revoked grant or unavailable policy | Deny/quarantine Research event; no model call and no ordinary reply. |
| Message says “Personal”, company name, privileged profile or destination | Treat as source content; cannot change trusted binding. |
| Same connection/identity/event ID and same canonical payload | Reuse durable accepted operation and ACK obligation. |
| Same key with changed sender/conversation/content/digest | Conflict/reject; never create another task. |

Explicit Personal preservation requires owner verification of its binding before enabling this guard. Do not install a global missing-metadata rejection against today's unverified Personal transport, or allow unidentified traffic to bypass Research checks. Inability to distinguish identities is an activation blocker.

## Durable intake and reply contract

The existing offline intake library uses recipient/profile/conversation/event scope and durable pending acquisition with one full-commit GitHub source. A reviewed live envelope must additionally bind stable connection and actual receiving/sending identity; version any operation-key change and preserve old records. Do not silently rekey pending operations or regard sender fallback as authenticated. Durable commit precedes acceptance ACK. Replays reuse one delivery obligation; uncertain sends require authoritative reconciliation, not blind replay.

ACK is acceptance only: source acquisition pending, no Research completion or packet digest. Genuine acquisition must independently attest source bytes/commit before task materialization. Final notification is separate and requires actual authorized completion. Both ACK and final reply bind the original approved Research sending connection/identity and exact conversation, with current authorization rechecked before send. Missing/deprovisioned connection denies; no Personal/default-account reroute.

Current intake requires OfflineHermesAuthentication and denies production=True; genuine acquisition denies unconditionally. Existing 27 intake tests/332 total prior Mac passes support synthetic behavior only. A real binding cannot activate that test implementation by filling IDs or toggling flags. Genuine authorization, registration, acquisition and delivery seams require separate review. No Memory/model/provider authority follows from an intake route.
