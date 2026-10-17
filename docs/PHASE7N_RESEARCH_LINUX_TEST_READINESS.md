# Phase 7N — Research Linux test readiness

2026-10-16. **PASS for the proposed eight-test assessment scope; BLOCKED for executing the full 305-test suite under unchanged historical controls.** No execution is authorized by this document. Stop after assessment; obtain separate authorization for the exact subset and supervisor in the execution plan.

## Evidence and boundaries

Read-only SSH inspection targeted only the extracted release at:
`/home/alfred/research-staging/research-v1/alfred-research-v1-0.1.0-phase7e-linux-stage-20261016`.

The inspection listed files and symlinks, read tests/source/pyproject/release inventory as text, and inspected installed Python runtime dependencies with ldd. Mac analysis used stdlib AST parsing and hashing only. No Research import, unittest discovery, test, installation, Linux write/configuration change, service request, credential/vault read, archive change, commit, push or deployment occurred. No staging symlinks were reported. Initial sandbox SSH denial was followed by approved read-only SSH access. Remote inspection commands completed with exit 0.

The text snapshot contained 31 source modules and 12 test modules. All 44 inspected manifest-listed text files matched their release-inventory SHA-256 values after UTF-8 re-encoding; this is scoped content evidence, not a new whole-release integrity certification. AST finds exactly 305 defined test methods, matching the inventory. The inventory's 40.528-second, 305-pass result is historical acceptance evidence, **not Linux execution evidence**.

Prior controls: [7K isolation](PHASE7K_BUBBLEWRAP_PROBE_RESULTS.md), [7L resources](PHASE7L_RESOURCE_CONTROL_RESULTS.md), [7L forced cleanup](PHASE7L_TIMEOUT_CLEANUP_RESULTS.md), [7M cgroup preflight](PHASE7M_CGROUP_PROBE_RESULTS.md). Their successful synthetic namespace/cleanup observations remain historical and do not prove package compatibility. Phase 7M did not create or test an aggregate cgroup; SSH-born process placement remains unresolved.

## Dependencies

`pyproject.toml`: Python >=3.10; runtime `dependencies = []`; build requires setuptools>=61. Tests use stdlib unittest, not pytest. Run directly from source, without pip, installation, setuptools or site-packages. Installed `/usr/bin/python3.12` and `/usr/lib/python3.12` are present. Package imports are stdlib and intra-package only. SQLite, fcntl/flock, filesystem identity/receipts, os.fwalk and permission semantics matter on Linux. PDF is explicitly unsupported; no Node, browser, PDF decoder or model provider is required for this suite.

Read-only ldd evidence identifies the required binary closure used in the proposed subset: loader, libc, libm, libz, libexpat, libsqlite3, libffi and libcrypto. The exact allowlist is in the plan. No broad `/usr`, `/lib`, host root or home mount is necessary. Dynamic import success remains to be validated inside the separately authorized sandbox.

## Inventory and effects

“SQLite/files” includes setup, inherited fixtures and invoked implementation, not only explicit imports. All persistent fixtures are synthetic and rooted in TemporaryDirectory. No multiprocessing, ProcessPoolExecutor, fork API or shell execution was found in the inspected Python code. Real subprocesses invoke `sys.executable -c` for restart/crash tests. Thread pools have explicit maxima (2–8 workers); no parallel test runner is proposed. Strings mentioning curl, fetch, executable hooks, URLs and scripts are inspected fixture content or denial checks, not transport/execution integrations.

| Test module | Defined tests | SQLite / filesystem effects | Process/concurrency |
| --- | ---: | --- | --- |
| `test_canary_contracts.py` | 27 | Temporary SQLite, journals/receipts; some higher-layer filesystem journals | Python restart/crash subprocess; bounded thread pools |
| `test_corrections.py` | 20 | Temporary SQLite, journals/receipts; some higher-layer filesystem journals | Python restart/crash subprocess; bounded thread pools |
| `test_execution_corrections.py` | 22 | Temporary SQLite, journals/receipts; some higher-layer filesystem journals | Python restart/crash subprocess; bounded thread pools |
| `test_foundation.py` | 31 | Temporary SQLite, journals/receipts; some higher-layer filesystem journals | Python restart/crash subprocess; bounded thread pools |
| `test_hot_recovery.py` | 10 | Temporary SQLite, journals/receipts; some higher-layer filesystem journals | Python restart/crash subprocess; bounded thread pools |
| `test_intelligence.py` | 23 | Temporary SQLite, journals/receipts; some higher-layer filesystem journals | Python restart/crash subprocess; bounded thread pools |
| `test_memory.py` | 30 | Temporary SQLite, journals/receipts; some higher-layer filesystem journals | Python restart/crash subprocess; bounded thread pools |
| `test_registration.py` | 20 | Temporary SQLite, journals/receipts; some higher-layer filesystem journals | 8-worker pool; inherited raw-spill crash helper |
| `test_research.py` | 37 | Temporary SQLite, journals/receipts; some higher-layer filesystem journals | Python restart/crash subprocess; bounded thread pools |
| `test_source_corrections.py` | 10 | No SQLite; synthetic directories/files, symlinks and permission tests | No real subprocess or thread workers |
| `test_sources.py` | 34 | No SQLite; synthetic directories/files, symlinks and permission tests | No real subprocess or thread workers |
| `test_workflow.py` | 41 | Temporary SQLite, journals/receipts; some higher-layer filesystem journals | Python restart/crash subprocess; bounded thread pools |

All source/network policy checks are offline. `urllib.parse` is URL parsing. Tests patch socket creation in fixtures/workers; those patches are supplemental checks, not the security boundary. Memory uses the package's fake offline boundary; workflow/notification/canary tests use synthetic contracts and local journals. No live Hermes, Photon, Memory, Obsidian, Development or HQ service is required or authorized. Environment labels such as personal/fintra/gabos represent synthetic tenant identities, not production account access.

The appendix identifies concrete process/thread call sites and helper callers, including registration's aliased crash helper. Other methods in SQLite modules still write through their fixtures even when they only check contracts.

## Resource and isolation decision

The historical 7K/7L file ceilings (1 MiB / 4 KiB), tiny tmpfs and 2–3-second process CPU ceilings cannot be adopted unchanged for all 305 tests. `test_hot_recovery.py:76` creates 500 claims with 8,000-character statements; `:104` writes 600 rows containing roughly 8,000 characters each before intentional `os._exit`. Registration reuses the raw-spill helper. Rollback journals, snapshots and JSON encoding add space/memory. Several subprocess.run calls omit timeouts; the external whole-namespace watchdog is mandatory. Concurrency tests and SQLite's 5-second busy timeout need a larger time/descriptor envelope.

**Safe candidates under the proposed controls:** the eight explicitly named tests in the plan, run serially in eight fresh namespaces. They launch no real subprocesses or worker threads. Foundation setup provisions temporary SQLite for every environment, so even contract-only foundation methods need libsqlite3 and writable temporary storage. Source tests inspect/create synthetic local fixtures and test cross-environment grants. Test imports themselves validate their transitive module imports; an explicit import sweep in the same sandbox covers all 31 source modules before each selected test.

**Require a stronger resource envelope/review before execution:** all restart/crash tests and helper callers, thread/race tests, and hot-journal/registration recovery tests. These need the same filesystem/network boundary, larger sized scratch mounts, bounded output, per-case whole-tree timeout, and cleanup verification. Stronger resource containment does not imply permission to expose service sockets or production data. Remaining serial offline tests are plausible follow-on candidates; they are not authorized by the eight-test recommendation.

Aggregate cgroups are **not essential to this minimal single-test/single-interpreter subset**: its reviewed code has no process/thread fan-out, per-process address-space/CPU ceilings apply to the interpreter, and both writable tmpfs mounts have total byte ceilings. Bubblewrap/reaper/supervisor overhead is outside that interpreter bound and must be allowed for. This is a cooperative reviewed-workload assessment, not protection against arbitrary hostile code or a general aggregate RSS guarantee.

Aggregate cgroups are also **not intrinsically required by SQLite or the full suite's finite process model**. A reviewed serial per-case plan with explicit fan-out accounting and accepted host headroom could replace them. That broader resource acceptance has not been established here: address-space limits multiply across subprocesses, thread stacks consume virtual space, RLIMIT_NPROC is shared with the alfred UID, and a wall timeout is not an aggregate CPU rate limit. Therefore the full-suite execution recommendation remains BLOCKED. Use an authorized, verified dedicated cgroup launch or an isolated fixed-resource host if strict aggregate guarantees are required. Do not change shared cgroup limits or attempt the blocked SSH migration route.

## Remaining blockers and recommendation

- Separate authorization is required to execute the exact eight-test plan, including the import sweep and its new resource values. No tests ran in this assessment.
- Proposed runtime allowlist and 16 MiB scratch / 256 MiB address-space / 10-second CPU ceilings are reasoned settings, not measured Research results. Missing libraries, resource denials, skips or count mismatches must fail closed; do not widen mounts automatically.
- Runtime may differ from historical probe snapshots. Recheck Bubblewrap options, UID and runtime files before authorized execution; service access is unnecessary.
- Full-suite larger resource envelope, per-case output/process monitoring and accepted aggregate-risk decision remain outstanding. No full-suite command is approved.
- PASS means the minimal plan is ready for separate review/authorization. Overall **BLOCKED for full 305-test execution under unchanged existing controls**. No Linux compatibility pass is claimed.

## Appendix — process and concurrency call sites

This static call-site inventory is conservative: helpers are included even when not named test methods. Line numbers refer to the inspected extracted baseline.


### tests/test_canary_contracts.py

- `CanaryContractsTests.test_concurrent_acquisition_materialization_one_task` (line 134): threads
- `CanaryContractsTests.test_pending_resolution_survives_fresh_process` (line 140): real Python subprocess
- `CanaryContractsTests.test_memory_concurrent_duplicate_commit_single_effect` (line 261): threads

### tests/test_corrections.py

- `CorrectionTests.test_concurrent_duplicate_packet_revision_has_one_effect` (line 82): threads
- `CorrectionTests.test_concurrent_conflicting_and_stale_revisions_rejected` (line 92): threads
- `CorrectionTests.test_cold_concurrent_initialization_is_safe` (line 207): threads
- `CorrectionTests.test_retry_concurrent_replay_has_one_counter_and_audit_effect` (line 248): threads
- `CorrectionTests.retry_crash` (line 291): real Python subprocess
- `CorrectionTests.test_committed_retry_crash_then_replay_has_one_effect` (line 328): calls crash subprocess helper
- `CorrectionTests.test_uncommitted_retry_crash_then_replay_has_one_effect` (line 331): calls crash subprocess helper

### tests/test_execution_corrections.py

- `ExecutionCorrectionTests.test_concurrent_port_and_director_one_execution_and_charge` (line 163): threads
- `ExecutionCorrectionTests.test_output_checkpoint_before_settlement_repairs_once` (line 191): threads
- `ExecutionCorrectionTests.test_fresh_process_director_resumes_port_checkpoint` (line 202): real Python subprocess

### tests/test_foundation.py

- `FoundationTests.test_concurrent_duplicate_requests` (line 111): threads
- `FoundationTests.test_process_crash_preserves_commit_and_rolls_back_uncommitted` (line 174): real Python subprocess
- `FoundationTests.test_budget_concurrent_reservations_cannot_overspend` (line 328): threads

### tests/test_hot_recovery.py

- `HotRecoveryTests.packet_crash` (line 55): real Python subprocess
- `HotRecoveryTests.raw_spill_crash` (line 93): real Python subprocess
- `HotRecoveryTests.test_large_packet_crash_reproduces_old_failure_then_recovers_all_committed_state` (line 113): calls crash subprocess helper
- `HotRecoveryTests.test_concurrent_openers_share_sqlite_hot_journal_recovery` (line 138): threads, calls crash subprocess helper
- `HotRecoveryTests.test_unregistered_hot_supported_file_fails_closed_without_recovery` (line 180): calls crash subprocess helper
- `HotRecoveryTests.test_hot_file_with_invalid_or_wrong_environment_receipt_is_not_recovered` (line 192): calls crash subprocess helper
- `HotRecoveryTests.test_replaced_hot_file_does_not_inherit_receipt_authority` (line 211): calls crash subprocess helper
- `HotRecoveryTests.test_unknown_incompatible_hot_database_is_not_mutated` (line 223): calls crash subprocess helper
- `HotRecoveryTests.test_known_file_recovering_to_unsupported_version_reports_possible_mutation` (line 238): calls crash subprocess helper

### tests/test_intelligence.py

- `IntelligenceTests.test_concurrent_replay_and_outbox_repair` (line 108): threads
- `IntelligenceTests.test_fresh_process_reads_committed_history_and_proposals` (line 182): real Python subprocess
- `IntelligenceTests.test_concurrent_corrections_cannot_overwrite_head` (line 216): threads
- `IntelligenceTests.test_concurrent_conflicting_duplicates_have_no_effects` (line 344): threads

### tests/test_memory.py

- `MemoryTests.test_out_of_order_concurrent_stale_mutations` (line 208): threads
- `MemoryTests.test_hq_failure_and_revocation_race_fail_closed` (line 218): threads
- `MemoryTests.test_fresh_process_replays_lost_receipt_and_reads_citations` (line 285): real Python subprocess
- `MemoryTests.test_concurrent_distinct_revisions_have_one_winner` (line 326): threads

### tests/test_registration.py

- `RegistrationTests.test_forged_receipt_diagnostic_never_registered_incompatible_hot_file` (line 40): calls crash subprocess helper
- `RegistrationTests.test_matching_receipt_without_trusted_ledger_record_is_denied` (line 75): calls crash subprocess helper
- `RegistrationTests.test_edited_registration_fields_are_denied_without_mutation` (line 88): calls crash subprocess helper
- `RegistrationTests.test_copied_or_retargeted_receipt_cannot_authorize_another_environment` (line 103): calls crash subprocess helper
- `RegistrationTests.test_retargeted_receipt_cannot_authorize_a_replacement_database_instance` (line 119): calls crash subprocess helper
- `RegistrationTests.test_revocation_blocks_replay_and_survives_current_trusted_test_snapshot` (line 135): calls crash subprocess helper
- `RegistrationTests.test_missing_trust_provider_fails_closed_before_recovery` (line 149): calls crash subprocess helper
- `RegistrationTests.test_epoch_rotation_is_scoped_and_old_receipts_are_rejected` (line 159): calls crash subprocess helper
- `RegistrationTests.test_director_replacement_invalidates_previous_receipt_replay` (line 196): calls crash subprocess helper
- `RegistrationTests.test_unknown_hot_file_cannot_be_registered_even_by_director` (line 212): calls crash subprocess helper
- `RegistrationTests.test_concurrent_unauthorized_provisioning_has_no_effects` (line 303): threads

### tests/test_research.py

- `ResearchTests.test_concurrent_replays_have_one_packet_and_decision_effect` (line 379): threads
- `ResearchTests.crash_worker` (line 395): real Python subprocess
- `ResearchTests.test_process_crash_before_packet_commit_reuses_model_checkpoint` (line 427): calls crash subprocess helper
- `ResearchTests.test_process_crash_after_packet_commit_has_no_duplicate_effects` (line 441): calls crash subprocess helper
- `ResearchTests.test_process_crash_before_verdict_commit_reuses_exact_review` (line 451): calls crash subprocess helper
- `ResearchTests.test_expired_deadline_does_not_wait_for_a_busy_workflow_lock` (line 566): threads

### tests/test_workflow.py

- `WorkflowTests.test_concurrent_duplicate_requests_have_one_flow` (line 305): threads
- `WorkflowTests.test_fresh_process_recovers_without_resupplied_fixture` (line 333): real Python subprocess
- `WorkflowTests.test_commit_outbox_gap_repaired_once_concurrent_restart` (line 427): threads
- `WorkflowTests.test_cached_result_unchanged_concurrent_restart_one_final` (line 576): threads
