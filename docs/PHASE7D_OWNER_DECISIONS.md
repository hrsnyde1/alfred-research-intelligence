# Phase 7D — Decisions and evidence for the first Personal canary

Status: proposals, not approvals. Read with PHASE7D_PERSONAL_CANARY_READINESS.md (C01–C11, G0–G6). Acceptance of Phase 7C does not establish missing interfaces. No secret value, private record or raw protected configuration is requested. Each closure needs owner/component sign-off, version/hash reference and redacted synthetic examples including errors and ambiguous outcomes.

## A. Decisions the owner can make now

| Decision | Minimum proposed choice for approval | Still requires component evidence |
|---|---|---|
| D01 — scope | Personal only; one approved public GitHub repository at a full commit, low-risk code/documentation claims; no imported execution, dependencies, submodules, private access or unrelated research. Select exact repository/commit later before any fetch. | C02,C04 acquisition wire and rights. |
| D02 — outputs | Real findings, independent verification, Personal Memory commit/promotion and fresh authorized specialist retrieval; concise ACK/FINAL. Exclude HQ, export/Sync and actual CTO delivery from this canary; retain inert local proposal. | C07–C09 actual receipt semantics. Exclusions do not remove full-V1 obligations. |
| D03 — conversation intent | Use an existing approved dedicated Personal Alfred Research scope with explicit authorized sender and recipient; fail closed for company/unknown scopes. Do not select an arbitrary existing DM or create a new messaging service. | Hermes owner supplies actual effective profile/space/sender IDs, membership/authentication and route mapping. |
| D04 — risk/evidence | Limit findings to what the pinned repository supports; distinguish descriptions from demonstrated runtime behavior. No execution claims, legal/tax assurance or unsupported effectiveness claims. Inaccessible, conflicting or insufficient evidence blocks approval. | Verifier owner approves per-claim assessment/authenticity policy. If corroboration is needed, stop for scoped approval or attach authorized supporting evidence to the same one-source task; no unsolicited second task. |
| D05 — principals/models | Approve the role structure below; choose actual exact provider/model IDs only after redacted entitlement/capability evidence. No default/fallback/substitution. | Runtime/Security supplies real identity, broker, model/API, billing and verifier authority evidence. |
| D06 — limits | Approve all required budget/limit fields and explicit numeric ceilings before enabling execution; no unlimited/null defaults. Excess or unresolved billing escalates/blocks. | Provider/Operations validates units, enforceability and lookup. Synthetic prices are not production prices. |
| D07 — Memory trust | Memory owns validation, commit, promotion and fresh retrieval. Research never obtains global Alfred authority to self-approve. Select permitted Personal classification, retention/expiry and specialist audience. | Memory owner signs exact candidate/receipt/read/currentness schema and least-privilege grants. |
| D08 — first development boundary | Authorize only the synthetic contract harness in PHASE7D_MAC_ADAPTER_SCOPE.md as the next task, if desired. | This document itself authorizes no code. Later production contract development, staging and deployment remain separate approvals. |

## Proposed exact role slots; provider/model selections remain unapproved

| Logical slot / environment | Existing role + specialty | Responsibility / separation | Assignment status |
|---|---|---|---|
| Personal Research Director | director / general | Authenticated planning, lead selection, authorization/budget/deadline/rework controls. Coordinator logic remains Research-specific. | provider_id/model_id/API revision/principal/grant **UNSET — execution blocked**. Director model slot required by current roster; don't invent a model call if coordination uses deterministic code. |
| Personal Technology and Code lead | researcher / technology_code | Exactly one accountable packet author; repository evidence and capabilities, findings versus inference, limitations. | provider_id/model_id/API revision/principal/grant **UNSET — execution blocked**. |
| Personal independent verifier | verifier / general | Independently authorized identity; assess every material claim/citation and exact packet/source/version, preserve verdict/rationale/limitations, no numeric confidence. Cannot be Director, lead or supporter principal. | provider_id/model_id/API revision/principal/grant **UNSET — execution blocked**. Owner must approve model/runtime independence policy; different principal alone does not prove independent execution. |
| Optional Personal support | researcher / one of technology_code, finance_tax, legal_compliance, business_market, general | Off by default for this canary. Only explicit justified same-environment delegation, distinct contributor identity, no approval power. | No automatic enrollment. Existing role-level assignment is shared; different per-specialty models need a reviewed versioned policy extension. |

Fixed assignments are keyed by environment and role in `budgets.ModelConfiguration`; `ResearchAgent` supplies logical specialty. Proposal: retain this mapping for the first canary. Do not invent five independently deployed processes or choose production IDs from test fixtures/Development defaults. A verifier may use the same provider only if the owner explicitly accepts independently scoped execution/credentials and evidence assessment; model diversity, if required, must be fixed and approved, never an implicit fallback.

### Required configuration fields to close D05/D06

These are proposed configuration requirements, not an installed Linux schema. Missing required values fail closed.

| Configuration group | Required fields / decisions |
|---|---|
| Policy identity | schema_version, environment_id, policy_id/version/digest, approved_by authority reference, approval_id, effective_at/expires_at, revocation reference, permitted purpose/source kinds. A boolean approved is insufficient live evidence. |
| Fixed assignment | role, logical specialties, authenticated principal/grant reference, exact provider_id/model_id/API revision, allowed capability/tools, credential_broker_ref (never credential value), execution mode, provider policy version. No automatic tool execution/source instructions. |
| Independence | distinct Director/lead/support/verifier identities and grants, verifier execution/channel separation, approved model diversity policy, signed/authenticated invocation and attestation issuer references. |
| Real pricing | currency or approved integer cost denomination, price schedule/version/effective time, input/output/cached/reasoning token treatment where applicable, minimum fees and other charges, conservative ceiling/rounding conversion to integer ledger units, authoritative usage source. Never use floats in canonical Research contracts. |
| Environment/task | environment spending limit and window/reset authority, concurrent task limit, max_task_cost, per-stage allocations including verifier/rework reserve, allowed increases/escalation approver, absolute task deadline. No implicit budget reset on restart. |
| Invocation | max input/output tokens and other billed units, max_call_units mapping to real units, max cost/reservation per call, provider timeout, concurrency, allowed cancellation, maximum attempt count/backoff and stable retry-operation ID. Existing offline 1–16 call units are synthetic, not a token policy. |
| Acquisition/worker | permitted GitHub host/repository/commit, egress/redirect/address policy, max files/depth/bytes/output/work, acquisition timeout/rate/concurrency, disk/CPU/RSS ceilings, sandbox/no execution, evidence retention/expiry. |
| Reconciliation | stable provider operation/request identity, authoritative status/usage lookup, accepted/unknown/failed distinction, reservation settlement/cancellation/overrun policy, no retry/refund until ambiguity is resolved or conservative budget hold/escalation. Unsupported provider lookup must be explicitly handled, never assumed exactly-once. |

No numeric production budget or approved model ID is supplied by existing evidence. Owner decisions must fill values after pricing/entitlement evidence; unresolved values keep the policy disabled.

## B. Missing component-owner contract evidence

| Responsible owner | Required redacted evidence | Consequence if absent |
|---|---|---|
| Hermes/Photon | Effective ingress/profile hook lifecycle, authenticated event envelope/issuer, exact Personal route/recipient scope, single-source pending intake/ACK semantics; operation send/lookup/definitive absence/delivery/currentness/correction schemas and retry owner. | C01,C02,C09 block real routing and truthful reliable notification. An existing send endpoint cannot supply missing guarantees by inference. |
| Memory | Active API version/action/schema/error examples and scoped caller grants; candidate attestation validation, commit/promotion/CAS/idempotency/status lookup; full citation-preserving specialist read and currentness/revocation policy; fresh receipt issuer. | C07,C08 block trusted storage/retrieval. Auto-approved create/capture and truncated search cannot substitute. |
| Research verifier/runtime | Genuine provider execution/usage receipts, exact assignments and account entitlement references, source authenticity and factual/inference/contradiction assessment policy, independent verifier attestation issuer and verification mechanism. | C05,C06 block actual research/verification. A synthetic result or model-generated authorization field is not evidence. |
| Security/Operations | Host-issued capabilities, Director-only provisioning/replacement, durable registration authority separate from database/receipt; trust storage/rotation/revocation/loss/restore; approved paths/users/limits and backup proof. | C03,C11 block safe real state and recovery. Do not ship test authority snapshots as production trust. |
| Source owner | Approved GitHub acquisition port/rights, full-commit authenticity, safe bounded tree materialization/no hooks, digest/provenance/error/retry receipts. | C04 blocks genuine acquisition. Local synthetic parsing remains usable only as such. |
| Specialist owner | Real Personal specialist principal, scope/classification/task/currentness grants and fresh-read permission. Existing `frontend` routing ID is a category, not a grant. | C08 blocks claiming authorized specialist retrieval. |

## C. Items requiring separately authorized Linux read-only discovery

Prefer component-owner redacted evidence; use discovery only for unresolved facts. Current Phase 7D does not reconnect to Linux.

1. Confirm active Hermes service-home profile/hook activation and Photon interface version, nonsecret route/receipt support and actual existing Personal conversation mapping. Do not dump message history or raw runtime configuration.
2. Confirm active Memory handler/version and nonsecret candidate/review/currentness/full-read port availability. Existing source may not be activated. Protected `/etc` directories require owner-supplied evidence; no sudo, token reads, private records or probing production writes.
3. Confirm approved worker Python/environment, service identity, isolation/allowed state locations, supervision and existing durable registration service availability. Read metadata only; no filesystem durability or restore test during read-only discovery.
4. Confirm effective nonsecret provider configuration/capabilities and GitHub acquisition port without auth login, credentials, entitlement probes or model/fetch calls. Account rights and real execution still require owner evidence/operational acceptance.
5. Obtain redacted backup/restore and delivery incident evidence if existing; logs that may contain private content require owner redaction. A timer's active state is insufficient.

Unknown after discovery remains unknown; it is not permission to create an API.

## D. Items requiring implementation/deployment authorization

Separate approvals are required for (1) Mac synthetic harness; (2) reviewed Mac live-contract/port changes and production adapter development; (3) Memory-owned candidate/attestation/full-read/currentness extensions if no sufficient port exists; (4) Hermes-owned authenticated attachment/intake and Photon-owned receipt/reconciliation extensions if absent; (5) protected identity/registration provisioning; (6) exact artifact transfer/extraction and isolated Linux execution; (7) any host installation/configuration/service action; (8) actual provider/source access with spend and egress; (9) scoped production Memory writes/retrieval and actual message recipients; (10) production canary dispatch/rollback diff.

Owner policy acceptance alone cannot manufacture component schemas or credential grants. Neither read-only SSH access nor Mac code approval authorizes Linux changes. Company/HQ, actual CTO handoff and Obsidian integration are separate later gates, not tasks for this first boundary.
