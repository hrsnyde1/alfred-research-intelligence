# Phase 2 executed test results

## Targeted correction results — latest

This section supersedes the initial 115-test counts below. Existing source and Phase 1 tests were preserved unchanged.

| Command/check | Actual outcome |
|---|---|
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v` | **125 passed, 0 failures/errors**, 2.720 seconds, exit 0; all 115 existing cases plus 10 new cases |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_source_corrections.py' -v` | 10 passed, 0 failures/errors, 0.019 seconds; before final URL bounds/IPv6 refinements; all 10 also passed in the final full suite |
| `PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_source_corrections.py' -k review_reproduction -v` | **2 passed, 0 failures/errors**, 0.003 seconds, exit 0, after final source changes |
| AST and in-memory compilation | All **19 Python files** passed; no bytecode written |
| Standard-library TOML metadata checks | Python >=3.10 and no runtime dependencies unchanged; no build/install |

New methods in `tests/test_source_corrections.py`:

- `test_review_reproduction_unreadable_subtree_reports_partial`: actual chmod-denied synthetic SKILL.md subtree, controlled EACCES fallback if required; accessible README retained; PARTIAL and omitted path/PermissionError/errno/reason reported; source identity unchanged and no new files.
- `test_injected_traversal_denial_is_reported_and_repeatable`: real fwalk with directory-open fault injection; repeated results equal; raw-file digest independently checked.
- `test_unreadable_only_subtree_returns_explicit_error`: no useful accessible evidence yields ERROR, empty evidence and disclosed omission.
- `test_other_traversal_errors_preserve_accessible_evidence`: controlled EIO is explicitly reported with retained accessible evidence.
- `test_propagated_scandir_error_also_reports_partial`: runtime-propagated scandir failure cannot bypass incomplete-inspection reporting.
- `test_review_reproduction_root_relative_canonical_preserves_body`: exact `/report` reproduction now resolves to `https://example.com/report`, with original text/digests/provenance retained.
- `test_path_relative_canonical_urls`: path-relative, parent-relative, query-relative and network-path references resolve without fetching.
- `test_absolute_canonical_urls_and_missing_metadata`: valid absolute and public IPv6 URLs retained; fragment removed; missing canonical remains absent.
- `test_invalid_canonical_metadata_preserves_body_and_omits_identity`: supplied and parsed metadata reject HTTP, javascript, credentials, private/link-local/loopback/IPv4-mapped destinations, private hostnames, invalid ports/IPv6, unsafe whitespace/backslashes; body evidence preserved with limitation.
- `test_relative_canonical_requires_safe_original_page_url`: fixture/non-HTTPS/private/credential-bearing bases cannot authorize relative resolution; extracted body remains available.

Each HTML case checks submitted identity, original file digest, evidence digest linkage, snapshot digest and fixture origin. Permission failures are injected at real OS operations so the actual fwalk callback/propagated-error paths are exercised; an assertion confirms the fault was triggered. Socket guards remain active. No imported script is executed.

Two early correction-only runs reported 3 errors (scandir propagation) and then 4 failures (Mac path aliases obscuring omitted location). Source handling was corrected; no test was removed or weakened. Current final suite and both reproduced failures pass. Existing child crash statuses 29/30 remain successful fault-injection coverage, not failures.

No new production capability is inferred from these results. All original Phase 2 limitations below remain, including unsupported PDF, fixture-only media, inactive transport, cooperative limits and unverified Linux filesystem/authority boundaries.


Date: 2026-10-15. Runtime: Python 3.14.3 / SQLite 3.50.4 on this Mac. All data/principals/credentials are synthetic; file fixtures use temporary directories. No live provider or Linux acceptance evidence is claimed.

## Executed commands

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_sources.py' -v
```

| Check | Actual outcome |
|---|---|
| Final full suite | **115 passed, 0 failures, 0 errors**, 2.658 seconds, exit 0 |
| Final Phase 2 source-only suite | **34 passed, 0 failures, 0 errors**, 0.041 seconds, exit 0 |
| In-memory AST/compile check | All **18 Python files** passed; exit 0; no bytecode written |
| Standard-library packaging checks | `pyproject.toml` parsed with tomllib; Python >=3.10, zero runtime dependencies and src package discovery configuration asserted; source package import passed |

The full count comprises all **81 unchanged Phase 1 tests** plus **34 new source-processing methods**. Four-environment and all-platform loops are subcases and do not inflate the test-method count. Earlier intermediate source runs passed 28, 33 and 34 methods; an earlier intermediate full run passed 113 before the last two source cases were added. No failed run was observed during this Phase 2 implementation. No wheel build, dependency resolution/install, network request or Linux test was performed.

The full suite re-executed the existing crash diagnostics: large packet children exited **29** in each of four environments, reproduced old SQLITE_READONLY_ROLLBACK and recovered committed task/revision/verdict/retry state; forged-receipt child exited **30**, with legacy/edited/fabricated JSON refused and database/hot journal/ledger unchanged. These exit statuses are intentional crash simulation, not failed tests.

## Phase 2 required acceptance mapping

Methods below are in `tests/test_sources.py` unless explicitly attributed to the existing Phase 1 suites.

| Requirement | Executed evidence |
|---|---|
| 1. Every source category | `test_all_source_categories_and_environments`: GitHub, website, article, PDF, document, YouTube, Instagram, TikTok, X across all four environments |
| 2. Representative extraction | All-category case plus `test_multi_skill_repository_independent_capabilities`, `test_html_ignores_script_style_and_preserves_locations`, `test_html_structured_metadata_extracted_and_conflicts_not_guessed`, `test_document_supported_text_and_unsupported_formats`, actual directory fixtures |
| 3. Explicit partial/inaccessible/auth/unsupported/error outcomes | `test_each_blocked_outcome_extracts_no_content`, `test_invalid_binary_and_empty_documents_report_partial`, `test_pdf_is_explicitly_unsupported_without_parser`, `test_invalid_platform_canonical_url_errors` |
| 4. No fabricated transcripts/content | `test_media_metadata_only_never_invents_transcripts`, `test_raw_media_not_watched_or_transcribed`, `test_user_supplied_transcript_provenance`; blocked results have no evidence |
| 5. Individual multi-skill identity | `test_multi_skill_repository_independent_capabilities`: two SKILL.md and one named JSON capability, independently linked to evidence |
| 6. Digests/provenance | `test_author_publisher_dates_and_canonical_identity`, `test_result_roundtrip_hash_and_determinism`, `test_snapshot_digest_covers_all_provenance`, `test_result_contract_rejects_dangling_or_mixed_evidence`; file digests compared against independent hashlib SHA-256 |
| 7–8. Injection is data; scripts never execute | `test_repository_security_flags_and_scripts_never_execute`: injection retained as evidence; subprocess/os.system forbidden and synthetic sentinel remains absent; HTML script exclusion and YAML tag preservation |
| 9. Unsafe paths/symlinks | `test_unsafe_paths_and_symlinks_are_not_extracted`; `test_local_fixture_directory_no_execution_symlink_follow_or_writes`: actual symlink to nonexistent external target is never followed |
| 10. Malformed/oversized inputs | `test_malformed_fixture_contracts_rejected`, `test_license_and_manifest_limitations`, `test_oversized_inputs_rejected_before_extraction`, `test_local_directory_requires_explicit_grant_and_limits` |
| 11. Missing/changing repo revisions | `test_missing_changed_and_invalid_repository_revisions`: unknown commit remains absent; changed hash is observed without changing submitted identity; malformed commit ERROR |
| 12. Tenant isolation | `test_every_cross_environment_pair_and_principal_denied`: all 12 unequal pairs; `test_local_fixture_roots_are_environment_isolated`: every environment with disjoint real temporary roots; `test_single_source_request_forgery_and_prompt_scope` |
| 13. Replay/idempotency | `test_no_persisted_effects_and_reordered_files_same_snapshot`: deterministic same results, reordered file snapshots same digest, SQLite forbidden. Source extraction has no persistent writes; existing Phase 1 durable request/retry/outbox idempotency cases still pass |
| 14. Bounded extraction/accounting | `test_output_and_work_limits_accounted`, `test_timeout_is_explicit`, `test_actual_directory_accounting_and_no_grant_copy`, oversize tests: byte/file limits, output truncation, work ceiling and deterministic fake-clock timeout |
| 15. Phase 1 retained | All 81 original/correction/registration/hot-recovery methods passed unchanged |
| 16. No network/production/company data | Socket creation blocked in source test setup; existing crash children retain network guards; `test_production_disabled_and_no_network`; no source persistence or service/client modules introduced |

Additional authorization coverage: `test_unissued_changed_revoked_permission_and_origin_denied` rejects forged/copied/revoked grants, unauthorized grant creation and user-supplied origin escalation. `test_future_network_policy_is_pure_and_rejects_private_addresses` exercises planned DNS/address/redirect validation without using DNS or a transport.

## Limits of these results

PDF has a tested UNSUPPORTED boundary, not an extraction parser. YAML/TOML/dependency declarations are text evidence with flags; YAML semantic validation, complete runtime compatibility and legal license interpretation are not tested capabilities. Media metadata/access outcomes are supplied fixtures; there is no real account, transcript provider or speech recognition. HTML is ordinary parser extraction, not a rendered browser or complete crawler. Commit format validation does not establish a supplied hash's Git object/tree authenticity.

Processing is stateless and storage-free. Trusted local fixture roots and grants are in-memory; no durable source registry, snapshot retention or production host authority exists. CPU deadline enforcement is cooperative; peak RSS, adversarial same-account filesystem races, Windows directory inspection, provider quotas and real billing remain unverified. Python >=3.10 remains the package declaration; positive execution evidence is only Python 3.14.3. No live SSRF prevention claim is made from a pure policy validator.

Phase 3 and production activation remain unauthorized by these results. No dependency installation, commit, push, deployment, Memory/vault access or existing Alfred service change occurred.
