# Phase 6 Mac acceptance matrix

All outcomes below are offline, synthetic and NON_PRODUCTION. Executed tests are in `tests/test_workflow.py`; prior source, budget, packet, intelligence, export and HQ suites remain enabled. This matrix does not establish Linux acceptance.

| Scenario | Executed test / observed behavior | Scope |
|---|---|---|
| A. Personal GitHub → Frontend and CTO | `test_personal_github_frontend_cto_complete`: approved packet, intelligence, distinct Memory submit/commit/promote/read, Frontend association and PROPOSAL_ONLY CTO handoff, two delivered fake notices; replay duplicates none | Complete synthetic path |
| B. Website/article | `test_article_source_preserves_identity`: raw HTML retains identity/evidence, PARTIAL extraction → NEEDS_MORE_RESEARCH, no promotion. `test_authorized_user_supplied_article_document_complete`: explicitly supplied article text → document extraction → classified Frontend intelligence and complete fake lifecycle | Raw HTML is safely incomplete, not a passed full HTML-promotion claim; supplied document path completes |
| C. Fintra → Memory/HQ/owner | `test_three_company_hq_partitions_owner_and_revocation`: separate Fintra lifecycle, exact source/evidence, protected HQ receipt and independently authorized personal owner read | Complete synthetic path |
| D. Gabos independent partition | Same parameterized test for Gabos; own Memory, HQ partition, source and actor scope | Complete synthetic path |
| E. SC Products independent partition | Same parameterized test for SC Products; own Memory, HQ partition, source and actor scope | Complete synthetic path |
| F. Inaccessible media | `test_inaccessible_social_truthful_no_fabrication`: YouTube, Instagram, TikTok all BLOCKED, no conclusions/Memory receipts; short unavailable-source notice | Safe blocked path |
| G. Rejected/NMR | `test_partial_and_verdict_rejected_or_more_research_no_promotion`: synthetic REJECTED and NEEDS_MORE_RESEARCH, plus partial source; none create approved intelligence or Memory promotion | Safe exclusion |
| H. Interrupted/restarted | 17 flow/notification boundary subtests, two transport boundary subtests, model output checkpoint reuse, fresh-process recovery without resupplied fixture; one task/lifecycle and two notices | Durable offline recovery |
| I. Commit/promotion failure | `test_failed_memory_commit_or_promotion_no_false_saved`: PARTIAL, no retrieval or combined saved/read claim | Honest receipt-based failure |
| J. Export/Sync failure | `test_export_and_sync_failure_truthful_final`: failed request, export and Sync separately; no missing-stage success claim. Successful path separately verifies exact export→Sync receipt link | Honest selected-stage results |
| K. Revoked company record | Three-company test revokes promoted records, denies current owner retrieval, writes HQ tombstone; prior Phase 5 stale-sync/revocation/supersession tests also pass | Retraction enforced |
| L. Wrong conversation/company | `test_all_twelve_pairs_wrong_conversation_and_notification_denied`: 48 attempts across 12 ordered unequal pairs denied. Valid requester with forged environment claim, lookalike context and source-message replay substitutions also rejected | Fail-closed ingress and delivery |

Additional tests prove justified support and distinct verifier, budget/deadline blocking, source injection containment, generic Department proposal-only behavior, no fabricated non-development reader grants, notification acceptance versus delivery versus workflow completion, unknown lookup without resend, three-attempt exhaustion, forged final text/reference rejection, concurrent duplicate processing and bounded durable input.

Raw website/HTML full-intelligence promotion and real non-development specialist credentials are remaining capability limits, not silently upgraded by the coordinator. Owner review must not treat the supplied-article document fixture as live website extraction. All five prior phases' fail-closed policies are preserved.

## Recovery correction acceptance addendum

| Boundary | Executed regression | Result |
|---|---|---|
| Sync effect / checkpoint | Later FAILED on same attempt, restart before and after checkpoint | PARTIAL; historical success retained but no current Sync-success claim |
| Revocation after Sync checkpoint | Revoke promoted record, restart | PARTIAL; no stale Sync claim |
| Memory commit / outbox enqueue | Interrupt enqueue, concurrent recoveries, duplicate restart | One original commit; exactly one repaired outbox event before COMPLETED |
| Missing/ambiguous reconciliation | Null result, lost response, no-op outbox repair | Incomplete outcome; no fabricated success |
| Unchanged successful Sync | Restart and repeat | COMPLETED; no duplicate Memory effects |

Latest full suite: 247 passed, zero failures/errors. Seven targeted diagnostics passed. No live operational acceptance is implied.

## Cached-result recovery acceptance addendum

| Scenario | Regression evidence | Result |
|---|---|---|
| COMPLETED checkpoint, later FAILED Sync, no FINAL yet | `test_cached_result_failed_sync_all_environments` | All four environments: PARTIAL, no Sync-success claim, one corrected FINAL; original checkpoint/history retained |
| Revocation / supersession before FINAL | `test_cached_result_revocation_and_supersession` | No current promotion/read/export/Sync/HQ success claims |
| Later failed HQ delivery | `test_cached_result_failed_hq_delivery` | PARTIAL; no stale HQ delivery claim |
| Promotion invalid, export not selected | `test_cached_result_promotion_invalid_without_export` | PARTIAL; no stale combined Memory success |
| Unchanged result, concurrent restart | `test_cached_result_unchanged_concurrent_restart_one_final` | One logical FINAL; no repeated model, verification, commit or promotion calls |
| Delivered FINAL followed by failure | `test_delivered_final_is_not_rewritten_after_sync_failure` | Corrected PARTIAL return/projection; original delivery retained; no duplicate/rewrite |
| Prepared but unsent FINAL followed by failure | `test_prepared_final_is_not_sent_after_sync_failure` | Obsolete notice stays unsent; public replay denied; no silent replacement |
| Missing/ambiguous reconciliation | `test_cached_result_missing_ambiguous_reconciliation` | PARTIAL/INCOMPLETE; no receipt-based success claims |
| Company isolation | `test_completion_snapshots_deny_cross_environment_receipts` | All 12 unequal pairs yield no foreign receipts; fabricated context denied |

No separate correction-notification channel exists. Changed results cannot rewrite prepared or delivered notices; an obsolete prepared outbox entry remains pending and cannot be sent via the public simulation API. Real delivery/correction behavior awaits owner-authorized Linux integration.

Latest executed validation: **256 passed**, zero failures/errors, 36.449 seconds; **12 targeted diagnostics passed**, zero failures/errors, 9.538 seconds. Compilation of 38 Python files and dependency-free metadata checks passed. Mac simulation only; no Phase 7 or deployment.
