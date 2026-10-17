# Phase 1 executed test results

## Latest Director-only provisioning validation

This section supersedes all earlier test counts and any earlier researcher-provisioning assumptions below.

| Command | Actual result |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v` | 81 passed, 0 failures/errors; 2.635 seconds; exit 0 |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -k large_packet -k forged_receipt -v` | 2 passed, 0 failures/errors; 0.475 seconds; exit 0 |

Five new methods in `tests/test_registration.py` passed:

- `test_director_provisioning_is_idempotent_all_environments`: initial registration names the Director, repeat provisioning changes neither raw files nor ledger, and researchers can create/read tasks afterward.
- `test_non_directors_cannot_provision_missing_databases`: researcher/verifier direct opens and Store reads fail in every environment; root stays empty and ledger unchanged.
- `test_forged_environment_cannot_provision`: valid requester with foreign payload scope and wrong-company Director fail across all 12 unequal pairs without persistent effects.
- `test_concurrent_unauthorized_provisioning_has_no_effects`: 32 researcher/verifier attempts across four environments all denied with no files/directories/ledger entries.
- `test_fabricated_registration_cannot_bypass_director_boundary`: fabricated identities and reconstructed Director contexts cannot call either registration entrypoint successfully.

All preceding 76 methods remain passing with explicit Director setup where required. Existing replacement authorization and company isolation coverage is retained. Large-packet crash children exit 29 in all four environments, reproduce SQLITE_READONLY_ROLLBACK under the old preflight, recover committed revisions/verdicts/retry state and discard uncommitted changes. Forged-receipt diagnostic child exits 30, with all forged formats rejected and DB/journal/ledger unchanged.

The initial setup-adaptation run reported 80 passing and one failure (an empty-root negative test was pre-provisioned). Its unprovisioned setup was restored, preserving the original assertion; the final full run above passed. Production recovery remains disabled; Linux authorization and durable trust storage are still unverified.


Date: 2026-10-15. Environment: local Mac, `python3` 3.14.3. Scope: offline internal Research foundation only.

## Commands and observed results

| Check | Observed outcome |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v` | Latest authorization correction: 76 tests, 76 passed, 0 failures, 0 errors; 2.295 seconds; OK |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -k large_packet -k forged_receipt -v` | 2 targeted diagnostics passed, 0 failures/errors; 0.473 seconds |
| `python3 -m compileall -q src tests` | Exit 0; compilation passed |
| Standard-library TOML parse of pyproject and AST parse of all package modules | Passed; no runtime dependencies and Python >=3.10 declaration confirmed |
| `python -m unittest discover -s tests -p 'test_*.py' -v` | Unsupported-interpreter probe: Python 3.9.6; 1 test-module import error, `dataclass() got an unexpected keyword argument 'kw_only'`; no acceptance tests ran under 3.9 |

The 3.9 failure is reported, not counted as a passing test or positive portability evidence. This package explicitly requires Python >=3.10. The original 31-test result is historical. Current corrected source is covered by 76 executed tests: 31 original cases, 20 original correction cases, 10 adapted hot-journal cases and 15 independent-authority cases. Build/install and Linux checks were not run.

## Current independent-authority regression results

Runtime: Python 3.14.3 / SQLite 3.50.4. All 15 methods in `tests/test_registration.py` passed. The injected test authority is separate from untrusted DB/receipt contents; no signing key, real credential or external service is used.

| Required assertion | Executed coverage |
|---|---|
| Fabricated matching JSON cannot grant recovery | `test_forged_receipt_diagnostic_never_registered_incompatible_hot_file`: child exit 30, real hot journal, previously unregistered version-999 database. Legacy public JSON, edited legitimate receipt and fabricated format-2 JSON all fail without DB/journal/ledger mutation. |
| Independent registration is required | `test_matching_receipt_without_trusted_ledger_record_is_denied`: an exact genuine receipt does not work under a fresh authority with no corresponding ledger entry. Original trusted authority still permits recovery. |
| Edited registrations rejected | `test_edited_registration_fields_are_denied_without_mutation`: changing authority ID, epoch, registration ID or registering principal cannot update the ledger or authorize recovery. |
| Cross-environment copying/substitution rejected | `test_copied_or_retargeted_receipt_cannot_authorize_another_environment`: both copied and correctly retargeted public identities fail. |
| Replay across database instances rejected | `test_retargeted_receipt_cannot_authorize_a_replacement_database_instance`: updating device/inode in an old receipt does not change its independent registration record. |
| Revocation persists through current trusted-state transfer | `test_revocation_blocks_replay_and_survives_current_trusted_test_snapshot`: live and reconstructed current authorities refuse replay without writes. |
| Missing trust fails closed | `test_missing_trust_provider_fails_closed_before_recovery`: no provider never falls back to public receipt verification. |
| Rotation is environment scoped | `test_epoch_rotation_is_scoped_and_old_receipts_are_rejected`: old personal registration invalidated; company registration remains valid. |
| Existing clean files are not registered implicitly | `test_existing_clean_database_is_not_automatically_registered`: matching schema alone is insufficient; researcher registration fails; explicit director registration succeeds without SQL-file mutation. |
| Registration/replacement require authorized context | `test_registration_and_replacement_require_issued_director_context`: researcher, reconstructed director context and other-company director all fail without ledger/file changes. |
| Authorized replacement prevents old receipt replay | `test_director_replacement_invalidates_previous_receipt_replay`: replacement creates a new active ID; old ID cannot authorize hot recovery; current registration succeeds. |
| Registration cannot bypass hot-journal validation | `test_unknown_hot_file_cannot_be_registered_even_by_director`: read-only validation fails before ledger replacement or receipt change. |
| Unsupported versions are not registered/migrated | `test_unsupported_schema_registration_has_no_effect`: v1 rejected without ledger/file mutation. Existing incompatible-schema regressions remain passing. |
| Scoped authority administration | `test_registration_scope_and_revocation_cannot_cross_companies`: wrong-company revocation and out-of-scope file registration denied. |
| Production authorization disabled | `test_test_authority_cannot_be_used_as_production_authorization`: explicit test-only constructor required; production Store/open/register paths refuse before writes. |

All 61 preceding methods also pass. The old clean-file auto-registration case now requires explicit director registration; crash fixtures receive current trusted authority state from the parent harness via stdin. Nothing loads authority state from a receipt or database file.

The previously successful large-packet regression continues to pass in all four environments with child exit 29: two committed revisions and their verdicts, task/audit/retry state persist; uncommitted changes roll back. The previously demonstrated forged-receipt diagnostic now passes by rejecting recovery, preserving the hot journal and leaving the independent ledger unchanged. Both diagnostics were also executed separately with the targeted command above.

Compilation and TOML/AST checks passed for 12 Python files. There are no new runtime dependencies. All historical counts below describe preceding milestones.

## Historical hot-journal regression results

Runtime: Python 3.14.3, SQLite 3.50.4. All 10 methods in `tests/test_hot_recovery.py` passed. The policy/opening sequence and its recovery-write trade-off are documented at the beginning of PHASE1_CORRECTION_REPORT.md.

| Required assertion | Executed evidence |
|---|---|
| New initialization and clean supported opening | `test_new_database_and_clean_supported_reopen_register_identity_without_sql_mutation`: schema v2 and exact file identity registered; clean reopen leaves main/receipt bytes unchanged |
| Older clean v2 compatibility | `test_older_clean_v2_file_requires_explicit_director_registration`: ordinary open is denied; explicit director registration succeeds without changing SQL file bytes |
| Supported hot recovery and original failure reproduced | `test_large_packet_crash_reproduces_old_failure_then_recovers_all_committed_state`: all four environments; 500 claims × 8,000 characters; child exits 29 with hot journal; old mode=ro sequence raises SQLITE_READONLY_ROLLBACK; corrected open succeeds through SQLite recovery |
| Committed tasks, revisions, verdicts and retry accounting retained | Same test: original task and retry count/result, two immutable revisions and exact per-version verdict hashes remain retrievable; replay of committed retry does not spend another allowance |
| Uncommitted changes absent | Same test: third revision/head change, extra packet audit and extra retry-counter increment roll back |
| Concurrent recovery | `test_concurrent_openers_share_sqlite_hot_journal_recovery`: child exits 29, eight concurrent reopeners see identical committed state and historical content |
| Ambiguous supported hot file | `test_unregistered_hot_supported_file_fails_closed_without_recovery`: missing receipt leads to RecoveryRequiredError(False); all main/journal bytes unchanged on repeated attempts |
| Ambiguous/corrupt identity | `test_hot_file_with_invalid_or_wrong_environment_receipt_is_not_recovered`: corrupt JSON, wrong tenant and duplicate-key receipt refused without changes |
| Replacement identity | `test_replaced_hot_file_does_not_inherit_receipt_authority`: replacement inode does not inherit the old receipt; hot file/journal remain unchanged |
| Unknown incompatible hot database | `test_unknown_incompatible_hot_database_is_not_mutated`: committed version 999 plus uncommitted version 2; child exits 30; no receipt means no recovery permission, main/journal remain byte-for-byte unchanged |
| Known file recovered to an unsupported schema | `test_known_file_recovering_to_unsupported_version_reports_possible_mutation`: previously registered file changed in place to committed version 999; child exits 30 after uncommitted changes. SQLite recovery restores committed dump and removes journal, then RecoveryValidationError(True) explicitly reports possible mutation; no migration to v2/application audit |
| Other read-only failures | `test_unrecognized_readonly_error_does_not_authorize_recovery`: unknown SQLite error never opens writable or changes files |
| Unsupported cold schemas/no automatic migration | Existing incompatible-schema snapshots, v1 rejection, corrupt/empty files and tenant-mismatch regressions still pass unchanged |
| Environment isolation and all prior behavior | All 51 previous methods pass, including the 12-pair isolation and valid-requester forgery matrix |

The tests never delete or rewrite hot journals. Journal disappearance in recovery-success cases is SQLite's own rollback behavior. Ambiguous-file snapshots read raw bytes instead of using a writable SQLite reader that could accidentally recover them. Temporary fixture cleanup occurs only after assertions.

Compilation passed with `python3 -m compileall -q src tests`. TOML/AST validation passed for all 10 Python files; no runtime dependency was added. Results for 51 tests and 9 files below describe the preceding correction milestone, not the latest source.

## Original Phase 1 acceptance mapping

Test names below refer to `FoundationTests` in `tests/test_foundation.py`. Four-environment loops and cross-environment pair loops are subtests/assertions within the reported test-method count, not extra test counts.

| # | Required assertion | Executed coverage |
|---|---|---|
| 1 | One durable task from a valid request | `test_valid_durable_request_all_environments` |
| 2 | Duplicate requests do not duplicate effects | `test_duplicate_request_one_effect_all_environments`, `test_concurrent_duplicate_requests`, `test_conflicting_idempotency_key` |
| 3 | Unknown environment rejected | `test_unknown_environment` |
| 4 | Forged identity rejected | `test_forged_and_foreign_authority_contexts`, `test_forged_request_identity` |
| 5 | Company A cannot read/modify B | `test_cross_environment_read_write_denied` tests every unequal environment pair; budget actor/scope checks in `test_budget_cross_environment_and_principal_denied` |
| 6 | Invalid/duplicate transitions safe | `test_invalid_and_duplicate_transitions_are_atomic` |
| 7 | Committed state survives crash | `test_process_crash_preserves_commit_and_rolls_back_uncommitted`, `test_audit_failure_rolls_back_task_creation` |
| 8 | Restart recovery idempotent | `test_retry_bound_and_recovery_idempotence`; committed/uncommitted retry crash regressions |
| 9 | Outbox survives restart | `test_outbox_restart_duplicate_and_delivery`; exhausted failure handling in `test_outbox_bounded_failures` |
| 10 | Deterministic hashes | `test_packet_roundtrip_and_determinism` |
| 11 | Content/scope/source mutations change digest | `test_all_approved_content_changes_digest`; malformed/mixed scopes rejected by `test_malformed_and_ambiguous_contracts` |
| 12 | Researcher cannot self-verify | `test_verification_independence_and_stale_decision` checks both unauthorized researcher role and explicit same-principal condition |
| 13 | Stale verdict cannot approve changed packet | `test_verification_independence_and_stale_decision` |
| 14 | Exhaustion blocks spending | `test_budget_exhaustion_isolated_and_durable`, `test_budget_concurrent_reservations_cannot_overspend`; reconciliation/cancellation in `test_budget_cancel_reconcile_and_duplicate` |
| 15 | Model/provider substitution rejected | `test_model_substitution_and_missing_configuration`, `test_recorded_model_substitution_rejected`, `test_model_role_escalation_rejected` |
| 16 | Missing production assignment fails closed | `test_model_substitution_and_missing_configuration` also confirms unapproved assignments fail and production execution remains disabled with an approved assignment |
| 17 | Audit preserves tenant and operation | `test_audit_environment_and_operation`; rollback test proves atomic task/audit behavior |
| 18 | No network/services/production writes | Socket creation blocked in test setup and crash child; `test_no_network_access` validates guard; all databases use TemporaryDirectory; implementation has no transport/provider/service integration |

Other executed coverage: `test_budget_policy_change_denied`, `test_verification_wrong_tenant_and_principal`, `test_rejected_and_more_research_outcomes`, and `test_rework_cannot_bypass_retry_budget`.

## Executed correction regressions

All 20 methods below in `CorrectionTests` passed. Loops cover all four environments or all 12 unequal environment pairs where noted; those assertions do not inflate the method count.

| Correction | Regression methods and observed assertions |
|---|---|
| Immutable packet history | `test_packet_history_and_exact_verdict_links_survive_restart`: all four environments, exact canonical content/digests/versions and historical verdicts after reopen; old decision rejected for revised head |
| Idempotent packet replay | `test_packet_replays_do_not_change_head_state_or_audit`: historical/current replay after approval leaves head, approval and row counts unchanged |
| Concurrent packet updates | `test_concurrent_duplicate_packet_revision_has_one_effect`; `test_concurrent_conflicting_and_stale_revisions_rejected`: one effect for identical revision, one winner for conflicting version, stale/skipped writes rejected |
| Immutable linked records | `test_packet_and_verdict_storage_are_immutable`; `test_verdict_foreign_key_requires_exact_revision_digest_and_environment`: updates/deletes and mismatched revision/digest/tenant linkage rejected |
| Atomic revision commit | `test_packet_revision_and_head_rollback_together`: audit failure rolls back inserted revision and head advance |
| Unsupported schema safety | `test_unsupported_schemas_rejected_without_any_database_mutation`: old v1, future version, missing metadata and malformed v2 remain identical by file bytes, SQL dump, sqlite_master, schema/user/application versions; repeated rejection creates no sidecars |
| Other storage safety | `test_existing_empty_or_corrupt_file_is_never_initialized`; `test_compatible_schema_open_preserves_every_existing_row`; `test_cold_concurrent_initialization_is_safe`; `test_database_tenant_mismatch_is_nonmutating` |
| Sequential retry replay | `test_retry_sequential_replay_returns_original_result_without_effects`: all environments; original result survives reopen, no repeated counter/audit/outbox effects, later task state not rolled back |
| Concurrent retry replay | `test_retry_concurrent_replay_has_one_counter_and_audit_effect`: 16 duplicate requests commit one operation/counter increment/audit event |
| Retry authorization/exhaustion | `test_retry_identity_conflicts_and_exhaustion_fail_closed`: new IDs spend allowance, replay still works after exhaustion, conflicting task/principal IDs and missing/blank IDs rejected |
| Retry rollback | `test_retry_failure_rolls_back_identity_counter_and_audit`: failed transaction leaves no partial result or increment |
| Retry crashes | `test_committed_retry_crash_then_replay_has_one_effect`; `test_uncommitted_retry_crash_then_replay_has_one_effect`: real child exits 24/25, restart replay ends with one result/counter/audit event and no outbox effects |
| Isolation matrix | `test_all_state_operations_enforce_cross_environment_boundaries`: all 12 unequal pairs; task/retry/packet/current/history/verification/outbox/delivery/budget boundaries, own-only audit/recovery listings, foreign-ID namespace collisions, byte-for-byte unchanged target database |
| Focused identity forgery | `test_valid_requester_with_forged_environment_rejected_by_scope`: valid authenticated requester and role, mismatched payload environment, all 12 unequal pairs rejected before any database creation |

Before the hot-journal correction, compilation passed with `python3 -m compileall -q src tests`. A standard-library metadata/AST check passed for all 9 Python files and confirmed Python >=3.10, no runtime dependencies and the unchanged setuptools build backend. No wheel was built or installed. The Python 3.9 failure above is from the original implementation run and was not rerun during corrections.

## Practical limits of this PASS

Automatic hot-journal recovery now requires both an untrusted receipt and a matching active record in the independently injected test authority, bound to path/environment/schema/device/inode and authority/registration/epoch IDs. Unregistered, revoked, edited, substituted, missing-trust or mismatched hot files are refused without writable recovery. For recognized files, current compatibility can be established only after recovery, and later rejection may follow SQLite physical changes; the exception reports this explicitly. No universal non-mutating rejection claim is made after writable recovery has been permitted. This is not an automatic v1-to-v2 migration or a manual journal repair.


This is a Phase 1 offline acceptance result. It establishes neither live agent research quality nor Linux/Hermes/Photon/Memory/CTO compatibility. No real credentials, private vaults, providers or third-party skills were accessed. OS-level tenant isolation, real delivery and billing receipts, trusted Memory promotion, and end-to-end V1 acceptance remain untested and deferred.

Production recovery authorization is disabled. This in-memory ledger is a test provider, not durable protected credential storage. Full authority-process loss fails closed; current test-state transfer exercises worker-process restart only. No automatic backup restoration or stale-snapshot adoption is supported. Production key/authority protection, current revocation state, anti-rollback restoration and Linux filesystem/process permissions remain unverified. See the current correction report for the exact trust boundary and lifecycle policy.
