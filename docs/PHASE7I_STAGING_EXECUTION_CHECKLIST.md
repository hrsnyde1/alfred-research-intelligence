# Phase 7I staging execution checklist

Documentation only, 2026-10-16. No commands below were executed. Supersedes the broad writable-source mount and full-Research-source transfer suggestions in the earlier execution plan. Existing files/hashes: 92-file allowlist in PHASE7I_BLOCKER_RESOLUTION.md. No Linux transfer or staging execution authorized by this document.

## 1. Approval and input gates

- Review reconstructed Phase 7H reports and current 92-file allowlist. Approve transfer of only these existing files, not an archive, runtime state or recursive repository copy.
- Approve reduced integration coverage: four Node cases may skip; PDF case may skip only if actual `pymupdf` import is absent. Do not claim skipped original failures fixed. No installation required for 23 extension tests.
- Approve one narrowly scoped synthetic public-key test harness, described below, applied identically to baseline/work; source and original test files remain unchanged.
- Approve private workspace creation, namespace preflight and bounded synthetic test execution, including ephemeral loopback HTTP/Unix fixtures. Production service starts, production network, /opt keys, vaults and host sockets remain forbidden.
- Proposed workspace `/home/alfred/research-staging/phase7i-memory-20261016` must be absent and non-symlink; verify parent owner/path first. After separate authorization, create parent if absent and leaf with umask 077, mode 0700. Refuse reuse rather than deleting/overwriting. Prepare a private results directory inside leaf.
- Transfer and hash-check exactly 92 files, preserving repo-relative layout. Baseline 34 original hashes must match BASELINE_MANIFEST.json. No imports from live /opt code or site-installed Alfred packages. Record runtime and fresh input hashes with outputs.

## 2. Sandbox preflight — mandatory before any copied test

Existing mechanism: `/usr/bin/bwrap`, previously observed installed, not proven functional or approved for this workload. AppArmor restricts unprivileged user namespaces. Do not disable AppArmor, change sysctls, sudo, or fall back to unsandboxed alfred execution. A writable same-user directory is insufficient. If sandbox preflight fails, stop and request an independently approved isolated VM/container; no deployment-host changes.

Validate library bind paths and symlink resolution before use. Namespace identities for network, mount and PID must differ from host (record host namespace inode metadata only). Sandbox has no host /home, /opt, /run, /var or credential environment; mounts expose only reviewed runtime paths and copied code. All source/test paths must be read-only; output directory and staging parent for saved runner logs are the only persistent writable host paths. Temp databases, synthetic vault trees and sockets live on private /tmp tmpfs. Use private /proc, /dev and IPC/PID/network namespaces, kill namespace children on timeout/exit.

Run bounded checks INSIDE sandbox, with only synthetic data:

1. Verify private namespace IDs, no external interfaces/default route, loopback available. Start a private ephemeral loopback listener and prove it works; no connection to host production ports. Check isolation using namespace/mount evidence, not probing live services.
2. Assert `/opt`, `/home/alfred`, production `/run` sockets and `/var` are absent; env contains only explicitly allowed variables. Enumerate sandbox mounts to verify no accidental home/root bind.
3. Attempt a write to a sacrificial COPY source-path sentinel: must fail read-only. Persistent test results must write only approved workspace output paths; temp files must resolve under private /tmp. No checks write production paths.
4. Create small synthetic files within private /tmp and invoke copied Linux atomic rename/exchange/no-replace helpers. Verify exchange and no-replace collision behavior, not just libc symbol existence. Any failure blocks race-test coverage.
5. Use a private socketpair and SO_PEERCRED; verify returned pid/uid/gid against namespace process identity. Do not weaken uid checking for a sandbox mismatch. Private AF_UNIX filesystem socket binding must succeed.
6. Open a synthetic SQLite database, commit/reopen/read back, exercise rollback and concurrent connection handling. Confirm Python 3.12.3, SQLite 3.45.1 and installed cryptography import inside sandbox. Check `pymupdf` and Node inside the actual sandbox (not just host PATH).
7. Import transferred fixture helper/staging module with controlled PYTHONPATH; assert all Alfred module `__file__` paths resolve under /workspace. Missing static-closure dependency is a blocker; revise allowlist on Mac and obtain approval, never import live production code.

Preflight scripts are not yet implemented or executed. Review/hash any such script before transfer. A generic namespace command success alone does not satisfy these seven checks.

## 3. Proposed sandbox command

After approvals, filesystem preparation, library-path review and preflight only. Set `STAGE` to exact approved workspace, refusing symlinks/existing unknown contents. Commands are templates pending host preflight, not verified launchers. `--unshare-all` supplies private networking to Python AND child processes; the old Python connect guard is defense in depth only. No host-root mount is used.

```sh
STAGE=/home/alfred/research-staging/phase7i-memory-20261016
MEM=artifacts/staging/phase7h-memory
/usr/bin/timeout --kill-after=5 240 /usr/bin/bwrap \
  --unshare-all --die-with-parent --new-session \
  --ro-bind /usr /usr --ro-bind /lib /lib --ro-bind /lib64 /lib64 \
  --dir /etc --ro-bind /etc/skel /etc/skel \
  --proc /proc --dev /dev --tmpfs /tmp \
  --bind "$STAGE" /workspace \
  --ro-bind "$STAGE/src" /workspace/src \
  --ro-bind "$STAGE/tests" /workspace/tests \
  --ro-bind "$STAGE/$MEM/baseline" "/workspace/$MEM/baseline" \
  --ro-bind "$STAGE/$MEM/work" "/workspace/$MEM/work" \
  --ro-bind "$STAGE/$MEM/run_tests.py" "/workspace/$MEM/run_tests.py" \
  --ro-bind "$STAGE/$MEM/BASELINE_MANIFEST.json" "/workspace/$MEM/BASELINE_MANIFEST.json" \
  --chdir /workspace \
  /usr/bin/env -i PATH=/usr/bin:/bin HOME=/tmp TMPDIR=/tmp \
  PYTHONDONTWRITEBYTECODE=1 \
  /usr/bin/python3 artifacts/staging/phase7h-memory/run_tests.py baseline
```

Capture exit code even when nonzero; 124 indicates timeout, not assertion failure. Preserve raw JSON/transcript/stderr in workspace results under `raw-baseline/` before running again. Repeat with final argument `work`, preserving `raw-work/`. Expected raw missing fixture error is evidence of isolation, not permission to expose production key files. Do not overwrite Mac results or earlier Linux run evidence. Existing child limit is 180 seconds; outer timeout bounds descendants; confirm namespace teardown.

For extension-only run, use same sandbox prefix/environment, controlled PYTHONPATH `/workspace/artifacts/staging/phase7h-memory/work:/workspace/src:/workspace/tests`, and:

```sh
/usr/bin/python3 -m unittest discover \
  -s /workspace/artifacts/staging/phase7h-memory/work/tests \
  -p test_research_memory_stage.py -v
```

These 23 cases are mandatory and must not skip. No Node/PDF is needed. Ubuntu skeleton tests use only public pinned /etc/skel files exposed read-only.

## 4. Synthetic fixture-adjusted comparison

Review before execution. Do not modify copied files. The minimal harness can load the existing runner text in memory, inserting the following child bootstrap immediately before its exact `suite=unittest.defaultTestLoader.discover('tests',pattern='test_*.py')` line. Require exactly one insertion point; otherwise stop. Execute the resulting runner with unchanged area selection, cwd, deadlines and result recording. Run baseline/work in separate clean processes, preserve outputs under `fixture-baseline/` and `fixture-work/`.

```python
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat
import test_obsidian_disposable_delivery as fixture_tests
import obsidian_candidate.disposable_delivery as disposable
key = Ed25519PrivateKey.generate()
public = key.public_key().public_bytes(Encoding.OpenSSH, PublicFormat.OpenSSH)
del key
key_type, key_data = public.split()[:2]
expected = (b'restrict,command="' + disposable.RECEIVE_KEY_COMMAND.encode()
            + b'" ' + key_type + b' ' + key_data + b'\n')
case_type = fixture_tests.DisposableDeliveryTests
original = case_type.test_initialization_rejects_existing_keys_and_authorized_file

def isolated_public_fixture(self):
    with patch.object(disposable, '_authorized_line', return_value=expected):
        return original(self)

case_type.test_initialization_rejects_existing_keys_and_authorized_file = isolated_public_fixture
```

The existing runner child already imports `patch` from unittest.mock. This harness creates no key files and supplies only a public expected line. All original assertion, ownership, digest and mutation checks in initialize remain active. Receipt/HMAC signatures elsewhere are unaffected. Do not apply a suite-wide patch, disable signature checks, fabricate an ownership result, or use a real installed key. Report this case as fixture-adjusted, not coverage of the production public-key file loader. The harness itself is a future reviewed execution artifact; no new code file has been created by this documentary task.

## 5. Required comparisons and stop conditions

Compare exact test IDs, outcomes, skip reasons, normalized traces and durations, with baseline/work same runtime, namespace and fixture mode. Counts alone are insufficient. Original discovery should remain 102 baseline / 125 work; 23 extra cases must pass. Report raw and fixture-adjusted results separately. Assuming no other differences, absent Node adds four explicit skips (two replacing prior failures, two previously passing); absent pymupdf leaves one PDF skip. Matching Ubuntu skeleton should allow two previously skipped cases to execute. Do not prescribe pass counts before execution.

Retest all 20 inherited case IDs individually; annotate two Node-dependent failures as NOT EXERCISED if skipped. Required nonoptional Linux atomic/race and peer-credential cases must execute and pass or retain an explicit failure/blocker. If fixture substitution resolves only the public-key case, preserve that narrow conclusion. Any new work-only failure/error, missing extension case, stale hash, source mutation, namespace failure, unexpected external attempt, production path visibility, timeout or ambiguous output blocks acceptance.

Full Node/PDF integration acceptance requires an approved available runtime/parser and execution of their cases, not reclassification as passed. Reduced-coverage extension validation may proceed after owner approval without installs. Linux test outcomes do not authorize production Research promotion, HTTP route registration, Memory migration or deployment.

## 6. Separate authorization requested later

Authorize only: create exact private workspace; transfer reviewed 92 source/helper files plus separately reviewed preflight/harness if needed; verify hashes; run bounded sandbox preflight; run raw, fixture-adjusted and extension-only synthetic tests after passing all gates; collect sanitized results. No package installation, host security modification, production service access or vault/credential access. Namespace or fixture-harness failure requires stopping, not expanding permissions. Subsequent workspace removal needs separate path-specific approval; never broad recursive cleanup outside recorded workspace.
