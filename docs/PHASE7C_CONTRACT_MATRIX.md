# Phase 7C — Integration contract matrix

## Scope, evidence and decision rules

This is a **local, documentation-only reconciliation**, not host-owner sign-off, adapter implementation or production activation. No Linux access occurred in Phase 7C. Evidence is the seven reports under `artifacts/audits/phase7b-20261015/`, whose Linux observation timestamp is 2026-10-16 04:41 UTC, the accepted Phase 7A manifest, Phase 0–6 reports/corrections, `docs/CONTRACT_GAPS.md`, and current local interfaces. Earlier milestone reports have historical counts/status; the accepted corrected baseline is 256 tests. No tests were newly executed for this documentation change.

The accepted release inventory has 77 payload files/79 archive members. Its recorded archive SHA-256 is `99d4384e1d00592ce193bbcf91678dda62ffe6509a49b3c107e57cb17225ead8`. All listed payload files were checked against current bytes before drafting. These four new documents are outside that frozen release; do not silently update, transfer or deploy it.

| Status | Meaning in this matrix |
|---|---|
| VERIFIED | The stated narrow fact/schema is established from inspected source/configuration/metadata, or inspected local code. Linux source verification is inherited from Phase 7B, not a fresh live probe. It does not assert API reachability, entitlement or end-to-end correctness. |
| PARTIAL | A usable part is known, but field mapping, effective configuration or lifecycle semantics remain incomplete. |
| MISSING | A required contract is not identified in the inspected scope. This does not assert that it cannot exist elsewhere. |
| BLOCKED | Required permission, approval or protected configuration/authority evidence prevents proceeding. |

Every non-VERIFIED row is a closure obligation. VERIFIED rows also require later authorized runtime acceptance. A complete production path is **BLOCKED**, not VERIFIED by combining several source observations. Proposed operations below are logical requirements, never invented installed URLs or credentials.

Evidence keys (all local Phase 7B report filenames share `artifacts/audits/phase7b-20261015/`): B = PHASE7B_LINUX_BASELINE.md; H = PHASE7B_HERMES_PHOTON_CONTRACTS.md; M = PHASE7B_MEMORY_OBSIDIAN_CONTRACTS.md; D = PHASE7B_DEVELOPMENT_CTO_CONTRACTS.md; C = PHASE7B_COMPANY_ISOLATION_GAPS.md; P = PHASE7B_PROVIDER_SOURCE_GAPS.md; I = PHASE7B_INTEGRATION_PLAN.md. The adapter spec resolves these to exact source files and fields; the acceptance document supplies test IDs.

## Research foundation and runtime

| ID | Contract | Status | Established evidence / missing closure | Owner; acceptance |
|---|---|---|---|---|
| R01 | Internal one-source task, immutable packets, exact verifier linkage, budget/retry/outbox state | VERIFIED | Local contracts.py, state.py, persistence.py and accepted tests; Research schema v2 is not Memory schema v3. | Research; T01,T04,T10,T11 |
| R02 | Production-safe execution/receipt contracts | BLOCKED | Current runtime/provider/registration, source origins, intelligence and message/Memory records deliberately require simulation or reject production. Explicit reviewed live variants/ports and genuine attestations are needed; never strip simulation markers. | Research + Security + Memory; T02,T05,T06 |
| R03 | Linux Python/SQLite/filesystem execution compatibility | PARTIAL | B: Ubuntu 24.04.5, Python 3.12.3, SQLite 3.45.1, required exception/POSIX APIs. Linux full suite, filesystem durability and worker isolation untested; >=3.11 is staging gate despite metadata >=3.10. | Operations; T01,T11,T19 |

## A. Hermes and Photon

| ID | Contract | Status | Established evidence / missing closure | Owner; acceptance |
|---|---|---|---|---|
| HP01 | Existing Research extension seam | VERIFIED | H: gateway/profile_routing.py and hooks.py provide profile-scoped routing/hooks. No registered Research hook is established. | Hermes; T03 |
| HP02 | Inbound messaging wire data | VERIFIED | H: Photon GET /inbound NDJSON, messageId/space/sender/content/timestamp normalized to MessageEvent. Authentication-to-Research mapping is a separate obligation. | Photon/Hermes; T03,T04 |
| HP03 | Authenticated Research request envelope | MISSING | No installed Research envelope/version or issuer/current grant contract identified. Define trusted subject/tenant/purpose/event binding and one submitted source; preserve source text as data. | Hermes + Security; T02–T04 |
| HP04 | Dedicated Personal/company conversation bindings | BLOCKED | H,C: no effective Research route map inspected. Need approved existing conversation/profile/sender/recipient scopes and tenant IDs; do not invent IDs or distinguish companies by message text. | Messaging owner + company owners; T03,T13 |
| HP05 | Existing outbound send wire | VERIFIED | H: token-protected POST /send with spaceId/text returns ok/messageId; sidecar listener observed at 127.0.0.1:8789. This is not confirmed delivery. | Photon; T12 |
| HP06 | ACK/FINAL identities and factual completion wording | PARTIAL | Local Notice IDs/states exist, but live envelope, correlation and permitted wording need mapping. ACK, task completion, send acceptance and delivery stay distinct. | Research + Photon; T04,T12 |
| HP07 | Message idempotency, authoritative lookup/absence and delivery reconciliation | MISSING | H: generic Hermes delivery ledger allows possible-duplicate retries; caller operation lookup/true delivery/definitive absence not established. Must not blindly resend ambiguous outcomes. | Photon/Hermes; T10,T12 |
| HP08 | Stale prepared/accepted notice cancellation and delivered correction event | MISSING | Phase 6 safely withholds stale prepared notices and does not rewrite delivered notices. No real cancellation/update contract identified. | Photon + Memory; T09,T12 |

## B. Memory and Obsidian

| ID | Contract | Status | Established evidence / missing closure | Owner; acceptance |
|---|---|---|---|---|
| MM01 | Existing Memory action dispatch/schema | VERIFIED | M: installed /v1/memory actions, JSON/size/auth/error boundary; installed /v1/obsidian-memory action allowlists/versioned writes. Not a complete Research API. | Memory; T06 |
| MM02 | Authentication and authorization mapping | PARTIAL | M: bearer→active principal; agent task assignment; Alfred-kind review; separate fixed-actor bridge bearer. Research principal/grant and packet authority mapping unidentified. | Memory + Security; T02,T06,T13 |
| MM03 | Active endpoint/configuration and permitted Research caller credentials | BLOCKED | Protected /etc/alfred-memory-v1 and /etc/alfred-obsidian-editor-hq inaccessible. Require redacted active contract/version/grant references, not secret values or broader filesystem access. | Memory owner; T06 |
| MM04 | Research candidate, durable commit, independent trusted promotion | MISSING | Existing capture/create can approve content directly and review digest is not Research packet digest. Need Memory-owned candidate/attestation and distinct operation receipts; reject synthetic verdicts. | Memory + Research verifier owner; T05–T07 |
| MM05 | Citation-preserving fresh specialist retrieval | PARTIAL | M: search returns approved task-scoped results, bounded/truncated content and version. Full evidence/citations, classification/currentness and actual specialist identities/grants are unestablished. | Memory + specialist owners; T07,T13 |
| MM06 | Correction/supersession/expiry/delete/revoke/conflict/currentness | PARTIAL | M: versioned writes and deletion ledger source exist. Research validity, conflicts, exact digest/decision revalidation, external CAS/receipt/revocation semantics remain unsettled. | Memory; T08–T10 |
| MM07 | Existing export/Sync pipeline and selection | PARTIAL | M,B: active editor/capture and waiting worker/Sync timers; Sync depends on Memory/editor/worker. Selected record/destination mapping, active capture/context endpoint and completion verifier remain unknown. | Memory/Obsidian; T09 |
| MM08 | Distinct export-request, EXPORTED and SYNCED receipts | MISSING | No established live receipt/attempt lookup suitable for Phase 5 prerequisites. Need current attempt/version/destination/prerequisite binding and independent remote-completion proof. | Obsidian/Memory; T09,T12 |

## C. Development CTO

| ID | Contract | Status | Established evidence / missing closure | Owner; acceptance |
|---|---|---|---|---|
| DC01 | Existing trusted Gateway envelope | VERIFIED | D: alfred.devreq/1, strict fields/64 KiB bound; workflow/company/approval fields stamped by trusted dispatcher. It is a Development request, not a Research proposal. | Development; T15 |
| DC02 | Existing authenticated intake/approval boundary | VERIFIED | D: Unix SO_PEERCRED; observe only sidecar UID, submit/status only Hermes UID with previously observed message/digest; separate privileged grant actions. | Development/Security; T15 |
| DC03 | Automated proposal-only Research→CTO intake and receipt | MISSING | No inspected proposal endpoint/operation identified. Need inert evidence-linked proposal reception and accepted/duplicate/rejected/status semantics; do not synthesize owner observations or inbox files. | Central CTO; T15 |
| DC04 | Existing eleven specialist identifiers | VERIFIED | D: frontend, backend, full_stack, devops, data_engineer, data_scientist, ai_ml, integration, security, mobile, performance. | CTO; T15 |
| DC05 | Research proposal caller grant and later Development execution approval | BLOCKED | Actual caller/owner/socket/grant references not approved for Research. Proposal acceptance never implies execution, installation, QA bypass, publication or deployment approval. | Owner + CTO; T15 |

## D. Companies and Alfred HQ

| ID | Contract | Status | Established evidence / missing closure | Owner; acceptance |
|---|---|---|---|---|
| CI01 | Inspected registry company entries | VERIFIED | C: companies section of trusted Development registry/projects.yaml contains only id alfred/display_name Alfred. This is not a global census of all host registrations. | Registry owner; T13 |
| CI02 | Gabos/Fintra/SC Research tenant and Memory mappings | MISSING | Bridge labels GABOS/FintraAI/SCPG are not verified live identities, vault IDs or consent. No authoritative four-environment manifest identified. | Company + Memory owners; T13 |
| CI03 | Separate credentials/OS/storage/grants/budgets | BLOCKED | Department service users/0700 roots observed, not complete company isolation. Need approved per-environment principal/credential references and role/provisioning/revocation policy. | Security/Operations; T02,T13,T19 |
| CI04 | Eligible company→protected HQ partition delivery | MISSING | Offline bridge abstractions/labels are known; live eligibility, company partitions, versions/policy/tombstone receipts and anti-replay not established. | Memory/HQ owners; T14 |
| CI05 | Independently authenticated owner retrieval and audit | PARTIAL | Source actor labels alfred/hayden and scoped references exist. Need owner capability issuance/expiry/revocation, partition/classification grants and audit; body actor labels cannot confer access. | Security + HQ owner; T13,T14 |
| CI06 | Production durable Research database registration authority | MISSING | Local OfflineRegistrationAuthority is in-memory test-only; no verified independently protected durable host equivalent. Director-only provisioning/replacement and recovery/key/restore policy must be agreed. | Security/Operations; T02,T11,T19 |

## E. Models, sources and operations

| ID | Contract | Status | Established evidence / missing closure | Owner; acceptance |
|---|---|---|---|---|
| PR01 | Existing provider/configuration mechanisms | VERIFIED | P: Hermes runtime_provider/config_providers/credential-pool and Development selection source. Source presence is not account entitlement or Research approval. | Runtime owner; T05 |
| PR02 | Fixed Research role/model assignments and real authorization | BLOCKED | Exact approved provider/model/role/environment/price/credential-reference manifest absent. Do not adopt a source-code default or Development fallback. | Owner + Research Director; T05 |
| PR03 | Live acquisition provenance and submitted-source lifecycle | MISSING | Current SourceFixture/SourceResult permit only fixture/user_supplied; source.v1 requires pinned revision/digest. Need genuine acquisition receipts and durable URL→snapshot correlation, not fabricated pins/origins. | Source + Research owners; T04,T16 |
| PR04 | Authorized GitHub and web retrieval | PARTIAL | P: Git and web-provider source exist. Rights, actual commit/tree authenticity, redirect/peer/DNS/proxy checks, bounds and provider receipts unverified. HTML remains PARTIAL/NMR locally. | Source/Security owners; T16,T17 |
| PR05 | PDF extraction | MISSING | No qualified parser in inspected system Python/PATH; service venvs not inspected. Keep UNSUPPORTED until parser/dependency/sandbox approval and tests. | Source/Operations; T17 |
| PR06 | YouTube/Instagram/TikTok retrieval/transcription | MISSING | No authorized platform-specific live contract established. Generic transcription source does not prove access, rights, captions or installed models. | Provider/account owners; T17 |
| PR07 | X search and genuine citation retrieval | PARTIAL | P: x_search source supports xAI credential resolution; approved account, model/cost and actual citations remain unverified. No inferred viewing or verification from generated answers. | Provider/Research owners; T17 |
| PR08 | Real independent factual verification | MISSING | Current exact-text synthetic assessment is not source authenticity/semantic corroboration. Need independent runtime identity, approved evidence policy and genuine attestation bound to packet/digest/environment. | Verification owner; T05,T06,T18 |
| PR09 | Provider usage, adaptive reservations, timeout/cancellation reconciliation | PARTIAL | Local integer ledgers/task caps/retry IDs work; real usage units, price version, request lookup and ambiguous billing/refund policy absent. | Provider + budget owner; T05,T10 |
| OP01 | Transfer/staging/production change authorization | BLOCKED | This task authorizes four documents only. Runtime locations, users, grants, installs and changes require exact separate approvals. | Owner/Operations; T01,T20 |
| OP02 | Backup, retention, anti-rollback and operational rollback | PARTIAL | B: backup timer/state path metadata exists. Backup success/restore proof and registry/Memory/HQ/notification ordering protections unverified. | Operations + Memory; T19,T20 |

## Closure requests and first-path gates

Request redacted owner-approved contract/version documents, capability/grant references and synthetic example schemas—not credentials, vault content or raw configuration dumps. Each owner must supply issuer, caller scope, field/type/error schemas, operation ID and receipt lookup, validity/CAS/revocation semantics, failure policy, evidence reference and sign-off. Only then may the matrix row be promoted; source inspection alone cannot close a runtime gate.

First Personal public-GitHub canary depends on R02, HP03/HP04/HP07, MM02–MM06, CI06 and PR02/PR03/PR04/PR08/PR09. Export/Sync and company HQ may be explicitly unselected for that narrow canary, with no success claims; MM07/MM08/CI02–CI05 still block full V1. DC03/DC05 block claiming actual CTO proposal reception; an inert local proposal is not a delivered handoff. Acceptance plan defines these separate gates without weakening the full agreed V1.
