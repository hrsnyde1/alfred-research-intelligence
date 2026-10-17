# Photon Node compatibility execution plan

2026-10-16. **Proposal only; no Linux test or transfer executed.** Runtime found: service-launch Node v26.7.0, SHA-256 ad19784f7e90ba789a099eccba77ede8dc90a778c424f1c10a70fed3ff903fdc. Use it read-only in a sandbox as UID 1000. No permission change, protected executable copy, package installation or Personal service action is needed.

## Required input inventory and staging approval

Owner must separately authorize a collision-free Linux directory beneath /home/alfred/research-staging/. Do not guess an existing path or overwrite any prior stage. Before transfer, freeze a complete file/hash manifest and verify it independently after transfer. No transfer is authorized here.

Inputs needed:

- Reviewed baseline/ and modified/ trees and bridge.patch from staging/photon-linux-compatibility-v1, verified against staging/photon-two-project-v1/SOURCE_INVENTORY.json. Three modified and two added production candidates; send-format.mjs remains unchanged evidence.
- Exact original test_guard.py (10 tests), research-project.test.mjs (11 tests) and sdk-source.test.mjs (2 tests).
- Nine previously copied public SDK entry/package/type files under linux-sdk/ for source-comparison tests, matching SDK_SOURCE_HASHES.json.
- A frozen synthetic Linux isolation preflight and bounded process-tree supervisor, reviewed against Phase 7L/7R pidfd/subreaper cleanup procedure. Freeze their hashes before authorizing execution; do not treat prose as an installed launcher.
- For a separate **import-only** SDK closure case, installed sidecar node_modules read-only at /runtime/node_modules. Review/hash the code tree and symlinks first; reject credential/state files or links outside the approved package tree. Do not run npm, postinstall scripts, the installed sidecar entrypoint or Spectrum(). No SDK copy/install is necessary.

Do not transfer the Mac-specific test_no_credentials.py unchanged: its home-directory denial expectation is platform-specific. Replace it with reviewed Linux namespace/environment/host-path assertions, not a weakening of controls. Full installed Hermes imports require additional explicit source/dependency inventory and authorization; the ten guard tests use fake interface modules and AST extraction, not a full Hermes boot.

## Isolation and ceilings

One serial sandbox per case. Reuse verified Bubblewrap user/mount/network/PID/IPC/UTS isolation, --die-with-parent, --new-session, no capabilities, clear environment and closed inherited descriptors. No host /home, /opt, /etc, /run, /var, credentials, sockets or production data mounts. Only the selected runtime file, exact library files, Python standard library, reviewed test/code trees and optional SDK code tree are read-only mounted. Root remounted read-only; synthetic /dev and private /proc. /tmp 32 MiB and /workspace 16 MiB private tmpfs; no host-backed writable test mount. HOME=/tmp/home, TMPDIR=/tmp. No credential references or Research-enabled flag in host/sandbox environment.

Proposed hard=soft limits: CPU 15 seconds/process; virtual address space 64 GiB/process; file size 8 MiB/file; NOFILE 128; CORE 0; NPROC 128 retained only as a shared-real-UID guard. Node old heap max 64 MiB; jitless mode; UV_THREADPOOL_SIZE=2. The 64 GiB virtual ceiling accommodates V8 reservation conservatively but is **not** a 64 GiB RSS grant or aggregate memory limit. Node threads/native allocations are not bounded by old heap alone. First preflight must measure virtual/RSS use under these limits; if Node cannot start, stop without widening limits or switching runtimes. Aggregate controls remain an owner gate if measured resource use or process behavior exceeds the bounded reviewed workload.

Node test runner: --test-isolation=none and --test-concurrency=1, avoiding test-file child processes. Tests themselves use finite fake transports and no arbitrary subprocesses. Python guard tests do not spawn children. One SDK import-only process is separate from fake tests. Stop on timeout, skip, mismatch, unexpected process count, resource failure or any attempt to authenticate. No broad suite discovery outside these explicit files.

45-second wall deadline/case; at most four cases, 180 seconds plus bounded cleanup. Supervisor must use exact pidfds/start identities and private PID-namespace teardown as already proven in Phase 7L/7R, monitor stdout/stderr at 1 MiB each, kill only its own tracked process tree on deadline, wait/reap within 3 seconds and prove identities gone. Never pkill/killall or account-wide cleanup. A GNU timeout/prlimit invocation alone is not substituted for the verified cleanup supervisor. No tests begin until a forced-timeout synthetic preflight verifies cleanup with Node's finite threads.

## Exact proposed inner commands

These are command arrays to the approved supervisor, not instructions to run them now. The outer supervisor applies the resource ceilings/deadline above. Set APPROVED_STAGE only to the later hash-verified owner-approved directory. No such Linux stage is allocated in this task.

```sh
NODE=/home/alfred/.hermes/tools/node-26.7.0-linux-x64/bin/node
# APPROVED_STAGE must be supplied by the owner-approved staging transfer.
: "${APPROVED_STAGE:?no approved Linux staging directory}"
test -d "$APPROVED_STAGE"
printf '%s  %s\n' ad19784f7e90ba789a099eccba77ede8dc90a778c424f1c10a70fed3ff903fdc "$NODE" | sha256sum -c -
```

Build the following Bubblewrap array inside the reviewed supervisor (Python list, no shell expansion). Libraries are exact read-only files; verify each resolved path/hash first. No directory-wide /lib or /usr mount:

```python
NODE = '/home/alfred/.hermes/tools/node-26.7.0-linux-x64/bin/node'
LIBS = ['/lib64/ld-linux-x86-64.so.2'] + [
    '/lib/x86_64-linux-gnu/' + name for name in (
        'libatomic.so.1','libdl.so.2','libm.so.6','libstdc++.so.6',
        'libgcc_s.so.1','libpthread.so.0','libc.so.6',
        'libz.so.1','libexpat.so.1','libssl.so.3','libcrypto.so.3')]
# STAGE comes from the separately approved verified transfer manifest.
bw = ['/usr/bin/bwrap','--unshare-all','--die-with-parent','--new-session',
      '--cap-drop','ALL','--clearenv','--dir','/runtime','--dir','/release',
      '--ro-bind',NODE,'/runtime/node',
      '--ro-bind','/usr/bin/python3.12','/usr/bin/python3.12',
      '--ro-bind','/usr/lib/python3.12','/usr/lib/python3.12']
for lib in LIBS:
    bw += ['--ro-bind',lib,lib]
for tree in ('baseline','modified','tests','linux-sdk'):
    bw += ['--ro-bind',str(STAGE/tree),'/release/'+tree]
bw += ['--proc','/proc','--dev','/dev',
       '--size','33554432','--tmpfs','/tmp',
       '--size','16777216','--tmpfs','/workspace',
       '--dir','/tmp/home','--setenv','HOME','/tmp/home',
       '--setenv','TMPDIR','/tmp','--setenv','UV_THREADPOOL_SIZE','2',
       '--chdir','/release','--remount-ro','/']
node = ['/runtime/node','--jitless','--max-old-space-size=64']
# Case A: reviewed Linux isolation/forced-timeout preflight, then Node version
# and source-only syntax checks; exact preflight launcher is a freeze gate.
version_case = bw + ['--'] + node + ['--version']
# Case B: 11 bridge tests + 2 copied SDK source checks (13 expected).
node_case = bw + ['--'] + node + ['--test','--test-isolation=none',
    '--test-concurrency=1','/release/tests/research-project.test.mjs',
    '/release/tests/sdk-source.test.mjs']
# Case C: exact 10 Python guard/Personal compatibility tests; no Mac probes.
python_case = bw + ['--','/usr/bin/python3.12','-I','-S','-B','-m','unittest',
    'discover','-s','/release/tests','-p','test_guard.py','-v']
# Case D: optional SDK import-only closure, after separate package inventory.
# Insert this bind BEFORE --remount-ro and --: SDK_MODULES is the verified
# /home/alfred/.hermes/hermes-agent/plugins/platforms/photon/sidecar/node_modules.
sdk_bw = bw[:-2] + ['--ro-bind',str(SDK_MODULES),'/runtime/node_modules'] + bw[-2:]
sdk_case = sdk_bw + ['--'] + node + ['--input-type=module','-e',
    "const a=await import('/runtime/node_modules/spectrum-ts/dist/index.js');"
    "const b=await import('/runtime/node_modules/@spectrum-ts/imessage/dist/index.js');"
    "if(typeof a.Spectrum!=='function'||typeof b.imessage!=='function')process.exit(1);"
    "console.log('SDK IMPORT ONLY; NO PROJECT INITIALIZATION');"]
```

The SDK import assertion must be checked against exact exports before freezing its launcher; do not invoke a factory to test an export. Module import may initialize library code, so it runs only with network denied and no secrets/host paths. Stop if any additional library is needed; review the exact dependency and mount, never broaden to host root. Reconfirm Node hash, SDK hashes and installed baseline before/after all cases.

## Acceptance and next action

Runtime closure is established by the service-launch path, executable/version/hash and compatible installed engine declarations. Linux test execution is still unperformed. Accept the later run only if all expected tests pass, original Personal compatibility assertions remain intact, Research factory stays disabled except synthetic injected configurations, no project credentials enter any process, IDs/ledgers remain separate, unknown outcomes never resend, and namespace/process cleanup is evidenced.

**Minimum next owner action:** authorize freezing the small launcher/preflight and transfer inventory, then a separately authorized bounded Linux compatibility run using the existing v26.7.0 binary. No Node copy/install or permission change. Remaining production approvals are unchanged: protected configuration, genuine intake authority, full host integration, coordinated installation/restart/rollback and controlled messaging. Research remains disabled.
