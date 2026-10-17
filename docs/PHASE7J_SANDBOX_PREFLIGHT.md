# Phase 7J sandbox preflight

2026-10-16 — **BLOCKED for isolated staging execution.** This was read-only Linux capability inspection and Mac-local source/document review, not a launched sandbox test. No namespace/container created; no package/code transfer, production API access, service change, credential/database/vault read or Linux write performed. SSH BatchMode=yes and StrictHostKeyChecking=yes succeeded as alfred on alfred.

## Directly observed capability evidence

| Boundary | Observed facts | What is not established |
| --- | --- | --- |
| Runtime | Python 3.12.3; SQLite 3.45.1; cryptography module present | Runtime inside a sandbox |
| Namespace tooling | bubblewrap 0.9.0, util-linux unshare 2.39.3; both root-owned 0755, not setuid | Successful unprivileged mount/user/network/PID/IPC isolation |
| Kernel policy | unprivileged_userns_clone=1; max_user_namespaces=31437; AppArmor enabled and restrict_unprivileged_userns=1 | Policy permission for proposed launcher |
| Current SSH process | AppArmor current label unconfined; CapEff=0, NoNewPrivs=0, Seccomp=0 | A confined test child; current login is not the sandbox |
| AppArmor evidence | /etc/apparmor.d/bwrap and bubblewrap absent; loaded profiles open denied despite os.access returning true | No conclusion that all applicable profiles are absent. Permission denial was not bypassed |
| Containers | Docker CLI 29.1.3 installed; /run/docker.sock exists mode 0660, not writable by current account. Podman absent from PATH | Docker API access or an approved image/container. No daemon API called |
| Resource tools | prlimit, timeout, systemd-run installed; cgroup v2 mounted | A delegated bounded test scope |
| Own session cgroup | memory.max, pids.max, cpu.max and cgroup.procs not writable | Cannot assume unprivileged cgroup limits can be set |
| Login rlimits | AS/CPU/file size unlimited; NPROC=31437; NOFILE soft 1024/hard 1048576; CORE soft 0 | Adequate aggregate limits for tests/children |
| Runtime path layout | /bin → usr/bin; /lib → usr/lib; /lib64 → usr/lib64 | Earlier bind layout must be corrected/verified, not copied blindly |
| Optional imports | pymupdf and fitz specs both absent now; cryptography spec present | PDF coverage; Node previously absent, not reprovisioned |
| Staging | /home/alfred/research-staging absent | No writable test workspace created |

Prior Phase 7I established ext4 home filesystem, libc renameat2 and SO_PEERCRED availability. Those are historical inspected facts, not proof that atomic operations/socket authentication work in the proposed namespace.

## Required boundary

Prefer existing bwrap only if a separately authorized launch proves it works. Use a new user/mount/PID/network/IPC/UTS namespace, private proc/dev/tmp, explicit reviewed read-only runtime and source mounts, a fresh result-only writable mount, empty environment and no inherited service descriptors/SSH agent. No host-root, host-home, /opt, /run, /var, Docker socket, vault, credential file or production Unix socket mount. Private loopback fixtures must not share host networking. Source paths remain read-only; symlink/mount escape attempts must fail.

Use no-new-privileges, drop capabilities in child and prevent namespace/mount reconfiguration after setup through an approved sandbox/seccomp policy. A shared kernel is not a VM guarantee; malicious privileged execution is not approved. Limit process tree, memory, CPU, output size and wall time, and prove all descendants terminate. Existing CLI availability is not proof of delegated cgroup control. Per-process prlimit plus timeout alone is not an aggregate memory/process-tree boundary; choose an approved effective mechanism or isolated VM with fixed resources.

No Docker access elevation, sudo, AppArmor edits, sysctl changes, service-manager launch or sandbox weakening is authorized. If unprivileged bwrap cannot satisfy the gate, use a separately approved isolated Linux VM/container environment outside production. Read-only inspection cannot turn missing dynamic evidence into PASS.

## Specific launcher corrections

The Phase 7I command is a template, not an approved executable launcher. Preserve merged-/usr symlinks, including /bin for any shebang subprocess. Tests invoke pwd.getpwuid/getpwnam; a sandbox with only /etc/skel lacks account lookup fixtures. Supply minimal synthetic passwd/group (and reviewed local-files NSS policy if needed) matching sandbox numeric UID/GID; do not mount host account/credential files or contact directory services. Verify uid/gid chown and SO_PEERCRED tests under that mapping.

Avoid exposing entire /usr blindly: review its runtime subtree/symlinks for installed Alfred code/config, and expose only required Python, libraries and approved tools. Prevent nonallowlisted installed Alfred imports. Replace broad writable workspace with source read-only mounts and separately scoped result-file outputs, adapting runner output destinations in a reviewed harness if necessary. Preserve original source/tests and disclose harness changes.

## Verdict

**BLOCKED.** Installed mechanisms could support isolation, but policy permission, effective namespace/mount/network denial, credential separation and aggregate resource controls have not been demonstrated. Creating a namespace was explicitly forbidden in this phase, so no dynamic checks were attempted. Permission to run a bounded sandbox-only smoke test and review a finalized launcher is the minimum next authorization; this does not include transferring/executing the Memory package.
