# Phase 3 implementation report

Date: 2026-10-15. Status: Mac-local synthetic workforce implemented and tested; awaiting independent owner review. Phase 4 has not begun. This is not V1 operational acceptance or real-world factual verification.

## Existing architecture preserved

Reviewed the approved decisions 1–20, Phase 0 audit/plan/gaps, Phase 1 contracts and corrected persistence/registration, Phase 2 extraction/review reports and tests, plus the supplied master plan and handoffs with ` (1)` filenames. Four independent environments, one submitted source per task, on-demand work, fixed approved models, adaptive bounded resources and separate verification remain authoritative.

Phase 3 reuses the existing issued context authority, ResearchStore, budget reservations/reconciliation, state transitions, SourceIdentity/SourceResult, canonical hashes, immutable packet revisions and exact-digest VerificationDecision storage. There is no SQLite schema change or automatic migration. All 125 existing tests and all Phase 2 modules are unchanged. The only Phase 1 source extension is an optional transaction deadline guard in ResearchStore; existing callers retain their behavior. This is a Research coordinator attached to those library interfaces, not another Alfred/Hermes orchestrator.

## Exact files created/modified

Created:

- `src/alfred_research/research/__init__.py` — public Research workflow exports.
- `src/alfred_research/research/contracts.py` — versioned role/plan/policy, invocation, assertion/draft, contribution trace and per-claim review contracts.
- `src/alfred_research/research/provider.py` — minimal model-provider Protocol and concrete deterministic test-only provider/fixtures.
- `src/alfred_research/research/journal.py` — environment-scoped, role-checked immutable Research checkpoints and bounded task locks.
- `src/alfred_research/research/workflow.py` — explicit roster, Research Director, accountable lead/support packet assembly, budget/deadline/retry enforcement and independent verification workflow.
- `tests/test_research.py` — 37 automated tests with synthetic actors/evidence, real temporary persistence, concurrency and child-process crash injection.
- `docs/PHASE3_IMPLEMENTATION_REPORT.md` — this report.
- `docs/PHASE3_TEST_RESULTS.md` — commands, actual results and acceptance mapping.
- `docs/PHASE3_AGENT_WORKFLOW.md` — interfaces, workflow, trust boundary, commit ordering and operational limits.

Modified `src/alfred_research/state.py` to add a context-local `bounded_commit` guard checked before/after SQLite lock acquisition and before commit; packet/decision writes roll back if the deadline expires inside the transaction. Modified `docs/CONTRACT_GAPS.md` to append Phase 3 integration requirements. No other earlier source, test, configuration or handoff file was changed. No dependency was installed and no Git commit/push occurred.

## Implemented behavior

The Director accepts an existing authorized task and a validated Phase 2 result owned by the same environment/original source. Routing uses authenticated objective keywords and a GitHub fallback, never instructions in the source. Exactly one lead owns the packet; up to two supporting domains are added only when the objective justifies them. Overbroad/missing staffing escalates. The five named research domains are logical configurable agent bindings, not deployed processes. Fixed Researcher-role model assignments may be deliberately shared across the five specialties, with separate Director/Verifier slots and exact approval/price/identity validation. No silent provider/model choice exists.

A plan permanently records actors, justifications, deadline, task cost ceiling and bounded adaptive call authorization. Only an explicitly instantiated synthetic test provider can execute. Every model call has a durable input pin, stable reservation identity and validated checkpoint. The existing environment ledger settles actual consumption; task authorization conservatively counts maximum call reservations across revisions. Deadlines apply before new work and at the existing SQLite transaction commit boundary, including rollback when expiry occurs during the write; lock acquisition cannot wait indefinitely. On-demand work cannot create unrelated tasks or a schedule.

Packets preserve actual source evidence/text digests, original submitted identity, observed revision and complete SourceResult digest. Separate immutable traces preserve each contributor, supporting/contradicting citations and claim kind; unknowns/limitations remain explicit. Unsupported citation IDs cannot be turned into fabricated evidence. Partial extraction remains limited and cannot become a complete simulated approved investigation.

Independent verification requires the assigned issued verifier, distinct from lead/supporters. It reconstructs the packet and assesses every claim and every supporting citation. Exact-text findings may be simulation-approved; incorrect findings are rejected; inference/unknown/declared contradiction, partial evidence and injection flags require more research. Synthetic model approval cannot override evidence failure. Complete reviews and corrections persist; decisions bind to exact immutable packet version/digest through the existing store. Cached reviews must equal a fresh deterministic assessment of their pinned source/contributions/proposal before decision replay.

NEEDS_MORE_RESEARCH permits a new immutable revision within the original policy and existing max_retries. The existing packet-write path spends one rework retry; no double transition charge is added. Old approval cannot authorize new evidence or packet content. REJECTED stays terminal. Budget/deadline/evidence/authorization failures are explicit and leave inspectable state instead of reporting successful completion.

Research-only checkpoint files supply durable plans/source results/model outputs/reviews without extending or replacing the existing task database. Reads and writes enforce environment/role boundaries, including supporter restrictions on plans/reviews. Source snapshots are extracted-text artifacts, not new Memory records. Crash ordering and idempotent commits are documented in PHASE3_AGENT_WORKFLOW.md.

## Actual validation

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_research.py' -v
```

Final full suite: **162 passed, 0 failures/errors**, **6.082 seconds**, exit 0, Python 3.14.3 / SQLite 3.50.4. This is all 125 previous tests plus 37 new Phase 3 tests. The final focused Phase 3 run passed 37 tests in 2.791 seconds. Both final runs include transaction-bound deadline checks and rollback regressions. AST/in-memory compilation passed for **25 Python files**. Research package imports and standard-library TOML checks passed; unchanged Python >=3.10, src package discovery and no runtime dependencies. No wheel build/install or Linux execution occurred.

Crash children intentionally exit **41** before packet commit (all four environments), **42** after packet commit, and **43** before verdict commit. Resume preserves exact outputs and commits one packet/decision and one reservation/settlement per logical call. Existing hot-journal crash children still exit 29 and forged-receipt fixture 30 with all prior assertions passing.

The first 29-method focused run had one test error: a self-approval fixture supplied a tuple instead of a validated VerificationDecision, so contract validation ran before authorization. That fixture was corrected to a valid decision that exercises the intended unauthorized role check. No existing test was removed or weakened. Subsequent full/focused runs passed; no unresolved failure remains.

## Remaining limitations and deferred capabilities

- All research and verdicts are simulated. Exact supplied-text consistency is not semantic truth, legal/tax assurance, source authenticity or real independent corroboration. Declared contradictions are preserved/checked; general contradiction discovery is not implemented. Source extraction provenance is the Phase 2 fixture boundary, not a signed external fetch receipt.
- Production providers remain disabled even with approved synthetic model assignments. No Grok/Claude/OpenAI connection, account, real credential or live platform was accessed. The model port is an internal interface, not a provider SDK/API integration.
- Checkpoints require POSIX flock/no-follow/hard-link support; Windows runtime, Linux filesystem permissions, multi-host locking, abrupt power-loss behavior, backup/restore, encryption and anti-rollback remain unverified. Same-account hostile code/filesystem mutation is outside this offline trust boundary. Private temporary staging is cleaned on ordinary exceptions; interrupted pre-publication staging may require separately reviewed cleanup.
- Plans/fixtures are immutable for replay. Deadline extensions, budget amendments, malformed-output correction and ambiguous reservation release require explicit operator policy; no automatic authority expansion or guessed refund occurs. Task caps conservatively count authorized reservations, while the existing environment ledger tracks actual settled usage.
- Research-local evidence artifacts now persist for restart/review. No automatic deletion, Memory storage, export, HQ synchronization or retention policy is invented. Host ownership/retention and approval-receipt provenance remain integration questions.
- Live Hermes ingress, host-issued principals, protected production registration/credential storage, real provider billing/cancellation/deadlines, source authentication, worker isolation and real verifier independence remain Linux acceptance gates.
- Phase 4 taxonomy, knowledge evolution/distribution, specialist knowledge profiles and CTO capability proposals are not implemented. No Memory/Obsidian writes, Photon messaging, Development changes, skills installation, commit/push, service startup or deployment occurred.

Stop for owner review and explicit authorization before any Phase 4 work.
