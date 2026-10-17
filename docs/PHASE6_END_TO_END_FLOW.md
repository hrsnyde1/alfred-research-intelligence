# Phase 6 offline end-to-end Research flow

Scope: on-demand, synthetic Mac integration only. No new orchestrator, messaging Gateway, Photon instance, phone number, Memory system or deployed agent. The approved 20 decisions remain authoritative; real V1 acceptance still requires separately authorized Linux integrations.

## Trusted ingress

ConversationRegistry requires four independently configured conversations: Personal Alfred Research, Gabos Holdings Research, Fintra AI Research and SC Products Group Research. Each binds a unique synthetic conversation ID to one environment and issued requester/recipient principals, plus allowed source kinds. ResearchMessage has exactly one same-environment SourceIdentity. Existing OfflineAuthority validates the actual issued caller; message text, source content, company labels or constructed lookalike contexts cannot supply authority.

ResearchWorkflow receives existing Director, verifier, IntelligenceOrganizer, FakeMemoryAdapter, Notifications and trusted options/readers. Source processing is the accepted pure SourceProcessor. Models remain concrete synthetic providers; Memory and conversation adapters are test-only. Supporting specialists and fixed assignments are selected by existing ResearchDirector, not new running processes. The coordinator never grants new model, specialist, tool or HQ permissions.

## Durable ordering

1. Authenticate conversation/requester/environment and validate the bounded fixture. Persist immutable Intake with exact ResearchMessage, source bytes/metadata, options and configuration digest in the environment intake index before task creation. Index limit: 128 intakes/environment; fixture snapshot limit: 64 files and 128,000 aggregate bytes. Existing source limits remain independently enforced.
2. Submit a ResearchRequest through ResearchStore with stable conversation/message-derived request ID. Persist the task's origin in a separate per-task flow namespace. Task UUID, originating conversation, requester and environment remain linked.
3. Prepare distinct ACK notification, enqueue its digest in existing SQLite outbox, and exercise fake transport acceptance/delivery.
4. Process and checkpoint SourceResult. Inaccessible/unsupported/auth-required/error sources stop safely; no invented transcripts. Source instructions remain untrusted data.
5. Use existing immutable Director plan, lead/support output checkpoints, budget reservations and packet revision storage. Independent verifier records exact-digest verdict through existing contracts. REJECTED or NEEDS_MORE_RESEARCH stops promotion; this integration does not loop indefinitely or invent new evidence. Existing authorized bounded-rework APIs remain available separately.
6. Approved research enters existing IntelligenceOrganizer classification/history. Persist its immutable Batch and proposal-only handoffs. Non-development categories may additionally produce an inert generic Department proposal; no Department or CTO task is submitted.
7. Create exact approved KnowledgeCandidate; confirm separate submit, commit and promotion receipts. Failure/partial outcome stops further claims of success. Existing repeated content may reuse already committed/promoted record receipts without creating another knowledge record.
8. Retrieve through an independently granted specialist context. Matching does not grant retrieval. A cached completed read interrupted before the flow checkpoint is reconciled against its stored operation receipt, actor/digest and current approved/promoted state. It is the original observation, not a fabricated fresh receipt.
9. If trusted per-conversation options explicitly permit company HQ synchronization, authorize and sync the exact record through the existing fake partitioned HQ port. Owner reads still require separate Personal Alfred owner grants. No source or message may set HQ eligibility.
10. If export is selected in trusted options, request/export/Sync use the corrected v2 attempt/destination/version and exact prerequisite-receipt bindings. Each failed stage remains incomplete; no Markdown is written.
11. Persist FlowResult with origin, outcome, references, proposals and actual stage receipts before preparing FINAL. Notification text is generated only from successful recorded operations and explicitly says SIMULATED. Result completion is independent from notification delivery.

Flow stages use existing WorkflowJournal Director-only immutable keys in a separate `flow-<task-hash>` namespace. This avoids recursive locking with accepted task/model, catalog and Memory locks. No SQLite schema migration. Separate commits are reconciled through stable IDs and stored receipts, not described as one distributed transaction.

## Notification state and recovery

Notice identity binds environment, task UUID, conversation, recipient and ACK/FINAL kind. It has a maximum 240-character SIMULATED message. Before accepting a Notice, Notifications confirms authenticated origin against the task request. ACK content is fixed and cannot claim downstream completion. FINAL must exactly match the persisted FlowResult's generated text and receipt references; arbitrary saved/exported/delivered claims are rejected.

Local states: PREPARED → SENDING → ACCEPTED → DELIVERED; UNKNOWN records ambiguity and FAILED records bounded send exhaustion. Sending is not acceptance; acceptance is not confirmed delivery; neither determines Research/flow completion. Existing outbox remains pending until fake DELIVERED confirmation, when its original idempotent delivery primitive is used. A workflow may be completed while notification remains accepted/pending.

The fake transport persists acceptance and delivery separately in immutable per-notice test transcripts. Dispatcher looks up the stable notification identity before sending. An unavailable lookup raises ambiguity and never authorizes resend. In this deterministic fake only, a successful lookup returning absent is definitive; then a bounded send with the same identity is safe. Maximum three send attempts; repeated recovery does not create another logical notice. No live provider's absence/receipt guarantees are inferred.

Receipt loss after transport acceptance or delivery is recovered by lookup, not blind retransmission. Repeated delivery confirmation does not spend another outbox attempt. Cached final messages describe test receipts recorded for that task; they are historical observations, not claims that revoked knowledge is currently available. Fresh specialist/HQ retrieval always remains subject to existing currentness and authorization checks.

## Recovery interface and limitations

`recover(issued_requester_context)` scans only that environment's authenticated intake index and replays that requester's intakes using saved fixture bytes. It handles tasks whose Research state is already APPROVED but whose later delivery stages were interrupted. It can also repair pending notifications on completed results. It is an explicitly invoked library operation, not a scheduler, daemon or cross-company worker.

Runtime crash exceptions propagate without inventing a final outcome. Durable stages and underlying receipts are reused on restart. Resource/authorization/validation exhaustion records a truthful BLOCKED/PARTIAL result and final notice, without unauthorized budget amendment or automatic infinite retries. A new authorized operation is required for deliberate policy/evidence changes; immutable intake replay rejects changed messages, fixtures or options.

Ordinary HTML is deliberately PARTIAL in accepted Phase 2 and therefore NEEDS_MORE_RESEARCH under Phase 3. This integration preserves that gate. Complete authorized user-supplied article text uses the document adapter with explicit user_supplied provenance; this is not evidence of live website fetching or HTML promotion. Non-development specialist identifiers remain proposal-only; without an actual independently configured reader grant, generic intelligence may commit/promote in simulation but cannot claim successful specialist retrieval, and the workflow reports PARTIAL.

Private local filesystem/bootstrap and POSIX locking assumptions remain unchanged. Production routing, requester/recipient credentials, transport receipt authentication, worker cancellation and Linux service permissions remain unverified. No trusted production knowledge or real messages are created.
