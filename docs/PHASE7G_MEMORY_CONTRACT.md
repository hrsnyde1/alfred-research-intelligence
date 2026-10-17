# Phase 7G — Minimum Memory-owned Research contract

## Status and evidence

This is a **proposal, not implementation or deployment approval**. VERIFIED below means installed source or service metadata inspected over read-only SSH as alfred@192.168.50.81. No database, vault, secret/configuration contents, application endpoint or private record was opened. No model, Memory, export or Sync operation was invoked. No tests were run in Phase 7G. The accepted 305 Mac tests are historical offline evidence only.

Memory service metadata: active as `alfred-memory`, working directory `/opt/alfred-obsidian-v1/current/source`, drop-in `50-obsidian-candidate.conf`; current symlink resolves to `/opt/alfred-obsidian-v1/releases/4d5ba29bd3027e74c808a8feaf1b5dadfded22f0`. Effective handlers/configuration, live database version and credentials remain UNKNOWN. Source schema v3 is not a production database inspection.

All remote references below are relative to `/opt/alfred-obsidian-v1/current/source/`.

| VERIFIED source | Established behavior / boundary |
|---|---|
| `focused_v1/server.py:14–26,46–67` | JSON bearer POST `/v1/memory`; capture/create/update/delete/search/forget/review/pending_reviews; 131072-byte request ceiling; review requires 64-hex proposal digest; 400/403/503 responses. No Research candidate/promotion action identified. |
| `focused_v1/store.py:68–125,145–190` | Explicit new-database initialization and source schema user_version=3; existing schema checked. Active principals are alfred or agent; agent requires task assignment; review requires Alfred-kind authority. No Research attestation/company policy in the inspected core schema. |
| `store.py:259–288,341–389` | Create can be pending or auto-approved; review digest covers Memory id/state/content/pending changes/hold/version. Neither represents independent Research factual verification. |
| `store.py:391–431` | Pending-review listing reports stored state/proposal digest. Search returns approved unsuppressed records, agent task scope, content truncated to 1536 characters. No full claim/citation/verification/currentness contract. |
| `obsidian_candidate/service_api.py:88–103,195–223,266–307` | get_current/snapshot_page expose full generic Memory content/state/version under Alfred or fixed bridge authority. Dedicated bearer dispatch has a fixed actor, no caller actor field. These are not specialist-scoped Research reads. |
| `store.py:297–389,433–511`; `service_api.py:26–86,166–193` | Versioned updates, pending review/deletion, hold/suppression and encrypted fsynced deletion intents. Candidate replay quarantines unresolved version/ownership conflicts. Preserve these mechanisms. Research expiration/conflict/attestation revocation still needs explicit semantics. |

Source integrity observed: store.py `5ca002bd93e486875191292c21ba782fb2df5eb3fa4d525654e80ad29069cf8c`; server.py `2042c95d517601da03654b942b04bf96ed69bedf5afa0351ef64463542eba5ea`; service_api.py `f7fdcd5b01bf12b13415b8f4bbd7edbb7629ae0856b7267bca743b6773282cc5`.

## Duplicate-create inconsistency: exact source trace

`store.py:266–267` chooses pending for an agent's ordinary personal memory; task_progress/development_lesson and Alfred-kind creation are auto-approved. First insert persists the chosen state at :283–285 and returns it at :288.

On a repeated source_message_id, :275–277 selects only id/principal/task_id/content. Matching actor/task/content returns `{id, review_state:"approved", saved:true, duplicate:true}` at :282. There is **no UPDATE in this branch**. Therefore, for example, a previously pending or rejected matching record can produce an approved-looking duplicate response while remaining pending or rejected. This is a verified source-level control-flow inconsistency, not a live database reproduction.

Authoritative state is the committed row plus current authorization/hold/suppression/deletion checks, not this response literal. Pending review uses actual row values (:397–412); search requires actual approved/unsuppressed rows (:423–430); generic get_current returns stored state (:88–93 in service_api.py). A pending edit can coexist with an approved original row, so even the correct stored review_state is not approval of proposed replacement content. Research promotion must additionally inspect its own exact revision/attestation/currentness.

Smallest response correction: select `review_state` in the duplicate branch and return that actual value, retaining id/saved/duplicate semantics and making no review mutation. Do not return the newly computed default or silently approve the row. Separately, the branch currently omits kind comparison; Memory owner should decide and test rejecting mismatched-kind replay rather than call it an exact duplicate. The new Research operations must compare the entire canonical operation payload regardless of this legacy decision.

## Proposed operations: one existing Memory authority

Names below are **logical proposed operations**, not installed URLs/action strings. Memory owner allocates the wire/version/dispatcher after review. Reuse the current service and transactional persistence, not a Research database masquerading as authoritative Memory.

| Operation | Required semantics |
|---|---|
| submit_candidate | Authenticated scoped caller submits immutable candidate; validate schema, provenance and independent attestation policy. Return distinct candidate acceptance receipt. No trusted visibility. |
| commit_candidate | CAS against candidate digest/version; durably store full structured intelligence/provenance and commit receipt together. Still excluded from trusted views. |
| promote_record | Separate authorized Memory decision over exact committed packet/candidate/attestation and current grants/policy. Atomically record promotion and trusted visibility. Rejected/NMR/synthetic/stale/expired/disputed/superseded inputs deny. |
| retrieve_current | Independently authorized specialist/purpose; evaluate current visibility/grants/validity and return full record plus a fresh retrieval receipt. No promotion replay substitutes for this read. |
| lookup_operation / reconcile | Authenticate same tenant/scope; recover the exact original durable receipt without repeating its effect. Distinguish definite absence, pending/unknown, failed and successful historical result. Historical success does not prove current authorization. |
| revise / invalidate | Immutable correction/supersession/validity revision or ordered expiration/conflict/delete/revoke event, expected-head/CAS, authoritative current-state lookup and audit. Revalidate as specified below. |

### Candidate payload: proposed versioned required fields

| Group | Minimum required data |
|---|---|
| Identity / idempotency | schema/version, caller operation ID, canonical payload digest, originating Research task/request/intake references, Memory-assigned candidate/record IDs and revisions in receipts. Changed payload under one operation ID conflicts. |
| Authenticated scope | Host-issued environment/tenant ID and company identity where applicable, trusted task mapping, subject/purpose/grant references, classification, access-policy ID/version, permitted audiences. Cross-check submitted claims of scope against trusted authority; never infer from source/model text. First live enablement is Personal only; other companies deny until registered. |
| Original source | Exactly one submitted source identity/reference; authorized acquisition receipt reference, acquisition time, source type, repository/URL or authorized file identity, submitted revision and acquired commit/tree/blob identities as applicable, byte/content digests, extraction status, limitations. No synthetic fixture origin relabeled genuine. |
| Packet | Full immutable packet or bounded embedded canonical packet plus authenticated immutable evidence payload; packet schema/ID/version/SHA-256, accountable researcher identity and fixed provider/model execution reference. Memory recomputes canonical digest. A mutable external path/hash-only pointer is insufficient for full retrieval. |
| Claims / citations | Every material claim ID/text/kind (source finding versus inference/forecast/unknown), supporting and contradicting evidence IDs; bounded evidence excerpts, file/path/line or other citation locations, content digests, source revision, contributors, unknowns/limitations. Evidence referenced by a claim must exist and belong to the original scope/source or explicitly permitted corroboration. |
| Independent verification | Decision/attestation ID and digest, exact packet/version/source bundle digest, verifier subject/role/provider/model, authenticated execution receipt and attestation issuer/key/grant references, issued/expiry times, evidence-policy version, APPROVED/REJECTED/NEEDS_MORE_RESEARCH, per-material-claim assessments, rationale/limitations. No numerical confidence score. |
| Organization / validity | Primary category/topics/specialist associations, classification/access restrictions, valid_from/valid_until with explicit time encoding and clock policy, correction/supersession/conflict links, impact/escalation flags. Validate all metadata before dedupe; conflicting duplicate validity rejects, no silent extension/shortening. |

All fields have strict types, length/cardinality/total-byte limits and unknown-field rejection. Exact limits, UTC representation and schema version require Memory-owner sign-off; preserve the existing HTTP limit unless explicitly reviewed. Oversize evidence denies/returns explicit incomplete status, never silently truncates citations. Research canonical hashing uses sorted compact UTF-8 JSON, ordered arrays and no floats; cross-runtime golden vectors are required.

### Independent factual attestation trust

Memory must verify an independently authenticated attestation or query an approved existing attestation authority. Hashes, provider-generated APPROVED text, a client boolean, personal Memory review or an Alfred-kind bearer alone cannot authenticate factual verification.

The authenticated envelope binds the complete candidate-sensitive packet/source/claims/classification/scope/validity relationship, verifier identity/model/execution and policy. If classification/validity lives outside packet.v1, bind its candidate digest explicitly too; changing it requires authorized revalidation. Memory validates trusted issuer material supplied independently of candidate data, active verifier grant and approved exact assignment, freshness/revocation, separation from Director/lead/all contributors, and evidence-policy compliance. No universal embedded secret or key derived from public metadata. Signature/MAC/transport-authority mechanism is UNKNOWN and must be chosen by existing Security/Memory owners; no new attestation service is prescribed.

One submitted source remains authoritative task scope. The policy must distinguish facts actually established by a pinned repository from descriptions/inferences and claims requiring additional corroboration. Unsupported runtime effectiveness cannot be approved merely from README text. Missing/conflicting evidence yields REJECTED or NEEDS_MORE_RESEARCH and cannot promote. Memory validates the genuine verifier decision; it does not call a model itself or pretend to rerun factual investigation.

Synthetic artifacts remain permanently ineligible, including synthetic data wrapped in a genuine-shaped envelope. Missing/expired/changed/revoked trust material fails closed. Trust loss/rotation/backup restoration must not revive prior authorizations; current retrieval denies when required current trust cannot be established. Exact issuer/revocation/retention rules remain owner decisions.

### Separate durable receipts and fresh reads

Each receipt binds schema/version, external Memory issuer and receipt ID, operation ID/type/payload digest, authenticated tenant/caller, candidate/record ID/version, packet and candidate digests, attestation/promotion references, state sequence/CAS, observed time and outcome/error/currentness. Receipt authority is the authenticated Memory boundary and durable operation ledger; a local hash or Research outbox is not an external receipt.

Candidate acceptance, COMMITTED, PROMOTED and RETRIEVED are separate observations. State change and durable receipt/idempotency entry commit in one Memory transaction. Commit timeout must reconcile by original operation ID; never synthesize a receipt or repeat a known commit. A failed operation cannot be represented as successful. Repeated mutations return the original result; retrieval is fresh only under a new read identity/current check. Replaying a historical read receipt never renews freshness. Missing/ambiguous lookup remains incomplete unless absence is authoritative.

For Personal Frontend, trusted configuration must grant the actual specialist subject read access to eligible Personal Development intelligence. The inspected Development routing ID `frontend` is a category, not an authenticated principal or grant. The same scoped mechanism supports the other ten specialties. Existing task assignments may be reused only where their scope is sufficient; don't grant global Alfred/bridge authority to obtain cross-task retrieval. Specialist association, user-supplied role and public source classification confer no permissions.

Full retrieval returns exact claims, excerpts/citations, source revision/acquisition limitations, packet/attestation/promotion references, topics/audiences, policy and currentness/version relationships. Check every read against active grants, suppression/deletion, disputes, supersession, validity and attestation policy. Bounded pagination must bind one record revision/digest; revision/policy changes invalidate continuation. Large records must not become a citation-truncated "success". An authorized historical audit read is distinct from current trusted retrieval.

## Knowledge lifecycle and Obsidian compatibility

| Change | Required authoritative behavior |
|---|---|
| Correction/update | New immutable revision with previous-head link/CAS, complete provenance and fresh attestation for changed evidence/claims. Original history remains subject to retention/legal deletion. Rejected/NMR replacements never promote. |
| Validity/access/classification change | Explicit authorized immutable policy revision; revalidate candidate/attestation bindings as required. Stricter policy/revocation takes effect immediately for reads, not after export. Duplicates cannot mutate policy. |
| Supersession | Retain historical link and invalidate old current visibility; new record becomes current only after its own valid promotion. No stale replay restores old version. |
| Expiration | Read-time clock evaluation excludes expired data even without a scheduled worker. Preserve historical promotion receipt; it is not current authorization. |
| Conflict/dispute | Retain both findings and contradiction references; high-impact conflicts block current trusted presentation pending independent re-verification or explicitly authorized escalation. No silent winner. Semantic conflict detection policy is not inferred from keyword matching. |
| Delete/forget/legal hold | Reuse existing deletion intent/replay/hold machinery and extend it to full structured Research payloads, indexes and projections. Honor deletion before new writes/replay; purge or suppress according to existing legal retention authority. Preserve non-content tombstones/audit when permitted, not undeletable full research history. |
| Revoke | Invalidate current promotion/subject grant/attestation as appropriate immediately; durable ordered event and propagation to authorized views/exports. Old events, caches, backups and delayed reads cannot revive access. |

Obsidian remains a selected view, not the authoritative structured payload. Existing bridge `MemoryPort` (:353–360), explicit registration (:625–657), owner scopes (:659–675), routes in `routing.py:14–58` and export/Sync pipeline remain in place. Never call synthetic `V1MemoryPort`'s direct database fallback (:363–393) from Research. No Research Markdown writer or default HQ capture route.

For the first canary, select no Research export/Sync/HQ mapping. For later approved export, Memory-owned bridge reads must expose only current eligible promoted Research projections; generic bridge edits/reviews cannot overwrite attested content in place. Requests, EXPORTED and SYNCED retain distinct attempt/record/version/destination/prerequisite identities. `cycle.py:68–102` explicitly says CLI exit is insufficient and includes an offline verifier boundary; actual live verifier/receipt activation remains UNKNOWN. Preserve repaired publication/quarantines and existing service ownership.
