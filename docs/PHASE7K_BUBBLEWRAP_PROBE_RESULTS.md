# Phase 7K Bubblewrap probe results

2026-10-16. **Synthetic isolation probe PASS; full Memory staging gate remains BLOCKED.** Only synthetic probe commands/files were executed on Linux. No Research/Memory package transferred or executed, production data/credentials read, production API contacted, service changed, or policy/privilege escalation attempted.

## Commands and outcomes

SSH transport for all remote commands:
`ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81`

Initial inspection remote command: `/usr/bin/bwrap --version; /usr/bin/bwrap --help; /usr/bin/ldd /usr/bin/true`. Exit 0; Bubblewrap 0.9.0. Help confirmed namespace, clearenv, cap-drop, disable-userns, readonly mounts, tmpfs size and root remount options. No sandbox yet.

Each attempt used a fresh mode-0700 directory made with tempfile.mkdtemp under /home/alfred; parent created only named synthetic files and removed only exact known entries after checking directory contents.

| Attempt | Directory | Workload exit | Evidence |
| --- | --- | ---: | --- |
| Startup option validation | .alfred-phase7k-probe-b9a__dg5 | 1 | bwrap: --disable-userns requires --unshare-user |
| Corrected startup | .alfred-phase7k-probe-8ol2zxwr | 0 | Explicit --unshare-user added; minimal /probe-true completed |
| Python isolation probe | .alfred-phase7k-probe-2gsj831n | 1 | Sandbox started; ctypes import lacked libffi.so.8 |
| Corrected Python probe | .alfred-phase7k-probe-01285p80 | 0 | Added only read-only libffi runtime; all 17 checks true, stderr empty |

Every attempt's outer SSH/Python reporting command exited 0 (it records child status rather than returning it). Runtime ldd inspection exited 0. No attempt hit the 10-second wall timeout. The first and third failures were option/runtime preparation errors, not AppArmor/namespace denials. No restriction was bypassed or security policy changed. After fixing preparation, unprivileged Bubblewrap worked despite prior uncertainty about AppArmor policy.

## Observed isolation

Final command executed Python with -I -S -B, fresh environment, UID 1000, private user/mount/network/PID/IPC/UTS namespaces, no effective capabilities, no-new-privileges, additional user namespaces disabled, root read-only. Mounted only Python runtime/stdlib and required shared libraries read-only, synthetic inputs read-only, synthetic workspace writable, private /tmp capped at 1 MiB, private proc/dev. No host-root, home, production runtime, vault, service socket or credential mount.

All 17 checks passed:
- Allowed synthetic input read; workspace and private temporary writes succeeded.
- Host /home and the outside-mount synthetic canary were not visible.
- /opt, /run, /var and /home were absent; production parent paths therefore unexposed without reading any contents.
- Writes to /outside.txt and read-only /inputs were denied.
- Six namespace identities differed from host.
- No nonloopback interfaces or IPv4 routes.
- A host-side listener created exclusively by this probe at 127.0.0.1 on an ephemeral port was unreachable from sandbox.
- Connection to TEST-NET address 192.0.2.1:9 failed after verifying namespace/interface separation. No production endpoint was probed.
- NoNewPrivs=1, CapEff=0; clearing no-new-privileges failed.
- Additional user namespace creation failed; UID was nonroot; setuid(0) failed.

Final namespace IDs: user 4026532692; mount 4026532311; network 4026532316; PID 4026532314; IPC 4026532313; UTS 4026532312. These are transient observations, not reusable authorization identities.

## Resource results and limits of evidence

All values below were set as both soft/hard limits in the child before exec, and read back inside the final sandbox:

| Limit | Value | Scope / limitation |
| --- | ---: | --- |
| CPU | 3 seconds | Per process; not aggregate CPU quota |
| Address space | 268435456 bytes | Per process virtual memory; not aggregate memory/RSS or tmpfs accounting |
| NPROC | 128 | Real-UID process/thread ceiling, shared with alfred account; not dedicated sandbox process quota |
| File size | 1048576 bytes | Per-file maximum; not total persistent workspace usage |
| Open descriptors | 32 | Per process |
| Core files | 0 | Core dumps disabled |
| Wall time | 10 seconds | Parent communicate timeout with process-group kill on expiry; expiry branch not exercised |
| Private /tmp | 1048576 bytes | Bubblewrap tmpfs size; not total sandbox memory bound |

Successful setrlimit plus readback demonstrates installed process-local ceilings, not stress validation of every enforcement path. No fork bomb, memory exhaustion or CPU exhaustion attempted. Normal exit was bounded and clean; whole-tree timeout/descendant cleanup has not been dynamically proven. Prior nondelegated cgroup facts remain unresolved. Full Memory test execution remains BLOCKED for aggregate resource/cleanup controls and test-specific harness/runtime gates.

## Cleanup

All four unique probe roots reported root_absent=true after removal of exact synthetic files/directories. The final parent explicitly closed its probe-owned listener. Private tmpfs disappeared with namespace exit. No preexisting file was removed. No unexpected entries or cleanup ambiguity occurred.

## Reproducible final remote command body

Executed via SSH as `python3 -B - <<'PHASE7K'` with the following body. This records only the final successful synthetic probe, not permission to rerun or execute a package. Earlier variants used the option/runtime changes in the table; the minimal startup workload was /usr/bin/true with its libc/loader mounts.

```python
import os,pathlib,tempfile,subprocess,socket,json,signal,re
root=pathlib.Path(tempfile.mkdtemp(prefix=".alfred-phase7k-probe-",dir=str(pathlib.Path.home())))
os.chmod(root,0o700);inputs=root/'inputs';work=root/'workspace';inputs.mkdir(mode=0o700);work.mkdir(mode=0o700)
(inputs/'allowed.txt').write_text('synthetic phase7k input\n');outside=root/'outside.txt';outside.write_text('synthetic outside canary\n')
probe="import os,json,pathlib,socket,resource,ctypes,errno\nchecks={}\ndef check(name,value):\n checks[name]=bool(value)\n if not value:raise RuntimeError(name)\nhost=json.loads(pathlib.Path('/inputs/host.json').read_text())\ncheck('allowed_input_read',pathlib.Path('/inputs/allowed.txt').read_text()=='synthetic phase7k input\\n')\npathlib.Path('/workspace/written.txt').write_text('synthetic output\\n')\npathlib.Path('/tmp/private.txt').write_text('synthetic private temporary file\\n')\ncheck('workspace_and_private_tmp_writable',True)\ncheck('host_home_and_outside_canary_hidden',not pathlib.Path('/home').exists() and not pathlib.Path(host['outside']).exists())\ncheck('production_parent_paths_hidden',all(not pathlib.Path(p).exists() for p in ('/opt','/run','/var','/home')))\nfor path in ('/outside.txt','/inputs/unauthorized.txt'):\n try:pathlib.Path(path).write_text('synthetic denied write')\n except OSError as e:check('write_denied_'+path,e.errno in (errno.EROFS,errno.EACCES,errno.ENOENT))\n else:check('write_denied_'+path,False)\nns={n:os.readlink('/proc/self/ns/'+n) for n in ('user','mnt','net','pid','ipc','uts')}\ncheck('private_namespaces',all(ns[n]!=host['namespaces'][n] for n in ns))\nroutes=pathlib.Path('/proc/net/route').read_text().splitlines()[1:]\ncheck('no_nonloopback_ipv4_routes',all(line.split()[0]=='lo' for line in routes if line.split()))\ncheck('no_nonloopback_interfaces',all(line.split(':')[0].strip()=='lo' for line in pathlib.Path('/proc/net/dev').read_text().splitlines()[2:] if ':' in line))\nfor name,target in [('host_synthetic_loopback_denied',('127.0.0.1',host['port'])),('outbound_testnet_denied',('192.0.2.1',9))]:\n with socket.socket() as s:\n  s.settimeout(0.3)\n  try:s.connect(target)\n  except OSError:check(name,True)\n  else:check(name,False)\nstatus={line.split(':',1)[0]:line.split(':',1)[1].strip() for line in pathlib.Path('/proc/self/status').read_text().splitlines() if ':' in line}\ncheck('no_new_privileges',status['NoNewPrivs']=='1')\ncheck('zero_effective_capabilities',int(status['CapEff'],16)==0)\nlibc=ctypes.CDLL(None,use_errno=True)\ncheck('cannot_clear_no_new_privileges',libc.prctl(38,0,0,0,0)==-1)\ncheck('additional_user_namespaces_disabled',libc.unshare(0x10000000)==-1)\ncheck('unprivileged_uid',os.getuid()!=0)\ntry:os.setuid(0)\nexcept OSError:check('setuid_root_denied',True)\nelse:check('setuid_root_denied',False)\nlimits={n:resource.getrlimit(getattr(resource,n)) for n in ('RLIMIT_CPU','RLIMIT_AS','RLIMIT_NPROC','RLIMIT_FSIZE','RLIMIT_NOFILE','RLIMIT_CORE')}\nprint(json.dumps({'checks':checks,'namespaces':ns,'uid':os.getuid(),'limits':limits,'status':'ALL_SYNTHETIC_CHECKS_PASS'}))\n"
(inputs/'probe.py').write_text(probe)
listener=socket.socket();listener.bind(('127.0.0.1',0));listener.listen(1)
host={'outside':str(outside),'port':listener.getsockname()[1],'namespaces':{n:os.readlink('/proc/self/ns/'+n) for n in ('user','mnt','net','pid','ipc','uts')}}
(inputs/'host.json').write_text(json.dumps(host))
ldd=subprocess.run(['/usr/bin/ldd','/usr/bin/python3.12'],capture_output=True,text=True,timeout=3,check=True)
libs=sorted(set(re.findall(r'(/[\w/+.\-]+)',ldd.stdout)) | {'/lib/x86_64-linux-gnu/libffi.so.8'})
cmd=['/usr/bin/bwrap','--unshare-all','--unshare-user','--disable-userns','--die-with-parent','--new-session','--cap-drop','ALL','--clearenv','--ro-bind','/usr/bin/python3.12','/usr/bin/python3.12','--ro-bind','/usr/lib/python3.12','/usr/lib/python3.12']
for lib in libs:cmd+=['--ro-bind',lib,lib]
cmd+=['--ro-bind',str(inputs),'/inputs','--bind',str(work),'/workspace','--size','1048576','--tmpfs','/tmp','--proc','/proc','--dev','/dev','--remount-ro','/','--chdir','/workspace','/usr/bin/python3.12','-I','-S','-B','/inputs/probe.py']
launcher="""import os,sys,resource,ctypes
for n,v in {'RLIMIT_CPU':3,'RLIMIT_AS':268435456,'RLIMIT_NPROC':128,'RLIMIT_FSIZE':1048576,'RLIMIT_NOFILE':32,'RLIMIT_CORE':0}.items():resource.setrlimit(getattr(resource,n),(v,v))
libc=ctypes.CDLL(None,use_errno=True)
if libc.prctl(38,1,0,0,0)!=0:raise RuntimeError('no_new_privs failed')
os.execv(sys.argv[1],sys.argv[1:])
"""
print(json.dumps({'probe_root':str(root),'bwrap_argv':cmd,'runtime_ldd_exit':ldd.returncode}),flush=True)
try:
 p=subprocess.Popen(['/usr/bin/python3','-B','-c',launcher,*cmd],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True,close_fds=True,env={'PATH':'/usr/bin:/bin','LANG':'C'})
 try:out,err=p.communicate(timeout=10);timedout=False
 except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);out,err=p.communicate(timeout=3);timedout=True
 print(json.dumps({'probe_exit':p.returncode,'timed_out':timedout,'stdout':out,'stderr':err}),flush=True)
finally:
 listener.close()
 try:
  expected_inputs={'allowed.txt','probe.py','host.json'}
  if {p.name for p in inputs.iterdir()}!=expected_inputs or {p.name for p in root.iterdir()}!={'inputs','workspace','outside.txt'}:raise RuntimeError('unexpected entries')
  if {p.name for p in work.iterdir()}-{'written.txt'}:raise RuntimeError('unexpected workspace entries')
  for n in expected_inputs:(inputs/n).unlink()
  if (work/'written.txt').exists():(work/'written.txt').unlink()
  outside.unlink();inputs.rmdir();work.rmdir();root.rmdir()
  print(json.dumps({'cleanup':'exact synthetic files removed','root_absent':not root.exists()}),flush=True)
 except Exception as e:print(json.dumps({'cleanup':'PRESERVED','path':str(root),'reason':str(e)}),flush=True)

```

