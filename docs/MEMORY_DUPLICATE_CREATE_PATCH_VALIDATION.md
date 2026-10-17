# Minimal Memory duplicate-create correction — validation

2026-10-16. **PASS — standalone patch prepared and validated; ready for owner-controlled installation review. Installation has not occurred.**

Reviewed [Phase 7U decision](PHASE7U_MEMORY_RELEASE_DECISION.md) and [inventory](PHASE7U_MINIMAL_CHANGE_INVENTORY.md). Only the existing Memory duplicate response changes. No Research module, endpoint, schema, grant, dependency or Obsidian source change is included.

## Patch and source identities

Artifact directory: `artifacts/releases/alfred-memory-duplicate-create-0.1.0-rc1-20261016`.

| Item | SHA-256 |
|---|---|
| Original installed/tested store.py (29,402 bytes) | `5ca002bd93e486875191292c21ba782fb2df5eb3fa4d525654e80ad29069cf8c` |
| Patched store.py (29,426 bytes) | `0d84c9c12c0715f14be7729a5007073ebc99f55fa7820e6bed81a55834d969c1` |
| duplicate-create-review-state.patch | `0b25c3b80d2c5878ed6a1b9f76a9f638b58e17ade7717bdb08e4e8e2566a3a4a` |
| focused_tests.py | `0c752c3ee14bb54a4f62a1ffa939491857fd87757e07e49c9aa94a8ca37f901c` |
| validate_linux.py | `a90987c60544423bda132e5617e3938f1b23981c6e3f94875620ee6c8424f66c` |

The complete patch changes two lines in `focused_v1/store.py`: select existing `review_state` with the original row, then return `prior["review_state"]` instead of literal `"approved"`. Response keys, provenance/identity/assignment checks, nonduplicate approval logic and database writes are unchanged. There is no duplicate-branch UPDATE. No migration, backfill, schema-version change or production data correction is required. An approved original row with a pending edit remains approved; replay does not approve the edit.

## Fresh installed baseline

Read-only SSH confirmed `/opt/alfred-obsidian-v1/current` still resolves to `/opt/alfred-obsidian-v1/releases/4d5ba29bd3027e74c808a8feaf1b5dadfded22f0`. All 34 reviewed installed source files matched their pinned bytes/digests. The previously staged 17-file source inventory and checksum manifest also matched in the initial read-only comparison. Baseline store hash is the original digest above. Installed Memory remained active/running before and after validation.

Release top-level entries are `bin`, `source`, `venv`; service metadata shows User/Group `alfred-memory` and WorkingDirectory `/opt/alfred-obsidian-v1/current/source`. No unit/environment configuration, process arguments, credentials, database, logs or vault content was read. This metadata does not establish effective launcher/import resolution or application health; owner approval must resolve those before switching current. The 34-file allowlist is not a full installed-release/consumer audit.

## Clean patch application

The supervisor created a collision-free 0700 temporary directory `/home/alfred/research-staging/memory-duplicate-validation-4nmhsdtw`. It copied only installed `focused_v1/__init__.py` and `focused_v1/store.py` into separate baseline/patched trees (0600 files), and streamed the patch into the temporary directory. No installed source was mounted or imported in tests.

Exact application arguments, with `TMP` denoting that recorded temporary directory:

```sh
/usr/bin/patch --batch --forward --fuzz=0 -p1 --input "$TMP/duplicate-create-review-state.patch" --dry-run
/usr/bin/patch --batch --forward --fuzz=0 -p1 --input "$TMP/duplicate-create-review-state.patch"
```

Both ran with cwd `$TMP/patched`, exit 0, empty stderr, no fuzz/offset; resulting source matched the reviewed patched digest exactly. The patched tree contained only the two intended source files, with no backup/reject file. After tests, a reverse application in this disposable copy exited 0 and restored the original hash. No production reverse patch was applied.

## Exact focused tests and results

Each case ran separately in a fresh sandbox. The exact class prefix is `__main__.DuplicateCreateFocusedTests.`. The first two methods retain the existing staging test method assertions, extracted statically and bound to a minimal MemoryStore fixture; the Research test module/ResearchStage/Research codecs were never imported. The other four are new, narrowly scoped synthetic regression checks, not a discovery run or certification of the wider suite.

| Exact test identifier | Baseline exit | Patched exit | Patched test seconds | Patched wall seconds | Patched peak RSS KiB |
|---|---:|---:|---:|---:|---:|
| `__main__.DuplicateCreateFocusedTests.test_duplicate_create_actual_pending_rejected_approved` | 1 | 0 | 0.017660 | 0.374300 | 29668 |
| `__main__.DuplicateCreateFocusedTests.test_duplicate_create_preserves_pending_edit_and_authorization` | 0 | 0 | 0.014928 | 0.416295 | 29712 |
| `__main__.DuplicateCreateFocusedTests.test_initial_approval_and_review_transition` | 0 | 0 | 0.021945 | 0.395150 | 29676 |
| `__main__.DuplicateCreateFocusedTests.test_provenance_task_and_revocation_denials_no_writes` | 0 | 0 | 0.030372 | 0.395099 | 29696 |
| `__main__.DuplicateCreateFocusedTests.test_deleted_source_and_held_suppression_not_reintroduced` | 0 | 0 | 0.032544 | 0.396903 | 29796 |
| `__main__.DuplicateCreateFocusedTests.test_schema_and_duplicate_response_contract_no_mutation` | 0 | 0 | 0.013812 | 0.417349 | 29744 |

**Patched: 6/6 passed, 0 failures, 0 errors, 0 skips. Baseline: 5 passed, 1 expected failure, 0 errors/skips.** Baseline review-state test failed only at its initial pending assertion (`'approved' != 'pending'`), so its subsequent rejected/approved checks did not run. The patched case completed all three. Baseline was not relabeled as green. SSH supervisor exit 0 means all expected outcomes/integrity checks passed.

Patched tests used 0.131261 seconds test runtime, 2.395097 seconds total sandbox wall, 1.760406 seconds interpreter self CPU; peak patched RSS 29,796 KiB. All 12 application invocations used 4.746329 seconds sandbox wall; maximum application self RSS 29,948 KiB. These are self statistics, not aggregate cgroup accounting. No Linux-specific defect was observed in the patched scope.

The checks cover accurate pending/rejected/approved duplicate values without row changes; pending replacement preservation and original-principal denial; initial approval and real owner approval transition; provenance/content/task mismatch, invalid synthetic token and revoked assignment denial without writes; deleted source refusal and held-row suppression preservation; response shape, all synthetic table/schema/ledger equality across an approved duplicate, schema version 3 and absence of Research tables.

Obsidian source hashes are unchanged. No Obsidian export or real vault test was executed, and full client/Obsidian integration compatibility is not certified. Broader inherited regressions and consumer behavior remain owner acceptance considerations, not silently counted as passes.

## Isolation, resource limits and cleanup

The established Bubblewrap controls were reused with a smaller code exposure: only the selected two-file temporary baseline or patched tree is read-only mounted at `/code`. Python executable/stdlib and the exact 85 pinned runtime/native/cryptography files are read-only mounted; no Research input is mounted. Complete actual argv and probe mountinfo are preserved in `linux-validation.stdout.txt`; the authoritative argv builder is `validate_linux.py`.

Private user/mount/network/PID/IPC/UTS namespaces, disable-userns, no capabilities, NoNewPrivs, cleared environment, private /proc and synthetic /dev passed preflight. Host `/home`, `/opt`, `/run`, `/var`, `/etc`, `/root`, service sockets, SSH_AUTH_SOCK, production Memory/Hermes/Photon/Obsidian/Development paths were absent. A probe-owned host-loopback listener and TEST-NET address were unreachable; no production endpoint was probed. Runtime was Python 3.12.3, cryptography 41.0.7 and OpenSSL 3.0.13.

Per-process hard=soft limits: CPU 10 seconds; address space 268,435,456 bytes; file size 8,388,608 bytes; descriptors 64; shared-UID NPROC 128; core 0. Wall watchdog 20 seconds/case; output ceiling 1 MiB/stream; campaign deadline 300 seconds. `/tmp` and `/workspace` each private 16,777,216-byte tmpfs; `/code` and root read-only. Bounded address-space/file enforcement, SQLite/AES synthetic round-trips and read-only checks passed. No cgroup/AppArmor modification or aggregate guarantee was assumed; the finite tests create no application child-process workload.

The sleeping synthetic preflight hit the actual 20-second watchdog (20.033749 seconds), raw exit -9; exact launcher pidfd kill and namespace teardown left no tracked PID:starttime identities. All application cases likewise ended with `remaining_tracked=[]`; no account-wide/process-name signaling. Copies remained unchanged throughout tests. Temporary staging and patch were removed by TemporaryDirectory cleanup. Final rehash verified all 34 installed source files plus 85 pinned runtime files unchanged (119 total). No source baseline was modified, no production API/DB/vault/credential was accessed, and no service restart, migration, package installation, Research activation, commit/push or deployment occurred.

## Reproducible commands and evidence

Executed from the Mac repository (stdin scripts streamed; not installed remotely):

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B -' < /tmp/phase7t_inspect.py > /tmp/memory-minimal-baseline.json
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B -' < artifacts/releases/alfred-memory-duplicate-create-0.1.0-rc1-20261016/validate_linux.py > /tmp/memory-minimal-validation.out 2> /tmp/memory-minimal-validation.err
```

The first script is preserved as `recheck_installed.py`; initial local sandbox SSH denials exited 255 before remote execution, then approved retries exited 0. Validation stderr is empty. Read-only layout inspection used pathlib directory entry metadata and `systemctl show alfred-memory-v1.service --property=ActiveState,SubState,WorkingDirectory,User,Group,FragmentPath --no-pager`; output is preserved in `installed-layout.txt`.

Raw stdout, JSON results, installed comparison, exact supervisor and harness are in the artifact directory. [Owner procedure](MEMORY_DUPLICATE_CREATE_OWNER_INSTALLATION.md) contains future commands only; none were executed. Stop after this candidate validation and await owner review.
