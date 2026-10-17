# Research iMessage activation plan

2026-10-16. **BLOCKED — owner review only. No activation or message is authorized by this audit.** Current recommendation D; see [support evidence](RESEARCH_IMESSAGE_IDENTITY_SUPPORT.md).

## Gates before identity creation or route installation

1. Photon/provider and messaging-device owners supply the redacted capability/binding manifest in [identity binding](RESEARCH_PHOTON_IDENTITY_BINDING.md). Prove independent Apple Account versus alias support, actual sign-in host custody, project entitlement, dedicated/shared mode, destination attestation and explicit outbound identity selection. Resolve whether an additional host/account connection is necessary; no second Photon service by default.
2. Personal owner approves preservation of its account, conversation/route revision, sender policy and operating behavior. Hermes/Photon owners approve the smallest source/config delta, one-consumer topology, endpoint contract versions, connection-scoped cache/deduplication and fail-closed guard covering every ingress lane.
3. Security/Research owners approve genuine host authorization, durable intake registration, least-privilege storage/retention and revocation/recovery. Keep offline/synthetic records non-production. Source acquisition and eventual Research execution remain separate gates; this controlled identity test must not run providers or write Memory.
4. Review exact installation/disable/rollback commands against then-current source/config digests and dependency versions. Active profile config is not yet verified and both units report CanReload=no; no safe reload/restart sequence is established here. Service owner must approve any required quiescence/restart and preserve in-flight Personal sends, ACK obligations and pending operations. Do not infer restarting Hermes alone suffices.
5. Obtain separate explicit approval for identity provisioning/sign-in, configuration installation and a narrowly budgeted controlled message exchange. None is performed in this task.

## Isolated negative acceptance first

Use synthetic identities and protected boundary fixtures, without live provider calls. Test missing/forged/ambiguous recipient, shared sentinel, repeated phone/instance collision, wrong sender, wrong conversation, missing Research profile/consumer, timeout/error, stale grant, source instructions, duplicate/conflicting event IDs, restart recovery and line removal. Exercise command, busy-session and pending-reply bypass lanes. Assert no Personal agent fallback, no cross-account send and one durable pending operation. Rehydration after restart must use the bound line; no random/default selection. Synthetic tests cannot establish actual Apple destination or sending account.

## Separately approved controlled exchange

Agree owner-designated authorized sender, dedicated Research conversation and opaque Research connection/address binding before starting. Use one harmless full-commit public GitHub reference plus a unique nonsecret test nonce. Do not access past chat history. Capture only redacted metadata/receipt references for the controlled test.

| Acceptance requirement | Required proof |
|---|---|
| 1. Arrives at Research identity | Owner addresses the approved Research receiving address; provider/device owner confirms actual receiving connection/alias for this one event. Body labels are not evidence. |
| 2. Photon identifies actual destination | Protected event binds stable connection and authoritative local destination; distinguish dedicated line label from actual alias. Missing/ambiguous fields stop the test. |
| 3. Correct Hermes profile | Audit receipt binds exact event/sender/conversation/recipient/route revision to served Research profile and one durable pending intake. |
| 4. No Personal fallback | Dispatch evidence proves ordinary Personal agent and every bypass lane were excluded; failure injection tested in isolation. Missing profile denies. |
| 5. Correct Research reply identity | One acceptance-only ACK uses the authorized Research connection/identity. Provider receipt plus controlled recipient observation verifies actual From identity; HTTP ok alone is insufficient. |
| 6. Personal continues working | Separately approved Personal control exchange, or owner-supplied contemporaneous noncontent operational evidence, proves original route and sending identity unchanged. The Research exchange alone cannot prove this. Budget a Personal control message separately if needed. |
| 7. Missing/forged metadata fails closed | Isolated tamper/omission tests at the trusted boundary deny before agent/send. Do not forge live provider events or subscribe a competing consumer. |

Replay the controlled event only through an approved synthetic/replay harness to prove idempotency; do not send a second real message and call that a duplicate platform event. ACK must explicitly say acquisition pending and Research incomplete. No live acquisition, model execution, final result or Memory promotion is authorized by this identity test. A later genuine completion notification requires separate approved execution and receipt gates.

## Stop, disable and rollback

Stop on any unknown destination, mismatched From identity, Personal fallback, duplicate operation/send, missing receipt, unexpected company routing, entitlement/line change or Personal regression. Disable Research admission and outbound obligations through the reviewed gate; retain pending and delivery evidence for reconciliation. Unknown send outcomes remain held. Do not requeue uncertain ACKs, roll back completed records or delete dedupe history.

Restore only the reviewed route/adapter/config revision through owner-approved rollback after reconciling in-flight sends and ensuring old code cannot consume new identity events. Research ingress must remain blocked upstream or by a retained compatible guard; simply removing its route risks Personal fallback. Preserve Personal binding, shared consumer and all existing state. Do not sign out Personal, rotate credentials, remove an account/device, rewind Memory/Obsidian records or start another consumer as rollback. Exact commands depend on unavailable active configuration and are a further installation-review gate.

**Next owner action:** obtain the nonsecret provider/device capability manifest and existing Personal binding confirmation. Then authorize a separate reviewed dedicated-line/guard staging proposal if supported. Do not create the Research Apple identity yet.
