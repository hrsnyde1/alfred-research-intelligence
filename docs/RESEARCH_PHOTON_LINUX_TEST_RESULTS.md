# Standalone Research Photon Linux test results

2026-10-16. **PASS — 17/17 approved connector tests passed, zero failed/skipped.** This is isolated synthetic Linux compatibility, not installation, live authentication, messaging or Hermes task integration.

## Candidate and integrity

Reviewed the three requested connector reports, exact staged connector/CLI/reused ResearchProject and17-test inventory. All eight local inventory entries match SHA256.json; no product/test changes were made for this run. Transferred only four reviewed .mjs files, original SHA256.json and independent TRANSFER_MANIFEST.json. Proposed service units, synthetic policy and historical Mac test log were not transferred or executed.

Collision-free Linux stage: `/home/alfred/research-staging/research-photon-20261016-zex17ike`. Six regular files, UID1000, directory0700/files0600, no extras/symlinks. Independently reverified after tests. Original manifest SHA256: `69d81db5e6444455fab5c5f8ba6fded94227ffb2f58cff793e81c40b470afe06`. Transfer manifest SHA256: `5deb7efa2fcd9ecfe243fd1679b3a069687ead86bb6004b0f197c19ce475101e`. Original manifest includes untransferred proposal/log files; TRANSFER_MANIFEST.json defines the exact selected subset, not the full original inventory.

| Transferred reviewed file | SHA-256 |
|---|---|
| connector.mjs | ad4c96df541dae51dcc0403cc13ffed1fe6f6596ce580cd34e830951ca77b9cf |
| connector.test.mjs | dd3b2a602261dc0cb6ef1e26fa838b98ea66cc7a5ded998244ae7930520058b6 |
| main.mjs | 701effc123e997ac6b328921b51f89117aa4f4742ade6de23daa500f8db5aba9 |
| research-project.mjs | ea65df22546e19233bb79e976aaf366470fb3fb5d197c1c40c006a9aa9cb6e96 |
| SHA256.json | 69d81db5e6444455fab5c5f8ba6fded94227ffb2f58cff793e81c40b470afe06 |

Complete audit commands, supervisor, manifests, stdout/stderr, pid/start identities and postchecks: `artifacts/audits/research-photon-linux-20261016/`. No credentials, active configuration, service sockets, message histories or runtime state copied. Source stays read-only; synthetic persistent state is private tmpfs and disappears at sandbox exit.

## Runtime and SDK scope

Linux Node v26.7.0 at `/home/alfred/.hermes/tools/node-26.7.0-linux-x64/bin/node`, SHA256 ad19784f7e90ba789a099eccba77ede8dc90a778c424f1c10a70fed3ff903fdc. Python supervisor3.12.3. All15 prior pinned host inputs match before transfer, before/after execution and independent postcheck: four original bridge/Hermes inputs, nine Spectrum public source/package/type files, Node binary and libffi. Spectrum facade/core/imessage package metadata/source remains12.7.0.

Connector fake-mode imports only Node builtins and local modules; enabled SDK factory is injected. No real Spectrum module or client was imported/initialized in the test sandbox. Installed SDK version/source compatibility is pinned static evidence; full transitive runtime import/credential/service deployment compatibility is still not qualified. Do not report17 passes as a live SDK login test.

## Accepted isolation reused

Unchanged accepted supervisor, namespaces, cleanup, file-library mounts and resource ceilings. Only old bridge source-tree mounts were replaced by a single read-only mount of this six-file standalone stage at /release. No SDK directory mount was enabled. Flags: unshare-all/user, disable-userns, die-with-parent, new-session, cap-drop ALL, clearenv; private proc/dev and read-only root. Node and Python executable/stdlib plus selected individual system libraries only. Libraries: loader, atomic,dl,m,stdc++,gcc_s,pthread,c,z,expat,ssl,crypto,ffi. No broad /lib directory bind.

Pinned libffi: /lib/x86_64-linux-gnu/libffi.so.8 resolves to /usr/lib/x86_64-linux-gnu/libffi.so.8.1.4; digest00f593fe192f2851b8ce23b25cec2488d769beb5a8f63e8c9e563071e1075153 verified. Python socket/ctypes isolation checks passed; blocked host-loopback probe used a temporary supervisor-owned listener, never a production socket; TEST-NET connection blocked. Probe listener closed. Host /home,/opt,/run,/var,/etc,/root absent; no token/secret/Photon/SSH-agent environment; separate user/mount/net/PID/IPC/UTS namespaces, NoNewPrivs, no effective caps, nested user namespace denied. Isolated writable /tmp32MiB,/workspace16MiB, synthetic HOME/TMPDIR only.

Limits hard=soft: CPU15s/process, virtual AS64GiB/process, NPROC128 shared UID guard, file8MiB, NOFILE128, core0. Node --jitless --max-old-space-size=64, UV_THREADPOOL_SIZE2, test isolation none/concurrency1. Test wall45s and monitored output1MiB per stream. Two forced preflight timeouts2s. Tests include one bounded disabled CLI child (2s spawn timeout); all children remain in the PID namespace/limits. AS is not RSS, NPROC is not a dedicated cgroup, rusage is outer waited-process maxrss, not aggregate memory. No cgroup/AppArmor changes.

| Case | Exit | Wall seconds | Waited-process maxrss KiB | Remaining identities |
|---|---|---|---|---|
| ISOLATION_TIMEOUT_PREFLIGHT | -9 | 2.030321 | 162688 | [] |
| NODE_RUNTIME_TIMEOUT_PREFLIGHT | -9 | 2.027160 | 162688 | [] |
| STANDALONE_CONNECTOR_TESTS | 0 | 0.303755 | 162688 | [] |
| ENTRYPOINT_SYNTAX | 0 | 0.086384 | 162688 | [] |

Forced -9 preflight exits are expected timeout successes. pidfd/start-identity tracking, subreaper and PID namespace teardown left no tracked process. Phase SSH exits all0; stderr files empty. No isolation widening or test substitution.

## Exact execution

Each phase used:

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B -'
```

stdin scripts in order: preflight.py, transfer.py, run_validation.py, postcheck.py under the audit directory. All executed script bytes are retained locally; supervisor was delivered through stdin, not an extra transferred executable. The supervisor records exact Bubblewrap argv for every case. Inner approved test command:

```sh
/runtime/node --jitless --max-old-space-size=64 --test --test-isolation=none --test-concurrency=1 /release/connector.test.mjs
/runtime/node --jitless --max-old-space-size=64 --check /release/main.mjs
```

Node runner17tests/17pass/0fail/0skip, duration172.840447ms. Exact17 names and full output are in linux-tests.jsonl. Tests cover disabled/no credentials, independent explicit Research factory, missing/wrong credentials, missing binding, durable pending correlation/replay, forged sender/line/conversation, conflicting replay, explicit Research outbound/dedupe, changed operation conflict, restart dedupe, independent auth failure, production intake seam refusal, UNKNOWN no-resend, scoped identities, actual disabled CLI without SDK, protected credential symlink rejection. No unrelated suites run.

## Postcheck and limits

All15 host hashes and all transferred bytes unchanged; no production source installation. Personal Photon PID140714 and Hermes PID454732 remain active/running, matching earlier recorded IDs. No service restart/config modification, actual credential access, messaging or route changes. The independent postcheck verified private ownership/permissions and six-file exact inventory. Stage retained for owner review; temporary output handles/namespace storage closed/removed.

No Linux-specific defect in tested scope. Basic task intent is a durable PENDING_INTAKE correlation, not a created Research task or acquired packet digest. Intake remains unavailable for live host dispatch; no synthetic event becomes production-trusted. Service resource/mount semantics, real credentials/project membership/line provenance and existing-Hermes attachment are separate gates in RESEARCH_PHOTON_LINUX_INSTALLATION_GATE.md.
