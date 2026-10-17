# Corrected Photon bridge Linux test results

2026-10-16. **PASS — all 41 approved corrected bridge tests passed on Linux**, 0 failed/skipped. No installation, production service action, actual Spectrum authentication or messaging occurred. Research remains unactivated.

## Reviewed candidate and baseline

Read all five requested corrected-candidate/acceptance documents and inspected exact bridge.patch, SOURCE_INVENTORY.json and TEST_INVENTORY.json. Corrected patch SHA-256: be1b8c0b900210f691b67e2e77cebea954b17909a9295d5f4edcbcacb29d632e. Frozen local test hashes matched before transfer; no test or product source was modified to obtain Linux passes.

Read-only preflight verified **15 pinned host hashes**: four installed bridge baseline files, nine Spectrum entry/package/type files, exact Node executable and libffi. All matched; rechecked immediately before transfer, before/after tests and in independent postcheck. Installed Spectrum source/packages remain **12.7.0**. Node is **v26.7.0** at /home/alfred/.hermes/tools/node-26.7.0-linux-x64/bin/node, SHA-256 ad19784f7e90ba789a099eccba77ede8dc90a778c424f1c10a70fed3ff903fdc. Python is 3.12.3.

Original and generated staged hashes, relative to the installed Hermes source root /home/alfred/.hermes/hermes-agent/:

| File | Original baseline SHA-256 | Staged SHA-256 |
|---|---|---|
| gateway/photon_research.py | ABSENT | 4aba0fdf6ed2b45ae5c401255e8d9d759e78e1bd2e4e38c7fbc4c63ccab5ee14 |
| gateway/run_inbound.py | 6a1a40708075e3550a824eae5519e98db97f52ea7995154e8c7e941de4e02144 | 89c3cf4daa0a04473d6302bf53f20b6d3839bd4960f0bc70674c27b9c429b018 |
| plugins/platforms/photon/adapter.py | 841ed6cb6e2d392fcec33f8983dd34fffe677c6a8d40e442bc449e66beeb16e5 | 540288fed36df43cb2e3049a1e46b94b1ddb0e94a4e8efad3f947e4f389e64c1 |
| plugins/platforms/photon/sidecar/caller-bindings.mjs | ABSENT | 1bafa6bb31376fcdf5cf237003555fc7ba7d289711bcc192335ed565232075bf |
| plugins/platforms/photon/sidecar/index.mjs | ef019d1d50e4ca680aede49276181f8eff8d396d9b7c22a73bb5da2b2d7bb8e4 | 2ac209c3864cf4165d55fbfff7ffa9e29d9a43b010d35937bc08ea51c73082ba |
| plugins/platforms/photon/sidecar/research-lifecycle.mjs | ABSENT | 6ae5e27a677cc6df9c2065e73ce727ccf11174c8a915d29134792fbe3df089dc |
| plugins/platforms/photon/sidecar/research-project.mjs | ABSENT | ea65df22546e19233bb79e976aaf366470fb3fb5d197c1c40c006a9aa9cb6e96 |
| plugins/platforms/photon/sidecar/research-worker.mjs | ABSENT | 98ac1071ae1c06d0cba0e31bde819cec5288fe16cb577479c9862a6c8bf501a7 |
| plugins/platforms/photon/sidecar/send-format.mjs | 827c6c0b3a7fd3b731365ecd17bb52d65b05c9a53e67795922ec2ebb79de58fe | 827c6c0b3a7fd3b731365ecd17bb52d65b05c9a53e67795922ec2ebb79de58fe |

The five additive module targets were not installed. send-format.mjs remains unchanged. Copied SDK digests are frozen in staging/photon-linux-compatibility-v1/SDK_SOURCE_HASHES.json and in the exact executed preflight EXPECTED map. No transitive SDK runtime was imported or installed.

## Preflight and sandbox

The frozen successful supervisor was reused, including pinned /lib/x86_64-linux-gnu/libffi.so.8 -> /usr/lib/x86_64-linux-gnu/libffi.so.8.1.4, SHA-256 00f593fe192f2851b8ce23b25cec2488d769beb5a8f63e8c9e563071e1075153. No broad system directory bind or changed limit.

Python preflight passed separate user/mount/network/PID/IPC/UTS namespaces, NoNewPrivs, no effective capabilities, denied nested user namespace, absent host /home /opt /run /var /etc /root, no provider/token/SSH-agent environment, exact read-only mounts, isolated temporary writes and blocked probe-owned host-loopback/TEST-NET connections. No production endpoint was probed. Probe listener closed in finally. Plain Node and the added narrowly scoped disposable-worker preflight reached readiness and were forcibly timed out successfully.

Bubblewrap flags: unshare-all/user, disable-userns, die-with-parent, new-session, cap-drop ALL, clearenv, private proc/dev, read-only root. Exact file mounts: selected Node, Python executable/stdlib, approved library files including libffi. Test source trees baseline/modified/tests/linux-sdk mounted read-only. Writable /tmp=32 MiB and /workspace=16 MiB are private tmpfs, with synthetic HOME/TMPDIR. No host-backed writable test path, production credential, config, socket, message store or service directory exposed.

Unchanged hard=soft limits: CPU 15 s/process; AS 64 GiB/process; NPROC 128 shared-real-UID guard; FSIZE 8 MiB; NOFILE 128; CORE 0. Node --jitless --max-old-space-size=64, UV_THREADPOOL_SIZE=2, test-isolation=none, concurrency=1. 45 s/test-case deadline and 1 MiB monitored output/stream. Three forced cleanup preflights used tighter 2 s deadlines. Exact pidfds/start identities, subreaper wait/reap and PID namespace teardown removed every tracked process. This includes an actual Node worker thread under the same limits; no limit was widened for the worker.

| Case | Exit | Wall seconds | Waited-process maxrss KiB | Remaining identities |
|---|---|---|---|---|
| ISOLATION_TIMEOUT_PREFLIGHT | -9 | 2.029520 | 162560 | [] |
| NODE_RUNTIME_TIMEOUT_PREFLIGHT | -9 | 2.021574 | 162560 | [] |
| NODE_WORKER_TIMEOUT_PREFLIGHT | -9 | 2.028579 | 162560 | [] |
| NODE_CORRECTED_BRIDGE_TESTS | 0 | 0.537292 | 162688 | [] |
| PYTHON_CORRECTED_GUARD_TESTS | 0 | 0.441401 | 162688 | [] |

Preflight -9 exits are expected deadline cleanup successes. Test exits are 0. Rusage is for the waited outer process, not aggregate cgroup peak memory or complete whole-tree CPU. The AS ceiling is virtual address space, not an RSS promise. No cgroup/AppArmor settings changed, and this finite workload does not authorize uncontrolled multiprocess tests.

## Exact executed commands

All commands used SSH BatchMode=yes, StrictHostKeyChecking=yes, ConnectTimeout=8 and ConnectionAttempts=1. Each successful remote phase exited 0; stderr phase-error files are empty. Initial local sandbox denial exited 255 before remote execution, followed by the approved read-only/synthetic retry.

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B -' < artifacts/audits/photon-corrected-linux-20261016/preflight.py > artifacts/audits/photon-corrected-linux-20261016/preflight.jsonl 2> artifacts/audits/photon-corrected-linux-20261016/preflight.err
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B -' < artifacts/audits/photon-corrected-linux-20261016/worker-preflight.py > artifacts/audits/photon-corrected-linux-20261016/worker-preflight.jsonl 2> artifacts/audits/photon-corrected-linux-20261016/worker-preflight.err
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B -' < artifacts/audits/photon-corrected-linux-20261016/transfer.py > artifacts/audits/photon-corrected-linux-20261016/transfer-result.json 2> artifacts/audits/photon-corrected-linux-20261016/transfer.err
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B /home/alfred/research-staging/photon-corrected-20261016-i4rcwpsy/run_validation.py' > artifacts/audits/photon-corrected-linux-20261016/linux-tests.jsonl 2> artifacts/audits/photon-corrected-linux-20261016/linux-tests.err
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B -' < artifacts/audits/photon-corrected-linux-20261016/postcheck.py > artifacts/audits/photon-corrected-linux-20261016/postcheck.txt
```

Exact Bubblewrap argv and supervisor source are retained under artifacts/audits/photon-corrected-linux-20261016/. Inner test commands:

```text
/runtime/node --jitless --max-old-space-size=64 --test --test-isolation=none --test-concurrency=1 /release/tests/research-project.test.mjs /release/tests/sdk-source.test.mjs /release/tests/compatibility-corrections.test.mjs
/usr/bin/python3.12 -I -S -B -m unittest discover -s /release/tests -p test_guard.py -v
```

## Transfer and patch verification

Collision-free stage: **/home/alfred/research-staging/photon-corrected-20261016-i4rcwpsy**. Transferred 20 manifest-listed payload files plus TRANSFER_MANIFEST.json (21): four baseline files, nine public SDK files, corrected patch, five test/fixture files and the bounded supervisor. Manifest SHA-256: e378848c49922484bf49646ce6913dc70544d89a61a639dc2f6220001a68d50e. Every transferred digest verified independently on Linux; complete list/lengths/digests in audit TRANSFER_MANIFEST.json. No real credentials or active configuration included; synthetic token/secret strings are fixtures only.

Copied baseline to modified within that stage; /usr/bin/patch -p1 exited 0. All nine result file hashes matched. Independent postcheck verifies exact **30 regular files**, no symlinks/extras, UID1000, directories0700/files0600, unchanged payload/candidate hashes and all 15 host inputs unchanged. No earlier stage or active installation was overwritten. Stage retained for owner review. Temporary test state/output handles were closed/removed; namespace tmpfs storage disappeared.

## Executed tests

**30 Node passed**, 0 failed/skipped, runner duration **408.726753 ms**. **11 Python passed**, 0 failed/skipped, unittest duration **0.268 s**. Overall **41/41 PASS**. Explicit count assertions in the supervisor reject skipped or incomplete output. No unrelated Hermes/Research suites or optional real SDK import case were executed; previous 347 Mac Research passes remain historical evidence.

Node names:

- original Development request reproduces and succeeds unchanged through Personal
- explicit Personal and authorized Research select independent connections concurrently
- legacy authority cannot elevate itself using a Research project field
- Research authority has no Personal default and no Personal send permission
- unknown or invalid credentials cannot use either project; no token fallback
- copied caller objects and colliding caller tokens cannot gain Research authority
- disabled Research performs no configuration/factory work; original Personal startup retained
- authentication stall cannot delay Personal readiness and is terminated without retries
- authentication failure never terminates or changes healthy Personal connection
- missing Research credentials or caller authority fails closed without affecting Personal
- Research send timeout rejects its pending state without Personal retry leakage
- shutdown and late ready events cannot revive Research; restart is a new independent lifecycle
- Research internal retries have a hard session lifetime and no automatic reconnect
- real disposable worker stall is terminated; no SDK/credentials are imported
- production worker protocol with substituted fake SDK keeps concurrent traffic separate
- cancelling Research delivery retains healthy Personal consumer and removes only its waiter
- original awaited startup blocker reproduces before correction and releases only after auth
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
- test_research_http_uses_separate_host_credential_and_missing_never_falls_back

## Findings and limits

Both original blockers reproduce in the immutable prior-handler fixture and pass after correction: authenticated legacy Development sends remain Personal without changing their body, and Research authentication cannot gate Personal readiness. Separate Research caller authority is required; project fields/caller copies/unknown credentials cannot elevate. Research cannot use Personal default, missing credentials fail closed, late readiness cannot revive a terminated lifecycle and concurrent fake traffic stays scoped. IDs, caches, durable accepted/UNKNOWN records and replay remain separated. No Linux-specific defect appeared in this subset.

The real disposable-worker stall test proves thread termination; the production-worker protocol test substitutes a fake SDK before execution. Tests never import a real Spectrum factory, authenticate, create a provider connection or send a real message. Network namespace and absent credentials additionally enforce this boundary. Research host/service flags and credentials were not changed; real Research remains inactive.

This qualifies synthetic compatibility, not live provider behavior, full Hermes plugin/served-profile installation, genuine intake authorization, credential-store mapping, indefinitely available Research sessions or actual delivery reconciliation. The five-minute session lease and no automatic worker restart still need owner approval. Both production services remained active/running at postcheck; no restart or service configuration change occurred.
