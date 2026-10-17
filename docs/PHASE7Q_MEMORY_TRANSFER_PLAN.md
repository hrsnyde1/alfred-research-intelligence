# Phase 7Q — exact Memory transfer and isolated comparison plan

2026-10-16. **Documentation only. No Linux writes, transfer, Memory import or Memory test execution occurred.** Everything labelled future below requires owner approval. Do not run the former full-discovery driver `artifacts/staging/phase7h-memory/run_tests.py`; it spawns a child, discovers the full copied suite and writes beside source evidence.

## Input inventory and destination

Proposed fresh Linux root: `/home/alfred/research-staging/phase7q-memory-20261016`, UID 1000, mode 0700. Read-only metadata inspection found it absent and its `/home/alfred/research-staging` parent owned by UID 1000. Absence is a snapshot, not a reservation: before a later transfer reject a preexisting/symlinked leaf or symlinked/unsafe parent. Refuse reuse; no delete/overwrite fallback. Preserve repository-relative paths below the new root.

Transfer exactly **17 existing Mac files**, **294,342 bytes**, below. This reduces the audited earlier 92-file Memory allowlist; no change to its existing files/hashes is proposed. The 92 entries and baseline 34 were all rehashed locally and match. Do not confuse these counts with the separate 92-file extracted Research release.

| Repository-relative transfer path | Bytes | SHA-256 |
| --- | ---: | --- |
| `artifacts/staging/phase7h-memory/BASELINE_MANIFEST.json` | 5936 | `13c01987ac459d9aa95ef266cc39884a909f88e93bc1dbc4fa5ed6fa03e7b700` |
| `artifacts/staging/phase7h-memory/baseline/deploy/focused-v1/obsidian_export.py` | 14044 | `ba42372ba7221a1273f14e07a10688694997abb468ab18ed92e601d2aef11d54` |
| `artifacts/staging/phase7h-memory/baseline/focused_v1/__init__.py` | 84 | `a45b4b3c132df7e1d8c830087185e752fc3dcd8f26b9d4a56e6626fe2dc3f8cb` |
| `artifacts/staging/phase7h-memory/baseline/focused_v1/store.py` | 29402 | `5ca002bd93e486875191292c21ba782fb2df5eb3fa4d525654e80ad29069cf8c` |
| `artifacts/staging/phase7h-memory/baseline/tests/test_focused_v1_obsidian_export.py` | 9810 | `8e7cc28875fc714a517ec13755af2a1e7e42b8cabefac37a075b253626d481b1` |
| `artifacts/staging/phase7h-memory/work/deploy/focused-v1/obsidian_export.py` | 14044 | `ba42372ba7221a1273f14e07a10688694997abb468ab18ed92e601d2aef11d54` |
| `artifacts/staging/phase7h-memory/work/focused_v1/__init__.py` | 84 | `a45b4b3c132df7e1d8c830087185e752fc3dcd8f26b9d4a56e6626fe2dc3f8cb` |
| `artifacts/staging/phase7h-memory/work/focused_v1/research_stage.py` | 23383 | `15e24eb7aa3f84f8796d12dd9d4684d2748943cfda58dc3fa8827428b12dcd3a` |
| `artifacts/staging/phase7h-memory/work/focused_v1/server.py` | 3971 | `2042c95d517601da03654b942b04bf96ed69bedf5afa0351ef64463542eba5ea` |
| `artifacts/staging/phase7h-memory/work/focused_v1/store.py` | 29426 | `0d84c9c12c0715f14be7729a5007073ebc99f55fa7820e6bed81a55834d969c1` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/__init__.py` | 226 | `ad5ff6eece3dceb083367cd470edd09eda66d1bb5fcd134905df9ed0a6a06e8f` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/bridge.py` | 92185 | `775448b247c3a8813cbd3f94a2b1e17fe211c9fca1a72033b165ee7e0226a818` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/outcome_gate.py` | 14151 | `9ebc79cb0eb4e93e35b17e9b54a30de100b0abd6d724dacfbb794a8ecab2de8f` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/service_api.py` | 22969 | `f7fdcd5b01bf12b13415b8f4bbd7edbb7629ae0856b7267bca743b6773282cc5` |
| `artifacts/staging/phase7h-memory/work/obsidian_candidate/snapshot.py` | 4167 | `d27b3b5dc2b67476da421ca10128651352ca0ed4c584cde40204ac6e5be47b43` |
| `artifacts/staging/phase7h-memory/work/tests/test_focused_v1_obsidian_export.py` | 9810 | `8e7cc28875fc714a517ec13755af2a1e7e42b8cabefac37a075b253626d481b1` |
| `artifacts/staging/phase7h-memory/work/tests/test_research_memory_stage.py` | 20650 | `53e1f0b095443401ec79daa8a0a7c534a48c47b649972395123af1d457e6cd1e` |

Baseline has four files: focused package/store plus one existing export test and its exporter. Work has twelve: those four, server, extension, extension tests, and five obsidian import-closure modules. The seventeenth file is BASELINE_MANIFEST.json for provenance/subset checks. This is a partial copy by design; do not expect full 34/36-file copied suites to import/run from it. No original test/source file is edited.

Do not transfer archives, prior result logs/JSON, CHANGES.patch, old full-suite runner, device/Node helpers, deployment/SSH/public-key fixtures, account/skeleton files, databases, ledgers, configs, .env, vaults, caches or credentials. The manifest contains source provenance only. Synthetic deletion keys/tokens are generated later inside private test memory and are not transfer inputs.

Reuse **20 exact files** from the already extracted Research release, without transfer or modification: 19 package modules and tests/test_research.py, listed in the machine manifest below. Reverify each hash/length and the frozen release integrity before a future launch. Map them to `/workspace/src/...` and `/workspace/tests/test_research.py`. This preserved layout is required because the extension test computes `Path(__file__).resolve().parents[5]` as `/workspace`; binding it at an arbitrary shallower root would break its fixture imports. Do not import from live `/opt`, installed Alfred packages or a differently revised local Research checkout.

## Runtime closure requiring new mount approval

The seven extension cases do not need Node, PDF parsing, network fixtures, Linux atomic-rename operations, account/NSS fixtures or privileged ownership changes. They **do need cryptography**: store.py unconditionally imports AESGCM, even when selected lifecycle tests never use real credentials. Existing Research runtime binds alone are therefore insufficient.

Read-only Linux inspection found cryptography source version **41.0.7**, one `_rust.abi3.so`, and `_cffi_backend.cpython-312-x86_64-linux-gnu.so`. ldd showed Rust bindings also require `libssl.so.3` and `libgcc_s.so.1` beyond existing libraries. The unchanged cryptography OpenSSL bootstrap attempts to load its legacy provider; include the exact public runtime file `/usr/lib/x86_64-linux-gnu/ossl-modules/legacy.so`. Do not expose `/etc/ssl`, OpenSSL config or whole distro/site-package directories, and do not disable legacy initialization to paper over a missing mount.

The machine manifest pins **85 individual runtime files**: the previously approved eight shared libraries plus **77 additions** (73 cryptography Python/native files, one CFFI backend, libssl, libgcc_s and legacy.so). Original source/resolved paths, byte counts and hashes were read without importing cryptography or executing Memory. The 77 additions total 4,410,762 bytes on disk; this is not a memory-consumption measurement. No cffi Python package/pycparser was found or selected; the installed cryptography bindings use the native backend. A missing runtime import must stop execution, not silently widen sys.path or mount an entire host tree.

All 85 files are proposed read-only same-path binds. Keep Python executable and `/usr/lib/python3.12` stdlib read-only as before. Explicitly insert `/usr/lib/python3/dist-packages` into isolated Python sys.path; mount **only listed files** beneath that path, no `.pth`, user site or auto-discovered package code. Validate resolved runtime targets and hashes before/after. A future in-sandbox crypto preflight must validate the AESGCM round-trip with random synthetic key/nonce, native package version/origins and temporary SQLite commit/reopen. Installed files/ldd are preparation evidence, not proof these imports work in the namespace.

## Mount, limits and output contract

Each case uses `--unshare-all --unshare-user --disable-userns --die-with-parent --new-session --cap-drop ALL --clearenv`, NoNewPrivs=1 and UID 1000. No host network, host PID namespace or inherited service descriptors. Source mounts are placed **after** private `/workspace` tmpfs creation and **before** root read-only remount, so scratch mounts cannot hide input binds.

| Destination | Source/access |
| --- | --- |
| `/workspace/artifacts/staging/phase7h-memory/<area>` | Only selected baseline OR work source copy, read-only |
| `/workspace/src/...` and `/workspace/tests/test_research.py` | Twenty exact existing extracted Research files, read-only |
| `/comparison/test_research_memory_stage.py` | Work test source read-only, only in duplicate comparison mode; parsed as text/AST, never imported into baseline |
| `/usr/bin/python3.12`, `/usr/lib/python3.12` | Existing read-only runtime |
| Runtime manifest's 85 absolute files | Exact same-path read-only binds |
| `/workspace`, `/tmp` | Fresh private 16 MiB tmpfs each; input submounts stay read-only |
| `/proc`, `/dev` | Private procfs and Bubblewrap synthetic dev |
| `/` | Read-only root |

Only `/tmp` and the unmounted scratch portions of `/workspace` receive test writes. HOME=`/tmp/home`, TMPDIR=`/tmp`, PWD=`/workspace`; environment contains only these, PATH, LANG and PYTHONDONTWRITEBYTECODE (plus Python locale metadata if emitted). No /home, /opt, /run, /var, /etc, host sockets, company vaults or SSH agent environment. No persistent writable result directory is exposed to test code. Supervisor uses per-case unlinked host `/tmp/phase7n-stdout-*` / `phase7n-stderr-*` logs, closing them after bounded capture; output is returned via SSH to **Mac-local** result files. Tests' stdio descriptors reference these logs; they are not general host filesystem mounts.

Hard=soft controls retained from Phase 7O/P: CPU 10 s/process, AS 268,435,456 bytes/process, NPROC 128 shared-UID guard, FSIZE 8,388,608 bytes/file, NOFILE 64, CORE 0. Per-case wall 20 s; monitored output 1 MiB/stream (8 MiB per-file hard ceiling on child writes); exact-pidfd kill and 3-second collection/reap/identity-check windows. Fresh namespaces serially, no xdist/thread pool/process workload. Additional campaign bound 300 s; do not start another case with less than 26 s remaining. No cgroup or AppArmor writes.

Preflight repeats namespace/mount/network/resource checks from 7P, adds exact Memory runtime AESGCM/SQLite checks, and forces only its own synthetic launcher through the cleanup path before importing Memory tests. Host-loopback denial uses only a probe-owned listener, closed before cases; outbound probe uses TEST-NET. No production endpoint is tested. Failure stops before Memory execution; no package installation or mount broadening fallback.

## Exact comparison cases

**Eleven planned invocations, not eleven claimed passes:** seven existing work extension methods, one original regression run in both copies, and a duplicate-response comparison probe in both copies. All require separate approval. The proposed owner-selected extension scope remains seven methods.

1. Baseline duplicate probe: `__main__.DuplicateStateComparison.test_duplicate_create_actual_pending_rejected_approved` — expected **one assertion failure** on pending response being wrongly approved, no errors/skips. Record raw exit 1; classify only that exact failure as the negative baseline witness.
2. Work duplicate probe: same ID and extracted method body, raw exit 0 required.
3. Baseline original regression: `test_focused_v1_obsidian_export.ObsidianExportTests.test_existing_unmanaged_note_is_not_overwritten` — raw exit 0 required.
4. Work original regression: same existing test ID/file bytes, raw exit 0 required.
5–11. Work only: the exact seven IDs in PHASE7Q_MEMORY_TEST_SCOPE.md / the CASES list below, one method per process. All must pass with no skip.

The duplicate probe preserves the existing method's original assertions, extracting **only that method** through AST into a standalone minimal MemoryStore fixture. It cannot import the absent baseline `research_stage.py`; no work extension is overlaid onto baseline. VersionedMemoryStore inherits this create branch unchanged, so a direct MemoryStore fixture tests the same changed implementation. Label this as a derived comparison harness, not an unchanged full-extension test on baseline. Baseline has no Research extension: extension methods are **NOT APPLICABLE**, never fabricated as baseline passes or missing-case failures.

The baseline negative witness is narrow: original test aborts on the first pending-state assertion, so do not claim it exercised rejected/approved states afterward. Work must complete all three states and unchanged-row assertions. An unexpected baseline pass, different failure, error/skip or any work failure blocks comparison; the harness does not swallow failures or change source assertions.

The original Obsidian control creates a temporary synthetic vault/Home.md and expects export refusal without altering those bytes or creating an archive. It does not use LIVE_DATABASE, the service account, /etc/passwd, renameat2, a real vault or live export. It is limited regression evidence, not validation of all Obsidian/HQ/Sync behavior.

Workload argument vectors (only inside the validated resource/supervisor prefix) are built exactly as follows; never run these unisolated on the host:

```text
/usr/bin/python3.12 -I -S -B -c <reviewed single-case runner> baseline duplicate __main__.DuplicateStateComparison.test_duplicate_create_actual_pending_rejected_approved
/usr/bin/python3.12 -I -S -B -c <same runner> work duplicate __main__.DuplicateStateComparison.test_duplicate_create_actual_pending_rejected_approved
/usr/bin/python3.12 -I -S -B -c <same runner> baseline legacy test_focused_v1_obsidian_export.ObsidianExportTests.test_existing_unmanaged_note_is_not_overwritten
/usr/bin/python3.12 -I -S -B -c <same runner> work legacy test_focused_v1_obsidian_export.ObsidianExportTests.test_existing_unmanaged_note_is_not_overwritten
```

For the seven work extension operations, area=`work`, mode=`extension`, and test_id is exactly one ID from the frozen list. The proposed supervisor below embeds all invocations; it performs no discovery.

## Future transfer commands — not run

First approve the 17 source/evidence bytes and the runtime/harness plan. The following Mac preparation parses only the document's manifest, verifies local source hashes/lengths and writes an exact rsync file list. It does not itself transfer or launch tests:

```python
import json,re,hashlib,pathlib
text=pathlib.Path('docs/PHASE7Q_MEMORY_TRANSFER_PLAN.md').read_text()
block=text.split('<!-- PHASE7Q_MANIFEST_BEGIN -->\n```json\n',1)[1].split('\n```\n<!-- PHASE7Q_MANIFEST_END -->',1)[0]
m=json.loads(block)
assert len(m['transfer'])==17
for row in m['transfer']:
 p=pathlib.Path(row['path'])
 assert not p.is_symlink() and p.is_file()
 assert p.stat().st_size==row['bytes'] and hashlib.sha256(p.read_bytes()).hexdigest()==row['sha256']
pathlib.Path('/tmp/phase7q-transfer.list').write_text(''.join(row['path']+'\n' for row in m['transfer']))
```

After separate transfer approval, use strict SSH to recheck parent metadata and create only the absent 0700 leaf (and implied approved relative directories). Refuse existing paths/symlinks; no reuse/delete. Future creation command:

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B -' <<'FUTURE_TRANSFER_APPROVAL_ONLY'
import os,pathlib
parent=pathlib.Path('/home/alfred/research-staging')
stage=parent/'phase7q-memory-20261016'
assert os.getuid()==1000 and parent.is_dir() and not parent.is_symlink()
assert parent.stat().st_uid==1000 and not parent.stat().st_mode & 0o022
assert not os.path.lexists(stage)
os.umask(0o077)
stage.mkdir(mode=0o700)
FUTURE_TRANSFER_APPROVAL_ONLY
```

Exact source-only transfer, future approval only (rsync availability is unverified; if absent, stop or review exact per-file scp, never install):

```sh
rsync --relative --files-from=/tmp/phase7q-transfer.list --chmod=D700,F600   -e 'ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1'   ./ alfred@192.168.50.81:/home/alfred/research-staging/phase7q-memory-20261016/
```

There is no `--delete`, recursive repository/archive transfer or source modification. Hash-check exact remote file membership against the 17-entry manifest before accepting transfer. Existing dirs must contain only approved implied paths; unknown entries/symlinks stop. Never use this plan to overwrite the existing Research release or service tree.

## Proposed executable supervisor — not run

The text below is a new, **unexecuted** adaptation of the verified 7P supervisor. It has been parsed locally for syntax only, with no Memory imports. The new read-only runtime/input binds and comparison harness need owner review and a future sandbox preflight. Do not describe this Memory-specific launcher as dynamically verified.

Supervisor body SHA-256: `b7077be1eab5137eb447ea6be1d96ad08ba1f7c9db237826845c31cc1b4b1338`.
Single-case harness SHA-256 (embedded string UTF-8 bytes): `13469aefa6ead7dd1a20b9e0abeff8e1dec1c00a55c442c39b2941d55581c8b5`.
Fully composed executable (`MANIFEST=` + repr(parsed manifest) + LF + body) SHA-256: `208b52a3a00066aedf0f2fcfb61588e6b50d183d1894ef99836776c91d17cbc6`.
Canonical manifest SHA-256 (json.dumps sort_keys=True, separators=(',',':') + LF): `9fb28a7c43f94214e2d93796e40cb53b812af34844387b25e5c058913188e566`.

After approval, reconstruct on the Mac, check these hashes, and only then stream to Linux. No executable artifact needs to be installed or mounted on Linux:

```python
import pathlib,json,hashlib
text=pathlib.Path('docs/PHASE7Q_MEMORY_TRANSFER_PLAN.md').read_text()
m=json.loads(text.split('<!-- PHASE7Q_MANIFEST_BEGIN -->\n```json\n',1)[1].split('\n```\n<!-- PHASE7Q_MANIFEST_END -->',1)[0])
body=text.split('<!-- PHASE7Q_SUPERVISOR_BEGIN -->\n```python\n',1)[1].split('\n```\n<!-- PHASE7Q_SUPERVISOR_END -->',1)[0]+'\n'
code='MANIFEST='+repr(m)+'\n'+body
assert hashlib.sha256(body.encode()).hexdigest()=='b7077be1eab5137eb447ea6be1d96ad08ba1f7c9db237826845c31cc1b4b1338'
assert hashlib.sha256(code.encode()).hexdigest()=='208b52a3a00066aedf0f2fcfb61588e6b50d183d1894ef99836776c91d17cbc6'
pathlib.Path('/tmp/phase7q-execution-proposed.py').write_text(code)
```

Future test execution command, only after both source-transfer and test/preflight approvals:

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B -'   < /tmp/phase7q-execution-proposed.py > /tmp/phase7q-linux-results.txt 2> /tmp/phase7q-linux-stderr.txt
```

<!-- PHASE7Q_SUPERVISOR_BEGIN -->
```python
import os,sys,pathlib,json,hashlib,subprocess,time,resource,ctypes,signal,tempfile,select,socket
from pathlib import Path
STAGE=Path('/home/alfred/research-staging/phase7q-memory-20261016')
RESEARCH=Path('/home/alfred/research-staging/research-v1/alfred-research-v1-0.1.0-phase7e-linux-stage-20261016')
MEM=Path('artifacts/staging/phase7h-memory')
LIBS=[row['path'] for row in MANIFEST['runtime']]
CAMPAIGN_DEADLINE=time.monotonic()+300

def integrity():
 assert os.getuid()==1000 and sys.version_info[:3]==(3,12,3)
 assert STAGE.is_dir() and not STAGE.is_symlink() and STAGE.stat().st_uid==1000
 paths=list(STAGE.rglob('*'))
 assert not any(p.is_symlink() for p in paths)
 assert all(p.is_file() or p.is_dir() for p in paths)
 expected={r['path']:r for r in MANIFEST['transfer']}
 assert len(expected)==17 and {str(p.relative_to(STAGE)) for p in paths if p.is_file()}==set(expected)
 hashes={}
 for category,base in [('transfer',STAGE),('reuse_research',RESEARCH),('runtime',Path('/'))]:
  for row in MANIFEST[category]:
   path=base/row['path']
   if category!='runtime':assert not path.is_symlink()
   assert path.is_file() and path.stat().st_size==row['bytes']
   data=hashlib.sha256(path.read_bytes()).hexdigest();assert data==row['sha256'],str(path)
   if category=='runtime':assert str(path.resolve())==row['resolved']
   hashes[str(path)]=data
 return hashes
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
def run_case(area,mode,test,runner,forced=False):
    started=time.monotonic()
    code=runner
    cmd=['/usr/bin/bwrap','--unshare-all','--unshare-user','--disable-userns',
         '--die-with-parent','--new-session','--cap-drop','ALL','--clearenv',
         '--ro-bind','/usr/bin/python3.12','/usr/bin/python3.12',
         '--ro-bind','/usr/lib/python3.12','/usr/lib/python3.12']
    for path in LIBS: cmd += ['--ro-bind',path,path]
    cmd += [
            '--size','16777216','--tmpfs','/workspace',
            '--size','16777216','--tmpfs','/tmp',
            '--proc','/proc','--dev','/dev','--remount-ro','/',
            '--setenv','HOME','/tmp/home','--setenv','TMPDIR','/tmp',
            '--setenv','PYTHONDONTWRITEBYTECODE','1',
            '--setenv','PATH','/usr/bin','--setenv','LANG','C.UTF-8',
            '--chdir','/workspace','/usr/bin/python3.12','-I','-S','-B','-c',code,area,mode,test]
    cmd[cmd.index('--remount-ro'):cmd.index('--remount-ro')]=['--ro-bind',str(STAGE/MEM/area),str(Path('/workspace')/MEM/area)]
    for row in MANIFEST['reuse_research']:
        cmd[cmd.index('--remount-ro'):cmd.index('--remount-ro')]=['--ro-bind',str(RESEARCH/row['path']),'/workspace/'+row['path']]
    if mode=='duplicate':
        cmd[cmd.index('--remount-ro'):cmd.index('--remount-ro')]=['--ro-bind',str(STAGE/MEM/'work/tests/test_research_memory_stage.py'),'/comparison/test_research_memory_stage.py']
    with tempfile.TemporaryFile(dir='/tmp', prefix='phase7n-stdout-') as stdout, tempfile.TemporaryFile(dir='/tmp', prefix='phase7n-stderr-') as stderr:
        p=subprocess.Popen(['/usr/bin/python3.12','-I','-S','-B','-c',launcher,*cmd],
            stdin=subprocess.DEVNULL,stdout=stdout,stderr=stderr,close_fds=True,
            start_new_session=True,env={'PATH':'/usr/bin','LANG':'C.UTF-8'})
        fd=os.pidfd_open(p.pid)
        ready_at=None
        tracked={}; reason=None
        try:
            deadline=min(time.monotonic()+20,CAMPAIGN_DEADLINE)
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
        elif area=='baseline' and mode=='duplicate':
            assert reason is None and p.returncode==1
            stdout.seek(0)
            summaries=[]
            for line in stdout.read(1048576).decode('utf-8','replace').splitlines():
                try: summaries.append(json.loads(line))
                except ValueError: pass
            assert len(summaries)==1
            result=summaries[0]
            assert result['actual_test']==test and result['run']==1
            assert not result['errors'] and not result['skipped'] and len(result['failures'])==1
            failed_id,trace=result['failures'][0]
            assert failed_id==test and "AssertionError: 'approved' != 'pending'" in trace
            assert 'test_duplicate_create_actual_pending_rejected_approved' in trace
            print('EXPECTED_BASELINE_DUPLICATE_STATE_FAILURE',flush=True)
        elif reason or p.returncode: raise SystemExit(1)
before=integrity()
print(json.dumps({'input_integrity_before':before}),flush=True)
libc=ctypes.CDLL(None,use_errno=True)
assert libc.prctl(36,1,0,0,0)==0
HOST_NS={n:os.readlink('/proc/self/ns/'+n) for n in ('user','mnt','net','pid','ipc','uts')}
listener=socket.socket();listener.bind(('127.0.0.1',0));listener.listen(1)
PORT=listener.getsockname()[1]
try:
 probe="import sys\nsys.path.insert(0,'/usr/lib/python3/dist-packages')\nimport os,sys,pathlib,json,resource,ctypes,socket,time,errno\nassert sys.version_info[:3]==(3,12,3) and os.getuid()==1000\nexpected={'RLIMIT_CPU':10,'RLIMIT_AS':268435456,'RLIMIT_NPROC':128,'RLIMIT_FSIZE':8388608,'RLIMIT_NOFILE':64,'RLIMIT_CORE':0}\nlimits={k:resource.getrlimit(getattr(resource,k)) for k in expected}\nassert all(limits[k]==(v,v) for k,v in expected.items())\nns={n:os.readlink('/proc/self/ns/'+n) for n in HOST_NS}\nassert all(ns[n]!=HOST_NS[n] for n in ns)\nstatus={l.split(':',1)[0]:l.split(':',1)[1].strip() for l in pathlib.Path('/proc/self/status').read_text().splitlines() if ':' in l}\nassert status['NoNewPrivs']=='1' and int(status['CapEff'],16)==0\nassert ctypes.CDLL(None,use_errno=True).unshare(0x10000000)==-1\nassert all(not pathlib.Path(p).exists() for p in ('/home','/opt','/run','/var','/etc','/root'))\nassert set(os.environ)<={'HOME','TMPDIR','PYTHONDONTWRITEBYTECODE','PATH','LANG','LC_CTYPE','PWD'}\nassert os.environ.get('PWD')=='/workspace'\nassert 'SSH_AUTH_SOCK' not in os.environ\nassert all(line.split(':')[0].strip()=='lo' for line in pathlib.Path('/proc/net/dev').read_text().splitlines()[2:] if ':' in line)\nassert all(line.split()[0]=='lo' for line in pathlib.Path('/proc/net/route').read_text().splitlines()[1:] if line.split())\nfor target in [('127.0.0.1',PORT),('192.0.2.1',9)]:\n with socket.socket() as sock:\n  sock.settimeout(0.3)\n  try:sock.connect(target)\n  except OSError:pass\n  else:raise AssertionError('network unexpectedly accessible')\nfor root in ('/workspace','/tmp'):\n st=os.statvfs(root);assert st.f_blocks*st.f_frsize==16777216\n p=pathlib.Path(root)/'synthetic-preflight';p.write_text('synthetic');p.unlink()\nfor target in ('/outside-synthetic',):\n try:pathlib.Path(target).write_text('synthetic')\n except OSError as exc:assert exc.errno in (errno.EROFS,errno.ENOENT,errno.EACCES)\n else:raise AssertionError('readonly confinement failed')\nmounts={line.split()[4]:line.split()[5].split(',') for line in pathlib.Path('/proc/self/mountinfo').read_text().splitlines()}\nassert all('ro' in mounts[p] for p in ('/','/workspace/artifacts/staging/phase7h-memory/work','/usr/bin/python3.12','/usr/lib/python3.12'))\nassert all('rw' in mounts[p] for p in ('/tmp','/workspace'))\nfrom cryptography.hazmat.primitives.ciphers.aead import AESGCM\nimport cryptography,_cffi_backend,secrets\nassert cryptography.__version__=='41.0.7'\nassert pathlib.Path(cryptography.__file__).is_relative_to('/usr/lib/python3/dist-packages/cryptography')\nassert pathlib.Path(_cffi_backend.__file__).is_relative_to('/usr/lib/python3/dist-packages')\nkey=secrets.token_bytes(32);nonce=secrets.token_bytes(12)\naes=AESGCM(key);cipher=aes.encrypt(nonce,b'synthetic-memory-fixture',b'phase7q')\nassert aes.decrypt(nonce,cipher,b'phase7q')==b'synthetic-memory-fixture'\ndel aes,key,nonce,cipher\nimport sqlite3,tempfile\nwith tempfile.TemporaryDirectory() as directory:\n path=pathlib.Path(directory)/'synthetic.sqlite3'\n with sqlite3.connect(path) as db:db.execute('CREATE TABLE synthetic(x)');db.execute('INSERT INTO synthetic VALUES(1)')\n with sqlite3.connect(path) as db:assert db.execute('SELECT x FROM synthetic').fetchone()==(1,)\nprint(json.dumps({'preflight':'ISOLATION_LIMITS_PASS','namespaces':ns,'limits':limits,'mountinfo':pathlib.Path('/proc/self/mountinfo').read_text()}),flush=True)\ntime.sleep(21)\n"
 run_case('work','preflight','SYNTHETIC_MEMORY_RUNTIME_PREFLIGHT','HOST_NS='+repr(HOST_NS)+'\nPORT='+repr(PORT)+'\n'+probe,forced=True)
finally:listener.close()
print('MEMORY_RUNTIME_PREFLIGHT_PASS',flush=True)
runner="EXTENSION_IDS=['test_research_memory_stage.MemoryResearchStageTests.test_duplicate_create_actual_pending_rejected_approved', 'test_research_memory_stage.MemoryResearchStageTests.test_production_default_missing_authority_and_synthetic_promotion_denied', 'test_research_memory_stage.MemoryResearchStageTests.test_exact_packet_version_digest_source_and_selfverification', 'test_research_memory_stage.MemoryResearchStageTests.test_distinct_commit_promotion_and_full_fresh_retrieval', 'test_research_memory_stage.MemoryResearchStageTests.test_commit_not_promotion_and_replay_idempotent', 'test_research_memory_stage.MemoryResearchStageTests.test_oversize_full_evidence_no_truncation_and_missing_specialist_grant', 'test_research_memory_stage.MemoryResearchStageTests.test_expiration_dispute_supersession_revocation_exclude_current']\nLEGACY_ID='test_focused_v1_obsidian_export.ObsidianExportTests.test_existing_unmanaged_note_is_not_overwritten'\nDUPLICATE_ID='__main__.DuplicateStateComparison.test_duplicate_create_actual_pending_rejected_approved'\nimport sys,os,json,ast,unittest,secrets,tempfile,resource,time\nfrom pathlib import Path\narea,mode,test_id=sys.argv[1:]\nassert area in ('baseline','work') and mode in ('extension','duplicate','legacy')\nmem=Path('/workspace/artifacts/staging/phase7h-memory')/area\nsys.path[:0]=[str(mem),str(mem/'tests'),'/workspace/src','/workspace/tests','/usr/lib/python3/dist-packages']\nos.mkdir('/tmp/home')\nif mode=='extension':\n assert area=='work' and test_id in EXTENSION_IDS\n suite=unittest.defaultTestLoader.loadTestsFromName(test_id)\nelif mode=='legacy':\n assert test_id==LEGACY_ID\n suite=unittest.defaultTestLoader.loadTestsFromName(test_id)\nelse:\n assert test_id==DUPLICATE_ID\n from focused_v1.store import MemoryStore\n # Load only the unchanged method AST as a comparison harness, not the work module.\n data=Path('/comparison/test_research_memory_stage.py').read_text()\n tree=ast.parse(data)\n cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='MemoryResearchStageTests')\n methods=[n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='test_duplicate_create_actual_pending_rejected_approved']\n assert len(methods)==1\n module=ast.Module(body=methods,type_ignores=[])\n scope={'__name__':'__main__'}\n exec(compile(ast.fix_missing_locations(module),'/comparison/test_research_memory_stage.py','exec'),scope)\n class DuplicateStateComparison(unittest.TestCase):\n  def setUp(self):\n   self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)\n   self.memory=MemoryStore(Path(self.temp.name)/'memory.sqlite3',deletion_key=secrets.token_bytes(32),initialize=True)\n   self.owner_token=secrets.token_urlsafe(32);self.agent_token=secrets.token_urlsafe(32)\n   self.memory.provision('owner','alfred',self.owner_token)\n   self.memory.provision('agent','agent',self.agent_token)\n   self.memory.assign(self.owner_token,'agent','test-task')\n setattr(DuplicateStateComparison,methods[0].name,scope[methods[0].name])\n suite=unittest.TestSuite((DuplicateStateComparison(methods[0].name),))\nassert suite.countTestCases()==1 and tuple(c.id() for c in suite)==(test_id,)\n# Validate source origins after module loading; no fallback to installed Alfred code.\nfor name,module in tuple(sys.modules.items()):\n if name.startswith(('focused_v1','obsidian_candidate')):\n  assert Path(module.__file__).resolve().is_relative_to(mem), (name,module.__file__)\n if name.startswith('alfred_research'):\n  assert Path(module.__file__).resolve().is_relative_to(Path('/workspace/src')), (name,module.__file__)\n if name=='test_research':assert Path(module.__file__)==Path('/workspace/tests/test_research.py')\nstarted=time.monotonic()\nresult=unittest.TextTestRunner(verbosity=2,failfast=True).run(suite)\nr=resource.getrusage(resource.RUSAGE_SELF)\nsummary={'area':area,'mode':mode,'actual_test':test_id,'run':result.testsRun,\n 'failures':[(t.id(),trace) for t,trace in result.failures],\n 'errors':[(t.id(),trace) for t,trace in result.errors],\n 'skipped':[(t.id(),reason) for t,reason in result.skipped],\n 'seconds':time.monotonic()-started,'user_cpu_s':r.ru_utime,'system_cpu_s':r.ru_stime,'maxrss_kib':r.ru_maxrss}\nprint(json.dumps(summary),flush=True)\nsys.exit(0 if result.wasSuccessful() and result.testsRun==1 and not result.skipped else 1)\n"
CASES=[('baseline', 'duplicate', '__main__.DuplicateStateComparison.test_duplicate_create_actual_pending_rejected_approved'), ('work', 'duplicate', '__main__.DuplicateStateComparison.test_duplicate_create_actual_pending_rejected_approved'), ('baseline', 'legacy', 'test_focused_v1_obsidian_export.ObsidianExportTests.test_existing_unmanaged_note_is_not_overwritten'), ('work', 'legacy', 'test_focused_v1_obsidian_export.ObsidianExportTests.test_existing_unmanaged_note_is_not_overwritten'), ('work', 'extension', 'test_research_memory_stage.MemoryResearchStageTests.test_duplicate_create_actual_pending_rejected_approved'), ('work', 'extension', 'test_research_memory_stage.MemoryResearchStageTests.test_production_default_missing_authority_and_synthetic_promotion_denied'), ('work', 'extension', 'test_research_memory_stage.MemoryResearchStageTests.test_exact_packet_version_digest_source_and_selfverification'), ('work', 'extension', 'test_research_memory_stage.MemoryResearchStageTests.test_distinct_commit_promotion_and_full_fresh_retrieval'), ('work', 'extension', 'test_research_memory_stage.MemoryResearchStageTests.test_commit_not_promotion_and_replay_idempotent'), ('work', 'extension', 'test_research_memory_stage.MemoryResearchStageTests.test_oversize_full_evidence_no_truncation_and_missing_specialist_grant'), ('work', 'extension', 'test_research_memory_stage.MemoryResearchStageTests.test_expiration_dispute_supersession_revocation_exclude_current')]
try:
 for area,mode,test in CASES:
  assert time.monotonic()+26<CAMPAIGN_DEADLINE, 'campaign deadline; do not launch next case'
  run_case(area,mode,test,runner)
 print('BOUNDED_MEMORY_SCOPE_COMPLETE',flush=True)
finally:
 after=integrity()
 print(json.dumps({'inputs_unchanged':after==before,'input_integrity_after':after}),flush=True)
 assert after==before
```
<!-- PHASE7Q_SUPERVISOR_END -->

## Exact machine-readable manifests

Paths under transfer are repository-relative; reuse_research paths are relative to the existing extracted Research root; runtime paths are absolute installed public-runtime files. These are byte/hash inventories, not credential manifests. Preserve this object's order for the composed Python repr hash above. All files were inspected read-only or hashed locally; no imports/tests occurred.

<!-- PHASE7Q_MANIFEST_BEGIN -->
```json
{
  "transfer": [
    {
      "path": "artifacts/staging/phase7h-memory/BASELINE_MANIFEST.json",
      "bytes": 5936,
      "sha256": "13c01987ac459d9aa95ef266cc39884a909f88e93bc1dbc4fa5ed6fa03e7b700"
    },
    {
      "path": "artifacts/staging/phase7h-memory/baseline/deploy/focused-v1/obsidian_export.py",
      "bytes": 14044,
      "sha256": "ba42372ba7221a1273f14e07a10688694997abb468ab18ed92e601d2aef11d54"
    },
    {
      "path": "artifacts/staging/phase7h-memory/baseline/focused_v1/__init__.py",
      "bytes": 84,
      "sha256": "a45b4b3c132df7e1d8c830087185e752fc3dcd8f26b9d4a56e6626fe2dc3f8cb"
    },
    {
      "path": "artifacts/staging/phase7h-memory/baseline/focused_v1/store.py",
      "bytes": 29402,
      "sha256": "5ca002bd93e486875191292c21ba782fb2df5eb3fa4d525654e80ad29069cf8c"
    },
    {
      "path": "artifacts/staging/phase7h-memory/baseline/tests/test_focused_v1_obsidian_export.py",
      "bytes": 9810,
      "sha256": "8e7cc28875fc714a517ec13755af2a1e7e42b8cabefac37a075b253626d481b1"
    },
    {
      "path": "artifacts/staging/phase7h-memory/work/deploy/focused-v1/obsidian_export.py",
      "bytes": 14044,
      "sha256": "ba42372ba7221a1273f14e07a10688694997abb468ab18ed92e601d2aef11d54"
    },
    {
      "path": "artifacts/staging/phase7h-memory/work/focused_v1/__init__.py",
      "bytes": 84,
      "sha256": "a45b4b3c132df7e1d8c830087185e752fc3dcd8f26b9d4a56e6626fe2dc3f8cb"
    },
    {
      "path": "artifacts/staging/phase7h-memory/work/focused_v1/research_stage.py",
      "bytes": 23383,
      "sha256": "15e24eb7aa3f84f8796d12dd9d4684d2748943cfda58dc3fa8827428b12dcd3a"
    },
    {
      "path": "artifacts/staging/phase7h-memory/work/focused_v1/server.py",
      "bytes": 3971,
      "sha256": "2042c95d517601da03654b942b04bf96ed69bedf5afa0351ef64463542eba5ea"
    },
    {
      "path": "artifacts/staging/phase7h-memory/work/focused_v1/store.py",
      "bytes": 29426,
      "sha256": "0d84c9c12c0715f14be7729a5007073ebc99f55fa7820e6bed81a55834d969c1"
    },
    {
      "path": "artifacts/staging/phase7h-memory/work/obsidian_candidate/__init__.py",
      "bytes": 226,
      "sha256": "ad5ff6eece3dceb083367cd470edd09eda66d1bb5fcd134905df9ed0a6a06e8f"
    },
    {
      "path": "artifacts/staging/phase7h-memory/work/obsidian_candidate/bridge.py",
      "bytes": 92185,
      "sha256": "775448b247c3a8813cbd3f94a2b1e17fe211c9fca1a72033b165ee7e0226a818"
    },
    {
      "path": "artifacts/staging/phase7h-memory/work/obsidian_candidate/outcome_gate.py",
      "bytes": 14151,
      "sha256": "9ebc79cb0eb4e93e35b17e9b54a30de100b0abd6d724dacfbb794a8ecab2de8f"
    },
    {
      "path": "artifacts/staging/phase7h-memory/work/obsidian_candidate/service_api.py",
      "bytes": 22969,
      "sha256": "f7fdcd5b01bf12b13415b8f4bbd7edbb7629ae0856b7267bca743b6773282cc5"
    },
    {
      "path": "artifacts/staging/phase7h-memory/work/obsidian_candidate/snapshot.py",
      "bytes": 4167,
      "sha256": "d27b3b5dc2b67476da421ca10128651352ca0ed4c584cde40204ac6e5be47b43"
    },
    {
      "path": "artifacts/staging/phase7h-memory/work/tests/test_focused_v1_obsidian_export.py",
      "bytes": 9810,
      "sha256": "8e7cc28875fc714a517ec13755af2a1e7e42b8cabefac37a075b253626d481b1"
    },
    {
      "path": "artifacts/staging/phase7h-memory/work/tests/test_research_memory_stage.py",
      "bytes": 20650,
      "sha256": "53e1f0b095443401ec79daa8a0a7c534a48c47b649972395123af1d457e6cd1e"
    }
  ],
  "reuse_research": [
    {
      "path": "src/alfred_research/__init__.py",
      "bytes": 97,
      "sha256": "2a60c397556e8490825530a85704189794e117e282102b60c9ff5edb8f2e72fc"
    },
    {
      "path": "src/alfred_research/budgets.py",
      "bytes": 1472,
      "sha256": "1ee260b88aff86f5c3adbaf6a70ee0966e8269632904f43d7b6721e3e01c8dc2"
    },
    {
      "path": "src/alfred_research/contracts.py",
      "bytes": 12209,
      "sha256": "af82cd018c2784c8c0d37bbab6d20eddf00626846c724d3462046ba0fe383e58"
    },
    {
      "path": "src/alfred_research/persistence.py",
      "bytes": 10895,
      "sha256": "29e154287fc4d84bcdbc2dc46bc9e73334ab91711566b570cb354dad55e6e65a"
    },
    {
      "path": "src/alfred_research/registration.py",
      "bytes": 6088,
      "sha256": "7d69330d4ac9f96eb873121c4be510258edefb1042a5473300c371c455cf2217"
    },
    {
      "path": "src/alfred_research/research/__init__.py",
      "bytes": 590,
      "sha256": "e1026ca5d72fa1f526f91cd95c08e65f6de2150602d2080fe6906e5eaf19cfe3"
    },
    {
      "path": "src/alfred_research/research/contracts.py",
      "bytes": 8603,
      "sha256": "fbee7a024940c7c8468a46bcefc9da5aac17afce5798c93814f1cbe544581c61"
    },
    {
      "path": "src/alfred_research/research/execution.py",
      "bytes": 7102,
      "sha256": "57eceb97c5e02155bf0f619ea8199631ca0eec5aa68b6f63a3d01614196dbfc0"
    },
    {
      "path": "src/alfred_research/research/journal.py",
      "bytes": 7244,
      "sha256": "3429382ab1f0d1481f134e4edbc77d03e7b69c33e7a48165558e19334aafe901"
    },
    {
      "path": "src/alfred_research/research/provider.py",
      "bytes": 3634,
      "sha256": "732166250bcdc8e75c08d8c6f4f501c9dac1850270c9b19e443fd3718a9ba5dd"
    },
    {
      "path": "src/alfred_research/research/workflow.py",
      "bytes": 21254,
      "sha256": "211a93c1539531bc8c86db0e82035ba839c27db7727723dbfb1fa05e53d9c5c5"
    },
    {
      "path": "src/alfred_research/sources/__init__.py",
      "bytes": 434,
      "sha256": "99428e6b8f94a5aa6ca188cd4e958bf12a084cf32bd8385ab3a8cd9a5dcc5d1b"
    },
    {
      "path": "src/alfred_research/sources/adapters.py",
      "bytes": 13463,
      "sha256": "158298b805597afe3cce6ba514b9ae3f8db91330eab6cd92dfe74b1614bc548a"
    },
    {
      "path": "src/alfred_research/sources/contracts.py",
      "bytes": 8678,
      "sha256": "927edf3ecb58863bc058eadec00c5aa719d3020432cb666c9cdf4b20d4e17efd"
    },
    {
      "path": "src/alfred_research/sources/policy.py",
      "bytes": 3196,
      "sha256": "b414a3a25cbcbf0cf69ec7c54d449bd2128ebf9a6b8b56c733fa785919e2513f"
    },
    {
      "path": "src/alfred_research/sources/processor.py",
      "bytes": 17082,
      "sha256": "19032ed0485f2fea21d7a5ac43b8b5d5fc270c45999ab28fe8365ec052703b5a"
    },
    {
      "path": "src/alfred_research/state.py",
      "bytes": 24169,
      "sha256": "6bfffa7887617ea8b8a0d2c8fd2fa10584550bfb6f89a3cb107b1da82ab43da7"
    },
    {
      "path": "src/alfred_research/tenancy.py",
      "bytes": 1826,
      "sha256": "2cefc72a8f86d8035e4c351963ad3398f14b04be04ab2f9e247c033088adf4f1"
    },
    {
      "path": "src/alfred_research/verification.py",
      "bytes": 851,
      "sha256": "093d6e6249ee6eec2d2595d5e703282155ccaa6c2daf3535e2382c1796f6841b"
    },
    {
      "path": "tests/test_research.py",
      "bytes": 40239,
      "sha256": "0607876fab47cab4df1dd5b1d2dbe6e52ddd3bbcc0a6cfc8c96c57a6ca294435"
    }
  ],
  "runtime": [
    {
      "path": "/lib/x86_64-linux-gnu/libc.so.6",
      "bytes": 2129424,
      "sha256": "3a15d66867d83762c7f2f1e37359cb8f6c5743edb369c65285cb0b1c4f7498bf",
      "resolved": "/usr/lib/x86_64-linux-gnu/libc.so.6"
    },
    {
      "path": "/lib/x86_64-linux-gnu/libcrypto.so.3",
      "bytes": 5309400,
      "sha256": "6866ed711dab8927e1bf82bf1cd30e828bdfc34f3cc1e83b1c9eb01ce6c37d9a",
      "resolved": "/usr/lib/x86_64-linux-gnu/libcrypto.so.3"
    },
    {
      "path": "/lib/x86_64-linux-gnu/libexpat.so.1",
      "bytes": 186624,
      "sha256": "286682ecbc5e59a638963b1a4e6351e65eb32fcf4bdcb9cb7569b6a61fe06a8d",
      "resolved": "/usr/lib/x86_64-linux-gnu/libexpat.so.1.9.1"
    },
    {
      "path": "/lib/x86_64-linux-gnu/libffi.so.8",
      "bytes": 47672,
      "sha256": "00f593fe192f2851b8ce23b25cec2488d769beb5a8f63e8c9e563071e1075153",
      "resolved": "/usr/lib/x86_64-linux-gnu/libffi.so.8.1.4"
    },
    {
      "path": "/lib/x86_64-linux-gnu/libgcc_s.so.1",
      "bytes": 183024,
      "sha256": "d93224d2b0dab4247598be683adca02f5cf00586f99c187579cd7e92058fb7cb",
      "resolved": "/usr/lib/x86_64-linux-gnu/libgcc_s.so.1"
    },
    {
      "path": "/lib/x86_64-linux-gnu/libm.so.6",
      "bytes": 952616,
      "sha256": "fce00b6f25f459cf4ae0b7fae4257909a1a8a86f9149e7c029a5d617baf1ccd0",
      "resolved": "/usr/lib/x86_64-linux-gnu/libm.so.6"
    },
    {
      "path": "/lib/x86_64-linux-gnu/libsqlite3.so.0",
      "bytes": 1468440,
      "sha256": "85265a9d4afca6f4b325ceb078b669c754fb881abed4cafe91ccebe9d625d975",
      "resolved": "/usr/lib/x86_64-linux-gnu/libsqlite3.so.0.8.6"
    },
    {
      "path": "/lib/x86_64-linux-gnu/libssl.so.3",
      "bytes": 696512,
      "sha256": "a40e7b67489bbd257e432c700ff8f6a1ad796425b5eccecdc2930127fdd86624",
      "resolved": "/usr/lib/x86_64-linux-gnu/libssl.so.3"
    },
    {
      "path": "/lib/x86_64-linux-gnu/libz.so.1",
      "bytes": 113000,
      "sha256": "86200da370f20476a2507e9097a789b5ef97269b4ca8d5e164ad82dab9d99892",
      "resolved": "/usr/lib/x86_64-linux-gnu/libz.so.1.3"
    },
    {
      "path": "/lib64/ld-linux-x86-64.so.2",
      "bytes": 236616,
      "sha256": "c20a2dc8917c755f02b94049356320fe1f62ac7d9f8994731f807d9df39302da",
      "resolved": "/usr/lib/x86_64-linux-gnu/ld-linux-x86-64.so.2"
    },
    {
      "path": "/usr/lib/python3/dist-packages/_cffi_backend.cpython-312-x86_64-linux-gnu.so",
      "bytes": 194512,
      "sha256": "5401195ab2db5412e46a2f4b1dcda10c60d2cc282933720cf2524668d445e7f0",
      "resolved": "/usr/lib/python3/dist-packages/_cffi_backend.cpython-312-x86_64-linux-gnu.so"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/__about__.py",
      "bytes": 445,
      "sha256": "b8f5cc6db729b6dec4cd9fe3965191c74a5574c9fe341b003382fbe213aff9bd",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/__about__.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/__init__.py",
      "bytes": 364,
      "sha256": "8953e50655d64c9ca215e45e77171b30f8721c1df8be238cd7477bdaf1a75ae1",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/__init__.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/exceptions.py",
      "bytes": 1118,
      "sha256": "1077bb5ccdbf3ad74e3356d9134722fb819486d3a5110e9f41784ad8881fd2a0",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/exceptions.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/fernet.py",
      "bytes": 6886,
      "sha256": "4d5672e03b64a65ee4588a6fb8a70d95d13de481234d0d0c7c7811b0b7670d23",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/fernet.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/__init__.py",
      "bytes": 455,
      "sha256": "e48c2b2d6ad5a7402312bff815d586fd5d39ecd489198fd6e1e80d36cb9cb748",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/__init__.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/_oid.py",
      "bytes": 14441,
      "sha256": "83184c1caa6ef57b22eae1c2199ffeb2860c5e3fe2cce2056b18d42966c23de1",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/_oid.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/backends/__init__.py",
      "bytes": 361,
      "sha256": "3b98ef28541d6675e129ea89f87b6e95a10bf4d8bb9abd660f3658e641e56212",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/backends/__init__.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/backends/openssl/__init__.py",
      "bytes": 305,
      "sha256": "a778e625f9c26a0f62139b1d32b37a56f544bb9e6ee3ac5a4bf223a08d12ae60",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/backends/openssl/__init__.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/backends/openssl/aead.py",
      "bytes": 15967,
      "sha256": "b37cd771541fd023883ae3b323cbac79b5a9ce71a7c99ec68679a5258bbb4170",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/backends/openssl/aead.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/backends/openssl/backend.py",
      "bytes": 73683,
      "sha256": "30000304c7c0e20235bc145095932d75a0d0862bcb0f97d35fc322f3ec2c6672",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/backends/openssl/backend.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/backends/openssl/ciphers.py",
      "bytes": 10358,
      "sha256": "9715abbe7b9fb9db032366e9c0db3673c5cb20b6c01368f6acc483d678673d58",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/backends/openssl/ciphers.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/backends/openssl/cmac.py",
      "bytes": 3035,
      "sha256": "a4781038845f4787080dae65b5c285b608ea3d35db38bc914269aabfd2656d49",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/backends/openssl/cmac.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/backends/openssl/decode_asn1.py",
      "bytes": 1148,
      "sha256": "933ea0cacf30b8986bc7843253a7a7631ed46ad347af42c1dd32358c7de8439e",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/backends/openssl/decode_asn1.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/backends/openssl/ec.py",
      "bytes": 11975,
      "sha256": "663903c095243271ebf0dead9f28ba872b8c51e98d0dec2366bdf8677cb2aca5",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/backends/openssl/ec.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/backends/openssl/rsa.py",
      "bytes": 21825,
      "sha256": "3ff6a4fb6cef03a541b7f3f495dcd3482524723a361a162dfc72e7f0256f5ad1",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/backends/openssl/rsa.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/backends/openssl/utils.py",
      "bytes": 2190,
      "sha256": "52882e3b6e90cf037896c30096db08ae00256e2dd239e4ab7b166cd7e40f36ef",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/backends/openssl/utils.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/bindings/__init__.py",
      "bytes": 180,
      "sha256": "b3da0a090db2705757a0445d4b58a669fb9e4a406c2fd92f6f27e085a6ae67d6",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/bindings/__init__.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/bindings/_rust.abi3.so",
      "bytes": 2647896,
      "sha256": "c928893c3fd432d2aaf84a8db7162ac8a7e1d03a4d121ccd2aec8a7bc4a4b165",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/bindings/_rust.abi3.so"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/bindings/openssl/__init__.py",
      "bytes": 180,
      "sha256": "b3da0a090db2705757a0445d4b58a669fb9e4a406c2fd92f6f27e085a6ae67d6",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/bindings/openssl/__init__.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/bindings/openssl/_conditional.py",
      "bytes": 9098,
      "sha256": "0de102abb00a82e86cdfdd199b1808b5da8f2f3cab286264fb72a51c93245e86",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/bindings/openssl/_conditional.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/bindings/openssl/binding.py",
      "bytes": 6696,
      "sha256": "d31de4cefab682b1eee206db804233115ad7eae9e9ef5104b35871d28faeb8e3",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/bindings/openssl/binding.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/__init__.py",
      "bytes": 180,
      "sha256": "b3da0a090db2705757a0445d4b58a669fb9e4a406c2fd92f6f27e085a6ae67d6",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/__init__.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/_asymmetric.py",
      "bytes": 532,
      "sha256": "46181ca2e501e874e214306b4752f1aa4323a54c4888dbd0d6bff3263446eaa4",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/_asymmetric.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/_cipheralgorithm.py",
      "bytes": 1093,
      "sha256": "ecb3e4a70f83ae0caf9813148ef5de06fa235593ed5e11607de9547ed9f13c6c",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/_cipheralgorithm.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/_serialization.py",
      "bytes": 5216,
      "sha256": "5340d4d19cce2c9a69090b21f44247eaf198a07a2d06895f372472c77c2bd65d",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/_serialization.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/__init__.py",
      "bytes": 180,
      "sha256": "b3da0a090db2705757a0445d4b58a669fb9e4a406c2fd92f6f27e085a6ae67d6",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/__init__.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/dh.py",
      "bytes": 7013,
      "sha256": "5ecb61aa3bc4c5658ec9e3ecd0fc53e0c7acb54f50786b8bf87c7b7d6cd382e4",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/dh.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/dsa.py",
      "bytes": 8263,
      "sha256": "69a4d8ec430b4f3696b3e8e138ca4c01f6b61a77e1a2ab022993ca02cdf92f8d",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/dsa.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/ec.py",
      "bytes": 12867,
      "sha256": "2f55a858f61ebc9e8f9364f57ad6e71dbbebe8079715c71c90f34d8b2515a0d3",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/ec.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/ed25519.py",
      "bytes": 3489,
      "sha256": "c25d8d0823f86d97540aa64632438e77a79ac63535bd73c0230cd4b853c4fffc",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/ed25519.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/ed448.py",
      "bytes": 3440,
      "sha256": "d8c089f3ba9cc820ac8e3d0ebeb7d61713d7f0281a0b77749abefc6edfef0c86",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/ed448.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/padding.py",
      "bytes": 2717,
      "sha256": "ea9f0e8e26b1ff6b5c9b56939cd3809229eb88227aee7493c6e820df87fe8739",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/padding.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/rsa.py",
      "bytes": 11623,
      "sha256": "bf1bceaf2174d162fc99942ff5bb3ff8b960a1b60b88f61f5f6e3afe3fc80ad0",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/rsa.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/types.py",
      "bytes": 2996,
      "sha256": "2e7b0e2729bec263d427b2a7bbfedb08d5379088842c277a92b39a5bf254d3c2",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/types.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/utils.py",
      "bytes": 790,
      "sha256": "0cf4ece93e05f94870cc541387ed5f484a50cdacc7da37f6c6922ba3722d178a",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/utils.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/x25519.py",
      "bytes": 3437,
      "sha256": "f1824021a53bc34f634e73d4fdc2f077df1f3072040a07c0dd1ecfdcab6ff820",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/x25519.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/x448.py",
      "bytes": 3358,
      "sha256": "cbe623fab81c8a2b87d60e8524b65fb6f02a80e9f34f5a27f600a2b2bbbbbc17",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/asymmetric/x448.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/ciphers/__init__.py",
      "bytes": 680,
      "sha256": "900c9bf4d49ccea4eb0968f41c4a15a770b1a3b0075bc89b3c5433f991ec3ad0",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/ciphers/__init__.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/ciphers/aead.py",
      "bytes": 12067,
      "sha256": "0d8eea2a66edd1b801d4607b8be7d0adb8c47f0146f307d47d51ef73b0c0d986",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/ciphers/aead.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/ciphers/algorithms.py",
      "bytes": 5000,
      "sha256": "4820ec91773dc72ceccf4363343ead017f2dd7b8d84db501dacc30d6e6fd1ae6",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/ciphers/algorithms.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/ciphers/base.py",
      "bytes": 8286,
      "sha256": "3ea34396d1dd0f10612e182d7ceef4ec7d3bb1238b03a655c236656a53894c0a",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/ciphers/base.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/ciphers/modes.py",
      "bytes": 8361,
      "sha256": "6094178b83c9188219d6b81c85b307e3b11df988947144a32cf10eb95f2b8061",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/ciphers/modes.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/cmac.py",
      "bytes": 2065,
      "sha256": "61a79692c0986aa568a9ff731d14e1009f7966f3d48a800e7d7c1951688fcc3f",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/cmac.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/constant_time.py",
      "bytes": 422,
      "sha256": "c5dba7593d277fc3af29d72a52186514a6b21a9e3f3e0549454d96d702d2aff0",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/constant_time.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/hashes.py",
      "bytes": 5115,
      "sha256": "549a676cadac40dd9b12ac114cea020789eec58c790a7a8589270c24dca1b2b2",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/hashes.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/hmac.py",
      "bytes": 423,
      "sha256": "469077cfdcf9b248ab090ae6ef341bb67a7da4b327023ae54d4bcaa85e5a0c37",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/hmac.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/kdf/__init__.py",
      "bytes": 750,
      "sha256": "e1789b667ad8ab8861e710635a2217cda616e852b1f213db55a6bf701f734bae",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/kdf/__init__.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/kdf/concatkdf.py",
      "bytes": 3726,
      "sha256": "c066168082e6c505a708f91b007d51a6c087add2a0998ac2115ac2bd75460a8f",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/kdf/concatkdf.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/kdf/hkdf.py",
      "bytes": 3045,
      "sha256": "6c162bd725086ce94920477a6682d87179bfc9df87e78027f6435c14827791ba",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/kdf/hkdf.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/kdf/kbkdf.py",
      "bytes": 9232,
      "sha256": "a8f2fa4e60d49a4bace825b7ca54c97c6f0df1e81986340ec97ad2c8b2e99da9",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/kdf/kbkdf.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/kdf/pbkdf2.py",
      "bytes": 2012,
      "sha256": "d42087f50e605d4a6765dddcf1df1b097829277b36859646067b86ec51f5c1a3",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/kdf/pbkdf2.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/kdf/scrypt.py",
      "bytes": 2354,
      "sha256": "e1038d863c40fd9b6e42d43b415dc59db07c7edac59cce760781cf7d5ee1172b",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/kdf/scrypt.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/kdf/x963kdf.py",
      "bytes": 2002,
      "sha256": "4b70781279366318fdb71a5a8aba2d69791abee66a43ab7a301e5adbc534d9e9",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/kdf/x963kdf.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/keywrap.py",
      "bytes": 5678,
      "sha256": "41bfcdd95fc4d43b62e55b435e7aed4d8b490d9f1a329babf01639cb1ad77258",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/keywrap.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/padding.py",
      "bytes": 6242,
      "sha256": "f2909e2daab040f4867f9d63d3a5390bf20dbe06165563efde6f66c541111a65",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/padding.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/poly1305.py",
      "bytes": 355,
      "sha256": "3f910f415f9107f1493da869834d6ed13b384bf3e7026b2ba312065db19e451a",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/poly1305.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/serialization/__init__.py",
      "bytes": 1653,
      "sha256": "e9994bdc489c133a0674c39ab7ceb0f32fd72020a79477428c523deeb3314438",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/serialization/__init__.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/serialization/base.py",
      "bytes": 1986,
      "sha256": "5598c822a9db6fec77f2aa60d967ff23166faa3b20704ccd42d4287898907e9c",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/serialization/base.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/serialization/pkcs12.py",
      "bytes": 6767,
      "sha256": "34ecc5c40ae56617637e07ee82cf27111868d5ec9ac6e8d728650a20d7217a4e",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/serialization/pkcs12.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/serialization/pkcs7.py",
      "bytes": 7392,
      "sha256": "042be53ee6d740eba76fbe9e98848af3d3d7f6a5dc0502360913cd7bce554d99",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/serialization/pkcs7.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/serialization/ssh.py",
      "bytes": 51027,
      "sha256": "68b0982cf6375b591eadf0b069d9f9698373c1cc08425f5ced172c07c08a7ee7",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/serialization/ssh.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/twofactor/__init__.py",
      "bytes": 258,
      "sha256": "b66319181fa0e08535afb94816a012534d7dcebd2e3e9ff010161cc1d0c22820",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/twofactor/__init__.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/twofactor/hotp.py",
      "bytes": 3010,
      "sha256": "b99d0f48a60364e2f4680a1b8b0d597761c3d16d848b59e250d0b6bfb4e7a5cf",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/twofactor/hotp.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/twofactor/totp.py",
      "bytes": 1473,
      "sha256": "70c6d69406a938cd527decc4c7d328307a425bd8a780d5c283a3ac1afe13f237",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/hazmat/primitives/twofactor/totp.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/utils.py",
      "bytes": 4018,
      "sha256": "0df75773d33892601ba04d9ad293e2212b792d59d6fa38615d4472f270c769ed",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/utils.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/x509/__init__.py",
      "bytes": 7870,
      "sha256": "0f3644f1b47ede28958b75ab72aefe8393e6eb87c2af96aab133728bfae326ed",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/x509/__init__.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/x509/base.py",
      "bytes": 35677,
      "sha256": "15b4ba105137b89dcefb36c53d18ec3ba0dc92b3523794c9359309727cd45854",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/x509/base.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/x509/certificate_transparency.py",
      "bytes": 2261,
      "sha256": "e87bf3003d1d952415c72ead9c38468f4fa98aca7531a27d6f140d46bf768a72",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/x509/certificate_transparency.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/x509/extensions.py",
      "bytes": 68365,
      "sha256": "ac511c7d9885bdc38db35a2dd3777af1d00c2b653be70d2cde0f6687258145c2",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/x509/extensions.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/x509/general_name.py",
      "bytes": 7868,
      "sha256": "ce6f06c4d81526e2c3eab378f3c739cdd1e1c69e60531791cf0f1e9d93160d0d",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/x509/general_name.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/x509/name.py",
      "bytes": 14855,
      "sha256": "699d9da6c8a7864cdadde4f14f5bcd996b85310edf99c03486ce27a609e47fd4",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/x509/name.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/x509/ocsp.py",
      "bytes": 18534,
      "sha256": "e3c896ef16d9f6664b10b48497b5b08dbe2f621390dca70db6a80ab006ff503d",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/x509/ocsp.py"
    },
    {
      "path": "/usr/lib/python3/dist-packages/cryptography/x509/oid.py",
      "bytes": 829,
      "sha256": "7c5a2c8c6b27201ff0ff462bcd9bf5820912570665ef1998d33a1f2993599030",
      "resolved": "/usr/lib/python3/dist-packages/cryptography/x509/oid.py"
    },
    {
      "path": "/usr/lib/x86_64-linux-gnu/ossl-modules/legacy.so",
      "bytes": 129256,
      "sha256": "e639c7121825222dc720bd38aa1fca3ddcedd7d1213dc72ce006b8ccf541b547",
      "resolved": "/usr/lib/x86_64-linux-gnu/ossl-modules/legacy.so"
    }
  ]
}
```
<!-- PHASE7Q_MANIFEST_END -->

## Read-only inspections performed in Phase 7Q

All remote reads used strict noninteractive SSH. Inspected only public `/usr/lib/python3/dist-packages/cryptography` bootstrap/version source, native library linkage (ldd), selected runtime file hashes/resolved paths and proposed-stage/parent metadata. No Linux package imports, synthetic crypto operation or Memory code executed. Runtime inventory read 73 cryptography files and the one CFFI backend; cffi/pycparser package paths were checked for existence only. ldd inspected Rust/CFFI native objects and the OpenSSL legacy provider. Read-only commands exited 0 after the initial sandbox SSH denial (255) was retried with tool approval. No production config/database/vault/socket/credential content was read.

## Cleanup and release preservation requirements

Later tests must log exact selected/actual IDs, per-case duration/self CPU/RSS, raw stdout/stderr and raw exit, including the expected baseline failure. No skips, swallowed errors or count-only comparison. Record input hashes before/after, runtime origins, scratch capacity and scoped observed-tree cleanup. Namespace teardown destroys private databases/ledgers/synthetic vaults; supervisor closes unlinked logs and its own listener. Never signal by name or remove preexisting paths. Persistent staging-source removal is a separate path-specific cleanup approval; leave it intact for owner review after a run. No archive/source edits, production rollback or service restart is part of this plan.
