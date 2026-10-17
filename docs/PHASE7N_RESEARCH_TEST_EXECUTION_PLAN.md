# Phase 7N — proposed Research Linux test execution plan

2026-10-16. **PROPOSAL ONLY — DO NOT EXECUTE without separate authorization.** The current task ends with this assessment. No package import or test execution occurred.

## Smallest useful authorized scope

Request authorization for these eight individual test IDs, serially, one fresh Bubblewrap sandbox per ID. Each sandbox first imports all package modules from an explicit static module list. This validates imports without importing on the host; unittest runs exactly one named method, with failfast and no discovery.

1. `test_foundation.FoundationTests.test_packet_roundtrip_and_determinism`
2. `test_foundation.FoundationTests.test_malformed_and_ambiguous_contracts`
3. `test_foundation.FoundationTests.test_cross_environment_read_write_denied`
4. `test_sources.SourceTests.test_all_source_categories_and_environments`
5. `test_sources.SourceTests.test_result_roundtrip_hash_and_determinism`
6. `test_sources.SourceTests.test_every_cross_environment_pair_and_principal_denied`
7. `test_sources.SourceTests.test_local_fixture_roots_are_environment_isolated`
8. `test_sources.SourceTests.test_local_fixture_directory_no_execution_symlink_follow_or_writes`

This covers import closure, packet/result serialization and contract rejection, all source categories (PDF remains unsupported), all company/principal source denials, temporary SQLite cross-company read/write denial, local fixture-root separation and script/symlink nonexecution. It does not validate live services, model execution, durable Memory integration or all 305 tests.

## Mount and resource contract

| Input / destination | Access |
| --- | --- |
| Staged `src` → `/release/src` | Read-only; exact baseline source only |
| Staged `tests` → `/release/tests` | Read-only; exact baseline tests only |
| `/usr/bin/python3.12` at same path | Read-only executable |
| `/usr/lib/python3.12` at same path | Read-only stdlib; `-I -S -B`, no site initialization |
| Eight library files listed in command | Read-only, exact same destination paths |
| `/workspace` | Fresh private 16 MiB tmpfs, cwd; disappears at namespace exit |
| `/tmp` | Fresh private 16 MiB tmpfs; TMPDIR and HOME point here |
| `/proc` | Private PID namespace procfs |
| `/dev` | Bubblewrap synthetic dev, no host device-directory bind |

No host-backed writable mount. No host root/home/opt/run/var/etc, DNS config, credentials, vault, sockets, production workspaces or release docs are mounted. A synthetic `/tmp/home` is created inside the namespace. Root is remounted read-only. `--unshare-all` includes a new network namespace; no share-net option or host network FD is permitted. The supervisor closes inherited descriptors and passes stdin=/dev/null. Clear environment and private filesystem paths remove service configuration. Network isolation blocks TCP/UDP and abstract UNIX access to host services; absent host socket mounts block pathname UNIX services. This boundary excludes Hermes, Photon, Memory, Obsidian and Development regardless of test mocks.

Hard=soft ceilings before Bubblewrap exec: CPU 10 s/process; virtual address space 256 MiB/process; file size 8 MiB/file; 64 open descriptors/process; core=0. RLIMIT_NPROC=128 is retained only as a shared-real-UID guard, not a dedicated process cap. Do not lower it below shared account usage or treat it as a cgroup replacement. No new threads/subprocesses are allowed by this subset's reviewed behavior. Writable tmpfs total capacity is 32 MiB; tmpfs consumes host memory independently of RLIMIT_AS.

Wall timeout: 20 s per sandbox; at most 160 s test lifetime plus bounded startup/cleanup across eight cases. Stop at first error, timeout, skip, resource denial or unexpected test count. Capture output in bounded regular temporary files in the **Mac SSH caller** if desired; the provided supervisor instead uses its own unlinked `/tmp/phase7n-stdout-*` and `/tmp/phase7n-stderr-*` TemporaryFile logs with an explicit 1 MiB monitor bound per stream. These supervisor files are outside the sandbox, contain only synthetic test output, and close on exit. A test cannot access their FDs (close_fds and stdio redirection only); its stdio descriptors do reference the log files. RLIMIT_FSIZE further caps writes through those descriptors at 8 MiB. Polling bounds can overshoot; maximum disk exposure is two 8 MiB files per active case.

## Exact proposed command

Run from the Mac only after authorization. This command creates no release files and installs nothing. It runs a stdlib supervisor through SSH stdin; all Research imports occur inside Bubblewrap. The explicit import list was generated statically from the inspected release. No `.pyc` writes are permitted. This is a proposed command, not a transcript of execution.

```sh
ssh -o BatchMode=yes -o StrictHostKeyChecking=yes -o ConnectTimeout=8 -o ConnectionAttempts=1 alfred@192.168.50.81 'python3 -I -S -B -' <<'PHASE7N_AUTHORIZED_ONLY'
import os, sys, pathlib, subprocess, resource, ctypes, signal, time, tempfile, json, select
BASE = pathlib.Path('/home/alfred/research-staging/research-v1/alfred-research-v1-0.1.0-phase7e-linux-stage-20261016')
assert os.getuid() == 1000
assert BASE.is_dir() and not BASE.is_symlink()
for tree in (BASE/'src', BASE/'tests'):
    assert tree.is_dir() and not tree.is_symlink()
    assert not any(p.is_symlink() for p in tree.rglob('*'))
LIBS = [
 '/lib64/ld-linux-x86-64.so.2',
 '/lib/x86_64-linux-gnu/libc.so.6',
 '/lib/x86_64-linux-gnu/libm.so.6',
 '/lib/x86_64-linux-gnu/libz.so.1',
 '/lib/x86_64-linux-gnu/libexpat.so.1',
 '/lib/x86_64-linux-gnu/libsqlite3.so.0',
 '/lib/x86_64-linux-gnu/libffi.so.8',
 '/lib/x86_64-linux-gnu/libcrypto.so.3',
]
assert all(pathlib.Path(p).is_file() for p in LIBS)
libc = ctypes.CDLL(None, use_errno=True)
assert libc.prctl(36, 1, 0, 0, 0) == 0  # Supervisor is child subreaper.
TESTS = ['test_foundation.FoundationTests.test_packet_roundtrip_and_determinism', 'test_foundation.FoundationTests.test_malformed_and_ambiguous_contracts', 'test_foundation.FoundationTests.test_cross_environment_read_write_denied', 'test_sources.SourceTests.test_all_source_categories_and_environments', 'test_sources.SourceTests.test_result_roundtrip_hash_and_determinism', 'test_sources.SourceTests.test_every_cross_environment_pair_and_principal_denied', 'test_sources.SourceTests.test_local_fixture_roots_are_environment_isolated', 'test_sources.SourceTests.test_local_fixture_directory_no_execution_symlink_follow_or_writes']
MODULES = ['alfred_research', 'alfred_research.budgets', 'alfred_research.contracts', 'alfred_research.integration', 'alfred_research.integration.canary_contracts', 'alfred_research.intelligence', 'alfred_research.intelligence.service', 'alfred_research.memory', 'alfred_research.memory.access', 'alfred_research.memory.contracts', 'alfred_research.memory.fake', 'alfred_research.persistence', 'alfred_research.registration', 'alfred_research.research', 'alfred_research.research.contracts', 'alfred_research.research.execution', 'alfred_research.research.journal', 'alfred_research.research.provider', 'alfred_research.research.workflow', 'alfred_research.sources', 'alfred_research.sources.adapters', 'alfred_research.sources.contracts', 'alfred_research.sources.policy', 'alfred_research.sources.processor', 'alfred_research.state', 'alfred_research.tenancy', 'alfred_research.verification', 'alfred_research.workflow', 'alfred_research.workflow.contracts', 'alfred_research.workflow.coordinator', 'alfred_research.workflow.notifications']
runner = """import sys,os,importlib,unittest
sys.path[:0]=['/release/src','/release/tests']
os.mkdir('/tmp/home')
for module in MODULES: importlib.import_module(module)
suite=unittest.defaultTestLoader.loadTestsFromName(TEST_ID)
assert suite.countTestCases()==1
result=unittest.TextTestRunner(verbosity=2,failfast=True).run(suite)
sys.exit(0 if result.wasSuccessful() and result.testsRun==1 and not result.skipped else 1)
"""
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
for test in TESTS:
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
        tracked={}; reason=None
        try:
            deadline=time.monotonic()+20
            while p.poll() is None:
                tracked.update(identities(p.pid))
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
                          'remaining_tracked':remaining}),flush=True)
        if reason or p.returncode: raise SystemExit(1)
print('EIGHT_SELECTED_TESTS_PASS')
PHASE7N_AUTHORIZED_ONLY
```

## Cleanup and acceptance

Bubblewrap PID namespace teardown, rather than process-group-only signaling, is the descendant cleanup boundary. The supervisor kills only its exact launcher pidfd on timeout/output excess and on exceptional exit from its monitoring loop. It acts as a subreaper and checks PID/starttime identities of observed descendants after reaping. The historical 7L forced-timeout probe covered a setsid branch; this subset itself has no intentional child workloads. Polling is not an exhaustive adversarial descendant audit. If cleanup cannot be verified, stop immediately and report exact identities; never signal by name or use broad account cleanup. All private tmpfs content disappears when the namespace dies. Supervisor output files close automatically. No release cleanup or writeback exists.

The SSH connection's lifetime is not the watchdog: the remote supervisor owns the 20-second deadline. An abruptly killed supervisor relies on Bubblewrap --die-with-parent. No systemd unit or cgroup is created. No production process is moved or signaled.

Accept only eight one-test successes, successful import sweeps, no skips, no timeouts/output-limit events, and no tracked remaining identities. Record host Python/Bubblewrap versions, exact argv, resource values and exit results in a separately authorized execution report. Missing shared objects are preparation blockers: inspect their binary dependency closure read-only and obtain review for any allowlist change. Do not mount entire library trees as a workaround.

## Full-suite follow-on — not ready or authorized

Do not run `unittest discover` on the host or append all tests to this subset command. A full-suite proposal must enumerate exactly 305 test IDs from the static baseline and run one at a time with fresh scratch mounts and the same no-network/no-service boundary. Its logical in-sandbox test operation is:

```python
suite = unittest.defaultTestLoader.loadTestsFromName(EXPLICIT_SINGLE_TEST_ID)
assert suite.countTestCases() == 1
result = unittest.TextTestRunner(verbosity=2, failfast=True).run(suite)
```

Candidate values for review (not accepted execution settings): 512 MiB address space/process, 60 CPU seconds/process, 90 wall seconds/case, 32 MiB/file, 128 descriptors, 64 MiB /tmp and 128 MiB /workspace. Single-case output monitoring and total campaign deadline (e.g. 900 seconds, stop on deadline) are required. The finite synchronous Python children and up-to-eight-worker pools need explicit concurrency/headroom accounting; do not infer a dedicated limit from RLIMIT_NPROC=128. A strict aggregate option would require a separately authorized/verified launch within a dedicated cgroup (suggested ceilings for review: memory.max 1 GiB, pids.max 32, cpu.max 100000 100000, plus accepted supervisor/scratch accounting), or an isolated fixed-resource Linux host. Phase 7M's direct SSH-to-delegated-cgroup migration is blocked and must not be attempted here.

**Remaining blockers:** separate subset execution authorization; actual sandbox runtime/import/resource results; full-suite resource envelope and aggregate-risk acceptance or verified dedicated containment. No package execution, Linux compatibility pass or deployment recommendation is issued by this assessment.
