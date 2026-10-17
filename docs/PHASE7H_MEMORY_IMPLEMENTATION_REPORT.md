# Phase 7H Memory implementation report — reconstructed

Reconstructed on 2026-10-16 from existing Mac artifacts; not a contemporaneous execution report. No tests rerun, Linux accessed, staging source/tests changed, or dependencies installed during reconstruction. Unknown details are explicitly marked.

Evidence: `artifacts/staging/phase7h-memory/BASELINE_MANIFEST.json`, `CHANGES.patch`, actual baseline/work source, JSON results and unittest transcripts. Prior review reports remain historical records that correctly said these three reports were absent at that time.

## Baseline and exact changes

Source origin recorded in manifest: `/opt/alfred-obsidian-v1/releases/4d5ba29bd3027e74c808a8feaf1b5dadfded22f0/source`. All 34 baseline file hashes match the manifest. Exact copied paths and original hashes are in that manifest (not inferred from a different release). The staging execution plan enumerates all paths. Transfer timing and original remote execution logs are not independently reconstructible from this manifest alone.

Only existing source change: `work/focused_v1/store.py:276,282` includes review_state in the duplicate lookup and returns the stored value rather than unconditional approved. It preserves provenance comparisons, dedup identity, authorization and stored review state. Added files: `work/focused_v1/research_stage.py` and `work/tests/test_research_memory_stage.py`. All other 33 copied baseline files, including existing tests, server and Obsidian modules, are byte-identical in work.

The extension uses the existing MemoryStore SQLite transaction boundary, with additive synthetic research_stage tables, immutable packet/candidate revisions, operation receipts, exact provenance/citation checks, independent injected test authority, scoped retrieval, currentness, reconciliation and revocation/conflict/supersession handling. Existing HTTP routes do not mount it. No projection into generic auto-approved memories or Obsidian export occurs.

Production constructor defaults deny; only explicit test_only=True and production=False with TestAuthority and authorized admin can initialize. `promote()` and `dispatch_research()` always deny. Simulated promotion remains explicitly NON_PRODUCTION. Production tenant identifiers, trusted verifier issuer/grants, schema migration, deletion/retention and Research export/Sync policy are not configured; deletion/export paths fail closed. This is not a deployable production Memory extension.

## Recorded validation and limitations

Saved baseline: 102 tests, 79 pass, 17 failures, 3 errors, 3 skips. Saved work: 125 tests, 102 pass, same 17 failures, 3 errors, 3 skips. The 23 additional cases pass in the saved complete work run. Detailed commands, evidence limitations and timings are in PHASE7H_MEMORY_TEST_RESULTS.md. No all-green copied Memory suite or Linux operational acceptance is claimed. The separately reported 305 Research passes lack a dedicated persisted result artifact in the staging evidence reviewed here and are historical reported evidence, not independently re-established.
