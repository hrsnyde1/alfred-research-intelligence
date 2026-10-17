# Phase 7J execution gate

2026-10-16 — **BLOCKED.** A read-only inspection cannot certify boundaries that have never been launched. No namespace/container or copied package has been executed. Reports: PHASE7J_SANDBOX_PREFLIGHT.md and PHASE7J_TEST_HARNESS_REVIEW.md.

## Gate 0 — required before any future launch

Owner approves a bounded sandbox-only probe, without Memory/Research package transfer. Review exact launcher/probe bytes/hash, approved runtime mount allowlist, resource controls and result location. No policy weakening, privileged launch, host service access or implicit fallback. AppArmor loaded-profile listing was permission-denied; leave unresolved or obtain component-owner policy evidence, never bypass it. Docker CLI is not an approved execution authority; inaccessible socket is not grounds to change groups/permissions.

## Gate 1 — launcher and runtime checks (future authorization only)

1. `readlink /proc/self/ns/{user,mnt,net,pid,ipc,uts}` inside probe must differ appropriately from recorded host IDs; private proc must contain only sandbox process tree. No host PID sharing or host descriptors retained. CapEff=0 and NoNewPrivs=1 in test child; prevent mount/setns escape with reviewed capability/seccomp controls.
2. Inspect sandbox mountinfo: only approved runtime files, source read-only, selected public fixtures, private /proc and /dev, private tmpfs, result-only writable paths. No host-root/home/opt/run/var/docker/credential/vault exposure. Synthetic account fixture must make pwd/getgr lookups local and correct; do not expose host passwd/shadow or NSS network providers. Merged-/usr symlinks and any required /bin/sh path must resolve only within allowed runtime.
3. Verify private network interfaces/routes, private loopback test listener and private Unix fixture; no host network or sockets. No production API probes. Check deny behavior against a separately approved synthetic outside-sandbox canary, never a real service. No external route/DNS/host networking should be available to Python or any subprocess.
4. Verify source write denial using a sacrificial COPY sentinel, and result write success only in new workspace result location. Temp SQLite, files and sockets resolve to private tmpfs. Host production paths must be absent/inaccessible without reading their contents. Symlink traversal/mount escape checks use synthetic canaries.
5. Apply and verify bounded process-tree memory, process count, CPU, output and wall time before workload. Proposed review values: aggregate memory 1 GiB, max 64 processes, at most 1 CPU, wall 240 s/run with 5 s kill grace, per-process file size 16 MiB, no core dumps, fd soft/hard 256. These are proposals, not owner-approved configuration. Validate against fixtures; aggregate controls cannot be replaced by per-process AS/CPU limits alone. Current session cgroup files are not writable; an approved delegated runtime/isolated VM may be required. Never change production cgroup controls.
6. Timeout/forced-exit probe must terminate all sandbox children and leave no services/listeners. Limits apply also to Node/Python descendants. tmpfs byte/inode consumption must be bounded by effective sandbox/VM resources.
7. Inside sandbox, check Python/SQLite/cryptography and genuine atomic exchange/no-replace, peer credential identity and temporary SQLite rollback/reopen using tiny synthetic probe data only. These require future execution authorization, not implied by installed symbols.

Any denial, unknown control, missing check or contradictory observation keeps gate BLOCKED. Do not use the earlier bwrap command verbatim until corrected/validated. No operational PASS is possible solely from utility --version output.

## Gate 2 — separately approve transfer and test harness

Only after Gate 1 passes: approve exact new workspace, 92 current source/helper hashes from PHASE7I_BLOCKER_RESOLUTION plus separately reviewed probe/harness artifacts. Rehash inputs and refuse symlinks/reuse; all 92 Mac hashes matched during Phase 7J. No archives, logs, runtime DBs, credentials, vaults or configuration transfer.

Finalize minimal synthetic account fixtures and one-case generated-public-key wrapper, preserve original source/tests. Ensure test helper import path exists before wrapper imports the test module. Review syntax and wrapper scope locally; label baseline/work raw versus adjusted runs independently. No current runnable harness or launcher is claimed validated.

## Gate 3 — future synthetic runs only

Use passed launcher and clean environment to run:

```sh
/usr/bin/python3 artifacts/staging/phase7h-memory/run_tests.py baseline
/usr/bin/python3 artifacts/staging/phase7h-memory/run_tests.py work
```

These are workload commands INSIDE the validated sandbox, never host shell commands. Run fixture-adjusted counterparts with identical approved wrapper, same inputs/runtime and separate output locations. Extension-only workload:

```sh
PYTHONPATH=/workspace/artifacts/staging/phase7h-memory/work:/workspace/src:/workspace/tests \
/usr/bin/python3 -m unittest discover \
  -s /workspace/artifacts/staging/phase7h-memory/work/tests \
  -p test_research_memory_stage.py -v
```

Require PYTHONDONTWRITEBYTECODE=1, synthetic HOME/TMPDIR, no user site/config, and verify imported Alfred modules resolve to allowlisted /workspace paths in parent and child. No services or real providers. All 23 extension tests execute/pass; original discovery remains 102/125, with explicit optional skips. Required atomic and peer cases actually execute; any skipped original reproduction stays unverified. Distinguish raw installed-fixture error from fixture-adjusted result. Compare exact failure/error/skip sets, tracebacks, input hashes and source integrity, not counts alone.

## Stop and rollback boundary

Any new work-only failure, identity mismatch, changed input/source, external interaction attempt, unsafe mount, resource breach or ambiguous outcome blocks testing/acceptance; retain sanitized evidence and terminate only new sandbox processes. No service rollback is expected because no production changes are permitted. Cleanup of newly created workspace requires separate path-specific approval. Passing synthetic staging does not approve Linux deployment, production Memory promotion or real credential grants.

## Current disposition

Installed bwrap is a candidate; unprivileged policy permission, functioning namespaces and aggregate limits remain unverified. Existing AppArmor restrictions and nondelegated cgroup access are substantive unresolved controls. Therefore **BLOCKED for Memory staging execution**. Minimum next step: separately approve a sandbox-only dynamic smoke test with a reviewed exact launcher/resource mechanism, or select an independently isolated Linux test host. This phase has not transferred or run the Memory package.
