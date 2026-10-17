# Phase 7I isolated test execution plan

Proposed only; none of these Linux writes, transfers or test commands has been executed. Readiness facts and blockers are in PHASE7I_LINUX_STAGING_READINESS.md.

## Exact proposed layout and transfer allowlist

Linux root: `/home/alfred/research-staging/phase7i-memory-20261016` (must be absent; refuse reuse/symlinks). Preserve repository-relative paths underneath it, so existing test parents[5] and runner parents[2] resolve correctly. Transfer no archive, .git, configuration, databases, journals, result logs, credentials, vaults or personal data.

Transfer each of the following 34 paths under BOTH `artifacts/staging/phase7h-memory/baseline/` and `artifacts/staging/phase7h-memory/work/`:

- `focused_v1/__init__.py`
- `focused_v1/store.py`
- `focused_v1/server.py`
- `obsidian_candidate/__init__.py`
- `obsidian_candidate/alfred_editor_v1.py`
- `obsidian_candidate/bridge.py`
- `obsidian_candidate/capture_routes.py`
- `obsidian_candidate/context.py`
- `obsidian_candidate/context_service.py`
- `obsidian_candidate/cycle.py`
- `obsidian_candidate/disposable_delivery.py`
- `obsidian_candidate/disposable_forced.py`
- `obsidian_candidate/editor_origin.py`
- `obsidian_candidate/editor_transport.py`
- `obsidian_candidate/hq_sync_once.py`
- `obsidian_candidate/ingress.py`
- `obsidian_candidate/notifications.py`
- `obsidian_candidate/outcome_gate.py`
- `obsidian_candidate/recovery.py`
- `obsidian_candidate/references.py`
- `obsidian_candidate/routing.py`
- `obsidian_candidate/scaffold.py`
- `obsidian_candidate/scoped_ports.py`
- `obsidian_candidate/service_api.py`
- `obsidian_candidate/snapshot.py`
- `tests/test_focused_v1_obsidian_export.py`
- `tests/test_obsidian_candidate.py`
- `tests/test_obsidian_disposable_delivery.py`
- `deploy/focused-v1/obsidian_export.py`
- `scripts/count_only_v1_ownership.py`
- `device/alfred-memory-editor/core.js`
- `device/alfred-memory-editor/device.js`
- `device/alfred-memory-editor/test/hq-integration-driver.js`
- `deploy/obsidian-editor/disposable-test/inspect-delivery-state.py`

Also transfer exactly:

- `artifacts/staging/phase7h-memory/work/focused_v1/research_stage.py`
- `artifacts/staging/phase7h-memory/work/tests/test_research_memory_stage.py`
- `artifacts/staging/phase7h-memory/BASELINE_MANIFEST.json`
- `artifacts/staging/phase7h-memory/CHANGES.patch`
- `artifacts/staging/phase7h-memory/run_tests.py`
- All current `.py` files under `src/alfred_research/` (local Research dependency tree), with explicit relative-path/hash enumeration approved before transfer; no caches or runtime data.
- `tests/test_research.py` (synthetic fixture helper imported by extension tests).

No frozen Phase 7A archive is needed or modified. Do not copy prior runtime stderr or result files; new Linux outputs must be distinguishable from Mac evidence. Generate a current allowlist manifest on the Mac before transfer authorization, verify every transferred byte on Linux, and verify baseline's 34 hashes against BASELINE_MANIFEST. Record changed/additional work hashes independently. Do not import code from installed production releases at execution time.

## Fixtures and permissions

Original tests provide synthetic keys, actors, vault-like temporary trees, memory databases, Node driver data and local server handlers. Copy the declared JS/helper scripts above. Public /etc/skel files may be exposed read-only to test the matching pinned skeleton. No production keys, sockets, Memory endpoint, vault or auth configuration may be exposed. A separately reviewed harness may patch only `obsidian_candidate.disposable_delivery._authorized_line` with the synthetic forced-public-key bytes used by neighboring tests; log this as a fixture-adjusted run. Run both copies identically. Never call real SSH/provider tools from fixtures.

After separate approval, create new workspace with umask 077 and mode 0700, refusing existing paths. Test temporary files must use a private tmpfs; result artifacts are written under the workspace only. Prevent shell environment credentials reaching test processes using env -i. Baseline/work original source files should be read-only during tests, output directory writable. Current runner writes under its staging parent, so preserve that bounded writable output location.

## Execution gates and exact commands

Gate 1: approve allowlist/hashes, missing reports, sandbox design and any fixture harness. Gate 2: prove private network and hidden production paths with a bounded sandbox preflight; no host-setting changes. Gate 3: execute tests. Commands below are a proposed bwrap configuration, NOT verified executable on this host. Confirm /lib and /lib64 mounts and required runtime paths in preflight; stop if unsupported. No /home, /opt, /run or production /var mount is exposed. /workspace contains only transferred files. A private network permits ephemeral test loopback listeners without access to host services.

```sh
STAGE=/home/alfred/research-staging/phase7i-memory-20261016
/usr/bin/timeout 240 /usr/bin/bwrap \
  --unshare-all --die-with-parent --new-session \
  --ro-bind /usr /usr --ro-bind /lib /lib --ro-bind /lib64 /lib64 \
  --dir /etc --ro-bind /etc/skel /etc/skel \
  --proc /proc --dev /dev --tmpfs /tmp \
  --bind "$STAGE" /workspace --chdir /workspace \
  /usr/bin/env -i PATH=/usr/bin:/bin HOME=/tmp TMPDIR=/tmp \
  PYTHONDONTWRITEBYTECODE=1 \
  /usr/bin/python3 artifacts/staging/phase7h-memory/run_tests.py baseline
```

Repeat the identical command replacing final `baseline` with `work`. Do not chain with `&&`: both failing suite outputs must be collected. Record each exit status; 124 means timeout, not a test assertion. Existing runner child limit is 180 seconds. An isolated Node runtime, if separately approved, needs its exact read-only runtime paths and ALFRED_TEST_NODE supplied; do not assume host Node exists.

For the 23 extension-only tests, use the same sandbox prefix and clean environment, with:

```sh
PYTHONPATH=/workspace/artifacts/staging/phase7h-memory/work:/workspace/src:/workspace/tests \
/usr/bin/python3 -m unittest discover \
  -s /workspace/artifacts/staging/phase7h-memory/work/tests \
  -p test_research_memory_stage.py -v
```

This direct invocation also needs PYTHONDONTWRITEBYTECODE=1 and private HOME/TMPDIR as above. Test-only synthetic data remains mandatory. No production module registration or HTTP route activation.

Unmodified discovery first preserves exact baseline behavior, including the expected missing-public-key error in a hidden /opt. A fixture-adjusted second comparison is allowed only after approving the harness. Do not silently label adjusted execution as an untouched test run. Node/PDF skips must remain explicit. Full-suite success is not promised; actual counts must be measured.

## Comparison and acceptance

Preserve baseline/work JSON, transcripts, runtime stderr, exit codes, Python/SQLite/dependency versions and input hashes. Compare exact failure/error/skip IDs and normalized traces, not counts alone. For the original 20 cases, record outcome changes individually. Required criteria: 23 new tests pass; no new existing-test failures/errors; approved duplicate-create response correction behaves as intended; production promotion stays disabled; atomic/race and peer-credential tests actually execute. Node-dependent cases skipped are missing coverage, not resolution of their prior failures. Separate baseline defects, fixture dependencies and extension regressions.

## Cleanup and stop

After results are reviewed, request separate explicit removal authorization for only the exact new workspace. Before cleanup, verify its recorded owner, canonical path and non-symlink boundaries; retain approved sanitized evidence locally. Never run a broad home-directory or production-path cleanup. No cleanup command is authorized here. Stop after proposed tests and reporting; deployment, service activation and production Memory writes require separate approval.
