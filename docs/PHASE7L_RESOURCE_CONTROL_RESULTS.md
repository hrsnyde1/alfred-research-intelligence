# Phase 7L resource control results

2026-10-16 — **BLOCKED for aggregate resource acceptance; file-size/descriptor enforcement PASS.**

Only synthetic Bubblewrap workloads ran. No Research/Memory code transfer or execution, production data/service access, installation, sudo, or host/cgroup/systemd configuration change. Read Phase 7K probe/decision and Phase 7J gate before execution.

## Exact inspection commands and exits

All commands used SSH BatchMode=yes, StrictHostKeyChecking=yes, ConnectTimeout=8, ConnectionAttempts=1 to alfred@192.168.50.81. Remote metadata inspection used python3 -B with the following operations, all exit 0:
1. Read /proc/self/cgroup; walk only its /sys/fs/cgroup ancestor directories. For memory.max, cpu.max, pids.max, cgroup.subtree_control and cgroup.procs report existence, os.access(W_OK), and quota/controller values (not process lists).
2. Inspect existence/owner/write access of user@1000.service, its app.slice and /run/user/1000/bus (no bus interaction).
3. Read cgroup.controllers, cgroup.subtree_control, memory.max, cpu.max, pids.max and write-access metadata at app.slice.
4. Repeat the same five controls at user@1000.service root.

Reproducible controller inspection command (used for app.slice and user-manager root):

```python
import os,json
base="/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service"
print(json.dumps({"path":base,"directory_writable":os.access(base,os.W_OK),
 "controls":{n:{"writable":os.access(base+"/"+n,os.W_OK),
 "value":open(base+"/"+n).read().strip()} for n in
 ("cgroup.controllers","cgroup.subtree_control","memory.max","cpu.max","pids.max")}}))
```

No writes or access to production process cmdlines/environments.

## Observed aggregate-control availability

| Location | Observation |
| --- | --- |
| SSH session-117.scope | Not writable; memory.max=max, cpu.max=max 100000, pids.max=max |
| user-1000.slice | Not writable; memory/CPU unlimited, pids.max=20748 shared across user workloads |
| user.slice | Not writable; memory/CPU/process ceilings unlimited |
| user@1000.service | UID 1000 owns writable directory; controllers AND enabled subtree controls are cpu memory pids; root quota files themselves not writable |
| user@1000.service/app.slice | Writable directory/quota files; controllers available cpu memory pids; enabled subtree controls memory pids only |

**Correction to earlier incomplete evidence:** writable user-manager delegation exists, even though SSH-session cgroup files are not writable. Direct creation of a new child at the user-manager root may support all three aggregate controllers without privileged/system-level changes. This was NOT attempted. Never modify app.slice or user-manager root quotas: those are shared existing infrastructure.

The task explicitly says “Do not change AppArmor, Docker, cgroups or systemd configuration.” Configuring a new probe cgroup would write cgroup control files. No exception to that restriction was assumed; no cgroup was created/configured, no process migrated, and no controller enabled. Therefore this report does not claim that aggregate limits require sudo or are technically impossible. They remain **unvalidated under the authorized no-cgroup-change boundary**.

## Synthetic enforcement measured inside Bubblewrap

Two repeated small tree probes applied hard=soft rlimits before exec, then read back inside sandbox. Exact executing script is in PHASE7L_TIMEOUT_CLEANUP_RESULTS.md.

| Control | Value | Actual result |
| --- | ---: | --- |
| CPU | 2 seconds/process | Read back; no busy-loop exhaustion test. Not aggregate CPU usage/rate quota |
| Address space | 64 MiB/process | Read back; only three 1 MiB synthetic buffers; no exhaustion. Not aggregate tree memory limit |
| NPROC | 128 for real UID | Read back; only four Python workload processes plus two Bubblewrap processes. No fork-to-limit test; shared-user ceiling, not dedicated tree quota |
| File size | 4096 bytes/file | Write 4096 bytes succeeds; next byte raises EFBIG in both runs; actual file size 4096 |
| Descriptors | 32/process | Open /dev/null bounded loop raises EMFILE in both runs; all opened descriptors closed |
| Core | 0 | Disabled before exec |
| Temp filesystem | 1 MiB | Private tmpfs mounted; not a bound on whole-tree RSS |
| Wall lifetime | readiness <=3 s, 0.5 s controlled run, exact launcher SIGKILL, <=3 s collection/reap windows | Both runs terminate full tracked tree; no timeout collection failures |

No host memory/CPU/process/disk exhaustion attempted. Kernel rlimits enforce the measured per-file/per-process denial paths; they do not supply a tested aggregate cap. Supervisor memory is not charged to a dedicated workload cgroup. A wall timeout also does not impose an aggregate CPU rate limit during its window.

## Remaining authorization/evidence

Full staging gate remains BLOCKED. A separate, explicit exception authorizing ONLY creation/configuration/removal of a unique synthetic child cgroup in the already delegated user-manager subtree could permit genuine aggregate testing without changing existing units or limits. Verify ownership/controller inheritance and no existing workloads before any such future action. Use tiny bounded workloads, fresh cgroup, no shared-quota changes and no host exhaustion. Do not infer this exception from the current synthetic-file authorization.

Alternatively use a separately approved fixed-resource isolated test environment. No package execution or deployment is authorized by this result.

