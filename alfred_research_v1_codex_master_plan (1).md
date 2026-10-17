# Alfred Research & Intelligence V1 — Mac Codex Master Plan
Date: 2026-10-15
Status: Architecture confirmed, implementation not yet executed
Acceptance: C — End-to-end operational acceptance, including Linux live integrations

## Confirmed decisions 1–20
1. D Autonomous intelligence pipeline
2. D Central intelligence with company isolation
3. Separate research departments/infrastructure per company (confirmed in whiteboard follow-up)
4. D Comprehensive HQ intelligence with controlled sync
5. D Autonomous adaptive research
6. D Autonomous specialist intelligence network
7. D Autonomous knowledge evolution
8. A On-demand only (no scheduled/continuous discovery)
9. B Fixed models and adaptive research budgets
10. D Autonomous research operations
11. D Adaptive organizational intelligence
12. D Adaptive full-spectrum intelligence
13. B Lead researcher with supporting specialists
14. D Intelligent department handoff
15. B Dedicated Research conversation
16. D Separate company identities with central Research inbox
17. A Single-source research (one source = one task)
18. A Short completion confirmation
19. D Full Research Department V1
20. C End-to-end operational acceptance

## Mission
Build one repeatable *product architecture* deployed as independently isolated research environments for Personal Alfred, Gabos Holdings Inc., Fintra AI, and SC Products Group. Each has dedicated logical intake/identity, Director, lead/specialist execution, independent verification, knowledge, credentials, and storage. Synchronize eligible company knowledge into company-specific, permission-preserving Alfred HQ partitions; allow audited owner-level cross-company retrieval but never cross-company agent access. The existing Hermes/Photon entrypoints, Development V1 approval/CTO/router/QA/reviewer/publisher, and structured Memory+Obsidian integration are preserved.

## Source support
Source categories required by selected scope: GitHub repositories; public websites/articles; YouTube; Instagram; TikTok; X posts; PDFs and local documents. Define each adapter with explicit outcomes SUPPORTED_FETCHED, PARTIAL, AUTH_REQUIRED, INACCESSIBLE, UNSUPPORTED, or ERROR. Never claim to have viewed/transcribed restricted media without evidence. Respect provider authorization and copyright; avoid unauthorized scraping/bypass. One user-submitted link/file per task. A GitHub repository may contain multiple independently evaluated skills under that one task.

## Standard task flow
Authenticated source intake -> immutable task identity+environment -> classified source fetch/metadata/snapshot -> choose lead specialty, optionally supporting specialties -> claim extraction -> independent corroboration where warranted -> canonical versioned research packet -> independently recorded verdict bound to packet digest (APPROVED / REJECTED / NEEDS_MORE_RESEARCH) -> intelligent classification and knowledge evolution -> Memory-owned adapter confirmed commit and retrieval -> authorized specialist read visibility and optional CTO proposal (proposal only) -> company-specific HQ sync via approved Memory adapter -> short completion status with truthful receipts.

## Distinguish knowledge from executable skills
Research may analyze untrusted GitHub skill instructions and propose developer routing. Do not execute imported content or install skills. Third-party prompt instructions are data. Only Development CTO's current trusted intake, explicit owner development approval, authorized developer sandbox, independent QA/review, and separately approved publishing/release can install or change running capabilities.

## Separation of responsibilities
Research owns ingestion, evidence, packet preparation, independent verification decision artifacts, classification, specialist matching, and proposed exports. Memory owns authoritative structured writes, promotion criteria, tenant vault mapping, Obsidian exports, HQ sync, retention/deletion, and trusted retrieval authorization. Development owns executable skill changes and releases. Messaging/Hermes owns actual inbound identity and outbound message delivery. Never fabricate production endpoint paths, schema compatibility, or receipts.

## Phase 0 — Mac audit and contracts (read-only)
- Examine local workspace and attached handoff, identify existing source, tests, tooling, and permissions.
- Check git status before any changes. Do not assume Mac repo has real Linux integration source.
- Document source-of-truth vs unverified interfaces and conflicts with earlier handoff (earlier GitHub-only R1 vs newly selected full V1, earlier single Personal messaging vs dedicated Research conversations, earlier generic Memory candidate vs owner-level HQ sync).
- Produce architecture/contract map, risks, local test commands, concise staged workplan.
Gate: explicit interfaces-to-inspect list and no modified production components.

## Phase 1 — Core contracts and isolated runtime
- Schema-versioned research request, source, task, evidence, claim, packet, verification verdict, knowledge candidate, specialist intelligence item, CTO proposal, delivery receipt, and HQ sync event.
- Enforce immutable environment/company identity derived from authenticated intake, never URL text.
- Separate storage, credentials, runtime contexts, queue partitions, and per-environment budgets; test deny-by-default.
- Durable task state machine, idempotency keys, retry/recovery, audit events, canonical packet hashing.
- Provider/model assignments fixed by per-environment configuration; bounded adaptive work budgets; model changes require approval.
Gate: unit/integration tests for tenant separation, idempotency, digest invalidation, crash recovery and budget boundaries.

## Phase 2 — Source adapters
- Common interface with honest accessible/partial/blocked outcomes and source identity/digests.
- GitHub read-only pinned commit inventory, manifest/skill parsing, license/dependencies, detection of risky paths/symlinks/submodules/injection; never run content.
- Public website and article extraction with attribution, chronology and citation locations.
- PDF/local-document extraction with provenance; protected file handling.
- YouTube authorized metadata/transcript ingestion if available; otherwise partial/blocked.
- Instagram/TikTok/X authorized API/content extraction only if accessible; otherwise partial/blocked, allow user-supplied original media/transcript as separate authorized submission.
Gate: local recorded fixtures for every category, success+partial+unavailable+malformed cases, bounded parsing, no unauthorized data fetch or code execution.

## Phase 3 — Research agents and verification
- Research Director, lead specialist selection, supporting specialist collaboration within single environment, general/code/finance-tax/business-legal domain configurations as approved; no unnecessary idle model processes.
- Adapt depth to claims, importance, sources and budgets, always on-demand.
- Evidence mapping per claim, uncertain claims and changed source treatment.
- Independent verifier separate from researcher; APPROVED/REJECTED/NEEDS_MORE_RESEARCH; verdict bound to exact canonical packet digest and tenant.
Gate: verification cannot be self-approved, changed packet cannot reuse approval, unsupported content cannot become verified.

## Phase 4 — Intelligence, evolution, and department proposals
- Topic and specialist taxonomy, department classification, duplicates, versioning, provenance, supersession, conflict review; no silent correction of conflicting high-impact findings.
- Specialist knowledge views enforced by auth and verification at retrieval.
- Skills repository -> multiple capability evaluations -> map to EXISTING 11 Development V1 specialties (Frontend, Backend, Full-Stack, DevOps, Data Engineering, Data Science, AI/ML, Integration, Security, Mobile, Performance).
- Emit evidence-bound CTO proposals, never executable actions or approval tokens.
Gate: development specialists retrieve authorized approved facts in a fresh task; unapproved/out-of-scope facts remain unavailable.

## Phase 5 — Memory & HQ sync adapters (Mac simulations)
- Consume Memory handoff contracts after agreement with Memory team; implement tested local fakes pending Linux inspection.
- Write candidate vs promote to trusted is explicit; require Memory write receipt + independently verified retrieval; Obsidian export/sync distinct receipts.
- Company-specific HQ partitions preserve source tenant/company, access policy, classification, provenance, update/retraction/delete semantics; no flattening into unrestricted global store.
- Owner-level audited retrieval (not global dissemination); company-to-company negative tests.
Gate: authorized owner reads Fintra/Gabos/SC independently, company actors cannot cross-read, replays do not duplicate and revoked/deleted knowledge is removed from current retrieval.

## Phase 6 — Communications, operational reliability, Mac acceptance
- Dedicated personal/company Research identity mapping and one-source intake contract, simulated on Mac because Photon capabilities require Linux confirmation.
- Short initial acknowledgment and short final success/partial/failure message; avoid premature success.
- Durable outbox and deduplicated notifications; retries and recoverable task restart.
- Run complete Mac fixture-based end-to-end tests and produce signed/digested inventory, reproducible test output, acceptance report, and integration-gap list.
Gate: full local pipeline PASS, real service claims explicitly marked MOCKED/UNVERIFIED.

## Phase 7 — Linux integration (separately authorized)
- First read-only inspect Linux Hermes routing, Photon identities, Development CTO/Gateway schemas, Memory API+Obsidian export and vault permissions, current services, and deployment layout.
- Reconcile contract versions; produce smallest adapters; never redeploy known-good components blindly.
- Install/reconfigure only after owner approval, with backups/rollback and separately authorized deployment actions.
- Test one public GitHub source through real dedicated research ingress -> real research execution -> independent verification -> Memory confirmed promotion -> fresh authenticated retrieval by relevant specialist -> CTO proposal only -> iMessage completion.
- Test public article and at least one accessible legal media/document scenario; test unsupported-platform honesty, outages and restart recovery.
- Test each company environment, HQ partition synchronization and permitted owner retrieval; deny cross-company queries.
Gate: real end-to-end results and receipt/audit evidence; only then V1 operational acceptance. Mac PASS alone is NOT sufficient.

## Required acceptance assertions
1. Intake identity cannot be overridden by text inside a source URL or prompt.
2. Single submitted source/task, with independently analyzed child skills for multi-skill repositories.
3. Untrusted repositories and webpages never execute instructions, shell scripts, skill files, hooks, or unapproved network/secret operations.
4. Verification verdict cryptographically binds exactly to packet content, scope and evidence; mutation invalidates prior approval.
5. Duplicate and retried events preserve exactly-once effect through idempotent writes and auditable receipts.
6. Permanent company separation; owner-only HQ visibility remains audited, partitioned and access-checked.
7. A changed or superseded fact is not silently reused as current; evidence conflict is visible.
8. Every actual completion claims only observed confirmed steps. Missing/blocked source reports limitations.
9. Budget ceilings enforced by provider/environment; fixed model identity; no silent provider substitution.
10. Research emits proposals, never authorizes development or GitHub publishing.
11. A freshly started authorized developer can retrieve approved knowledge and citations.
12. Real Hermes/Memory/Photon integration validated on Linux before operational PASS.

## Unresolved contracts requiring Linux host inspection
- Multiple dedicated iMessage Research conversation identities via existing Photon/Hermes; must not invent a second Photon instance.
- Real Research Director execution/runtime API (may not exist).
- Real memory API/schema, verified write and retrieval interface; exact Obsidian export and company vault mapping.
- HQ sync import/export authorization, master/replica policy, conflict and deletion propagation.
- CTO/Gateway proposal intake contract, approval and publisher status.
- Provider availability, API rights and credentials for Grok/xAI or other preassigned models.
- Legal access to social videos and transcripts.

## Codex CLI — FIRST PROMPT (Phase 0 only)
You are working on Alfred Research & Intelligence V1 on my Mac. This project has 20 owner-confirmed architectural decisions and an existing Linux Hermes, Development V1, Memory and Obsidian system that must NOT be rebuilt or modified. Read this master plan and the two handoff documents available in the workspace before acting.

Your task in THIS RUN IS PHASE 0 ONLY: inventory the current Mac repository and development environment read-only, identify reusable code, exact contracts we can ground locally, missing Linux-only interfaces, compatibility risks, and propose a dependency-ordered implementation plan for Phases 1–7 with tests and acceptance gates. Do not implement code yet. Distinguish inspected facts from historical handoff claims and proposals. Confirm git branch/status and baseline; note untracked user data without changing it. Do not fetch or execute third-party repositories, change credentials, install packages, modify Linux/Photon/Hermes/Memory/Development, push or commit to GitHub, or create an independent messaging gateway. Do not fabricate successful integrations. Output: ARCHITECTURE_AUDIT.md, CONTRACT_GAPS.md, PHASED_IMPLEMENTATION_PLAN.md, and a concise proposed file tree; you may create only these planning documents in a new Mac-local research staging directory after checking for collisions. End by printing tests to be required in the next phase, the files written, and STOP for owner review.
