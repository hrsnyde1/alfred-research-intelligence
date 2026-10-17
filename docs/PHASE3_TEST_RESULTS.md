# Phase 3 executed test results

Date: 2026-10-15. Runtime: Python 3.14.3 / SQLite 3.50.4 on this Mac. All new model identities, prices, source content, authority state and tasks are synthetic. No live model/service/Linux acceptance is claimed.

## Commands and actual outcomes

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_research.py' -v
```

| Check | Actual result |
|---|---|
| Final complete suite | **162 passed, 0 failures, 0 errors**, 6.082 seconds, exit 0 |
| Focused Phase 3 suite | **37 passed, 0 failures, 0 errors**, 2.791 seconds, exit 0; final source including transaction-bound deadline checks |
| AST/in-memory compilation | **25 Python files** passed, exit 0; no bytecode written |
| Packaging checks | Research package imports; stdlib tomllib parse; unchanged Python >=3.10, src package discovery and zero runtime dependencies asserted; no wheel build or installation |

The complete count comprises **125 unchanged Phase 1/2 tests + 37 new Phase 3 methods**. Loops/subcases across environments/categories do not inflate that count. An initial 29-case focused run had 28 passes and one error caused by a malformed self-approval test fixture. It was replaced with a valid VerificationDecision targeting the unauthorized researcher role; no existing assertion was removed/weakened. The intermediate 154-case suite and subsequent 34/35-case focused runs passed before the final complete run. No unresolved failure remains.

## Required acceptance mapping

All named new methods are in `tests/test_research.py`.

| # | Required assertion | Executed coverage |
|---|---|---|
| 1 | Representative lead selection | `test_correct_lead_selection_for_source_categories`: GitHub, article, document, website, YouTube, Instagram, TikTok and X with code/finance/legal/business/general objectives. Unsupported PDF cannot invent usable evidence. |
| 2 | One lead per task | `test_one_accountable_lead_and_justified_support_all_environments`: all four environments, lead owns the combined packet and distinct supporting actor contributes traceable claims. |
| 3 | Support only when justified | Representative routing cases have no supporters; mixed tax/legal objective requests exactly one support with a reason. `test_overbroad_support_scope_escalates` prevents silently exceeding two supporters. |
| 4 | Claims trace to evidence | `test_source_provenance_and_simulation_are_bound_in_packet`, `test_every_supporting_citation_and_material_claim_is_assessed`: full SourceResult/evidence hashes, contributor traces and complete per-claim assessments. |
| 5 | Partial/inaccessible honesty | `test_partial_source_never_becomes_complete_approved_investigation`, `test_inaccessible_and_unsupported_sources_stop_before_model_spending`: no fabricated evidence or false completion; unsupported/blocked inputs stop before model reservations. |
| 6 | Injection cannot control Director | `test_prompt_injection_cannot_change_lead_permissions_or_verdict`: hostile SKILL.md retains code routing and researcher role; no execution/cross-company task; independent review requests more research. |
| 7 | Self-approval denied | `test_self_approval_forged_and_unassigned_verifiers_rejected`, `test_supporters_cannot_grant_permissions_or_write_verdict_checkpoints`: authentic researcher/support contexts cannot review or write verification records. |
| 8 | Forged verifier denied | Reconstructed verifier context, forged researcher-role elevation and other-company verifier rejected by issued context checks. |
| 9 | Stale approval denied | `test_bounded_rework_and_historical_decisions`: old packet review after a new revision fails; historical decisions remain exactly linked. Existing Phase 1 stale/hash tests also pass. |
| 10 | Evidence changes require fresh review | `test_changed_source_requires_new_revision_and_verdict`: same revision cannot replace source; next revision changes evidence/packet digests and has no inherited decision. |
| 11 | REJECTED remains untrusted | `test_incorrect_claim_rejected_even_with_approving_test_model`: approving model proposal cannot override rejected evidence; task is terminal rejected and cannot rework into approved. No Memory/promotion code exists. |
| 12 | Bounded NEEDS_MORE_RESEARCH | `test_bounded_rework_and_historical_decisions`, `test_rework_exhaustion_cannot_spend_or_loop`: corrections durable, next packet immutable, retry increments once, new independent decision required, cap prevents extra spending. |
| 13 | Budget/deadline stop safely | `test_environment_and_task_budgets_stop_further_work`, `test_deadline_exhaustion_before_and_after_model_execution`, `test_expired_deadline_does_not_wait_for_a_busy_workflow_lock`, `test_adaptive_reservations_reconcile_actual_consumption`, `test_deadline_expiring_inside_packet_transaction_rolls_back`, `test_deadline_expiring_inside_verdict_transaction_rolls_back`. Actual work is reconciled; deadline prevents packet/decision commit and no unlimited lock wait occurs. |
| 14 | Interrupted research resumes | Three process-crash methods plus `test_concurrent_replays_have_one_packet_and_decision_effect`: durable results reused, one mutation per logical packet/verdict/call, no duplicate spending. |
| 15 | Cross-company access denied | `test_cross_company_coordination_and_history_denied`: all 12 unequal environment pairs; Director run, verifier review/history and journal namespace isolation. Foreign support context in roster rejected. |
| 16 | No live providers/production writes | `test_no_live_provider_or_memory_integration`, `test_fixed_model_and_provider_fail_closed`: socket/execution guards, temporary roots, production flag/unknown provider rejected; no vaults or Memory transport. |
| 17 | Existing regression suite intact | All 125 Phase 1/2 cases execute successfully, including Director-only database provisioning, hot-journal recovery, forged receipts and both extraction corrections. |

Additional adversarial/operational cases:

- Incorrect claim with a valid citation → REJECTED; unrelated supporting citation → REJECTED even when another citation supports the text; every material claim is still assessed.
- Unsupported citation IDs → explicit contract failure, no fabricated evidence/packet.
- Inference, unknown and declared contradictory evidence → preserved and NEEDS_MORE_RESEARCH, not silently approved.
- Changed provider fixture configuration, model ID, approval or price → fail closed.
- Excessive consumed units → invalid result rejected; reserved allowance remains held, no packet or false settlement.
- Replayed plan cannot extend deadline, increase cost authorization or change lead. Expiry injected after packet/decision SQL writes but before commit rolls back state, rows and mutation audit events; completed synthetic consumption remains reconciled.
- Cached review claiming approval, wrong source digest or wrong packet version → recomputation rejects the checkpoint; rejected task cannot become approved.
- Researcher journal writes to Director/verifier keys and reconstructed authenticated contexts → rejected.

## Real child-process fault injection

| Crash boundary | Intentional exit | Observed recovery |
|---|---|---|
| Model checkpoint/accounting completed, before packet commit | **41**, independently in all four environments | New runtime reuses committed draft without calling provider again; one reservation, settlement and packet commit. |
| Packet committed, before response | **42** | Replay retrieves original immutable packet; no duplicate packet or budget reservation. |
| Verifier output/accounting/review checkpoint completed, before SQLite decision | **43** | New verifier runtime recomputes cached review against pinned evidence and reuses it without provider execution; one exact-digest decision and two total call reservations/settlements. |

Workers reconstruct only trusted current test registration authority state supplied by the parent harness over stdin. They never read registration trust from DB/receipt/model/source text. Each child blocks socket creation. The parent checks actual exit status, persisted records and mutation audit counts; Python exceptions alone are not the crash evidence.

The full suite also reran the original large-transaction recovery diagnostic (child **29** in all four environments, SQLite-managed recovery) and forged-receipt diagnostic (child **30**, unregistered recovery denied with DB/journal/ledger unchanged).

## Evidence limits

This PASS is for synthetic offline workflow behavior. Verification checks exact supplied-text excerpts and explicit evidence annotations, not real-world truth or general semantic contradiction discovery. All review/packet/decision artifacts carry the simulation warning; there is no confidence score. Source data remains fixture/user-supplied Phase 2 evidence, not an authenticated external provider receipt.

The test registration authority remains in-memory; tests establish worker-process restart while trusted parent bootstrap persists, not production host identity recovery. Journal and SQLite use replay-safe separate commits; full distributed atomicity and exactly-once live provider execution are not claimed. Power loss, hostile same-account file mutation, Linux grants/storage/backup/retention, Windows runtime, provider billing/cancellation and real verifier execution remain unverified. No dependency, account connection, company data, service, commit/push or deployment was used. Phase 4 has not begun.
