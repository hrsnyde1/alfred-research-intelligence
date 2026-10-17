# Photon Linux isolated bridge test results

2026-10-16. **PASS — approved isolated Linux subset: 23 passed, 0 failed, 0 skipped.** Production installation/activation remains unapproved. No real Spectrum connection, provider authentication or messaging occurred.

## Original stop and authorized correction

The original attempt stopped before tests because the exact library list omitted libffi.so.8, required by Python ctypes. Original reports and logs are retained under artifacts/audits/photon-linux-bridge-20261016/ (original-blocked-*.md, preflight.jsonl, preflight.err). This retry was explicitly authorized by the owner.

Read all four requested prior reports and inspected the exact previous supervisor/diff. The only preflight correction was adding a pinned **read-only file mount** for /lib/x86_64-linux-gnu/libffi.so.8. readlink -e resolves it to /usr/lib/x86_64-linux-gnu/libffi.so.8.1.4. namei confirms root-owned system parents, the expected symlink and root-owned 0644 target. dpkg-query identifies libffi8:amd64. SHA-256 is 00f593fe192f2851b8ce23b25cec2488d769beb5a8f63e8c9e563071e1075153. The system library was not modified, copied or installed. No directory-wide system access was added. All prior isolation and resource limits were retained.

## Commands and exit codes

All SSH commands used BatchMode=yes, StrictHostKeyChecking=yes, ConnectTimeout=8, ConnectionAttempts=1 and alfred@192.168.50.81. Exact source for each invocation is retained in the audit directory. Shell commands executed from the Mac repository root:

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B -' < artifacts/audits/photon-linux-bridge-20261016/corrected-preflight.PROPOSED.py > artifacts/audits/photon-linux-bridge-20261016/retry-preflight.jsonl 2> artifacts/audits/photon-linux-bridge-20261016/retry-preflight.err
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B -' < artifacts/audits/photon-linux-bridge-20261016/transfer.py > artifacts/audits/photon-linux-bridge-20261016/transfer-result.json 2> artifacts/audits/photon-linux-bridge-20261016/transfer.err
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B /home/alfred/research-staging/photon-two-project-20261016-kk95dzvp/run_validation.py' > artifacts/audits/photon-linux-bridge-20261016/linux-tests.jsonl 2> artifacts/audits/photon-linux-bridge-20261016/linux-tests.err
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B -' < artifacts/audits/photon-linux-bridge-20261016/retry-postcheck.py > artifacts/audits/photon-linux-bridge-20261016/retry-postcheck.txt
```

Each successful remote phase exited **0**, with empty phase-error files. An initial read-only SSH sandbox denial preceded the approved library-verification retry; no remote isolation was weakened. The corrected script retains PROPOSED in its filename for historical continuity but is now the exact executed authorized preflight.

Inner commands, after the recorded Bubblewrap prefix:

```text
/runtime/node --jitless --max-old-space-size=64 --test --test-isolation=none --test-concurrency=1 /release/tests/research-project.test.mjs /release/tests/sdk-source.test.mjs
/usr/bin/python3.12 -I -S -B -m unittest discover -s /release/tests -p test_guard.py -v
```

## Preflight, bounds and cleanup

Python 3.12.3 passed namespace, no-privilege, nested-user-namespace denial, host-path absence, no credential/provider/SSH-agent environment, read-only mount and temporary write assertions. Probe-owned host-loopback listener and TEST-NET endpoint were unreachable. Listener closed in finally. User/mount/network/PID/IPC/UTS namespace IDs differ from host. Host /home, /opt, /run, /var, /etc and /root were absent. No production socket or data directory was mounted.

Node runtime was the exact verified /home/alfred/.hermes/tools/node-26.7.0-linux-x64/bin/node, version v26.7.0, SHA-256 ad19784f7e90ba789a099eccba77ede8dc90a778c424f1c10a70fed3ff903fdc. It successfully initialized V8 under the unchanged limits and reached PREFLIGHT_READY before its deliberate timeout.

Bubblewrap used unshare-all/user, disable-userns, die-with-parent, new-session, cap-drop ALL, clearenv, private proc/dev and read-only root. Only exact runtime/library files, Python stdlib and approved code/test/SDK-entry trees were mounted read-only. Private /tmp=32 MiB and /workspace=16 MiB; no host-backed writable test mount. Hard=soft limits: CPU 15 s/process, AS 64 GiB/process, NPROC 128 shared-real-UID guard, FSIZE 8 MiB, NOFILE 128, CORE 0. Node old heap max 64 MiB, jitless, UV_THREADPOOL_SIZE=2, file isolation none and concurrency 1. No limit changed to obtain a pass.

Preflight forced deadlines were 2 s; test-case deadlines 45 s. Output ceiling 1 MiB per stream. Supervisor used exact pidfds/start identities, subreaper wait/reap and private PID namespace teardown. Both forced preflights exited -9 at the expected wall deadline, with all tracked identities gone. Both actual test cases exited 0 and left no tracked identities. No account/process-name signals were used. Logs were unlinked temporary files closed at completion, and sandbox tmpfs writes disappeared with namespaces.

| Case | Exit | Wall seconds | Waited-process maxrss KiB | Remaining identities |
|---|---|---|---|---|
| ISOLATION_TIMEOUT_PREFLIGHT | -9 | 2.031923 | 162688 | [] |
| NODE_RUNTIME_TIMEOUT_PREFLIGHT | -9 | 2.025845 | 162688 | [] |
| NODE_BRIDGE_AND_SDK_SOURCE_TESTS | 0 | 0.193774 | 162560 | [] |
| PYTHON_GUARD_AND_PERSONAL_COMPATIBILITY | 0 | 0.419565 | 162560 | [] |

Resource observations are the waited outer process's rusage; they are not aggregate cgroup peak RSS or a complete whole-tree CPU measurement. The 64 GiB limit bounds virtual address space, not RSS. Finite serial tests and successful cleanup do not qualify uncontrolled multiprocess workloads.

## Transfer and integrity

Before transfer, all 15 pinned host inputs matched: four bridge baseline files, nine SDK entry/package/type files and Node, plus libffi. Spectrum source/package versions are 12.7.0. The frozen patch and three test files matched their previously recorded local digests; baseline/candidate and SDK sources matched their frozen inventories.

New collision-free destination: **/home/alfred/research-staging/photon-two-project-20261016-kk95dzvp**. Transferred 18 inventoried payload files plus TRANSFER_MANIFEST.json (19 files), with restrictive umask. Manifest SHA-256: 724545760cde654a73968d72ecbc416f70a530a503ef2648041a02beaba52c25. No active configuration, private message data or real credential was included. Test secret-like strings are explicitly synthetic fixtures only.

Copied baseline to modified inside this new stage and applied bridge.patch using /usr/bin/patch -p1; exit 0. Verified all six resulting candidate hashes. Independent postcheck proves exact 25-file stage (19 transferred plus six generated modified files), no symlinks or extras, UID 1000, directories 0700/files 0600. All transfer/candidate hashes and all 15 host input hashes remain unchanged. Stage is retained for owner review; no production path was overwritten.

| Payload path | Bytes | SHA-256 |
|---|---|---|
| baseline/gateway/run_inbound.py | 116765 | 6a1a40708075e3550a824eae5519e98db97f52ea7995154e8c7e941de4e02144 |
| baseline/plugins/platforms/photon/adapter.py | 97349 | 841ed6cb6e2d392fcec33f8983dd34fffe677c6a8d40e442bc449e66beeb16e5 |
| baseline/plugins/platforms/photon/sidecar/send-format.mjs | 1063 | 827c6c0b3a7fd3b731365ecd17bb52d65b05c9a53e67795922ec2ebb79de58fe |
| baseline/plugins/platforms/photon/sidecar/index.mjs | 51183 | ef019d1d50e4ca680aede49276181f8eff8d396d9b7c22a73bb5da2b2d7bb8e4 |
| linux-sdk/spectrum-ts/package.json | 1389 | 1e01f443648c68897507cc5babef554aca4fc4c340a9175819bdea37824905ff |
| linux-sdk/@spectrum-ts/core/package.json | 1295 | 5afa03a122341fbe4853315e15ab9d4a6f6ece6c61d7b234ec8286ee538a9da2 |
| linux-sdk/@spectrum-ts/imessage/package.json | 1096 | 9bedec8c79efebe5786a1daa341ec730501e7c9809703a7122ffd671a08455a6 |
| linux-sdk/@spectrum-ts/imessage/dist/index.js | 114927 | 9faf0be1530dde1e2f80b580d12377a1fa6b0995c3595794648237a2c8f241ee |
| linux-sdk/@spectrum-ts/imessage/dist/index.d.ts | 35270 | 06b9442709fa2832f3e1abb985291d87787dcf2c406b372cba1c59c75929f26d |
| linux-sdk/@spectrum-ts/core/dist/index.js | 138924 | 2ca2e743caadb223a77159cc39749e38d672a54c8bc249ea0fdd665b2560b8ab |
| linux-sdk/@spectrum-ts/core/dist/index.d.ts | 4558 | 9ebd5adaa5e8100a547e4bf48963ad872e89f0d52df26e621a623c8e19248ef3 |
| linux-sdk/spectrum-ts/dist/index.js | 46 | e60437a1d30c76ed3270a4208658379dcc11684afe971bfd50d6e6dd7b1a1101 |
| linux-sdk/spectrum-ts/dist/index.d.ts | 34 | ede89b7bc2b923b70c83245525ccb59f3e122f3452be14e88a9ba39aef143242 |
| bridge.patch | 16698 | 37c71715155cfef1444b8c393c4fa178ed221f0d0b63f21043c56ae9a30465ea |
| tests/test_guard.py | 9404 | de75bf46f6b8e2708776629a7ee43b48482879f95bbf583f255a331baef56d98 |
| tests/research-project.test.mjs | 5522 | 963d4088fcfe35917ef5528a7513085ef2877cc13d54313deca2c09ecc782cf9 |
| tests/sdk-source.test.mjs | 1154 | 026b80cf4604873574111f6aeae8c3c97b8b0bd9dc4d4079c148a3574a68dc8a |
| run_validation.py | 9712 | fd27d5e7c6ce480f5fd0597d95c15ef1c183972df3857d6ef3f9590c3fc15b88 |

The manifest itself is validated by its separately recorded digest above. It is not included recursively in its own entry list.

## Exact tests and counts

Node: **13 passed**, 0 failed/skipped; runner duration 72.153153 ms. Python: **10 passed**, 0 failed/skipped; unittest duration 0.236 s. Total **23 passed**: original 21 bridge tests plus two previously reviewed copied-SDK source checks.

JavaScript test names:

- disabled mode never initializes or subscribes Research
- missing credentials and reused Personal credentials deny enabled Research
- inbound project and message namespaces are independent of Personal originals
- wrong line sender or space cannot enter shared consumer
- explicit project and exact scope required for send
- cache restore pins dedicated line and duplicate logical send is accepted once
- same ACK for separate inbound operations does not collapse
- ambiguous external outcome never resends
- restart with protected durable ledger preserves project send separation
- unsupported Research media/actions deny without Personal fallback
- separate app receives only explicit Research project credentials
- copied installed SDK packages are consistently 12.7.0
- installed client selector selects exact line and rejects another project line

Python test_guard.Tests methods:

- test_adapter_dispatch_prefix_is_terminal_and_personal_tail_unchanged
- test_gateway_guard_precedes_all_ordinary_paths
- test_identity_survives_and_only_research_hook_runs
- test_installed_personal_http_payload_only_adds_explicit_project
- test_installed_personal_send_function_matches_staged_with_fake_transport
- test_missing_profile_and_disabled_mode_deny
- test_missing_unknown_and_forged_identity_denied
- test_outbound_projects_explicit_and_no_caller_override
- test_personal_initialization_and_handlers_preserved_structurally
- test_personal_route_is_untouched_and_unknown_reserved_never_falls_back

No Mac-specific isolation tests, full Hermes suites, Research regression expansion or SDK import-only closure were run. Both Spectrum connections in the tests use injected fake objects. The real SDK factory, bridge server and provider authentication were never initialized. The installed selector check evaluates only extracted pure functions from copied pinned SDK source.

## Findings and limitations

Personal initialization/handler preservation, fake transport function equivalence, explicit project tagging, disabled Research initialization, authenticated project/line/sender/scope checks, scoped IDs/caches/ledger, duplicate/conflict handling, unknown-outcome no-resend, restart replay and terminal Research failure all passed on Linux. No Linux-specific defect appeared within this subset.

This is synthetic bridge compatibility, not end-to-end active Hermes/Photon qualification. Full SDK import/lifecycle, live identity assertions, actual plugin loading/served-profile configuration, genuine intake issuer, provider delivery reconciliation, production service-user ledger access and coordinated restart/rollback still require separate approval/testing. No activation permission follows from these passes. Production service status remained active/running at postcheck; Photon PID 140714 and Hermes PID 454732 were observed. No service action was performed.
