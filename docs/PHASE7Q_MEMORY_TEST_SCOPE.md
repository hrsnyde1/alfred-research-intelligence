# Phase 7Q — Memory test scope

2026-10-16. **Prepared for owner review; no transfer or Memory execution authorized/performed.** Smallest proposed extension tranche: **seven existing test methods**, serially, one fresh sandbox per method. Baseline comparison adds the narrowly defined paired controls in the transfer plan; it does not run 102/125-case discovery or all 23 extension cases.

## Evidence actually reviewed

Read Phase 7H baseline-failure/regression reports, Phase 7I checklist, Phase 7J execution gate and Phase 7P results. The exact requested `PHASE7H_MEMORY_CHANGE_PLAN.md` and `PHASE7H_MEMORY_ACCEPTANCE_TESTS.md` are absent after a repository search. Reviewed the existing [Phase 7G change plan](PHASE7G_MEMORY_CHANGE_PLAN.md) and [acceptance cases](PHASE7G_MEMORY_ACCEPTANCE_TESTS.md), plus reconstructed [7H implementation](PHASE7H_MEMORY_IMPLEMENTATION_REPORT.md), [7H tests](PHASE7H_MEMORY_TEST_RESULTS.md) and [7H diff](PHASE7H_MEMORY_DIFF_REVIEW.md). These are explicitly identified substitutes/context, not invented missing Phase 7H documents. Owner should accept this documentary mapping or supply the missing originals before approval.

Inspected actual Mac staging source, all 23 extension methods and setup/helpers, original tests, `BASELINE_MANIFEST.json`, `TRANSFER_PLAN.json`, saved runner/results and the 92-file table in `PHASE7I_BLOCKER_RESOLUTION.md`. All **92** table hashes and all **34** baseline hashes match current files. Between baseline/work shared paths, only `focused_v1/store.py` differs; `research_stage.py` and its test file are the two additions. Historical `TRANSFER_PLAN.json` has 30 primary plus 4 supplemental original paths; it is not the later complete 92-file execution allowlist. The 92 list comprises baseline 34 + work 36 + two helper/evidence files + 19 Research modules + one Research fixture helper.

Canonical audited 92-row digest (sorted path + TAB + hash + LF): `f82672d4b80eb3f4f084b4c511bc081282e9ddf9aea319510152c2780700fc2a`. This Memory inventory is separate from the 92-file extracted Research release; identical counts do not imply identical contents.

Historical Memory results remain baseline 102 run / 79 pass / 17 failures / 3 errors / 3 skips and work 125 run / 102 pass / same failures/errors/skips. The 23 added cases passed in saved Mac evidence. No Linux Memory pass is inferred. Phase 7O/P's **16 Research tests** validated the launcher for their own scopes; they did not approve Memory tests or cryptography runtime mounts.

## Exact proposed extension methods

Class prefix for every row: `test_research_memory_stage.MemoryResearchStageTests`.

| Exact method identifier | Priority covered | Work-file line |
| --- | --- | ---: |
| `test_research_memory_stage.MemoryResearchStageTests.test_duplicate_create_actual_pending_rejected_approved` | Stored pending/rejected/approved state is returned on duplicate create; unchanged-row assertions remain active | 59 |
| `test_research_memory_stage.MemoryResearchStageTests.test_production_default_missing_authority_and_synthetic_promotion_denied` | Explicit test-only constructor required; production and synthetic-to-production promotion denied; rejected/NMR attestation issuance denied | 86 |
| `test_research_memory_stage.MemoryResearchStageTests.test_exact_packet_version_digest_source_and_selfverification` | Packet version/digest/source revision, independent contributors and candidate-bound policy metadata validated | 96 |
| `test_research_memory_stage.MemoryResearchStageTests.test_distinct_commit_promotion_and_full_fresh_retrieval` | Distinct submit/commit/simulate-promote/retrieve receipts; full candidate preserved; new versus historical read receipts distinguished | 117 |
| `test_research_memory_stage.MemoryResearchStageTests.test_commit_not_promotion_and_replay_idempotent` | Commit alone is not readable promoted knowledge; operation replay idempotent and changed candidate denied | 128 |
| `test_research_memory_stage.MemoryResearchStageTests.test_oversize_full_evidence_no_truncation_and_missing_specialist_grant` | Full source excerpt >1536 characters retained, oversize contract denied, wrong specialist audience denied | 197 |
| `test_research_memory_stage.MemoryResearchStageTests.test_expiration_dispute_supersession_revocation_exclude_current` | Expired/disputed/superseded/revoked records and clock-expired knowledge excluded from current reads | 137 |

These seven form the smallest proposed tranche covering the requested priorities with existing tests: digest/source validation also validates candidate structure; production-rejection case also denies REJECTED/NMR issuance; full retrieval plus audience denial covers scoped specialist reads; the invalidation case includes revocation. It is not a proof of exhaustive acceptance. Test-only synthetic attestations are deliberately accepted for simulation and **never authorize real promotion**; no genuine attestation issuer exists here.

Every method uses `MemoryResearchStageTests.setUp`: inherited Research fixture setup, four synthetic Research SQLite stores, a fresh VersionedMemoryStore, generated random deletion key/tokens, test assignments/grants and explicit test-only schema initialization. `candidate()` uses deterministic SyntheticModelProvider, exact per-claim review and in-memory TestAuthority; `promoted()` performs separate submit/commit/simulate_promotion operations. Test authority roles and tables exist only in fresh temporary databases; they are not Alfred service registrations or production migrations.

All seven are single-interpreter, finite synthetic workloads. No subprocess/worker thread/socket server, account lookup, credential-file read, installed public-key fixture, Node, PDF parser, chown/root operation, actual vault, live Memory endpoint or external model provider is needed. Ordinary chmod(0600) and SQLite WAL/journal/ledger writes target owned private temporary files. The >1536-character test uses roughly 2 KiB of evidence and a deliberately invalid ~160 KiB candidate, not a large crash workload. Invalidation creates five small records sequentially.

## Risk separation for all 23 extension methods

Same class prefix applies below. “Eligible later” means static fit with this finite-process isolation model, not approval or a passing runtime result. None is executed by the proposed seven-ID command.

- `test_duplicate_create_actual_pending_rejected_approved` (line 59): Selected — current seven-method proposal.
- `test_duplicate_create_preserves_pending_edit_and_authorization` (line 69): Eligible later — serial local contract/lifecycle test; unnecessary for smallest first tranche.
- `test_existing_routes_and_new_records_never_use_autoapproval` (line 78): Eligible later — serial local contract/lifecycle test; unnecessary for smallest first tranche.
- `test_production_default_missing_authority_and_synthetic_promotion_denied` (line 86): Selected — current seven-method proposal.
- `test_exact_packet_version_digest_source_and_selfverification` (line 96): Selected — current seven-method proposal.
- `test_forged_edited_missing_revoked_attestation` (line 105): Eligible later — serial local contract/lifecycle test; unnecessary for smallest first tranche.
- `test_no_default_promoter_and_forged_context` (line 111): Eligible later — serial local contract/lifecycle test; unnecessary for smallest first tranche.
- `test_distinct_commit_promotion_and_full_fresh_retrieval` (line 117): Selected — current seven-method proposal.
- `test_commit_not_promotion_and_replay_idempotent` (line 128): Selected — current seven-method proposal.
- `test_expiration_dispute_supersession_revocation_exclude_current` (line 137): Selected — current seven-method proposal.
- `test_attestation_and_reader_revocation_take_effect_immediately` (line 146): Eligible later — serial local contract/lifecycle test; unnecessary for smallest first tranche.
- `test_validity_duplicate_conflict_and_authorized_immutable_revision` (line 153): Eligible later — serial local contract/lifecycle test; unnecessary for smallest first tranche.
- `test_concurrent_duplicate_and_stale_revisions` (line 165): Deferred — four-worker thread pool; requires separate concurrency/headroom acceptance.
- `test_crash_after_commit_restart_reconciles_one_effect` (line 175): Eligible later — exception-hook/reopen in the same interpreter, NOT an os._exit/process crash.
- `test_all_twelve_environment_pairs_deny_reads_writes_and_receipts` (line 187): Eligible later — serial local contract/lifecycle test; unnecessary for smallest first tranche.
- `test_oversize_full_evidence_no_truncation_and_missing_specialist_grant` (line 197): Selected — current seven-method proposal.
- `test_unapproved_deletion_and_export_fail_closed` (line 207): Eligible later — serial local contract/lifecycle test; unnecessary for smallest first tranche.
- `test_conflicting_findings_both_flagged_without_a_winner` (line 211): Eligible later — serial local contract/lifecycle test; unnecessary for smallest first tranche.
- `test_incomplete_review_and_missing_trust_on_restart_denied` (line 219): Eligible later — serial local contract/lifecycle test; unnecessary for smallest first tranche.
- `test_historical_promotion_cannot_authorize_new_revision` (line 229): Eligible later — serial local contract/lifecycle test; unnecessary for smallest first tranche.
- `test_changed_verifier_assignment_denies_promotion` (line 238): Eligible later — serial local contract/lifecycle test; unnecessary for smallest first tranche.
- `test_fresh_process_recovers_commit_without_new_effect` (line 244): Excluded from this tranche — Python child restart, synthetic key transfer and inherited-env handling; separate process-tree/resource review.
- `test_missing_schema_does_not_automatically_migrate` (line 268): Eligible later — serial local contract/lifecycle test; unnecessary for smallest first tranche.

The fourteen unselected serial methods remain outside this first tranche. The thread and child-process methods are separately deferred. Original Memory suites add HTTP/Unix fixtures, Node children, atomic rename race paths, pinned account/skeleton and public-key dependencies; they are not pulled into scope by importing their modules. The only selected original control is the no-network, no-privilege unmanaged-note refusal case in the transfer plan. All remaining original tests, including the 20 inherited failure/error reproductions, remain untested here.

## Why aggregate cgroups are not essential for this tranche

One selected case at a time; reviewed paths create no Python/Node child or worker thread. Per-process 256 MiB address-space and 10-second CPU ceilings therefore bound the test interpreter; 20-second watchdog bounds lifetime, and two sized tmpfs mounts bound scratch capacity to 32 MiB. Existing exact-pidfd PID-namespace teardown/reaper checks cover the finite launcher/reaper/interpreter tree. Supervisor and native/runtime overhead are not charged to a dedicated aggregate cgroup, and tmpfs is outside RLIMIT_AS. This is accepted cooperative-code reasoning, not an aggregate RSS guarantee or hostile-code defense. RLIMIT_NPROC=128 is shared by UID 1000 and is not a per-sandbox process quota.

The old Phase 7J aggregate-control requirement remains applicable to its broader multi-process/full-compatibility campaign. It is not silently waived globally. This newly scoped proposal can be separately approved under the Phase 7O/P finite-process controls after its new cryptography runtime preflight passes. No cgroup creation, service-manager launch or host policy change is proposed.

## Remaining scope blockers

1. Owner approval of exact seven methods, paired controls and reduced transfer; Research approvals supply no Memory authorization.
2. Exact **77 additional read-only runtime file mounts** (cryptography/CFFI backend/OpenSSL dependencies) require review. Installed source/linkage/hashes were inspected read-only; no cryptography or Memory code imported. AESGCM/cryptography dynamic compatibility inside the sandbox remains unverified.
3. Review the proposed single-case/duplicate-comparison harness and supervisor construction. They are included as text with hashes in the transfer plan; no Memory tests or synthetic Memory preflight ran here.
4. Missing requested Phase 7H plan/acceptance names need owner documentary acknowledgement, as described above.
5. Future staging creation, transfer integrity, fresh isolation/runtime/resource preflight and before/after input verification must pass before any Memory method executes.

**Disposition: scope ready for review; execution BLOCKED pending separate approval and Memory runtime preflight.** No Linux writes/transfers, tests, installations, vault/database/credential access, service/configuration/cgroup/AppArmor changes, commits/pushes or deployment occurred.
