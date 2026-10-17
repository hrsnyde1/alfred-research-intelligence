# Phase 7L forced-timeout cleanup results

2026-10-16 — **PASS for the two bounded synthetic process-tree cleanup probes.** Full staging resource gate remains separate.

## Execution and identity evidence

Remote command: strict noninteractive SSH to alfred@192.168.50.81, running `python3 -B - <<'PHASE7L'` with the full body below. Outer SSH/reporting command exit **0**; runtime ldd exit **0**. Synthetic Bubblewrap launcher exits **-9 (SIGKILL)** in both runs, intentionally.

Unique temporary root: /home/alfred/.alfred-phase7l-probe-x2ezjer7, mode 0700. Synthetic tree.py read-only input; work1/work2 writable; private 1 MiB tmpfs; minimal Python runtime/stdlib/libs read-only; host home/opt/run/var not mounted; root read-only; user/network/PID/mount/IPC/UTS namespaces; capabilities dropped, NoNewPrivs set, nested user namespaces disabled.

Each workload creates a parent, one setsid child with grandchild, and a second child. All sleep; three hold 1 MiB buffers. SIGTERM is ignored by workload processes, testing forced shutdown rather than graceful cooperative exit.

| Run | Tracked host PIDs | Starttime ticks in same order | Result |
| --- | --- | --- | --- |
| 1 | 160121,160122,160123,160124,160126,160125 | 2781665,2781668,2781669,2781672,2781672,2781672 | Six pidfds report exit; no matching /proc identities remain |
| 2 | 160132,160133,160134,160135,160137,160136 | 2781726,2781729,2781729,2781732,2781732,2781732 | Six pidfds report exit; no matching /proc identities remain |

Each tree includes outer Bubblewrap, inner namespace reaper and four Python workload processes. Inner PID namespace 4026532314 differed from host 4026531836 (namespace inode reuse between completed runs is not persistent identity). Separate-session child SIDs were 160124 and 160135, demonstrating cleanup extends beyond the launcher's process group.

Supervisor traverses ONLY /proc entries rooted at its own exact Popen PID via task children links, records PID+starttime and opens pidfds. It waits at most 3 seconds to establish the bounded six-process tree, runs 0.5 seconds, then sends SIGKILL only through the launcher pidfd. Bubblewrap death/namespace teardown terminates descendants, including the setsid branch. Parent acts as child subreaper and waits only tracked descendants, avoiding orphan zombies. All pidfds signaled and all matching starttime identities disappeared. No process-name matching or production signals.

The 3-second post-kill communicate/reap windows succeeded in both attempts; stdout includes READY and both resource denials, stderr empty. No broad external process inventory or production process data was read. No escape or arbitrary reparenting/fork-bomb behavior was tested; this is a bounded synthetic tree proof, not an adversarial unlimited tree guarantee.

## Cleanup

Both size.bin files were exactly 4096 bytes. Parent verified directory entries against the exact synthetic allowlist and removed only those files, tree.py and created directories. cleanup_root_absent=true. No preexisting files removed; no synthetic PID identity remained. All pidfds closed.

## Exact remote Python body executed

```python
import os,json,pathlib,tempfile,subprocess,signal,time,ctypes,select,re
libc=ctypes.CDLL(None,use_errno=True)
if libc.prctl(36,1,0,0,0)!=0:raise RuntimeError('subreaper unavailable')
root=pathlib.Path(tempfile.mkdtemp(prefix='.alfred-phase7l-probe-',dir=str(pathlib.Path.home())))
os.chmod(root,0o700);inputs=root/'inputs';inputs.mkdir(mode=0o700)
workload="import os,time,resource,errno,json,signal\nsignal.signal(signal.SIGXFSZ,signal.SIG_IGN)\nfsize=False\ntry:\n with open('/workspace/size.bin','wb',buffering=0) as f:\n  f.write(b'x'*4096)\n  f.write(b'x')\nexcept OSError as e:fsize=e.errno==errno.EFBIG\nfds=[];fdlimit=False\ntry:\n for _ in range(40):fds.append(os.open('/dev/null',os.O_RDONLY))\nexcept OSError as e:fdlimit=e.errno==errno.EMFILE\nfinally:\n for fd in fds:os.close(fd)\nlimits={n:resource.getrlimit(getattr(resource,n)) for n in ('RLIMIT_CPU','RLIMIT_AS','RLIMIT_NPROC','RLIMIT_FSIZE','RLIMIT_NOFILE')}\nprint(json.dumps({'file_size_denied':fsize,'fd_denied':fdlimit,'file_bytes':os.stat('/workspace/size.bin').st_size,'limits':limits}),flush=True)\nif not fsize or not fdlimit:raise RuntimeError('resource probe failed')\nsignal.signal(signal.SIGTERM,signal.SIG_IGN)\npid=os.fork()\nif pid==0:\n os.setsid()\n if os.fork()==0:\n  buf=bytearray(1048576)\n  while True:time.sleep(0.1)\n buf=bytearray(1048576)\n while True:time.sleep(0.1)\npid2=os.fork()\nif pid2==0:\n buf=bytearray(1048576)\n while True:time.sleep(0.1)\nprint('READY',flush=True)\nwhile True:time.sleep(0.1)\n"
(inputs/'tree.py').write_text(workload)
ldd=subprocess.run(['/usr/bin/ldd','/usr/bin/python3.12'],capture_output=True,text=True,timeout=3,check=True)
libs=sorted(set(re.findall(r'(/[\w/+.\-]+)',ldd.stdout)))
launcher="""import os,sys,resource,ctypes
for n,v in {'RLIMIT_CPU':2,'RLIMIT_AS':67108864,'RLIMIT_NPROC':128,'RLIMIT_FSIZE':4096,'RLIMIT_NOFILE':32,'RLIMIT_CORE':0}.items():resource.setrlimit(getattr(resource,n),(v,v))
libc=ctypes.CDLL(None,use_errno=True)
if libc.prctl(38,1,0,0,0)!=0:raise RuntimeError('NoNewPrivs')
os.execv(sys.argv[1],sys.argv[1:])
"""
def snapshot(pid):
 rows=[]
 def walk(n):
  try:
   s=pathlib.Path('/proc/'+str(n)+'/stat').read_text();fields=s.rsplit(')',1)[1].split()
   rows.append({'pid':n,'starttime':fields[19],'state':fields[0],'pid_namespace':os.readlink('/proc/'+str(n)+'/ns/pid'),'sid':int(fields[3])})
   children=pathlib.Path('/proc/'+str(n)+'/task/'+str(n)+'/children').read_text().split()
   for child in children:walk(int(child))
  except FileNotFoundError:pass
 walk(pid);return rows
all_results=[]
print(json.dumps({'probe_root':str(root),'ldd_exit':ldd.returncode}),flush=True)
try:
 for attempt in (1,2):
  work=root/('work'+str(attempt));work.mkdir(mode=0o700)
  cmd=['/usr/bin/bwrap','--unshare-all','--unshare-user','--disable-userns','--die-with-parent','--new-session','--cap-drop','ALL','--clearenv','--ro-bind','/usr/bin/python3.12','/usr/bin/python3.12','--ro-bind','/usr/lib/python3.12','/usr/lib/python3.12']
  for lib in libs:cmd+=['--ro-bind',lib,lib]
  cmd+=['--ro-bind',str(inputs),'/inputs','--bind',str(work),'/workspace','--size','1048576','--tmpfs','/tmp','--proc','/proc','--dev','/dev','--remount-ro','/','--chdir','/workspace','/usr/bin/python3.12','-I','-S','-B','/inputs/tree.py']
  print(json.dumps({'attempt':attempt,'argv':cmd}),flush=True)
  p=subprocess.Popen(['/usr/bin/python3','-B','-c',launcher,*cmd],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,start_new_session=True,close_fds=True,env={'PATH':'/usr/bin:/bin','LANG':'C'})
  tracked={};handles={};terminated=False
  try:
   deadline=time.monotonic()+3
   while time.monotonic()<deadline and p.poll() is None:
    for row in snapshot(p.pid):
     if row['pid'] not in tracked:
      tracked[row['pid']]=row;handles[row['pid']]=os.pidfd_open(row['pid'])
    if len(tracked)>=6:break
    time.sleep(0.05)
   if len(tracked)<6:raise RuntimeError('expected synthetic tree not established')
   hostns=os.readlink('/proc/self/ns/pid')
   inner=[r for r in tracked.values() if r['pid_namespace']!=hostns]
   if len(inner)<4:raise RuntimeError('private tree incomplete')
   time.sleep(0.5)
   # Exact pidfd identity only: terminate the bwrap launcher, never a process-name match.
   signal.pidfd_send_signal(handles[p.pid],signal.SIGKILL);terminated=True
   out,err=p.communicate(timeout=3)
   deadline=time.monotonic()+3
   while time.monotonic()<deadline:
    for pid in tracked:
     try:os.waitpid(pid,os.WNOHANG)
     except ChildProcessError:pass
    if all(select.select([fd],[],[],0)[0] for fd in handles.values()):break
    time.sleep(0.05)
   exited={str(pid):bool(select.select([fd],[],[],0)[0]) for pid,fd in handles.items()}
   remaining=[]
   for row in tracked.values():
    q=pathlib.Path('/proc/'+str(row['pid'])+'/stat')
    if q.exists():
     fields=q.read_text().rsplit(')',1)[1].split()
     if fields[19]==row['starttime']:remaining.append({'pid':row['pid'],'state':fields[0]})
   result={'attempt':attempt,'launcher_exit':p.returncode,'timeout_action':'exact pidfd SIGKILL after bounded tree readiness','tracked':list(tracked.values()),'pidfds_exited':exited,'remaining_same_identity':remaining,'stdout':out,'stderr':err}
   all_results.append(result);print(json.dumps(result),flush=True)
   if not all(exited.values()) or remaining:raise RuntimeError('cleanup identity still present')
  finally:
   if p.poll() is None:signal.pidfd_send_signal(handles[p.pid] if p.pid in handles else os.pidfd_open(p.pid),signal.SIGKILL);p.wait(timeout=3)
   for pid,fd in handles.items():
    if not select.select([fd],[],[],0)[0]:signal.pidfd_send_signal(fd,signal.SIGKILL)
   for pid in tracked:
    try:os.waitpid(pid,os.WNOHANG)
    except ChildProcessError:pass
   for fd in handles.values():os.close(fd)
 print(json.dumps({'repeated_timeout_cleanup_pass':len(all_results)==2 and all(not r['remaining_same_identity'] for r in all_results)}),flush=True)
finally:
 try:
  if {p.name for p in root.iterdir()}-{'inputs','work1','work2'}:raise RuntimeError('unexpected root')
  if {p.name for p in inputs.iterdir()}!={'tree.py'}:raise RuntimeError('unexpected input')
  for name in ('work1','work2'):
   w=root/name
   if w.exists():
    if {p.name for p in w.iterdir()}-{'size.bin'}:raise RuntimeError('unexpected work')
    if (w/'size.bin').exists():(w/'size.bin').unlink()
    w.rmdir()
  (inputs/'tree.py').unlink();inputs.rmdir();root.rmdir()
  print(json.dumps({'cleanup_root_absent':not root.exists()}),flush=True)
 except Exception as e:print(json.dumps({'cleanup_preserved':str(root),'reason':str(e)}),flush=True)

```

