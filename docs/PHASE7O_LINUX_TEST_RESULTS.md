# Phase 7O — limited Linux compatibility test results

2026-10-16 — **PASS: exactly 8 approved tests executed, 8 passed, 0 failures, 0 errors, 0 skips.** Successful retry SSH/supervisor exit: **0**. No full-suite execution, production integration, activation or deployment occurred.

## Original mistake and corrected validation

The original Phase 7O attempt stopped before application execution with exit 1: its validator incorrectly expected `FILES.sha256` to contain only the payload inventory's 90 paths. A read-only diagnostic established the legitimate 91st entry was `RELEASE_INVENTORY.json`. No application tests ran in that original attempt.

The mistaken assertion was `set(sha_entries) == set(expected)`. The corrected coverage assertion is `set(sums) == set(expected) | {'RELEASE_INVENTORY.json'}`, combined with the independent content pins and every listed checksum comparison.

The owner authorized this correction and retry. We inspected the actual staged archive and checksum files. The corrected validator distinguishes:

- **90 payload files** declared in `RELEASE_INVENTORY.json.files`.
- **91 checksum entries** covering exactly those 90 paths plus `RELEASE_INVENTORY.json`.
- **92 extracted regular files and archive members**, adding `FILES.sha256` itself.

Acceptance of the extra inventory checksum is exact and independently pinned, not a general extra-file exception. The validator rejects unsafe/absolute/dot/parent/control-character paths, duplicate JSON keys, duplicate inventory/checksum/archive paths, malformed lowercase SHA-256 lines, missing or extra files, symlinks/special archive members, wrong byte counts and content mismatches. Every archive member is compared byte-for-byte with staging without extracting it. The archive digest is pinned to the Mac release copy; external `SHA256SUMS` must contain precisely that archive entry. The inventory and checksum-file digests are separately pinned to prior accepted inspection evidence.

During synthetic sandbox preflight, a second validator assumption rejected Bubblewrap's generated `PWD` variable. No Research imports or tests had occurred. A synthetic diagnostic printed **variable names only** and found `HOME, LANG, PATH, PWD, PYTHONDONTWRITEBYTECODE, TMPDIR`. The environment check was corrected to permit `PWD` only with the exact value `/workspace`. This corrected validation of benign sandbox metadata; it did not change environment clearing, mounts, namespaces, resource limits or application scope. No unrelated isolation requirement failed. The failed synthetic attempts and their clean exits are recorded below.

## Integrity and runtime

Release root:
`/home/alfred/research-staging/research-v1/alfred-research-v1-0.1.0-phase7e-linux-stage-20261016`.

| Check | Result |
| --- | --- |
| Mac-pinned archive SHA-256 | `ec6dedd835e8c926d5e862a15d392c090e6831fbc84b41f1d5e6848d2c3fe63e` |
| Pinned inventory SHA-256 | `202e45ca9977f538f4e9ce37b187e61e27cc61cba553d0dbac6cdf829cc904c5` |
| Pinned FILES.sha256 SHA-256 | `d3353a8a459bf0f4a606a8ea01430187b1cdc55990136bc4fd75fb8a63f69ad2` |
| Archive / extracted regular files | 92 / 92; all member bytes match |
| Payload / checksum entries | 90 / 91; all verified |
| Static test inventory | 305 methods; exact approved eight confirmed without imports |
| Python | `3.12.3 (main, Aug 31 2026, 10:18:26) [GCC 13.3.0]` |
| Bubblewrap | `bubblewrap 0.9.0` |
| Post-run release and archive comparison | **Unchanged**, all 92 file hashes and archive digest equal before-run values |

## Preflight and controls actually applied

The successful synthetic preflight used the **same Phase 7N Bubblewrap argv, mounts, limits and supervisor** as the application cases. Instrumentation and gating were added for preflight/results; the test runner, eight identifiers, explicit 31-module import list and security/resource settings were retained.

- New user/mount/network/PID/IPC/UTS namespaces verified against host namespace identities; UID 1000, zero effective capabilities, NoNewPrivs=1; additional user namespace creation denied.
- Host `/home`, `/opt`, `/run`, `/var`, `/etc`, `/root` absent. Environment cleared; no SSH_AUTH_SOCK or other inherited service/credential configuration. No host sockets, credential/vault directories or production data mounted. No credential values were inspected.
- No nonloopback interfaces or IPv4 routes. Connection to the preflight's own host-loopback listener was denied; TEST-NET `192.0.2.1:9` connection was denied. No production endpoint was probed. The listener was closed before Research execution.
- `/release/src` and `/release/tests`, Python executable/stdlib, and the eight exact libraries were read-only. Root read-only. Mount flags verified. No broad host-root/home/library mount or host-backed writable workspace was exposed.
- Private `/tmp` and `/workspace` tmpfs mounts each read back **16,777,216 bytes** and permitted synthetic writes. Host root writes denied. HOME was `/tmp/home`; application cases created that synthetic directory. No write attempts were made against release source/test files.
- Hard and soft rlimits read back exactly: CPU 10 s/process, AS 268,435,456 bytes/process, NPROC 128 (shared UID guard), FSIZE 8,388,608 bytes/file, NOFILE 64, CORE 0.
- Supervisor's 20-second wall watchdog and 1 MiB monitored stdout/stderr thresholds remained active. Before application tests, the synthetic namespace was deliberately SIGKILLed through the exact launcher pidfd after readiness plus 0.3 s. Exit **-9** was expected; all three observed PID/starttime identities disappeared within the 3-second cleanup window. This exercised the same kill/reap path while retaining the 20-second deadline. It did not wait for deadline exhaustion; historical 7L covers a separate-session descendant tree.

These checks exclude live Hermes, Photon, Memory, Obsidian and Development access through filesystem/socket/network exposure. Source and SQLite fixtures were synthetic and private. Importing the package's offline Memory modules in the approved import sweep made no production Memory call.

## Exact test results

Each row is a separate fresh namespace and exactly one unittest method. All 31 source modules imported before that method. Wall time includes launcher/import/test/cleanup; unittest duration is the rounded runner transcript value. CPU and RSS are interpreter self-usage (including imports), not aggregate namespace accounting.

| Approved test identifier | Exit | Result | Wall s | CPU s | Peak RSS KiB |
| --- | ---: | --- | ---: | ---: | ---: |
| `test_foundation.FoundationTests.test_packet_roundtrip_and_determinism` | 0 | PASS (1 run, 0 failures/errors/skips) | 0.394937 | 0.337916 | 27012 |
| `test_foundation.FoundationTests.test_malformed_and_ambiguous_contracts` | 0 | PASS (1 run, 0 failures/errors/skips) | 0.416540 | 0.344756 | 27076 |
| `test_foundation.FoundationTests.test_cross_environment_read_write_denied` | 0 | PASS (1 run, 0 failures/errors/skips) | 0.498623 | 0.426725 | 27088 |
| `test_sources.SourceTests.test_all_source_categories_and_environments` | 0 | PASS (1 run, 0 failures/errors/skips) | 0.395631 | 0.332867 | 27056 |
| `test_sources.SourceTests.test_result_roundtrip_hash_and_determinism` | 0 | PASS (1 run, 0 failures/errors/skips) | 0.374401 | 0.313368 | 26580 |
| `test_sources.SourceTests.test_every_cross_environment_pair_and_principal_denied` | 0 | PASS (1 run, 0 failures/errors/skips) | 0.376638 | 0.314585 | 26584 |
| `test_sources.SourceTests.test_local_fixture_roots_are_environment_isolated` | 0 | PASS (1 run, 0 failures/errors/skips) | 0.397530 | 0.340861 | 27032 |
| `test_sources.SourceTests.test_local_fixture_directory_no_execution_symlink_follow_or_writes` | 0 | PASS (1 run, 0 failures/errors/skips) | 0.395985 | 0.320282 | 27008 |

Total application sandbox wall time: **3.250286 s**. Sum of rounded unittest durations: **0.249 s**. Sum of interpreter self CPU: **2.731360 s**. Maximum interpreter peak RSS: **27,088 KiB**. Successful synthetic forced-cleanup case: **0.419002 s**. These totals exclude transport, static archive preflight and validator-diagnostic attempts.

No application timeout, output-ceiling event, resource denial or Linux compatibility failure occurred. No whole-tree peak memory, aggregate CPU quota or tmpfs high-water measurement was made; cgroups were not changed or tested. tmpfs capacity and per-process ceilings are verified limits, not measured peak consumption.

## Cleanup evidence

Every application run and every synthetic preflight attempt reported `remaining_tracked=[]`. The supervisor tracked only descendants of its own launcher via task children links, recording PID/starttime, and used an exact pidfd for forced termination. It acted as child subreaper, checked matching identities after waits, and never used process-name/account-wide signaling. No separate application child or thread was observed; each case showed outer launcher, namespace reaper and interpreter. Polling is scoped observed-tree evidence, not an adversarial unlimited-fan-out guarantee.

The successful run's tracked identities (PID:starttime ticks):

- `SYNTHETIC_PREFLIGHT`: 333134:5709627, 333135:5709629, 333136:5709630; none remained.
- `test_foundation.FoundationTests.test_packet_roundtrip_and_determinism`: 333159:5709669, 333160:5709671, 333161:5709672; none remained.
- `test_foundation.FoundationTests.test_malformed_and_ambiguous_contracts`: 333162:5709708, 333163:5709711, 333164:5709711; none remained.
- `test_foundation.FoundationTests.test_cross_environment_read_write_denied`: 333165:5709750, 333166:5709752, 333167:5709753; none remained.
- `test_sources.SourceTests.test_all_source_categories_and_environments`: 333168:5709800, 333169:5709802, 333170:5709803; none remained.
- `test_sources.SourceTests.test_result_roundtrip_hash_and_determinism`: 333175:5709840, 333176:5709842, 333177:5709842; none remained.
- `test_sources.SourceTests.test_every_cross_environment_pair_and_principal_denied`: 333178:5709877, 333179:5709879, 333180:5709880; none remained.
- `test_sources.SourceTests.test_local_fixture_roots_are_environment_isolated`: 333182:5709915, 333183:5709917, 333184:5709918; none remained.
- `test_sources.SourceTests.test_local_fixture_directory_no_execution_symlink_follow_or_writes`: 333188:5709955, 333189:5709957, 333190:5709957; none remained.

Private tmpfs mounts vanished with their namespaces. Unlinked supervisor TemporaryFile logs were closed at each case's context exit. The synthetic host listener closed in finally. No release writeback or Linux script installation occurred. Before/after integrity validation verified all extracted source/tests, manifests and other release files unchanged; no `.pyc` or extra release files appeared.

## Command accounting

SSH used BatchMode=yes, StrictHostKeyChecking=yes, ConnectTimeout=8 and ConnectionAttempts=1 throughout. An initial sandbox-denied locator call exited 255 before remote execution, then the approved retry exited 0. Read-only locator command:

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'find /home/alfred/research-staging/research-v1 -maxdepth 2 -type f -print'
```

Read-only checksum-format inspection, exit 0:

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'cat /home/alfred/research-staging/research-v1/SHA256SUMS; head -n 4 /home/alfred/research-staging/research-v1/alfred-research-v1-0.1.0-phase7e-linux-stage-20261016/FILES.sha256'
```

All script paths below are **Mac-local**, streamed on SSH stdin; scripts were not saved on Linux:

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B -' < /tmp/phase7o_retry_integrity.py > /tmp/phase7o_retry_integrity.out 2> /tmp/phase7o_retry_integrity.err
```

Exit **0**: corrected static/archive validation only.

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B -' < /tmp/phase7o_retry_run.py > /tmp/phase7o_retry_run.out 2> /tmp/phase7o_retry_run.err
```

Exit **1**: synthetic environment validator rejection; zero Research tests.

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B -' < /tmp/phase7o_retry_env.py > /tmp/phase7o_retry_env.out 2> /tmp/phase7o_retry_env.err
```

Exit **1**: synthetic variable-name diagnostic; zero Research tests.

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B -' < /tmp/phase7o_retry_corrected.py > /tmp/phase7o_retry_corrected.out 2> /tmp/phase7o_retry_corrected.err
```

Exit **0**: successful preflight and exact eight tests.

The first synthetic runner differed from the successful body below only in rejecting PWD in the environment allowlist. The diagnostic body used that same failing check with a variable-name print immediately before it, and omitted the application-execution tail entirely. Thus neither failed attempt could import or run Research. Their observed launcher exits were 1, no stop_reason/timeouts, and no tracked identities remained:

```json
{"test": "SYNTHETIC_PREFLIGHT", "exit": 1, "stop_reason": null, "remaining_tracked": [], "tracked": {"329023": "5645876", "329024": "5645878", "329025": "5645879"}, "seconds": 0.08381738899333868}
```

```json
{"test": "SYNTHETIC_PREFLIGHT", "exit": 1, "stop_reason": null, "remaining_tracked": [], "tracked": {"332933": "5707545", "332934": "5707547", "332935": "5707548"}, "seconds": 0.08430643799511017}
```

The standalone integrity script consisted of the successful body's imports/constants/integrity helpers through the end of `integrity()`, followed by `print(json.dumps(integrity()),flush=True)`. The complete successful executable body follows, preserving exact constants, mount allowlist, limits, test IDs and cleanup operations. Local syntax checks parsed this body without importing Research.

```python
import os,sys,pathlib,json,hashlib,ast,re,tarfile,subprocess,time,resource,ctypes,signal,tempfile,select,socket
BASE=pathlib.Path('/home/alfred/research-staging/research-v1/alfred-research-v1-0.1.0-phase7e-linux-stage-20261016')
TESTS=['test_foundation.FoundationTests.test_packet_roundtrip_and_determinism', 'test_foundation.FoundationTests.test_malformed_and_ambiguous_contracts', 'test_foundation.FoundationTests.test_cross_environment_read_write_denied', 'test_sources.SourceTests.test_all_source_categories_and_environments', 'test_sources.SourceTests.test_result_roundtrip_hash_and_determinism', 'test_sources.SourceTests.test_every_cross_environment_pair_and_principal_denied', 'test_sources.SourceTests.test_local_fixture_roots_are_environment_isolated', 'test_sources.SourceTests.test_local_fixture_directory_no_execution_symlink_follow_or_writes']
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
runner="import sys,os,importlib,unittest\nsys.path[:0]=['/release/src','/release/tests']\nos.mkdir('/tmp/home')\nfor module in MODULES: importlib.import_module(module)\nsuite=unittest.defaultTestLoader.loadTestsFromName(TEST_ID)\nassert suite.countTestCases()==1\nresult=unittest.TextTestRunner(verbosity=2,failfast=True).run(suite)\nimport resource,json\nr=resource.getrusage(resource.RUSAGE_SELF)\nprint(json.dumps({'test_result':TEST_ID,'testsRun':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'imports':len(MODULES),'user_cpu_s':r.ru_utime,'system_cpu_s':r.ru_stime,'maxrss_kib':r.ru_maxrss}),flush=True)\nsys.exit(0 if result.wasSuccessful() and result.testsRun==1 and not result.skipped else 1)\n"
try:
 for test in TESTS:run_case(test,runner)
 print('EIGHT_SELECTED_TESTS_PASS',flush=True)
finally:
 after=integrity()
 print(json.dumps({'integrity_after':after,'release_unchanged':after==before}),flush=True)
 assert after==before
```

## Final disposition

**PASS for the limited eight-test Linux compatibility subset only.** The full 305-test suite was not run and remains outside this authorization. No package installation, service/configuration change, cgroup/AppArmor modification, company-data/vault/credential access, live provider call, production Memory/Obsidian write, Research activation/registration, commit, push or deployment occurred. Stop after reporting and await owner review.
