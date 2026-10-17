# Phase 7M temporary cgroup probe results

2026-10-16 — **BLOCKED at preflight; no temporary cgroup created or aggregate probe executed.**

Reviewed Phase 7L resource/cleanup/gate reports and Phase 7K isolation decision. SSH strict noninteractive authentication succeeded. Only read-only Linux metadata/counter checks occurred; no files/cgroups created, quotas changed, processes moved/signaled, services modified or Research/Memory code transferred/executed.

## Delegation and headroom evidence

Intended delegated parent: /sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service.

- Effective user UID 1000 matches parent directory owner; directory writable.
- cgroup.controllers and cgroup.subtree_control both cpu memory pids.
- Parent memory.max=max, memory.current=5849088 bytes; cpu.max=max 100000; pids.max=max, pids.current=3.
- User slice memory.current approximately 2.17 GB; pids.current=71 against pids.max=20748. Ancestor memory limits observed max; CPU limits observed max 100000.
- Host MemAvailable=6569680 kB. The read-only headroom check required more than 262144 kB and passed.
- These counters are snapshots, not reserved capacity or proof that a future quota is enforced.
- No child path/name was allocated: preflight stopped before tempfile/UUID/mkdir.

Directory ownership demonstrates permission to attempt child creation; no creation was used to test it because the subsequent process-placement check failed.

## Blocking process-placement permission

The second SSH command observed its own source membership as:
`0::/user.slice/user-1000.slice/session-123.scope`.

| File | Owner UID:GID | Mode | Writable by alfred |
| --- | --- | --- | --- |
| session-123.scope/cgroup.procs | 0:0 | 0644 | No |
| user@1000.service/cgroup.procs | 1000:1000 | 0644 | Yes |
| user-1000.slice/cgroup.procs | 0:0 | 0644 | No |

All paths above are beneath /sys/fs/cgroup/user.slice/user-1000.slice except the last file, which is directly inside that slice.

The common ancestor between this SSH source and any prospective child beneath user@1000.service is user-1000.slice. Its cgroup.procs is not writable. Non-root migration requires write access both to destination cgroup.procs and to the common ancestor's cgroup.procs, per [Linux kernel cgroup v2 delegation containment](https://docs.kernel.org/admin-guide/cgroup-v2.html#delegation-containment). Thus writable child-creation delegation alone does not permit pulling SSH-born processes into it.

No migration syscall/write was attempted; expected denial follows inspected access metadata plus documented containment requirements. Do not describe this as an observed failed migration or as lack of all user delegation. The installed user-manager may launch processes already within delegation, but that path was not invoked or authorized by this one-child probe.

## Exact commands executed and statuses

Transport for both inspections:

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81
```

Remote command form: `python3 -B - <<'PHASE7M'` followed by the bodies below. Both SSH/Python commands exited **0** (successful inspection/reporting, not successful aggregate tests).

First body:

```python
import os,json,pathlib
base=pathlib.Path("/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service")
assert os.getuid()==1000 and base.stat().st_uid==os.getuid() and os.access(base,os.W_OK)
ctl={n:(base/n).read_text().strip() for n in ("cgroup.controllers","cgroup.subtree_control","memory.max","memory.current","cpu.max","pids.max","pids.current")}
assert {"cpu","memory","pids"}<=set(ctl["cgroup.controllers"].split()) & set(ctl["cgroup.subtree_control"].split())
mem={line.split(":",1)[0]:line.split(":",1)[1].strip() for line in pathlib.Path("/proc/meminfo").read_text().splitlines()}
assert int(mem["MemAvailable"].split()[0])>262144
anc=[]
p=base
while p!=pathlib.Path("/sys/fs"):
 row={"path":str(p)}
 for n in ("memory.max","memory.current","cpu.max","pids.max","pids.current"):
  if (p/n).exists():row[n]=(p/n).read_text().strip()
 anc.append(row)
 if p==pathlib.Path("/sys/fs/cgroup"):break
 p=p.parent
print(json.dumps({"delegated_parent":str(base),"uid":os.getuid(),"parent":ctl,"MemAvailable":mem["MemAvailable"],"ancestors":anc,"preflight":"no child created"}))
```

Second body:

```python
import os,pathlib,json
mount=pathlib.Path("/sys/fs/cgroup")
source=mount/pathlib.Path("/proc/self/cgroup").read_text().strip().split("::",1)[1].lstrip("/")
dest=mount/"user.slice/user-1000.slice/user@1000.service"
common=pathlib.Path(os.path.commonpath((str(source),str(dest))))
rows=[]
for p in (source,dest,common):
 q=p/"cgroup.procs";s=q.stat()
 rows.append({"path":str(q),"uid":s.st_uid,"gid":s.st_gid,"mode":oct(s.st_mode & 0o777),"writable":os.access(q,os.W_OK)})
print(json.dumps({"uid":os.getuid(),"source_cgroup":str(source),"destination_parent":str(dest),"common_ancestor":str(common),"migration_permission_metadata":rows,"source_membership":pathlib.Path("/proc/self/cgroup").read_text().strip()}))
```

The public kernel documentation was consulted on the Mac to validate containment semantics; no production API/data consulted.

## Required-test accounting

| Requirement | Result |
| --- | --- |
| Delegated directory/controllers | Verified read-only |
| Tiny-workload headroom | Snapshot check passed |
| Authorized process placement from SSH | BLOCKED by common-ancestor permissions |
| Aggregate memory/CPU/pids enforcement | NOT RUN |
| All children in intended probe cgroup | NOT RUN; no child exists |
| Timeout cleanup in resource-limited cgroup | NOT RUN; Phase 7L earlier unconstrained-cgroup synthetic cleanup remains historical evidence |
| No existing production process moved | No cgroup membership writes or signals made |
| Parent settings unchanged by this task | No control files written; no claim of an atomic externally stable snapshot |
| Cleanup | Nothing created, nothing to remove; no residual probe resources |

The authorization required stopping without creating anything if a preflight check failed. This condition was honored. No alternative privilege, common-ancestor permission change, process migration workaround, user-manager request or systemd unit creation was attempted.

