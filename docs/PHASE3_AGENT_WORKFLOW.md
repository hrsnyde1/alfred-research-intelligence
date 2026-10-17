# Phase 3 Research agent workflow

This is an on-demand, offline Research workflow. All model execution and verification are deterministic simulations. No model processes, services, scheduler, external transport, Memory promotion or Development task router are launched.

## Trusted inputs and roles

The existing host/test bootstrap issues authenticated contexts through `OfflineAuthority`, provisions each environment through the Director-only Phase 1 database boundary, configures fixed `ModelConfiguration` assignments and injects the existing `ResearchStore`. `AgentRoster` consumes explicit `ResearchAgent` records and those already issued contexts. It never derives principals, model approvals or permissions from source content.

Five configurable logical researcher specialties are available:

| Specialty | Internal identifier | Selection from authenticated objective |
|---|---|---|
| Technology and Code | technology_code | code, technology, software, repository, programming; GitHub is the fallback when no objective specialty matches |
| Finance and Tax | finance_tax | tax, taxation, finance, financial, accounting |
| Legal and Compliance | legal_compliance | legal, compliance, law, contract, regulation |
| Business and Market | business_market | business, market, marketing, competitor, sales |
| General | general | fallback for other source types/objectives |

The deterministic priority is finance → legal → business → technology for mixed objectives. One lead owns the combined packet. Other explicitly matched domains justify supporting researchers, up to two. More support needs escalate instead of silently dropping a domain. Source instructions and model recommendations cannot change routing. These rules are small offline fixtures, not an exhaustive language classifier or Phase 4 knowledge taxonomy.

Researcher specialties currently use the explicitly approved existing `researcher` model slot per environment. Each logical agent binding names that exact assignment; models may be deliberately shared across specialties. Director and Verifier use their fixed `director` and `verifier` slots. Full assignment equality includes approval and price, not just a model string. No provider/model is inferred or substituted. Distinct models per logical researcher would need an explicit contract extension; this implementation does not silently extend the existing specialist enum.

## Call sequence

```text
trusted one-source task + Phase 2 SourceResult
  → Director.plan: authenticate, classify, bind lead/support/verifier and immutable policy
  → Director.run: received → collecting → researching
  → reserve synthetic call budget → deterministic draft → durable output → reconcile consumption
  → lead combines claims, evidence, contradictions, unknowns and provenance
  → existing immutable packet storage → awaiting_verification
  → separately authenticated IndependentVerificationAgent.verify
  → assess every claim against cited source evidence; persist complete review
  → existing exact-digest VerificationDecision
       APPROVED: simulated evidence consistency only
       REJECTED: terminal rejected task; no knowledge promotion
       NEEDS_MORE_RESEARCH: corrections retained; bounded next packet revision
```

The caller invokes `plan(director_context, task_id, source_result, ResearchPolicy(...))`, then `run(director_context, task_id, source_result, packet_version=1)`. Verification is a separate call with the assigned issued verifier context, exact version and digest: `verify(verifier_context, task_id, packet_version, packet_digest)`. SourceResult must match the original task's submitted source and environment exactly. Plan replay cannot extend deadlines, change the lead or increase task authorization.

An inaccessible, authentication-required, unsupported, empty or error source is escalated before model spending. PARTIAL evidence may produce an explicitly limited packet, but this conservative offline verifier requires NEEDS_MORE_RESEARCH rather than complete approval. No video is watched and no additional source is fetched. A changed observed source needs a new packet revision; it cannot mutate an existing checkpoint or submitted task identity.

## Evidence and verification semantics

A simulated research provider normally emits source excerpts. Configured adversarial fixtures can supply incorrect findings, inferences, unknowns or contradictions for testing. Imported source instructions remain quoted data, never commands. Unsupported citation IDs fail closed rather than generating synthetic evidence to satisfy a contract.

The existing ResearchPacket stores claims and all available Phase 2 evidence identities. Evidence digests hash the complete SourceEvidence record (text, file digest, location, origin, environment). Packet limitations include the SourceResult digest, observed source revision/outcome, contribution digests, source limitations/flags, explicit unknowns and the simulation warning. A linked immutable PacketPreparation retains the supporting versus contradicting references and contributor for every claim. The lead is the sole packet researcher; supporters neither own nor approve it.

Independent review reconstructs the packet from the persisted specialist contributions and source result, then checks every material claim. Every supporting citation must exist and contain the exact claimed excerpt. Inferences/forecasts/unknowns are distinguishable and require more research. Declared contradicting evidence, partial extraction, unresolved unknowns or injection flags prevent simulated approval. An incorrect finding is REJECTED even when the synthetic verifier proposes APPROVED. Model proposals cannot override the deterministic evidence gate.

This is **text consistency testing, not external factual verification, semantic legal/tax analysis, authenticity validation or independent corroboration**. Contradictions supplied through explicit evidence annotations are checked; the system is not a general natural-language contradiction detector. Both the packet and decision rationale say `SIMULATED research/verification only; not real-world factual verification`. No numerical verification score exists. No APPROVED result is written to Memory or distributed as trusted knowledge in Phase 3.

The complete VerificationReview records per-claim verdict/rationale, corrections, source/packet digests, version, verifier and limitations. The existing SQLite decision binds the exact packet and points to the review digest. A cached review is recomputed against its durable verifier proposal and all current pinned evidence before a decision can commit. Historical packets and decisions remain available through the original authenticated store APIs; `history(context, task_id)` provides supplementary workflow review checkpoints, which can include a pending review before its SQLite decision commits.

## Durable checkpoints and crash ordering

SQLite schema v2 remains unchanged. The authoritative task state, retry counts, packets, verdicts, audit and cost ledger remain in ResearchStore. Research-only inputs/outputs not represented by that schema are stored as immutable canonical JSON under:

`<research-root>/<environment>/research-workflow/<SHA256(task_id)>/`

Names derive from hashed checkpoint keys. Envelopes bind environment, task and key; every read/write checks the existing issued context. Director-only keys hold plans, source snapshots and packet preparations; researcher/verifier model keys require the assigned actor, and review keys require a verifier. No-follow regular-file checks, private staging, fsynced no-overwrite publication and a task file lock protect ordinary local execution. Lock acquisition is bounded by the task deadline and a five-second busy window. This requires POSIX flock/no-follow/hard-link support; unsupported hosts fail closed.

For each call:

1. Persist an immutable invocation intent, including source/packet pins, actor/model, units, deadline and synthetic fixture configuration digest.
2. Reserve through the existing per-environment budget ledger with a stable task/version/actor reservation ID.
3. Execute only the concrete test-only SyntheticModelProvider.
4. Persist the validated response before reconciling actual consumed units through the existing budget ledger.
5. Prepare/checkpoint the packet, then use the existing immutable packet write.
6. For verification, checkpoint the complete review before the exact-digest SQLite decision.

Replay reuses committed outputs, reservations, packets and decisions. A crash before an output checkpoint can repeat a deterministic synthetic computation; no exactly-once live provider execution is claimed. A crash after a checkpoint resumes accounting/commit without repeating its committed model result. The journal and SQLite are separate commits with explicitly replay-safe ordering, not a claimed distributed atomic transaction. A cached result is never enough to authorize a changed packet/source.

Research-local checkpoints contain extracted text and provenance, not raw downloaded repositories or media. They have no automatic expiry/deletion/export. Retention, encryption, backups, authenticated restoration, safe cleanup after power-loss staging, multi-host locking and adversarial same-account filesystem guarantees remain owner/Linux integration questions. No production credential authority is introduced.

## Bounds and rework

Packet and decision commits use the optional existing-store `bounded_commit` context. Its context-local guard checks the issued actor before transaction work, after SQLite locking and immediately before commit. Expiry during writes rolls back the complete application transaction and its audit events. This does not bypass SQLite hot-journal recovery, promise a hard wall-clock return from blocked filesystem I/O, or refund model work already completed. Existing store callers outside that context are unchanged.

Each plan has a fixed Unix-seconds deadline, a maximum synthetic task cost and a maximum call-unit allowance (1–16). Call reservation depth adapts to extracted text size, bounded by that allowance. The existing environment ledger reconciles reserved versus consumed units. The task cap conservatively counts maximum authorized call reservations across all versions, including intent records whose reservation later failed; it can stop earlier than actual consumption, never authorize extra spending. Policy cannot be raised by replay.

After NEEDS_MORE_RESEARCH, requested corrections remain in the review and decision. `run(..., packet_version=n+1)` creates a new source checkpoint/contribution set/packet. The existing `put_packet` rework path advances the retry count exactly once; the workflow does not additionally spend a transition retry. Identical revision replay has no new packet/budget/decision effects. REJECTED is terminal. Deadline, evidence, missing assignment, task/environment budget or retry exhaustion stops with an explicit error/escalation and leaves durable state for inspection; it is not falsely marked complete.

Malformed or excessive model responses fail closed. A reservation left by an ambiguous failed call remains held until the same deterministic operation resumes or an explicitly authorized operator reconciles it; there is no automatic guessed refund. This milestone does not implement policy amendments, a global retry service or automatic correction of malformed fixture outputs.
