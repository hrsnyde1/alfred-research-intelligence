# Hermes Research line route diff proposal

2026-10-16. **Disabled design; not executable configuration and not an installed source diff.** Exact live project/line/sender/conversation/profile values remain unverified. Owner-reported Research dedicated-number provisioning supersedes earlier “identity uncreated” assumptions only for that number; it does not establish project binding or authorize activation.

## Before and proposed after

Current Photon source builds a generic MessageEvent with raw normalized event, but source serialization lacks an authenticated line. profile_routes matches platform/chat/user/thread/bot_profile, not receiving line. No-match can retain Personal routing. Existing post_gateway_admission hook fails open and is reached after some command/busy/pending-reply paths. Thus adding a chat/user route row cannot ensure Research-line isolation.

Proposed admission predicate is exact equality of:

`trusted issuer + connection + receiving dedicated line + explicit sender + conversation scope + current grant/policy -> Research profile`

Use real receiving line from the protected client stream, never a body field, display name, source URL, bot_profile or sender fallback. Verify provider line-to-instance binding before treating space.phone as authority. Reject duplicate phone labels or an unknown instance. PERSONAL_LINE and RESEARCH_LINE are opaque design labels only.

## File-by-file implementation proposal

Paths relative to /home/alfred/.hermes/hermes-agent/. Hermes references are from prior captured source, not a new full gateway digest audit; recheck before implementation.

| File / contract | Proposed reviewed change |
|---|---|
| plugins/platforms/photon/sidecar/index.mjs | Versioned connection/line provenance and protected manifest binding; explicit line on resolution/probe; connection/line-scoped caches; no random, shared or default sending fallback. |
| plugins/platforms/photon/adapter.py | Require explicit raw sender for Research; retain connection/line identity on MessageEvent/source; include trusted delivery binding in every sidecar action; fail on missing/conflicting binding. |
| gateway/session.py (SessionSource serialization) | Add optional versioned transport identity metadata and preserve it through durable session/delivery correlation. Existing legacy records must not be automatically treated as Research-authorized. Review all serialization readers and state compatibility before migration decisions. |
| gateway/platforms/base.py build_source | Bind actual receiving transport owner separately from routed profile and verified receiving identity; no user-controlled overrides. |
| gateway/profile_routing.py + gateway/config.py | Add validated exact connection/line discriminators and reservation/deny semantics; reject overlapping ambiguous bindings. Preserve existing Personal route rows and precedence. Existing bot_profile must not be redefined as a phone identity. |
| gateway/run.py route resolution | Require Research target served and current approved policy; missing target/config denies, never Personal fallback. Validate effective multiplex/served set rather than globally enabling by assumption. |
| gateway/run_inbound.py | Central Research reservation guard before ordinary agent, command, running-session, pending-reply and plugin lanes, with authenticated provenance available. Unknown/ambiguous line denies; valid Personal binding preserves existing flow. |
| gateway/run_inbound_consumer.py | For reserved Research traffic, absent consumer/error/timeout/invalid result becomes terminal denial/quarantine rather than fallthrough. Consumer receives trusted complete identity/event/text envelope. |
| Existing outbound obligation/session recovery writers and readers | Trace implementation call sites before coding; persist originating connection/line/space and immutable operation scope, carry it through retry/recovery and reauthorize before send. No new parallel delivery engine. Exact additional files cannot be fixed without tracing this contract. |

This is a responsibility inventory, not a claim that all listed files necessarily require edits. Implementation should choose the smallest coherent patch after tracing callers; source inventory and on-disk baseline must be reverified first. No schema/database migration is authorized or asserted unnecessary for a future durable binding change.

## Proposed configuration delta

A new versioned policy loader would consume the following logical shape. These are proposed keys requiring implementation; do not insert them into current config. Nulls are deliberately invalid for activation.

```json
{
  "schema": "research_photon_line_bindings.v1",
  "research_enabled": false,
  "personal": {
    "connection_ref": null,
    "line_ref": null,
    "existing_route_revision": null
  },
  "research": {
    "connection_ref": null,
    "line_ref": null,
    "provider_instance_ref": null,
    "explicit_sender_id": null,
    "conversation_id": null,
    "conversation_policy_ref": null,
    "transport_owner_profile": null,
    "target_profile": null,
    "issuer_ref": null,
    "grant_ref": null,
    "route_revision": null
  }
}
```

Actual phone-to-line and project-to-connection mappings remain protected owner configuration. Reports contain only opaque references; message input cannot choose them. Same-project design retains current project authentication and adds explicit pinned routing. Separate-project design requires independently approved scoped connection support; never swap the current project's credentials.

## Required fail-closed matrix

- Verified PERSONAL_LINE: retain original Personal profile, policy, conversation scope and original sending line. Missing legacy delivery binding may be resolved only by an owner-approved unambiguous Personal mapping; never guessed from cache or “first client.”
- Verified RESEARCH_LINE plus authorized sender/conversation: invoke only approved Research intake; missing profile, grant or consumer denies. Current offline-only adapter is not a live authority.
- Research line with wrong sender/conversation: reject before generic route matching. No lower-specificity Personal match.
- Unknown, missing, shared or ambiguous line/connection: quarantine/reject before agent and send. Do not install this against unverified Personal metadata; establish its binding first.
- Every outbound action: require current protected origin binding, resolve exact line, verify returned space binding, then act. Revocation/line loss denies without another-line retry.
- Replay: scope key by connection/line/event and canonical payload; identical input reuses pending operation and delivery obligation, changed input conflicts. Version any change to existing intake operation keys; never silently adopt old synthetic state.

## Acceptance and rollback gates

Synthetic tests must cover each ingress lane, missing consumer and failure path, cache collisions, restart rehydration, line removal and every Personal outbound feature/fallback. Verify no Research text reaches Personal ordinary agent and no Personal send selects Research after discovery. Keep one existing inbound consumer; no /inbound inspection probe.

Owner-approved later controlled messaging must prove receiving line, correct profile, acceptance-only pending ACK, actual Research From identity and unchanged Personal identity. No such message is sent now. Genuine source acquisition, completion notifications, Research execution and Memory remain separately gated.

Rollback must disable Research admission and outbound work while retaining a guard; route deletion alone risks fallback. Old bridge cannot be restored while it can discover multiple lines without an approved Personal-only scope restriction. Preserve pending/dedupe/delivery state and reconcile uncertain outcomes. Shared-process restart/quiescence and exact rollback commands require service-owner review of current effective config; no stops, restarts, credential changes, line changes or production writes are authorized by this proposal.

**Installation blockers:** same/separate project comparison; dedicated mode and line-instance mapping; explicit authorized sender/conversation/Research profile; active route metadata; reviewed bridge/guard/delivery implementation; synthetic regression evidence; owner-approved restart/rollback and controlled message permissions.
