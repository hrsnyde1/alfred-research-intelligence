# Phase 7H baseline failure analysis

Read-only investigation, 2026-10-16. No tests were rerun, source/tests modified, dependencies installed, or Linux systems contacted during this review. Only the two requested review documents were created.

## Evidence and comparison

Evidence root: `artifacts/staging/phase7h-memory/`. Inspected `baseline-results.json`, `work-results.json`, both `*-tests.txt`, both `*-runtime-stderr.txt`, `compatibility-comparison.json`, `run_tests.py`, `BASELINE_MANIFEST.json`, `CHANGES.patch`, and actual baseline/work source and tests. All 34 baseline files match their recorded SHA-256 hashes. Every failure/error traceback matches exactly after normalizing `/baseline/` and `/work/` paths; failure, error and skip identities are identical.

| Recorded suite | Run | Passed | Failures | Errors | Skips | Exit |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Untouched copied Memory | 102 | 79 | 17 | 3 | 3 | 1 |
| Modified staging, including new tests | 125 | 102 | 17 | 3 | 3 | 1 |

The 23 additional staging cases pass in the saved work run. The separately reported 305 Research passes are not part of these Memory result files and are not independently rerun here. Neither complete copied Memory suite passed.

Final comparison used macOS arm64, Homebrew Python 3.14.8, installed cryptography and Node, and synthetic temporary state. The saved runner reproduces discovery from each copy with `PYTHONDONTWRITEBYTECODE=1`, `PYTHONPATH` containing that copy plus Research `src` and `tests`, and external TCP connect calls blocked (loopback/Unix socket fixtures permitted). Earlier incomplete-copy or sandbox-denied socket runs must not be substituted for these final results. Python 3.14.8 is not the Linux Python 3.12.3 target.

Reproduction commands for a separately authorized rerun, from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 artifacts/staging/phase7h-memory/run_tests.py baseline
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 artifacts/staging/phase7h-memory/run_tests.py work
```

The baseline final run used the equivalent inline guarded runner; the saved driver captures its discovery/environment policy. These commands write result artifacts and were not run in this read-only review.

## Root-cause groups and classification

**A — Unsupported Mac/Linux behavior (15 failures).** `baseline/obsidian_candidate/bridge.py:65–84` explicitly requires Linux libc `renameat2` for atomic exchange/no-replace. A side-effect-free local symbol check confirmed it absent. Direct HQ note refresh calls these primitives; `editor_origin.py:317–323` catches the resulting exception and reports `queued/export_unavailable`. Race tests never reach their expected atomic conflict outcome, and confirmation tests stay pending. This is strong source/platform evidence, not an instrumented rerun of each exception. Preserve the fail-closed primitive; do not replace it with an unsafe ordinary rename to obtain green Mac tests. Minimum next action: run unchanged cases in an isolated Linux filesystem with synthetic state, checking atomic-rename support and race protections.

**B — Unsupported Mac/Linux behavior (2 failures, 2 errors).** `baseline/obsidian_candidate/ingress.py:97` uses Linux `socket.SO_PEERCRED` and Linux credential layout. Both runtime stderr logs show the exact AttributeError at this line; a local attribute check confirms absence. Server threads abort, producing empty replies (JSONDecodeError) or uncertain transport outcomes. No unavailable remote Photon/SSH service is demonstrated. Minimum next action: unchanged tests in an isolated Linux environment with synthetic Unix sockets and actors. Do not disable peer authentication or substitute a differently shaped Mac credential structure without a reviewed portability change.

**C — Missing Mac deployment fixture/tooling (1 error), with a baseline test-isolation weakness.** `baseline/obsidian_candidate/disposable_delivery.py:39,142,190` reads the installed forced-public-key fixture before validating an existing authorized-key file. The test at `tests/test_obsidian_disposable_delivery.py:159–173` substitutes state/account/skeleton but does not substitute `_authorized_line`; the real installation path is absent. It expects ValueError, gets FileNotFoundError. The code fails closed; this does not prove a Linux production defect. Minimum next action: separately authorize a synthetic fixture injection in an isolated test harness, consistent with neighboring test setup, and rerun the existing-file rejection cases. Do not copy credentials or create production `/opt` paths on the Mac.

No case provides evidence of an unavailable external service or a new Research extension regression. No runtime implementation defect is established by these 20 cases beyond host assumptions; C exposes an inherited non-hermetic test dependency. A passing isolated Linux rerun is still required to establish Linux behavior.

## Every failing/erroring case

Paths in the test column are relative to `baseline/tests/` (same lines in work); implementation references are relative to `baseline/obsidian_candidate/` and unchanged in work. Group letters define classification, root cause, and minimum next action above. Each observed result and normalized traceback is identical in both copies.

| Exact test identity | Test location | Baseline versus modified observation | Group / implementation | Research implicated? |
| --- | --- | --- | --- | --- |
| `test_obsidian_candidate.CandidateTests.test_actual_node_journal_and_python_bridge_confirm_three_version_sequence` | `test_obsidian_candidate.py:1848` | FAIL in both; export_unavailable instead of committed/local_edit_conflict | A; `bridge.py:65–84; editor_origin.py:323` | No new extension path; inherited |
| `test_obsidian_candidate.CandidateTests.test_actual_node_signed_hq_edit_reaches_confirmed_memory_outcome` | `test_obsidian_candidate.py:2139` | FAIL in both; export_unavailable instead of committed/local_edit_conflict | A; `bridge.py:65–84; editor_origin.py:323` | No new extension path; inherited |
| `test_obsidian_candidate.CandidateTests.test_alfred_hq_delete_after_move_never_discards_recreated_destination` | `test_obsidian_candidate.py:1979` | FAIL in both; export_unavailable instead of committed/local_edit_conflict | A; `bridge.py:65–84; editor_origin.py:323` | No new extension path; inherited |
| `test_obsidian_candidate.CandidateTests.test_alfred_hq_delete_race_before_atomic_move_preserves_newer_bytes` | `test_obsidian_candidate.py:1933` | FAIL in both; export_unavailable instead of committed/local_edit_conflict | A; `bridge.py:65–84; editor_origin.py:323` | No new extension path; inherited |
| `test_obsidian_candidate.CandidateTests.test_alfred_hq_edit_after_exchange_never_discards_changed_destination` | `test_obsidian_candidate.py:1954` | FAIL in both; export_unavailable instead of committed/local_edit_conflict | A; `bridge.py:65–84; editor_origin.py:323` | No new extension path; inherited |
| `test_obsidian_candidate.CandidateTests.test_alfred_hq_edit_race_before_atomic_exchange_preserves_newer_bytes` | `test_obsidian_candidate.py:1902` | FAIL in both; export_unavailable instead of committed/local_edit_conflict | A; `bridge.py:65–84; editor_origin.py:323` | No new extension path; inherited |
| `test_obsidian_candidate.CandidateTests.test_alfred_hq_exact_signed_edit_arriving_through_sync_confirms` | `test_obsidian_candidate.py:1785` | FAIL in both; export_unavailable instead of committed/local_edit_conflict | A; `bridge.py:65–84; editor_origin.py:323` | No new extension path; inherited |
| `test_obsidian_candidate.CandidateTests.test_alfred_hq_held_delete_confirms_suppression_and_keeps_history` | `test_obsidian_candidate.py:2191` | FAIL in both; export_unavailable instead of committed/local_edit_conflict | A; `bridge.py:65–84; editor_origin.py:323` | No new extension path; inherited |
| `test_obsidian_candidate.CandidateTests.test_alfred_hq_outage_keeps_same_receipt_pending_until_confirmed` | `test_obsidian_candidate.py:2279` | FAIL in both; export_unavailable instead of committed/local_edit_conflict | A; `bridge.py:65–84; editor_origin.py:323` | No new extension path; inherited |
| `test_obsidian_candidate.CandidateTests.test_alfred_hq_receipt_completes_only_after_v1_readback_and_note_v2` | `test_obsidian_candidate.py:1762` | FAIL in both; export_unavailable instead of committed/local_edit_conflict | A; `bridge.py:65–84; editor_origin.py:323` | No new extension path; inherited |
| `test_obsidian_candidate.CandidateTests.test_alfred_hq_restart_after_bridge_commit_recovers_same_event` | `test_obsidian_candidate.py:2239` | FAIL in both; export_unavailable instead of committed/local_edit_conflict | A; `bridge.py:65–84; editor_origin.py:323` | No new extension path; inherited |
| `test_obsidian_candidate.CandidateTests.test_alfred_hq_signed_noncanonical_note_is_bound_to_exact_bytes` | `test_obsidian_candidate.py:1808` | FAIL in both; export_unavailable instead of committed/local_edit_conflict | A; `bridge.py:65–84; editor_origin.py:323` | No new extension path; inherited |
| `test_obsidian_candidate.CandidateTests.test_alfred_hq_unheld_delete_confirms_absence_and_no_reexport` | `test_obsidian_candidate.py:2214` | FAIL in both; export_unavailable instead of committed/local_edit_conflict | A; `bridge.py:65–84; editor_origin.py:323` | No new extension path; inherited |
| `test_obsidian_candidate.CandidateTests.test_alfred_only_runner_is_editor_only_and_confirms_bounded_pass` | `test_obsidian_candidate.py:2295` | FAIL in both; confirmed=0, pending=1, remaining=1 instead of confirmed=1, pending=0, remaining=0 | A; `bridge.py:65–84; editor_origin.py:323` | No new extension path; inherited |
| `test_obsidian_candidate.CandidateTests.test_cross_device_recovery_keeps_conflict_file_and_blocks_sync` | `test_obsidian_candidate.py:2057` | FAIL in both; export_unavailable instead of committed/local_edit_conflict | A; `bridge.py:65–84; editor_origin.py:323` | No new extension path; inherited |
| `test_obsidian_candidate.CandidateTests.test_editor_ssh_relay_restricts_payload_and_preserves_uncertain_outcome` | `test_obsidian_candidate.py:2358` | FAIL in both; outcome_unknown / transport_or_ingress_unavailable instead of queued | B; `ingress.py:97` | No new extension path; inherited |
| `test_obsidian_disposable_delivery.DisposableDeliveryTests.test_unix_socket_transport_when_sandbox_permits_bind` | `test_obsidian_disposable_delivery.py:476` | FAIL in both; outcome_unknown / transport_or_ingress_unavailable instead of queued | B; `ingress.py:97` | No new extension path; inherited |
| `test_obsidian_candidate.CandidateTests.test_editor_ingress_group_socket_serves_bounded_repeated_connections` | `test_obsidian_candidate.py:2403` | ERROR in both; JSONDecodeError from empty reply | B; `ingress.py:97` | No new extension path; inherited |
| `test_obsidian_candidate.CandidateTests.test_signed_local_ingress_checks_peer_and_photon_decision` | `test_obsidian_candidate.py:966` | ERROR in both; JSONDecodeError from empty reply | B; `ingress.py:97` | No new extension path; inherited |
| `test_obsidian_disposable_delivery.DisposableDeliveryTests.test_initialization_rejects_existing_keys_and_authorized_file) (name='.ssh/authorized_keys'` | `test_obsidian_disposable_delivery.py:170` | ERROR in both; FileNotFoundError: missing installed public-key fixture | C; `disposable_delivery.py:39,142,190` | No new extension path; inherited |

## Skips and retest boundary

The three unchanged skips are `test_obsidian_candidate.CandidateTests.test_pdf_reference_when_reviewed_parser_available` (PyMuPDF missing), `test_obsidian_disposable_delivery.DisposableDeliveryTests.test_initialization_accepts_exact_pinned_ubuntu_skeleton`, and `test_obsidian_disposable_delivery.DisposableDeliveryTests.test_pinned_ubuntu_skeleton_hashes` (matching Ubuntu `/etc/skel` missing). They are existing explicit skips, not new staging exclusions.

Groups A/B (19 cases) can be retested on an isolated Linux VM/container with appropriate libc, filesystem and Unix socket capabilities, using synthetic state and no production services. C can be retested with a separately approved synthetic fixture harness on the Mac or Linux. No installation, harness alteration or environment creation is performed by this investigation. The skipped PDF test requires separately authorized parser availability; Ubuntu skeleton tests require matching isolated fixtures.
