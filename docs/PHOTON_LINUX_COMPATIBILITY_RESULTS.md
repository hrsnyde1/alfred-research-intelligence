# Photon Linux-source compatibility results

2026-10-16. **BLOCKED for complete Linux runtime/install readiness. Isolated Mac compatibility tests PASS: 25/25.** Exact Linux bridge baseline and copied SDK source match. No tests were run on Linux, and the active Node executable/launch wrapper could not be verified without additional owner-provided metadata. Passing fake transports does not qualify the full installed Hermes/SDK runtime.

## Read-only inspection

Reviewed all three requested reports, complete bridge.patch, baseline and modified source inventory. SSH used `-o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81`. Only source/package files, executable path metadata and selected systemd metadata were read. No credentials, configuration values, process environment/argv, logs, sessions, messages, database or vault content were read. No Linux files were written. Initial sandbox SSH denial was followed by the approved read-only retry.

### Baseline comparison

All four originally captured files match Linux exactly:

| Installed path relative to /home/alfred/.hermes/hermes-agent | SHA-256 | Comparison |
|---|---|---|
| plugins/platforms/photon/sidecar/index.mjs | ef019d1d50e4ca680aede49276181f8eff8d396d9b7c22a73bb5da2b2d7bb8e4 | MATCH |
| plugins/platforms/photon/adapter.py | 841ed6cb6e2d392fcec33f8983dd34fffe677c6a8d40e442bc449e66beeb16e5 | MATCH |
| plugins/platforms/photon/sidecar/send-format.mjs | 827c6c0b3a7fd3b731365ecd17bb52d65b05c9a53e67795922ec2ebb79de58fe | MATCH; unchanged by patch |
| gateway/run_inbound.py | 6a1a40708075e3550a824eae5519e98db97f52ea7995154e8c7e941de4e02144 | MATCH |

Spectrum, @spectrum-ts/core and @spectrum-ts/imessage package versions are all **12.7.0**. Copied each package's package.json, dist/index.js and dist/index.d.ts (nine public code/metadata files only). Every local digest matches an independent Linux digest; see `staging/photon-linux-compatibility-v1/SDK_SOURCE_HASHES.json` and `evidence/linux-sdk-metadata.json`. The iMessage JS/types match previously recorded digests. Core/spectrum entry files had no prior recorded digest, so this establishes fresh continuity, not retrospective proof that every dependency matched the previous test date. No transitive dependency tree, native binary or credential-bearing runtime inventory was copied.

### Runtime and services

`node --version` failed in the SSH PATH. Metadata discovery found these binaries; explicit version commands returned:

- /home/alfred/.hermes/tools/node-26.7.0-linux-x64/bin/node — v26.7.0.
- /opt/alfred-obsidian-headless/releases/0.0.14-node-22.22.0/node-v22.22.0-linux-x64/bin/node — v22.22.0. This belongs to another component; it was not selected or changed for Photon.
- Linux Python — 3.12.3.

Photon MainPID 140714 reports comm node-MainThread, but readlink of /proc/140714/exe returns PermissionError. Package main and service cwd identify the **declared** entrypoint /home/alfred/.hermes/hermes-agent/plugins/platforms/photon/sidecar/index.mjs. Exact active executable, wrapper and loaded code cannot be confirmed from these metadata alone. No argv/environment or credential-bearing unit text was read to bypass this boundary.

Both services are active/running and CanReload=no. Photon runs as alfredphoton in the sidecar directory; Hermes runs as alfredmsg with cwd /var/lib/alfredmsg/hermes. Hermes Requires and After include alfred-photon.service. Both Want and After include alfred-development-intake.service and network-online.target; neither has BindsTo or PartOf entries. Development observer dependencies must remain unchanged.

Fresh permission metadata: both DynamicUser=no, PrivateTmp=yes, ProtectHome=read-only, ProtectSystem=strict, NoNewPrivileges=yes; allowed address families AF_INET/AF_INET6/AF_UNIX. Photon ReadWritePaths=/var/lib/alfredphoton; Hermes ReadWritePaths=/var/lib/alfredmsg. No changes made. Research ledger can be proposed beneath Photon's existing writable root, subject to owner-approved directory creation/ownership. No new network family or package is required by the patch.

## Isolated execution

Workspace: `staging/photon-linux-compatibility-v1/`. Copied the reviewed baseline and tests; applied bridge.patch to modified/ only. All six resulting file digests match the tested candidate. Original staging baseline and Linux source remain unchanged.

Sandbox: macOS sandbox-exec with network denied, home-data reads denied except the compatibility workspace and Node runtime, writes allowed only under workspace tmp/, and an empty inherited environment (`env -i`). HOME points to an empty staging directory and TMPDIR to isolated temporary storage. Tests never import/initialize the Spectrum SDK or production bridge entrypoint. The SDK selector test evaluates only extracted pure selector functions from copied Linux source in a VM with synthetic clients. No live HTTP listener/provider connection is created.

Outer sandbox initially rejected sandbox-exec; approved capability probe succeeded. First Python attempt could not resolve a repository-root cwd outside allowed reads; using the compatibility cwd fixed it. First Node attempt could not lstat home ancestors; allowed only required ancestor metadata while home-data and network denials remained. Isolation controls were retained, not removed. Python probes confirm loopback connection denial, home-directory listing denial and no inherited Photon/token/secret variables. No credential files were used in those probes.

Commands, from the compatibility workspace, with the recorded sandbox profile and explicit runtime paths:

```sh
sandbox-exec -f no-network.sb /usr/bin/env -i PATH=/usr/bin:/bin HOME="$PWD/empty-home" TMPDIR="$PWD/tmp" PYTHONDONTWRITEBYTECODE=1 /Library/Frameworks/Python.framework/Versions/3.14/bin/python3 -B -m unittest discover -s tests -p 'test_*.py' -v
sandbox-exec -f no-network.sb /usr/bin/env -i PATH=/usr/bin:/bin HOME="$PWD/empty-home" TMPDIR="$PWD/tmp" /Users/haydensnyder/.local/node24/bin/node --test tests/research-project.test.mjs tests/sdk-source.test.mjs
```

| Tests | Actual result | Exit/runtime |
|---|---|---|
| Original 11 JavaScript bridge tests + 2 installed-SDK compatibility tests | 13 passed, 0 failed | 0; 62.254 ms |
| Original 10 Python guard/compatibility tests + 2 isolation checks | 12 passed, 0 failed | 0; 0.072 s |
| Patch application to isolated baseline | all six candidate digests match | 0 |

Logs under workspace evidence/. Existing 21 tests are copied unchanged from the reviewed staging artifact. Added tests check SDK package consistency, installed exact-line selector behavior, empty credential environment and sandbox enforcement. Prior 347 Research regression passes remain prior evidence; they were not unnecessarily rerun because Research source was unchanged.

## Findings and differences from Linux

Personal function equivalence, preserved initialization/handlers and payload project tagging pass the same fake-transport/AST checks as before. Disabled Research never creates an app. Strict project/line/sender/space validation and terminal hook handling pass. Scoped IDs, independent ledger/cache, explicit outbound selection, duplicate/conflict handling, restart replay and UNKNOWN no-resend tests pass. Missing or forged binding cannot enter ordinary Personal routing.

Mac tests used Node v24.21.0 and Python 3.14.3; Linux has the discovered Node 26.7.0/22.22.0 binaries and Python 3.12.3. Which Node actually serves Photon remains unverified. POSIX getuid, file ownership, 0700/0600, atomic rename and fsync are compatible APIs by source inspection, but Linux/systemd filesystem and crash behavior were not executed. Full SDK construction, gRPC dependencies, dynamic SDK patching, full Hermes plugin/profile loading and source-to-process correspondence remain untested. Partial SDK code copy is not a runnable vendored dependency installation.

**Decision:** synthetic compatibility PASS; complete Linux runtime readiness **BLOCKED** on exact active launch metadata and separately authorized Linux-isolated fake-SDK/Hermes execution. See PHOTON_LINUX_INSTALLATION_GATES.md. No missing packages were identified for this patch; no production installation is approved.
