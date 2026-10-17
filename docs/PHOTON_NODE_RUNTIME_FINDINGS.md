# Photon Node runtime findings

2026-10-16. **Compatible runtime found: existing service-launch Node v26.7.0.** The prior inability to read /proc/140714/exe is not a Node execution failure. No service, permissions or policy were changed; no Linux bridge/SDK tests or provider initialization occurred.

## Authoritative launch evidence

Read all four requested reports. Read-only SSH used BatchMode=yes, StrictHostKeyChecking=yes, ConnectTimeout=8, ConnectionAttempts=1. Sanitized systemctl ExecStart metadata returned only matching absolute Node/index.mjs paths; no raw argv, environment or credential values were printed or retained. Active service metadata: alfred-photon.service, MainPID 140714, User/Group alfredphoton, unit /etc/systemd/system/alfred-photon.service, no drop-ins.

- Configured Node executable: `/home/alfred/.hermes/tools/node-26.7.0-linux-x64/bin/node`.
- Configured script: `/home/alfred/.hermes/hermes-agent/plugins/platforms/photon/sidecar/index.mjs`.
- Explicit execution by SSH user alfred (UID 1000) returned **v26.7.0**, exit 0.
- Executable SHA-256: `ad19784f7e90ba789a099eccba77ede8dc90a778c424f1c10a70fed3ff903fdc`.
- Realpath equals configured path; executable is not a symlink. This confirms the service-launch runtime, not an independently dereferenced loaded process image. Proc inspection remains denied and is not needed for isolated use of the configured binary.

## Ownership, permissions and denial cause

`namei -l` and stat show:

| Component | Owner/group | Mode |
|---|---|---|
| / and /home | root/root | 0755 |
| /home/alfred | alfred/alfred | 0750 |
| .hermes | alfred/alfred | 0710 |
| tools, node-26.7.0-linux-x64, bin | alfred/alfred | 0775 |
| bin/node | alfred/alfred, UID/GID 1000 | 0755 |

No symlink component was reported in this path. The binary and its parent directories are owner/group writable; later tests must pin and recheck digests and avoid concurrent replacement. No permission hardening is performed or implied.

The denied operation was readlink of `/proc/140714/exe`: PermissionError, errno 13 (EACCES). The observer is UID 1000, while Photon is UID 983/GID 974; observer CapEff is zero. Proc executable inspection is subject to process-access authorization, independent of whether the target executable can be run. These observations support a cross-UID process-inspection permission boundary, not a missing/execution-denied Node binary. Exact individual LSM attribution is not established. Service ProtectProc=default and ProcSubset=all do not show a service-specific hide-proc override.

Host Yama ptrace_scope is 1. [Kernel Yama documentation](https://www.kernel.org/doc/html/latest/admin-guide/LSM/Yama.html) describes restricted attachment relationships; this is additional policy context, not proof that Yama specifically caused this readlink denial. No ptrace, sudo, capability request or policy change was attempted. The earlier Mac SSH Operation not permitted was a separate outer-tool sandbox boundary; approved read-only SSH succeeded. SSH PATH lacking node was yet another separate lookup issue, resolved by the explicit path.

## Compatibility evidence

Installed spectrum-ts, @spectrum-ts/core and @spectrum-ts/imessage are 12.7.0. Their package.json files do not declare a Node engines restriction. The sidecar declares Node >=18.17, but transitive packages require newer releases. Read-only installed package metadata inspection found, among others:

| Dependency | Declared Node range |
|---|---|
| @photon-ai/advanced-imessage | >=18.17 |
| @photon-ai/otel, marked, open-graph-scraper | >=20 (or >=20.0.0) |
| cheerio, undici | >=20.18.1 |
| lru-cache | 20 or >=22 |
| OpenTelemetry SDK packages | ^18.19.0 or >=20.6.0 |
| @grpc/grpc-js | >=12.10.0 |

All observed engine ranges admit v26.7.0. No requirement for exactly Node 22/24/26 was found. This is declared/source compatibility plus successful runtime startup, not completed SDK initialization or bridge test qualification. SDK factory-local state and exact line-selection source were reviewed previously; Node built-ins used by the patch need no additional package.

Installed Node help confirms --test-concurrency and --test-isolation options. Use the configured runtime, not another component's executable. A root-owned 0755 alternative at `/opt/alfred-obsidian-headless/releases/0.0.14-node-22.22.0/node-v22.22.0-linux-x64/bin/node` also returns v22.22.0 and has traversable root-owned 0755 parents. Its declared engine compatibility does not justify substituting it or borrowing the Obsidian release for Photon tests when the service's configured runtime is accessible.

`ldd` for the selected Node lists only loader, libatomic, libdl, libm, libstdc++, libgcc_s, libpthread and libc. Exact mounts are in the execution plan. No executable was copied and no package installed. Installed bwrap, timeout and prlimit are at /usr/bin. Python is 3.12.3. Node's V8 address reservation means previous Python-only 256 MiB address-space ceilings cannot be assumed usable for Node.

## Decision

**Node access/version blocker closed.** Minimum next action: separately approve an isolated staging transfer and bounded fake-transport/import-only validation using this exact runtime and the plan below. No permission changes, alternate runtime, Node installation or service restart are needed for that test.

Remaining activation gates: Linux sandbox runtime preflight/resource fit, full staged bridge/Hermes integration, protected project/binding configuration, genuine intake authority, provider ambiguity reconciliation, coordinated installation/rollback and separately approved controlled messaging. Research stays disabled on the host throughout compatibility work.
