# Photon outbound identity audit

2026-10-16. Read-only review. **Current bridge is not ready for safe two-line integration.** Research dedicated number provisioning is owner-reported in this task; account/project assignment is not independently verified.

## Evidence

Fresh SSH used BatchMode=yes, StrictHostKeyChecking=yes, ConnectTimeout=8, ConnectionAttempts=1 to alfred@192.168.50.81. Source root: /home/alfred/.hermes/hermes-agent/. On-disk bridge digests still match prior inspection:

- plugins/platforms/photon/sidecar/index.mjs: ef019d1d50e4ca680aede49276181f8eff8d396d9b7c22a73bb5da2b2d7bb8e4
- plugins/platforms/photon/adapter.py: 841ed6cb6e2d392fcec33f8983dd34fffe677c6a8d40e442bc449e66beeb16e5

Fresh remote reads verified /send and SDK attachment selection; other call sites below were examined in prior captured source, whose bridge digests match. SDK 12.7.0 source previously hashed in RESEARCH_IMESSAGE_IDENTITY_SUPPORT.md. No code was imported, initialized or tested. alfred-photon.service is active as alfredphoton in the established sidecar directory. No EnvironmentFiles entry was returned; this does not establish effective project or mode. No credentials, raw environment, logs, sessions or messages were read.

## Exact omission inventory

| Source location | Current behavior | Two-line failure and required correction |
|---|---|---|
| sidecar/index.mjs:344–350 | One Spectrum app; project authentication; imessage.config() | Discovers project clients without owner line allowlist. Validate discovered lines against protected approved bindings; deny/quarantine unknown lines. |
| index.mjs:385–401,984–986 | knownSpaces keyed by conversation ID, including aliases; knownMessages keyed by message ID | Cross-line collisions can select the wrong cached object. Scope every key by connection and line, plus conversation/message as appropriate. |
| index.mjs:997 | im.space.create(phoneTarget) omits params.phone | Dedicated SDK can choose a random line with multiple clients. Require explicit trusted selected phone; never use bare target as sending identity. |
| index.mjs:1010 | im.space.get(spaceId) omits params.phone | Throws when multiple dedicated clients exist. Supply explicit phone from protected binding. Never retry another line. |
| index.mjs:786 | Probe im.space.get(PROBE_SPACE_ID) omits phone | Probe behavior changes in multi-line mode. Pin probe to an approved line and isolate its health semantics; no production chat used as arbitrary probe. |
| index.mjs:1099–1119 | /send reads spaceId/text/format; resolveSpace(spaceId); space.send(builder) | No protected connection/line assertion. Require versioned binding on request and verify resolved space.phone. SDK send follows the selected space, not an independent From argument. |
| index.mjs:1126,1139,1175 | Richlink, attachment/voice paths resolve space without line, including caption fallback sends | All fallbacks must retain same binding. Disable Research media initially; preserve Personal features with explicit Personal identity. |
| index.mjs:1198–1200,1235–1236 | Reactions and message lookups use unscoped caches/resolution | Scope message target to connection/line/conversation; reject cross-line targets. |
| index.mjs:1262,1276,1288 | Poll/effect/typing use same unscoped resolver | Apply same explicit selection, including ancillary actions. No default line for typing. |
| adapter.py:1329–1331 | send accepts metadata/reply_to but calls _sidecar_send with chat only | Protected binding must survive gateway delivery to adapter and every fallback. Merely supplying metadata today does not select a line. |
| adapter.py:1334–1380,1393,1528 onward | Clarify/poll, file/media, typing and plain fallback helpers | Audit and update each payload/helper; missing or conflicting binding must fail, never route via Personal. |

Provider SDK index.js:1883–1905 selects dedicated client by phone; shared mode returns one shared client regardless. space.get requires phone with multiple dedicated clients, space.create can choose randomly without phone, send at2972 uses space.phone. getAttachment at2988–3002 also requires phone in multi-line mode. Any future direct attachment lookup must pass it. Duplicate phone labels must deny ambiguous selection; internal instance keys alone do not fix clientForPhone's first matching label behavior.

The [official connection/routing documentation](https://photon.codes/docs/spectrum-ts/providers/imessage/connection-and-routing), reviewed today, confirms explicit per-phone dedicated routing and the changed get/create behavior when a second line appears. This verifies SDK behavior, not active project entitlement or account binding.

## Required outgoing invariant

A trusted delivery obligation binds (project/connection reference, approved line reference, conversation ID, origin event/operation, route revision). The sidecar derives actual phone privately from protected owner configuration, resolves that exact client/space and checks consistency. SDK calls become conceptually `im.space.get(spaceId, {phone: approvedPhone})` or, only for an authorized new conversation, `im.space.create(target, {phone: approvedPhone})`. These are API examples, not commands to execute now.

Never accept a message-body From/phone field. Reject missing, unknown, shared-sentinel or ambiguous line; revoked connection; wrong profile; cache mismatch; unavailable line; and expired grant. Return a stable denial, not a retry on another account. ACK/final receipts must record opaque selected identity and operation scope. SDK ok/messageId alone does not prove recipient delivery or actual Apple From; controlled acceptance must verify both after separate approval. Preserve unknown-send obligations without blind retries.
