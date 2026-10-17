"""Proposed owner-only code transaction. No credential/state/message operations."""
import base64,hashlib,json,os,pathlib,tempfile,subprocess,sys

def digest(data):return hashlib.sha256(data).hexdigest()
def target(root,name):
    rel=pathlib.PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts or str(rel)!=name:raise ValueError('unsafe manifest path')
    p=root/rel
    for ancestor in [p,*p.parents]:
        if ancestor==root.parent:break
        if ancestor.is_symlink():raise ValueError('symlink target')
    return p

def read_attrs(p):
    if hasattr(os,'listxattr'):
        return {k:os.getxattr(p,k) for k in os.listxattr(p)}
    if sys.platform!='darwin':raise RuntimeError('xattr support required')
    names=subprocess.check_output(['/usr/bin/xattr',str(p)],text=True).splitlines()
    return {k:bytes.fromhex(subprocess.check_output(['/usr/bin/xattr','-px',k,str(p)],text=True)) for k in names}
def write_attr(p,k,value):
    if hasattr(os,'setxattr'):os.setxattr(p,k,value)
    elif sys.platform=='darwin':subprocess.run(['/usr/bin/xattr','-wx',k,value.hex(),str(p)],check=True,capture_output=True)
    else:raise RuntimeError('xattr support required')

def metadata(p):
    st=p.stat()
    return {'uid':st.st_uid,'gid':st.st_gid,'mode':st.st_mode&0o7777,
        'xattrs':{k:base64.b64encode(v).decode() for k,v in read_attrs(p).items()}}

def syncdir(p):
    fd=os.open(p,os.O_RDONLY)
    try:os.fsync(fd)
    finally:os.close(fd)

def replace(p,data,meta):
    fd,name=tempfile.mkstemp(prefix='.photon-review-',dir=p.parent)
    try:
        with os.fdopen(fd,'wb') as out:
            out.write(data);out.flush();os.fchown(out.fileno(),meta['uid'],meta['gid'])
            os.fchmod(out.fileno(),meta['mode'])
            for k,v in meta.get('xattrs',{}).items():write_attr(name,k,base64.b64decode(v))
            os.fsync(out.fileno())
        assert digest(pathlib.Path(name).read_bytes())==digest(data)
        assert metadata(pathlib.Path(name))==meta
        os.replace(name,p)
        d=os.open(p.parent,os.O_RDONLY)
        try:os.fsync(d)
        finally:os.close(d)
    finally:
        if os.path.exists(name):os.unlink(name)

def verify(root,artifact,records):
    for r in records:
        p=target(root,r['path']);src=target(artifact,r['artifact'])
        if not src.is_file() or digest(src.read_bytes())!=r['new']:raise ValueError('artifact drift')
        if r['old'] is None:
            if p.exists():raise ValueError('unexpected existing target')
        elif not p.is_file() or digest(p.read_bytes())!=r['old']:raise ValueError('baseline drift')

def apply(root,artifact,backup,records,guard,hook=lambda n:None):
    verify(root,artifact,records)
    for r in records:
        p=target(root,r['path'])
        if p.exists():assert metadata(p)['uid']==r['old_uid'] and metadata(p)['gid']==r['old_gid'] and metadata(p)['mode']==r['old_mode']
    for g in guard:
        p=target(root,g['path']);assert digest(p.read_bytes())==g['sha256']
    backup.mkdir(mode=0o700,parents=False,exist_ok=False);syncdir(backup.parent)
    saved=[]
    for i,r in enumerate(records):
        p=target(root,r['path']);entry={**r,'old_metadata':metadata(p) if p.exists() else None}
        if p.exists():replace(backup/str(i),p.read_bytes(),{'uid':os.geteuid(),'gid':os.getegid(),'mode':0o600,'xattrs':{}})
        saved.append(entry)
    plan={'records':saved,'guards':guard,'created_dirs':[]}
    replace(backup/'snapshot.json',json.dumps(plan,sort_keys=True).encode(),{'uid':os.geteuid(),'gid':os.getegid(),'mode':0o600,'xattrs':{}})
    for i,r in enumerate(saved):
        p=target(root,r['path']);missing=[];parent=p.parent
        while not parent.exists():missing.append(parent);parent=parent.parent
        for directory in reversed(missing):
            plan['created_dirs'].append(str(directory.relative_to(root)))
            replace(backup/'snapshot.json',json.dumps(plan,sort_keys=True).encode(),{'uid':os.geteuid(),'gid':os.getegid(),'mode':0o600,'xattrs':{}})
            directory.mkdir(mode=0o755);syncdir(directory.parent)
        meta=r['old_metadata'] or {'uid':r['new_uid'],'gid':r['new_gid'],'mode':r['new_mode'],'xattrs':{}}
        replace(p,target(artifact,r['artifact']).read_bytes(),meta)
        assert digest(p.read_bytes())==r['new'];hook(i)
    for g in guard:assert digest(target(root,g['path']).read_bytes())==g['sha256']

def rollback(root,backup):
    plan=json.loads((backup/'snapshot.json').read_text())
    for i,r in enumerate(plan['records']):
        p=target(root,r['path']);current=digest(p.read_bytes()) if p.exists() else None
        if current not in (r['old'],r['new']):raise ValueError('unknown current version; stop')
        if r['old'] is not None and digest((backup/str(i)).read_bytes())!=r['old']:raise ValueError('backup drift')
    for g in plan['guards']:assert digest(target(root,g['path']).read_bytes())==g['sha256']
    for i,r in enumerate(plan['records']):
        p=target(root,r['path'])
        if r['old'] is None:
            if p.exists():p.unlink();syncdir(p.parent)
        else:replace(p,(backup/str(i)).read_bytes(),r['old_metadata'])
    for name in reversed(plan['created_dirs']):
        p=target(root,name)
        if p.exists():p.rmdir();syncdir(p.parent) # never recurse

if __name__=='__main__':
    if os.geteuid()!=0:raise SystemExit('owner administrator/root execution required')
    if len(sys.argv)!=4:raise SystemExit('usage: operator.py verify|install|rollback ARTIFACT BACKUP')
    action,art,back=sys.argv[1:];artifact=pathlib.Path(art).resolve();backup=pathlib.Path(back)
    m=json.loads((artifact/'INSTALL_MANIFEST.json').read_text())
    # Offline services are a necessary gate, not authorization or quiescence proof.
    if action in ('install','rollback'):
        for service in ('alfred-hermes.service','alfred-photon.service'):
            state=subprocess.check_output(['systemctl','show',service,'-p','ActiveState','--value'],text=True).strip()
            if state!='inactive':raise SystemExit('service must be inactive: '+service)
    if action=='verify':
        verify(pathlib.Path('/'),artifact,m['records'])
        for g in m['guards']:assert digest(target(pathlib.Path('/'),g['path']).read_bytes())==g['sha256']
        for r in m['records']:
            if r['old'] is not None:
                md=metadata(target(pathlib.Path('/'),r['path']))
                assert (md['uid'],md['gid'],md['mode'])==(r['old_uid'],r['old_gid'],r['old_mode'])
    elif action=='install':apply(pathlib.Path('/'),artifact,backup,m['records'],m['guards'])
    elif action=='rollback':rollback(pathlib.Path('/'),backup)
    else:raise SystemExit('unknown action')
