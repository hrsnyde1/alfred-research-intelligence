# Phase 7P — bounded Linux test results

2026-10-16 — **PASS: 8 additional tests ran, 8 passed, 0 failures, 0 errors, 0 skips.** SSH/supervisor exit **0**, remote stderr empty. Phase 7P ran only the eight explicitly announced additional methods, each in a fresh Bubblewrap sandbox. The eight Phase 7O methods were not rerun; cumulative distinct Linux coverage is **16 of 305 methods**, not a full-suite pass.

## Prior review and bounded selection

Reviewed [7N readiness](PHASE7N_RESEARCH_LINUX_TEST_READINESS.md), [7N execution plan](PHASE7N_RESEARCH_TEST_EXECUTION_PLAN.md), [7O results](PHASE7O_LINUX_TEST_RESULTS.md) and [7O findings](PHASE7O_LINUX_COMPATIBILITY_FINDINGS.md). Before execution, the exact eight additional names and unchanged resource values were reported to the owner in commentary, as requested. The current mission authorized selection and execution of a conservative subset; no broader suite authorization was inferred.

Static inspection covered the selected methods, aliased/inherited setup, helper chains, synthetic provider, fake Memory adapter, Director/verification path, and workflow composition. All fixture roots are TemporaryDirectory paths, redirected into private `/tmp`. Setup initializes synthetic identities/model assignments and four temporary SQLite databases. Runtime helpers explicitly construct `SyntheticModelProvider(test_only=True)`, `FakeMemoryAdapter`, `TestMemoryAccess` and fake conversation transport. Workflow journals/SQLite writes remain under the temporary fixture root. Notifications are fake records, not external messages. The simulated registrations are local test-ledger objects, not registration or activation of Alfred agents.

Selected tests contain no subprocess launch, multiprocessing, thread worker, crash helper, large transaction simulation or live transport. They use small text fixtures and finite loops: eight lead-selection cases, six categories, four lifecycle companies, and twelve cross-company pairs. Actual provider research/verify calls here are deterministic local Python methods; no model service is called. Cross-company export/HQ method names denote fake authorization checks; no Obsidian vault or HQ service is involved. **No new isolation requirement was identified.**

| Exact selected identifier | Why selected |
| --- | --- |
| `test_workflow.WorkflowTests.test_personal_github_frontend_cto_complete` | Director composition through approved simulation, frontend proposal, fake submit/commit/promote/retrieve and idempotent replay |
| `test_workflow.WorkflowTests.test_supporting_specialist_is_justified_and_verifier_independent` | Finance/tax lead, justified legal support, verifier principal independent of all researchers |
| `test_research.ResearchTests.test_correct_lead_selection_for_source_categories` | Eight source/objective cases selecting accountable specialty and packet researcher |
| `test_research.ResearchTests.test_self_approval_forged_and_unassigned_verifiers_rejected` | Reject self-approval, forged/unassigned verifier and foreign-company authority |
| `test_foundation.FoundationTests.test_all_approved_content_changes_digest` | Packet digest changes with claims, evidence, source revision, classification, limitations, version and company |
| `test_intelligence.IntelligenceTests.test_categories_and_environment_extensions` | Six built-in categories, tenant-specific extension and unknown-category rejection |
| `test_memory.MemoryTests.test_four_environment_lifecycle_and_citations` | Four-company simulated submit/commit/promote/retrieve lifecycle, citations and exact verification packet digest |
| `test_memory.MemoryTests.test_all_twelve_pairs_deny_memory_and_hq_operations` | All twelve directed company pairs, fourteen fake Memory/HQ operations per pair: 168 authorization denials |

The loader asserted exactly one case and exact `case.id()==TEST_ID` before every run. The 31-module source import sweep ran inside each sandbox. Imports/discovery were not performed on the host. The raw transcript reports the actual ID for each method.

## Preflight and release integrity

Release: `/home/alfred/research-staging/research-v1/alfred-research-v1-0.1.0-phase7e-linux-stage-20261016`.

The corrected Phase 7O validator was retained: exactly 90 payload inventory entries, 91 checksum entries including the independently pinned `RELEASE_INVENTORY.json`, and 92 extracted regular files/archive members. Every checksum, payload byte count, pinned control-file digest, archive digest and archive-to-staging byte comparison passed. Duplicate JSON keys/paths, unsafe/missing/extra/modified entries, symlinks and special members are rejected. The selected local static-snapshot test-module hashes matched current staging before application execution.

- Python: `3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0]`; UID 1000.
- Bubblewrap: `bubblewrap 0.9.0`.
- Archive SHA-256: `ec6dedd835e8c926d5e862a15d392c090e6831fbc84b41f1d5e6848d2c3fe63e`.
- RELEASE_INVENTORY.json SHA-256: `202e45ca9977f538f4e9ce37b187e61e27cc61cba553d0dbac6cdf829cc904c5`.
- FILES.sha256 SHA-256: `d3353a8a459bf0f4a606a8ea01430187b1cdc55990136bc4fd75fb8a63f69ad2`.
- Static inventory: 305 distinct methods; only the announced eight selected.
- Post-run check: **all 92 file hashes and archive digest unchanged**, no new release files or `.pyc` files.

Synthetic preflight verified private user/mount/network/PID/IPC/UTS namespaces, UID 1000, zero capabilities, NoNewPrivs=1 and denial of nested user namespaces. Host `/home`, `/opt`, `/run`, `/var`, `/etc`, `/root` were absent. Environment clearing was verified, with PWD constrained to `/workspace` and no SSH_AUTH_SOCK. No credentials, vaults, service sockets or production paths were mounted or read. There were no nonloopback interfaces/IPv4 routes; the probe's own host-loopback listener and TEST-NET endpoint were unreachable. The listener was closed before application execution.

The exact existing mount boundary remained:

| Mount | Access |
| --- | --- |
| Staged src → `/release/src`; staged tests → `/release/tests` | Read-only |
| `/usr/bin/python3.12`, `/usr/lib/python3.12` | Read-only; `-I -S -B` |
| Loader, libc, libm, libz, libexpat, libsqlite3, libffi, libcrypto | Exact read-only files; full paths in command body |
| `/tmp`, `/workspace` | Separate private tmpfs, 16,777,216 bytes each |
| `/proc`, `/dev` | Private PID-namespace procfs and Bubblewrap synthetic dev |
| Root | Read-only |

No host-backed writable workspace, broad host-root/home mount, production socket or host networking was exposed. Scratch capacity and writable/read-only mount flags were checked in synthetic preflight. No release write probes were attempted.

## Limits and measured results

Hard=soft limits read back unchanged: CPU **10 s/process**, address space **268,435,456 bytes/process**, file size **8,388,608 bytes/file**, descriptors **64/process**, NPROC **128** (shared-real-UID guard, not dedicated quota), core **0**. Wall watchdog **20 s/case**; output threshold **1 MiB per stream**, polled; cleanup wait and verification windows **3 s** each. Each scratch filesystem is 16 MiB. No limit was widened.

| Exact test identifier | Exit | Passed | unittest s | Sandbox wall s | Self CPU s | Self peak RSS KiB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `test_workflow.WorkflowTests.test_personal_github_frontend_cto_complete` | 0 | 1 | 0.796 | 1.184876 | 1.126265 | 29328 |
| `test_workflow.WorkflowTests.test_supporting_specialist_is_justified_and_verifier_independent` | 0 | 1 | 0.695 | 1.101754 | 1.029882 | 29472 |
| `test_research.ResearchTests.test_correct_lead_selection_for_source_categories` | 0 | 1 | 0.457 | 0.859968 | 0.783634 | 28488 |
| `test_research.ResearchTests.test_self_approval_forged_and_unassigned_verifiers_rejected` | 0 | 1 | 0.095 | 0.500551 | 0.423528 | 27684 |
| `test_foundation.FoundationTests.test_all_approved_content_changes_digest` | 0 | 1 | 0.031 | 0.416894 | 0.355111 | 27056 |
| `test_intelligence.IntelligenceTests.test_categories_and_environment_extensions` | 0 | 1 | 0.165 | 0.584967 | 0.506672 | 28312 |
| `test_memory.MemoryTests.test_four_environment_lifecycle_and_citations` | 0 | 1 | 1.233 | 1.641060 | 1.568900 | 29536 |
| `test_memory.MemoryTests.test_all_twelve_pairs_deny_memory_and_hq_operations` | 0 | 1 | 1.358 | 1.763461 | 1.695971 | 29948 |

Total application sandbox wall: **8.053530 s** (includes launcher/import/test/cleanup). Sum of rounded unittest durations: **4.830 s**. Interpreter self CPU total: **7.489963 s**. Maximum interpreter self peak RSS: **29,948 KiB** (29.25 MiB). There were no application resource denials, timeouts, output-limit events or skips.

RUSAGE_SELF includes Python imports and test work. It is not aggregate sandbox RSS/CPU accounting. No cgroup quota was created or measured. tmpfs capacities were verified; tmpfs high-water usage was not measured. The report does not infer a dedicated process cap from RLIMIT_NPROC or a whole-tree memory cap from RLIMIT_AS.

## Cleanup evidence

Before application execution, the same supervisor deliberately killed its exact synthetic launcher pidfd after readiness plus 0.3 s, with the 20-second watchdog still active. Expected exit **-9**; case wall **0.419260 s**. This exercises the same force-kill/reap path; it is not a full wall-deadline exhaustion or a new adversarial process-tree test. No application needed forced termination.

Each case recorded three observed process identities (outer Bubblewrap/launcher, namespace reaper, interpreter). All had disappeared at cleanup; `remaining_tracked=[]` for every case. Identity evidence is PID:starttime ticks:

- `SYNTHETIC_PREFLIGHT`: 335458:5746009, 335459:5746011, 335460:5746011; none remained.
- `test_workflow.WorkflowTests.test_personal_github_frontend_cto_complete`: 335486:5746050, 335487:5746053, 335488:5746053; none remained.
- `test_workflow.WorkflowTests.test_supporting_specialist_is_justified_and_verifier_independent`: 335489:5746169, 335490:5746171, 335491:5746172; none remained.
- `test_research.ResearchTests.test_correct_lead_selection_for_source_categories`: 335496:5746279, 335497:5746281, 335498:5746282; none remained.
- `test_research.ResearchTests.test_self_approval_forged_and_unassigned_verifiers_rejected`: 335502:5746365, 335503:5746367, 335504:5746368; none remained.
- `test_foundation.FoundationTests.test_all_approved_content_changes_digest`: 335506:5746415, 335507:5746418, 335508:5746418; none remained.
- `test_intelligence.IntelligenceTests.test_categories_and_environment_extensions`: 335513:5746457, 335514:5746460, 335515:5746461; none remained.
- `test_memory.MemoryTests.test_four_environment_lifecycle_and_citations`: 335523:5746515, 335524:5746518, 335525:5746518; none remained.
- `test_memory.MemoryTests.test_all_twelve_pairs_deny_memory_and_hq_operations`: 335530:5746680, 335531:5746682, 335532:5746682; none remained.

The subreaper supervisor traversed only descendants of its own launcher, used an exact pidfd for termination, and verified tracked PID/starttime identities after bounded waits. No process-name or account-wide signaling occurred. Polling covers the observed finite tree, not an adversarial unlimited-fan-out guarantee. Private tmpfs mounts disappeared with namespaces; unlinked stdout/stderr TemporaryFile logs closed per case. No Linux script was installed or saved. Release integrity was rechecked after all cases.

## Exact execution command

The first call was denied by the Mac execution sandbox (exit 255, no remote execution); the authorized SSH retry completed with exit **0**. No application method was rerun. The script/output paths below are Mac-local and were streamed over stdin:

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B -' < /tmp/phase7p_run.py > /tmp/phase7p_run.out 2> /tmp/phase7p_run.err
```

`/tmp/phase7p_run.py` follows exactly. It reuses the successful Phase 7O validator, sandbox argv, resource launcher, synthetic isolation preflight and process cleanup. Changes are the eight explicitly selected IDs, exact loaded-ID reporting/assertion, and Phase 7P success marker; security controls are unchanged.

```python
import os,sys,pathlib,json,hashlib,ast,re,tarfile,subprocess,time,resource,ctypes,signal,tempfile,select,socket
BASE=pathlib.Path('/home/alfred/research-staging/research-v1/alfred-research-v1-0.1.0-phase7e-linux-stage-20261016')
TESTS=['test_workflow.WorkflowTests.test_personal_github_frontend_cto_complete', 'test_workflow.WorkflowTests.test_supporting_specialist_is_justified_and_verifier_independent', 'test_research.ResearchTests.test_correct_lead_selection_for_source_categories', 'test_research.ResearchTests.test_self_approval_forged_and_unassigned_verifiers_rejected', 'test_foundation.FoundationTests.test_all_approved_content_changes_digest', 'test_intelligence.IntelligenceTests.test_categories_and_environment_extensions', 'test_memory.MemoryTests.test_four_environment_lifecycle_and_citations', 'test_memory.MemoryTests.test_all_twelve_pairs_deny_memory_and_hq_operations']
MODULES=['alfred_research', 'alfred_research.budgets', 'alfred_research.contracts', 'alfred_research.integration', 'alfred_research.integration.canary_contracts', 'alfred_research.intelligence', 'alfred_research.intelligence.service', 'alfred_research.memory', 'alfred_research.memory.access', 'alfred_research.memory.contracts', 'alfred_research.memory.fake', 'alfred_research.persistence', 'alfred_research.registration', 'alfred_research.research', 'alfred_research.research.contracts', 'alfred_research.research.execution', 'alfred_research.research.journal', 'alfred_research.research.provider', 'alfred_research.research.workflow', 'alfred_research.sources', 'alfred_research.sources.adapters', 'alfred_research.sources.contracts', 'alfred_research.sources.policy', 'alfred_research.sources.processor', 'alfred_research.state', 'alfred_research.tenancy', 'alfred_research.verification', 'alfred_research.workflow', 'alfred_research.workflow.contracts', 'alfred_research.workflow.coordinator', 'alfred_research.workflow.notifications']
LIBS=['/lib64/ld-linux-x86-64.so.2', '/lib/x86_64-linux-gnu/libc.so.6', '/lib/x86_64-linux-gnu/libm.so.6', '/lib/x86_64-linux-gnu/libz.so.1', '/lib/x86_64-linux-gnu/libexpat.so.1', '/lib/x86_64-linux-gnu/libsqlite3.so.0', '/lib/x86_64-linux-gnu/libffi.so.8', '/lib/x86_64-linux-gnu/libcrypto.so.3']
ARCHIVE_PIN='ec6dedd835e8c926d5e862a15d392c090e6831fbc84b41f1d5e6848d2c3fe63e'
INVENTORY_PIN='202e45ca9977f538f4e9ce37b187e61e27cc61cba553d0dbac6cdf829cc904c5'
FILES_PIN='d3353a8a459bf0f4a606a8ea01430187b1cdc55990136bc4fd75fb8a63f69ad2'

def safe(name):
 assert isinstance(name,str) and name and not name.startswith('/') and '\\' not in name
 assert all(part not in ('','.','..') for part in name.split('/'))
 assert not any(ord(c)<32 or ord(c)==127 for c in name)
 return name
def digest(data):return hashlib.sha256(data).hexdigest()
def unique(pairs):
 result={}
 for k,v in pairs:
  assert k not in result, ('duplicate JSON key',k)
  result[k]=v
 return result
def checksum(data):
 result={}
 for line in data.decode('utf-8').splitlines():
  m=re.fullmatch(r'([0-9a-f]{64})  (.+)',line);assert m, 'checksum format'
  d,n=m.groups();safe(n);assert n not in result, ('duplicate checksum path',n)
  result[n]=d
 return result
def integrity():
 assert os.getuid()==1000 and sys.version_info[:3]==(3,12,3), sys.version
 assert BASE.is_dir() and not BASE.is_symlink()
 for parent in [BASE.parent,BASE.parent.parent]:assert not parent.is_symlink()
 paths=list(BASE.rglob('*'));assert not any(p.is_symlink() for p in paths)
 assert all(p.is_dir() or p.is_file() for p in paths)
 files={safe(str(p.relative_to(BASE))):p.read_bytes() for p in paths if p.is_file()}
 assert len(files)==92
 assert digest(files['RELEASE_INVENTORY.json'])==INVENTORY_PIN
 assert digest(files['FILES.sha256'])==FILES_PIN
 inv=json.loads(files['RELEASE_INVENTORY.json'],object_pairs_hook=unique)
 expected={}
 for row in inv['files']:
  n=safe(row['path']);assert n not in expected and re.fullmatch('[0-9a-f]{64}',row['sha256'])
  assert type(row['bytes']) is int and row['bytes']>=0
  expected[n]=row
 assert len(expected)==90 and set(files)==set(expected)|{'RELEASE_INVENTORY.json','FILES.sha256'}
 for n,row in expected.items():assert digest(files[n])==row['sha256'] and len(files[n])==row['bytes'],n
 sums=checksum(files['FILES.sha256'])
 assert len(sums)==91 and set(sums)==set(expected)|{'RELEASE_INVENTORY.json'}
 for n,d in sums.items():assert digest(files[n])==d,n
 archive=BASE.parent/(BASE.name+'.tar.gz');assert archive.is_file() and not archive.is_symlink()
 archive_hash=digest(archive.read_bytes());assert archive_hash==ARCHIVE_PIN
 outside=BASE.parent/'SHA256SUMS';assert outside.is_file() and not outside.is_symlink()
 assert checksum(outside.read_bytes())=={archive.name:ARCHIVE_PIN}
 with tarfile.open(archive,'r:gz') as tar:
  members=tar.getmembers();assert len(members)==92
  seen=set()
  for member in members:
   safe(member.name);assert member.isfile() and member.name.startswith(BASE.name+'/')
   n=member.name[len(BASE.name)+1:];safe(n);assert n not in seen and n in files
   seen.add(n);assert tar.extractfile(member).read()==files[n],n
  assert seen==set(files)
 names=[]
 for n,data in files.items():
  if n.startswith('tests/') and n.endswith('.py'):
   for cls in ast.parse(data).body:
    if isinstance(cls,ast.ClassDef):
     for fn in cls.body:
      if isinstance(fn,ast.FunctionDef) and fn.name.startswith('test_'):names.append(pathlib.Path(n).stem+'.'+cls.name+'.'+fn.name)
 assert len(names)==305 and len(set(names))==305 and len(TESTS)==8 and len(set(TESTS))==8 and set(TESTS)<=set(names)
 assert all(pathlib.Path(p).is_file() for p in LIBS)
 helptext=subprocess.run(['/usr/bin/bwrap','--help'],capture_output=True,text=True,timeout=3,check=True).stdout
 for option in ('--unshare-all','--unshare-user','--disable-userns','--die-with-parent','--new-session','--cap-drop','--clearenv','--ro-bind','--size','--tmpfs','--remount-ro'):assert option in helptext
 version=subprocess.run(['/usr/bin/bwrap','--version'],capture_output=True,text=True,timeout=3,check=True).stdout.strip()
 return {'hashes':{n:digest(data) for n,data in sorted(files.items())},'archive_sha256':archive_hash,'regular_files':92,'payload':90,'checksum_entries':91,'static_tests':305,'python':sys.version,'bwrap':version}
launcher = """import os,sys,resource,ctypes
for name,value in {'RLIMIT_CPU':10,'RLIMIT_AS':268435456,'RLIMIT_NPROC':128,'RLIMIT_FSIZE':8388608,'RLIMIT_NOFILE':64,'RLIMIT_CORE':0}.items():
 resource.setrlimit(getattr(resource,name),(value,value))
assert ctypes.CDLL(None,use_errno=True).prctl(38,1,0,0,0)==0
os.execv(sys.argv[1],sys.argv[1:])
"""
def identities(pid):
    result={}
    def visit(n):
        try:
            fields=pathlib.Path(f'/proc/{n}/stat').read_text().rsplit(')',1)[1].split()
            result[n]=fields[19]
            for child in pathlib.Path(f'/proc/{n}/task/{n}/children').read_text().split():
                visit(int(child))
        except FileNotFoundError:
            pass
    visit(pid)
    return result
def run_case(test, runner, forced=False):
    started=time.monotonic()
    code='MODULES='+repr(MODULES)+'\nTEST_ID='+repr(test)+'\n'+runner
    cmd=['/usr/bin/bwrap','--unshare-all','--unshare-user','--disable-userns',
         '--die-with-parent','--new-session','--cap-drop','ALL','--clearenv',
         '--ro-bind','/usr/bin/python3.12','/usr/bin/python3.12',
         '--ro-bind','/usr/lib/python3.12','/usr/lib/python3.12']
    for path in LIBS: cmd += ['--ro-bind',path,path]
    cmd += ['--ro-bind',str(BASE/'src'),'/release/src',
            '--ro-bind',str(BASE/'tests'),'/release/tests',
            '--size','16777216','--tmpfs','/workspace',
            '--size','16777216','--tmpfs','/tmp',
            '--proc','/proc','--dev','/dev','--remount-ro','/',
            '--setenv','HOME','/tmp/home','--setenv','TMPDIR','/tmp',
            '--setenv','PYTHONDONTWRITEBYTECODE','1',
            '--setenv','PATH','/usr/bin','--setenv','LANG','C.UTF-8',
            '--chdir','/workspace','/usr/bin/python3.12','-I','-S','-B','-c',code]
    with tempfile.TemporaryFile(dir='/tmp', prefix='phase7n-stdout-') as stdout, tempfile.TemporaryFile(dir='/tmp', prefix='phase7n-stderr-') as stderr:
        p=subprocess.Popen(['/usr/bin/python3.12','-I','-S','-B','-c',launcher,*cmd],
            stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,close_fds=True,
            start_new_session=True,env={'PATH':'/usr/bin','LANG':'C.UTF-8'})
        fd=os.pidfd_open(p.pid)
        ready_at=None
        tracked={}; reason=None
        try:
            deadline=time.monotonic()+20
            while p.poll() is None:
                tracked.update(identities(p.pid))
                if forced and os.fstat(stdout.fileno()).st_size and ready_at is None:
                    ready_at=time.monotonic()
                if forced and ready_at is not None and time.monotonic()-ready_at>=0.3:
                    reason='forced preflight cleanup'; break
                if time.monotonic()>=deadline:
                    reason='wall timeout'; break
                if any(os.fstat(f.fileno()).st_size>1048576 for f in (stdout,stderr)):
                    reason='output ceiling'; break
                time.sleep(0.02)
        finally:
            # Kill exact outer launcher. PID-namespace init death kills descendants,
            # including any separate-session descendants; never pkill/killall.
            if not select.select([fd],[],[],0)[0]:
                signal.pidfd_send_signal(fd,signal.SIGKILL)
            p.wait(timeout=3)
            os.close(fd)
            cleanup_deadline=time.monotonic()+3
            while time.monotonic()<cleanup_deadline:
                remaining=[]
                for pid,start in tracked.items():
                    try: os.waitpid(pid,os.WNOHANG)
                    except ChildProcessError: pass
                    path=pathlib.Path(f'/proc/{pid}/stat')
                    try:
                        if path.read_text().rsplit(')',1)[1].split()[19]==start:
                            remaining.append(pid)
                    except FileNotFoundError: pass
                if not remaining: break
                time.sleep(0.02)
            if remaining: raise RuntimeError('tracked process cleanup incomplete; stop')
        for stream in (stdout,stderr):
            stream.seek(0)
            print(stream.read(1048576).decode('utf-8','replace'),flush=True)
        print(json.dumps({'test':test,'exit':p.returncode,'stop_reason':reason,
                          'remaining_tracked':remaining,'tracked':tracked,'seconds':time.monotonic()-started}),flush=True)
        if forced:
            assert reason=='forced preflight cleanup' and p.returncode==-9
            assert len(tracked)>=3
        elif reason or p.returncode: raise SystemExit(1)
before=integrity()
print(json.dumps({'integrity_before':before}),flush=True)
libc=ctypes.CDLL(None,use_errno=True)
assert libc.prctl(36,1,0,0,0)==0
HOST_NS={n:os.readlink('/proc/self/ns/'+n) for n in ('user','mnt','net','pid','ipc','uts')}
listener=socket.socket();listener.bind(('127.0.0.1',0));listener.listen(1)
PORT=listener.getsockname()[1]
try:
    probe="import os,sys,pathlib,json,resource,ctypes,socket,time,errno\nassert sys.version_info[:3]==(3,12,3) and os.getuid()==1000\nexpected={'RLIMIT_CPU':10,'RLIMIT_AS':268435456,'RLIMIT_NPROC':128,'RLIMIT_FSIZE':8388608,'RLIMIT_NOFILE':64,'RLIMIT_CORE':0}\nlimits={k:resource.getrlimit(getattr(resource,k)) for k in expected}\nassert all(limits[k]==(v,v) for k,v in expected.items())\nns={n:os.readlink('/proc/self/ns/'+n) for n in HOST_NS}\nassert all(ns[n]!=HOST_NS[n] for n in ns)\nstatus={l.split(':',1)[0]:l.split(':',1)[1].strip() for l in pathlib.Path('/proc/self/status').read_text().splitlines() if ':' in l}\nassert status['NoNewPrivs']=='1' and int(status['CapEff'],16)==0\nassert ctypes.CDLL(None,use_errno=True).unshare(0x10000000)==-1\nassert all(not pathlib.Path(p).exists() for p in ('/home','/opt','/run','/var','/etc','/root'))\nassert set(os.environ)<={'HOME','TMPDIR','PYTHONDONTWRITEBYTECODE','PATH','LANG','LC_CTYPE','PWD'}\nassert os.environ.get('PWD')=='/workspace'\nassert 'SSH_AUTH_SOCK' not in os.environ\nassert all(line.split(':')[0].strip()=='lo' for line in pathlib.Path('/proc/net/dev').read_text().splitlines()[2:] if ':' in line)\nassert all(line.split()[0]=='lo' for line in pathlib.Path('/proc/net/route').read_text().splitlines()[1:] if line.split())\nfor target in [('127.0.0.1',PORT),('192.0.2.1',9)]:\n with socket.socket() as sock:\n  sock.settimeout(0.3)\n  try:sock.connect(target)\n  except OSError:pass\n  else:raise AssertionError('network unexpectedly accessible')\nfor root in ('/workspace','/tmp'):\n st=os.statvfs(root);assert st.f_blocks*st.f_frsize==16777216\n p=pathlib.Path(root)/'synthetic-preflight';p.write_text('synthetic');p.unlink()\nfor target in ('/outside-synthetic',):\n try:pathlib.Path(target).write_text('synthetic')\n except OSError as exc:assert exc.errno in (errno.EROFS,errno.ENOENT,errno.EACCES)\n else:raise AssertionError('readonly confinement failed')\nmounts={line.split()[4]:line.split()[5].split(',') for line in pathlib.Path('/proc/self/mountinfo').read_text().splitlines()}\nassert all('ro' in mounts[p] for p in ('/','/release/src','/release/tests','/usr/bin/python3.12','/usr/lib/python3.12'))\nassert all('rw' in mounts[p] for p in ('/tmp','/workspace'))\nprint(json.dumps({'preflight':'ISOLATION_LIMITS_PASS','namespaces':ns,'limits':limits,'mountinfo':pathlib.Path('/proc/self/mountinfo').read_text()}),flush=True)\ntime.sleep(21)\n"
    run_case('SYNTHETIC_PREFLIGHT', 'HOST_NS='+repr(HOST_NS)+'\nPORT='+repr(PORT)+'\n'+probe,forced=True)
finally:listener.close()
print('ALL_PREFLIGHT_PASS',flush=True)
runner="import sys,os,importlib,unittest,json\nsys.path[:0]=['/release/src','/release/tests']\nos.mkdir('/tmp/home')\nfor module in MODULES: importlib.import_module(module)\nsuite=unittest.defaultTestLoader.loadTestsFromName(TEST_ID)\nassert suite.countTestCases()==1\nassert tuple(case.id() for case in suite)==(TEST_ID,)\nprint(json.dumps({'actual_test_id':TEST_ID}),flush=True)\nresult=unittest.TextTestRunner(verbosity=2,failfast=True).run(suite)\nimport resource,json\nr=resource.getrusage(resource.RUSAGE_SELF)\nprint(json.dumps({'test_result':TEST_ID,'testsRun':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'imports':len(MODULES),'user_cpu_s':r.ru_utime,'system_cpu_s':r.ru_stime,'maxrss_kib':r.ru_maxrss}),flush=True)\nsys.exit(0 if result.wasSuccessful() and result.testsRun==1 and not result.skipped else 1)\n"
try:
 for test in TESTS:run_case(test,runner)
 print('PHASE7P_EIGHT_SELECTED_TESTS_PASS',flush=True)
finally:
 after=integrity()
 print(json.dumps({'integrity_after':after,'release_unchanged':after==before}),flush=True)
 assert after==before
```

## Disposition

**PASS for these eight additional Linux methods.** No Linux-specific application defect was observed. No Research activation, production Memory/Obsidian access, live model/provider call, Hermes/Photon change, dependency installation, service/configuration change, cgroup/AppArmor modification, commit, push or deployment occurred. Stop after these reports. Full-suite execution and any activation remain outside this result.
