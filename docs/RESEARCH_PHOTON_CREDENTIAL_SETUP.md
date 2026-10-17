# Research Photon protected credential setup

2026-10-16. **Owner-operated future procedure only. No credentials read, requested or provisioned in this task.** Separate standalone service; no Personal secret reuse or fallback.

Required secret references:

| systemd credential | Root-only source |
|---|---|
| research-project-id | /etc/alfred-research-photon/credentials/research-project-id |
| research-project-secret | /etc/alfred-research-photon/credentials/research-project-secret |

LoadCredential exposes these under the service's generated **CREDENTIALS_DIRECTORY**; main.mjs reads that variable only as a path. No PHOTON_PROJECT_ID/SECRET, PHOTON_RESEARCH_* or Personal token environment variables are required. Explicit Spectrum options are projectId/projectSecret from these files. Ambient SDK credential fallback is not used; missing/invalid files or mismatched policy project_id fail closed.

Nonsecret but private identity policy: /etc/alfred-research-photon/policy.json, root:alfredresearchphoton0640, root-controlled parent0750. Required fields: role='research', enabled=false initially, intake_enabled=false, project_id, dedicated line (never shared), approved space, authorized sender, Research profile, fixed connection_ref, state_dir='/var/lib/alfredresearch-photon'. Owner enters actual bindings directly on Linux using sudoedit; no values should return to chat/Git/logs. Do not infer recipient/sender/space from message text or widen scope to discover unknown identities. Obtain verified provider/device metadata first.

## Direct terminal entry after approved installation

The owner authenticates sudo directly. Secret source parent must already be root-owned0700 from reviewed installation; stop on symlinks/unknown ownership. Do not set shell xtrace, echo values, export secrets, pass them in arguments, use shell history assignments, cat files, print systemctl Environment, or copy Personal credentials. The following creates new files only and refuses overwrite; enter values through the terminal's non-echo prompt:

```sh
sudo python3 -I -S -B - <<'PY'
import os,pathlib,getpass,stat
root=pathlib.Path('/etc/alfred-research-photon/credentials')
assert os.geteuid()==0
for p in [root,*root.parents]:
 assert not p.is_symlink()
st=root.stat();assert st.st_uid==0 and stat.S_IMODE(st.st_mode)==0o700
for name in ('research-project-id','research-project-secret'):
 value=getpass.getpass(name+' (hidden terminal input): ')
 if not value or value!=value.strip() or len(value)>256 or '\n' in value or '\r' in value:
  raise SystemExit('Invalid credential format; nothing truncated')
 p=root/name
 fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600)
 with os.fdopen(fd,'w') as f:
  f.write(value);f.flush();os.fsync(f.fileno())
 del value
fd=os.open(root,os.O_RDONLY|os.O_DIRECTORY)
os.fsync(fd);os.close(fd)
print('Research credential sources created; values suppressed')
PY
```

No values appear in this command/script. Python getpass uses the controlling terminal even with script stdin redirected; abort if terminal warns echo cannot be disabled. If interrupted after one file, retain it and have owner reconcile partial setup; do not overwrite, print or blindly rerun. Root0600 sources are mapped to service-private read-only systemd credential files. Service file-mode behavior and effective access must be checked by owner using fake credentials before live setup; syntax/import validation did not run a real credential-bearing unit.

Owner creates policy via sudoedit, validates JSON privately, then sets root:alfredresearchphoton0640. Source project ID must exactly match policy; no default. Owner confirms project credentials belong solely to Research and line mapping is provisioned. No credentials are stored in state/health/documents/fixtures/repository. Dedicated service UID has no Personal groups; namespace exposes only selected runtime/SDK and its own state/config/credential mount. The host root administrator remains trusted.

Do not activate enabled=true as part of credential entry. Research-to-Hermes intake remains disabled regardless of transport enable. A secret/reference setup authorization does not authorize a live login or message. Use RESEARCH_PHOTON_FIRST_LIVE_TEST.md only after the owner approves those separate operations.
