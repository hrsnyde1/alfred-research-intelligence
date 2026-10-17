# Research & Intelligence V1 — Phase 0 architecture audit

Audit date: 2026-10-15. Scope: this Mac Research repository only. No Linux inspection or operational acceptance occurred.

## Evidence and authority

Labels used throughout these documents:

- **VERIFIED LOCAL:** directly inspected in this repository or through read-only tooling checks.
- **REQUIREMENT:** owner-approved architecture, including the confirmed 20-decision master plan.
- **HISTORICAL:** reported handoff behavior; not independently tested here or evidence of current availability.
- **PROPOSED:** local design or future interface; not an existing production contract.
- **UNKNOWN LINUX:** requires separately authorized inspection and contract reconciliation.

The exact requested filenames `alfred_research_v1_codex_master_plan.md`, `Alfred_Memory_Research_Intelligence_Handoff.txt`, and `README.md` are missing. These supplied filename variants were read instead, without renaming them:

| Supplied document | Inspected identity and authority |
|---|---|
| `alfred_research_v1_codex_master_plan (1).md` | Mac master plan, dated 2026-10-15; confirmed decisions 1–20 and Phases 0–7 |
| `Alfred_Memory_Research_Intelligence_Handoff (1).txt` | Memory design reference, dated 15 October 2026; historical results, requirements, breadcrumbs and unknowns |
| `README (1).md` | Title explicitly identifies Research & Intelligence → Development & Memory cross-chat handoff, dated 2026-10-15; not an unrelated README |

The current user instruction governs Phase 0 scope. The confirmed master plan governs architectural decisions over older handoff proposals. Nothing in the earlier instruction to implement R1 authorizes implementation in this run.

## Verified local baseline

- Repository: `/Users/haydensnyder/Git/alfred-research-intelligence`; branch `main`, with no commits. `git ls-files` returned no tracked files.
- Initial untracked files: `.gitignore` and the three supplied handoffs above. An ignored `error.log` exists; its contents were not needed or inspected.
- No existing Research source, tests, dependency manifest, service configuration, or reusable integration implementation was found. No local `AGENTS.md` or checked ancestor instruction file was found.
- `.gitignore` excludes environment files, virtual environments, caches, logs, secrets, and data/runtime/artifact directories. It is unchanged.
- This audit creates only the three requested documents in the previously absent `docs/` directory. Existing user files remain unchanged.

| Tool | Observed result | Practical implication |
|---|---|---|
| `python3` | Python 3.14.3, `/Library/Frameworks/Python.framework/Versions/3.14/bin/python3` | Available; Linux compatibility not established |
| `python` | Python 3.9.6, `/usr/local/bin/python` | Different interpreter; future commands must select explicitly |
| Git | 2.33.0 | Available; repository has no baseline commit |
| uv | 0.9.17 | Available, not used to resolve/install anything |
| pip for `python3` | 26.1.1 | Available, no installation performed |
| Node / npm | v24.21.0 / 11.19.0 | Available, not required for proposed Python core |
| make | GNU Make 3.81 | Available |
| Docker | Executable located at `/usr/local/bin/docker` | Daemon, version and operational readiness not tested |
| pytest / ruff / mypy / poetry | No executable found on PATH | Do not assume available |
| Python 3.14 modules | pytest, ruff, mypy, pydantic, yaml not import-discoverable | Standard-library offline core is feasible; dependencies need later authorization |

No services, networks, company vaults, credentials, other project repositories, or third-party skills were accessed. No tests exist to run; this is document validation, not a functional PASS.

## Historical functionality versus new requirements

**HISTORICAL Memory:** phone conversation save and fresh-conversation recall; explicit HQ capture through `alfred_memory_v1` action `save_to_alfred_hq`; exported Markdown visible in Windows Obsidian; two exports with matching hashes and zero pending files after repair. Ordinary conversation saving did not prove structured fact extraction or automatic Obsidian export. Research promotion and company isolation were not verified. Server shutdown was reported; current host status is unknown.

**HISTORICAL Development:** existing Photon/Hermes, trusted intake/Gateway, Central CTO and 11 specialist categories; disposable T-0002 calculator task passed Developer/QA/Reviewer. Publisher had 26 staging tests but was not installed/published. A separate Mac notification/mock package reportedly had 791 passing tests; it is not present here and proves no live compatibility. Recorded hashes and destinations are historical evidence, not new authorization.

**REQUIREMENT:** four independent environments: Personal Alfred, Gabos Holdings Inc., Fintra AI, SC Products Group. Each has a Director, lead researcher, optional task-specific support, independent verification and isolated Memory. Reusable code does not imply shared runtime authority, credentials, data, queues or budgets. Owner-only HQ retrieval preserves company partitions and audit; company agents cannot cross-read.

**REQUIREMENT:** on-demand, one submitted source per task; GitHub, websites/articles, PDFs/local documents, YouTube, Instagram, TikTok and X. A repository can yield multiple child capability evaluations. Fixed model assignments, bounded adaptive budgets, no silent provider substitution. Independent verdicts are APPROVED, REJECTED or NEEDS_MORE_RESEARCH and bind to the exact packet digest. No numerical verification confidence scores.

**REQUIREMENT:** automatic classification, versioning and authorized specialist distribution after verification and Memory promotion; dedicated personal/company Research conversations; short truthful completion notifications; CTO approval workflow for executable capabilities; real Linux end-to-end evidence before V1 acceptance.

## Reconciliation of handoffs

| Earlier handoff statement | Governing interpretation |
|---|---|
| GitHub R1; social/media/company directors later | Full selected V1 includes all named sources and four environments, delivered in stages |
| Dedicated iMessage identity optional | Dedicated Research conversations are planned requirements; actual Photon mapping remains unknown |
| Central Research/shared infrastructure | One repeatable product architecture with independent environment authority and storage boundaries |
| No cross-company sharing | Still enforced; protected owner HQ access is an audited exception for owner retrieval, not company-to-company dissemination |
| Candidate export to Memory | Preserve candidate/commit/promotion distinction; add approved specialist views and protected HQ sync through Memory-owned adapters |
| Confidence examples in proposed README schema | Use evidence, limitations and verdict rationale; no numerical verification scores per Memory handoff |
| Grok/xAI preference | Not an exact approved model assignment or evidence of provider access; configuration remains blocked pending confirmed assignments |

## Proposed minimal architecture

A Python library and Research task runner attached to existing Hermes execution/routing. This runner coordinates only Research tasks; it is not a replacement orchestrator, messaging gateway, Memory service, or Development workforce. Begin with standard-library contracts, hashing, SQLite task metadata and offline tests; SQLite here is Research-local state, not a claim about Memory storage.

Proposed module tree (future files, not created in Phase 0):

```text
src/alfred_research/
  contracts/        # schema versions, request, evidence, packet, verdict, receipts
  tenancy.py        # authenticated immutable context and policy checks
  state.py          # per-environment durable tasks, audit, retries, outbox
  budgets.py        # fixed assignment checks and bounded reservations
  sources/          # common result + github, web, document, media adapters
  research/         # Director coordination, lead/support roles, model port
  verification.py   # independent role and exact packet-digest binding
  intelligence/     # taxonomy, specialist matching, versions, conflicts
  ports/            # host intake, Memory, CTO, notification interfaces
  adapters/         # offline fakes first; reviewed Linux mappings later
tests/
  fixtures/         # synthetic data; no executable imported skills
  unit/
  integration/
  acceptance/
docs/
```

Proposed flow: authenticated intake → immutable tenant/task → bounded source snapshot → lead/support evidence extraction → canonical packet → independent verifier → approved candidate → Memory commit/promotion and fresh authorized retrieval → scoped specialist visibility / optional CTO proposal → Memory-owned protected HQ sync → receipt-based short completion.

Proposed state separates research outcome from delivery: received → collecting → researching → awaiting verification → approved/rejected/needs-more-research. Approved packets proceed through candidate delivery, confirmed commit, confirmed promotion and retrieval; HQ/export/notification have separate receipt states. Failures can be retryable, blocked, exhausted or terminal. Revisions require a new packet version and verdict; bounded rework cannot loop indefinitely. Historical versions remain linked, while superseded/disputed knowledge is excluded from current trusted views according to Memory policy.

Independent verification requires a distinct verifier principal/role, separate execution context and authenticated decision artifact; a different prompt alone is insufficient. Hash input includes schema version, environment, scope/access metadata, claims, evidence identities/digests and source version. Define deterministic serialization before implementing hashes. Delivery timestamps and retry receipts live outside the approved payload. A digest alone authenticates neither the actor nor permission to promote.

Local credential configuration contains references only. Runtime authority is supplied by trusted host context, never by source text. Each environment gets separate state/snapshot roots, queue partitions, budget ledgers and credential references. Production process/OS isolation and secret broker behavior require Linux agreement; Mac tests cannot prove those controls.

## Independent Mac work and limits

After Phase 1 authorization, contracts, synthetic identity contexts, local durable state, canonicalization, policy checks, budget logic and offline fakes can be implemented without Linux. Later Mac stages can add fixture-backed source parsers, deterministic specialist matching, independent verification harnesses, version/conflict logic and simulated delivery. Real providers, live fetching and actual host adapters have separate readiness gates.

Do not implement vector search, a Memory database, vault writers, Photon delivery, CTO approvals, installers, publishers or a new global scheduler. Do not claim real model research from deterministic fixtures. Linux API paths, database technology, tenant IDs, vault mappings, model IDs, deployment layout and authorization formats remain unknown; see CONTRACT_GAPS.md.
