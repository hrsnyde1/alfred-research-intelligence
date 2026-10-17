# Phase 7H Memory test results — reconstructed

Reconstructed on 2026-10-16 from existing Mac artifacts; not a contemporaneous execution report. No tests rerun, Linux accessed, staging source/tests changed, or dependencies installed during reconstruction. Unknown details are explicitly marked.

## Actual saved outcomes

| Suite | Run | Pass | Failure | Error | Skip | Recorded duration |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| Untouched Memory baseline | 102 | 79 | 17 | 3 | 3 | 8.030 s |
| Modified Memory plus extension | 125 | 102 | 17 | 3 | 3 | 9.448 s |

Sources: baseline/work-results.json, baseline/work-tests.txt, baseline/work-runtime-stderr.txt, compatibility-comparison.json. Both unittest transcripts report FAILED; saved runner returns nonzero for these outcomes. An independently persisted shell exit-status log is unavailable. Twenty failure/error traces match after normalizing copy paths; skip IDs and reasons match. See PHASE7H_BASELINE_FAILURE_ANALYSIS.md for every case.

The 23 added test methods all report ok in the work transcript. A separate final standalone-run log is not available in these artifacts. The prior 305 Research passes are reported historical results; this reconstruction does not claim to have executed them.

## Environment and commands

Historical evidence identifies macOS arm64 and `/opt/homebrew/bin/python3` Python 3.14.8, available cryptography and Node, unavailable PyMuPDF. Exact historical Node/cryptography versions and complete shell environment were not captured in the result JSON. Linux target Python 3.12.3 has not run these tests.

Saved reproduction driver (not newly executed):

```sh
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 artifacts/staging/phase7h-memory/run_tests.py baseline
PYTHONDONTWRITEBYTECODE=1 /opt/homebrew/bin/python3 artifacts/staging/phase7h-memory/run_tests.py work
```

Baseline was historically recorded using an equivalent inline guarded runner, per prior review evidence; its exact original shell command is not independently present. Work driver uses child unittest discovery `discover('tests', pattern='test_*.py')`, verbosity 2, copy-relative cwd, and PYTHONPATH containing copy, Research src/tests. The Python guard blocks external tuple-address connections, permits loopback/Unix fixtures, and is not an OS-level sandbox or Node network control. Tests used synthetic temporary state. No production isolation claim should rest on that guard alone.

15 failures depend on Linux renameat2; 2 failures and 2 errors depend on Linux SO_PEERCRED; 1 error requires an installed public-key fixture not supplied by the test. Three existing skips: one PDF dependency and two pinned Ubuntu skeleton cases. The extension is not implicated by these shared failures. Linux retesting remains necessary; optional dependency skips must be disclosed separately from mandatory extension coverage.
