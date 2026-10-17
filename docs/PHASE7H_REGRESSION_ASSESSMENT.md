# Phase 7H regression assessment

Read-only assessment, 2026-10-16. No source/test changes, test executions, installations, Linux access or deployment were performed. This document and `PHASE7H_BASELINE_FAILURE_ANALYSIS.md` are the only review deliverables created.

## Conclusion

No new acceptance-blocking regression is demonstrated by the 17 failures and 3 errors: all 20 identities and normalized tracebacks are identical in the untouched and modified copies. Fifteen failures require Linux atomic rename, four failure/error cases require Linux socket peer credentials, and one error depends on a missing installed public-key fixture. The complete copied Memory suite remains failing; inherited failures must not be described as a full compatibility PASS or Linux operational acceptance.

The recorded modified run adds 23 passing staging cases (125 total, 102 passing, 17 failures, 3 errors, 3 skips). The reported 305 passing Research cases are separate. See the companion analysis for all exact case names, locations, comparisons and retest actions.

## Actual source-diff review

Baseline: `artifacts/staging/phase7h-memory/baseline/`; modified: adjacent `work/`. All 34 original files match `BASELINE_MANIFEST.json` hashes in baseline. Comparing actual files shows exactly one modified original file and two added Python files:

| File under work | Change | Effect |
| --- | --- | --- |
| `focused_v1/store.py:276,282` | Add `review_state` to existing duplicate lookup and return `prior["review_state"]` instead of literal `approved` | Response correction only; no SQL approval mutation, new promotion, or changed dedup/provenance checks |
| `focused_v1/research_stage.py` | New explicitly test-only Research contract/lifecycle extension | Additive synthetic tables and separate receipts in isolated MemoryStore; not mounted on existing HTTP routes |
| `tests/test_research_memory_stage.py` | 23 new regression cases | No original tests altered or weakened |

Reviewed `CHANGES.patch` against the actual changed files, including the new test file. The duplicate branch still requires matching source message, principal, task and content. Existing-record stored approval remains authoritative. Regression cases at new test lines 59–76 exercise approved, pending and rejected responses, pending edits and authorization denial.

The 20 failing cases exercise unchanged Obsidian bridge, editor, ingress and disposable-delivery code. Some use MemoryStore for setup or existing record operations, but their failure traces do not implicate the changed duplicate-response branch. The shared CandidateTests helper (`baseline/tests/test_obsidian_candidate.py:92–96`) creates records without a source-message ID, bypassing that branch. No original test imports the new Research module. Identical baseline failures provide direct evidence these failures do not require the Research changes to occur; they do not prove absence of every possible regression.

All other original files are byte-identical, including `focused_v1/server.py`, all copied `obsidian_candidate` modules, `deploy/focused-v1/obsidian_export.py`, device scripts and existing tests. Existing `/v1/memory` and `/v1/obsidian-memory` routing is unchanged. Their one intentional behavioral difference is that duplicate-create now reports stored review state accurately. Research records are not projected into legacy auto-approved memories or the existing export path.

## Production-disable evidence

References below are to `artifacts/staging/phase7h-memory/work/focused_v1/research_stage.py`:

- Lines 99–100: TestAuthority requires explicit `test_only=True`, `production=False`; no production authority or automatic grants.
- Lines 161–166: ResearchStage requires the same explicit flags, exact test-authority type, and independently authorized admin before staging setup.
- Lines 169–183: additive `research_stage_*` tables require explicit initialization; unsupported staging schema is rejected. This is synthetic setup, not an approved production migration.
- Lines 249–250: production `promote()` always denies; synthetic attestations cannot authorize real trusted promotion.
- Lines 371–373: production dispatch always denies; no Research HTTP action is enabled.

The explicit `simulate_promotion` path is test-only, with SIMULATED/NON_PRODUCTION candidates and receipts. Real credential storage, verifier issuer trust, tenant mapping, host grants and production schema policy remain unresolved. The module depends on local Research codecs and is not a standalone production Memory release. Revocation, currentness and immutable revision behavior have synthetic coverage; these tests are not genuine factual verification or proof of production authorization.

## Remaining evidence gaps and acceptance boundary

The three originally requested Phase 7H implementation/report documents were not present at the time of this review. This assessment relies on actual staging source, manifest, patch, transcripts and structured results rather than inferring their contents. This documentation gap does not change the reproduced failure classification, but those delivery documents should be completed before an implementation approval decision.

No new regression is identified from the reviewed failures or isolated diff. Compatibility validation is incomplete for Linux-only Obsidian atomic/race behavior and authenticated Unix ingress. The inherited failures block claiming an all-green copied Memory compatibility suite; they do not establish that the Research candidate, commit or simulated promotion extension is incorrect.

Hard deletion/retention mapping and Research Obsidian export are deliberately fail-closed, pending Memory-owner policy. Production attestation authority, production schema/migration approval and grants are not supplied. These are deployment prerequisites, not regressions introduced into existing Memory operations.

## Minimum next action

1. Preserve baseline/work source and failure artifacts; do not change security primitives to make Mac tests green.
2. Obtain separate authorization for an isolated Linux compatibility environment, independent of production. Run the unchanged 19 Linux-dependent failure/error cases in both copies, then both full copied suites using the same environment and synthetic data.
3. For the public-key fixture case, authorize only a synthetic test-harness fixture substitution; verify malformed existing key rejection and unchanged bytes. Never import production credentials.
4. Require matching baseline-versus-work outcomes, all new staging tests passing, and documented resolution of any Linux-only failure before production approval. Validate the target Python 3.12.3 environment separately from Mac Python 3.14.8.
5. Complete missing implementation documentation and resolve Memory-owned trust/schema/export/retention decisions. Keep production Research disabled; no Linux integration or deployment is authorized by this review.
