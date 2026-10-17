# Phase 7I Linux staging readiness

Assessment: 2026-10-16. **Conditionally feasible; not authorized or ready for unrestricted test execution.** No staging directory was created, code transferred, staging tests executed, dependencies installed, or Linux files changed. SSH used BatchMode=yes, StrictHostKeyChecking=yes, bounded connection timeouts, and existing authentication. Initial sandbox SSH denial was resolved through approved tool escalation; strict SSH then succeeded as alfred on hostname alfred.

## Evidence reviewed and missing

Read both Phase 7H baseline/regression review documents and actual staging manifest, test sources, runner and result artifacts. These requested inputs are absent: `PHASE7H_MEMORY_IMPLEMENTATION_REPORT.md`, `PHASE7H_MEMORY_TEST_RESULTS.md`, `PHASE7H_MEMORY_DIFF_REVIEW.md`. Do not treat the two review documents as replacements. Complete those reports before transfer approval.

Recorded baseline: 102 run, 79 pass, 17 failures, 3 errors, 3 skips. Modified: 125 run, 102 pass, same 17 failures, 3 errors and 3 skips. Of the 20 cases, 15 involve missing Mac renameat2 and four involve missing Mac SO_PEERCRED; the twentieth is a missing installed public-key fixture, not purely an OS limitation. Linux support makes 19 cases suitable for retest, not proven passing. No tests were rerun in Phase 7I.

## Directly verified Linux facts

| Check | Observation |
| --- | --- |
| Runtime | /usr/bin/python3 3.12.3; SQLite 3.45.1 |
| Platform | x86_64 Linux 6.8.0-147-generic, glibc 2.39 |
| Atomic rename | libc exports renameat2; actual filesystem operations not exercised |
| Peer credentials | socket.SO_PEERCRED exists; authenticated socket exchange not exercised |
| Filesystem | /home/alfred is on ext4 mounted rw,relatime |
| Account/path | uid 1000; /home/alfred is writable, non-symlink, mode 0750 |
| Proposed staging parents | /home/alfred/research-staging and child phase7i-memory-20261016 do not exist |
| Available dependencies | cryptography 41.0.7; stdlib unittest/sqlite3 |
| Missing login dependencies | Node absent from PATH and /usr/bin/node, /usr/local/bin/node, /home/alfred/.local/bin/node; fitz/PyMuPDF and pytest absent from system Python |
| Tools | timeout, unshare, bwrap, git available |
| Isolation settings | unprivileged_userns_clone=1; apparmor_restrict_unprivileged_userns=1. Working unprivileged namespace sandbox NOT established |
| Ubuntu skeleton | All three /etc/skel file hashes match copied source's pinned SKELETON |
| Installed public-key fixture | Known /opt/.../authorized-public.pub exists; contents deliberately not read |

Only system Python was checked. The two conventional Memory venv paths checked do not exist; other isolated runtimes or Node locations remain unknown. No package installation is proposed without approval. Pytest is unnecessary for these unittest suites. PyMuPDF and Node omissions must be reported as skips, not passing extraction/device coverage.

## Isolation and service conflicts

Observed running services include alfred-hermes, alfred-photon, alfred-memory-v1, alfred-hq-capture, alfred-obsidian-editor-hq and alfred-development-intake. Development gateway was activating at the snapshot. Service names/states only were inspected; no configuration, credential values, production sockets or databases were opened.

Propose `/home/alfred/research-staging/phase7i-memory-20261016`, owned by alfred, new directories mode 0700 and umask 077 after separate authorization. It is outside /opt releases, vaults and service state. Same-user directories alone do not enforce isolation from production resources accessible to alfred. Tests create temporary synthetic SQLite databases and local HTTP/Unix-socket fixtures; they must run in a private filesystem/network namespace without host production paths or host network. These fixtures are ephemeral test processes, not production services; separate execution approval must explicitly allow them.

Existing Python connect guard permits all loopback and Unix connections and does not constrain Node subprocesses. It is insufficient alone to prove production isolation. Namespace availability needs a separately authorized bounded sandbox smoke test before test execution; AppArmor may prevent it. Do not weaken host settings. If blocked, use a separately approved isolated Linux VM/container elsewhere rather than touching production.

The existing-file test reads a deployment key fixture unless substituted. Hide /opt and inject an explicitly synthetic `_authorized_line` fixture in a reviewed test-only harness, identically for baseline/work; preserve original source/tests and disclose the harness difference. Never use the real installed public key. With no harness approval, retain the inherited failure rather than access that path.

## Blockers and minimum next authorization

1. Missing three Phase 7H implementation documents and current explicit transfer hash allowlist.
2. Working filesystem/network sandbox is unverified; AppArmor user namespace restriction present.
3. Node unavailable; full device coverage requires finding an already installed approved runtime or separately approving a dependency/environment. No installation now.
4. Synthetic public-key fixture harness requires approval; no production credential fixture access.
5. PDF parser missing; approve explicit skip for compatibility-only runs or supply an already reviewed isolated parser separately.

Minimum separate authorization: create only the proposed private workspace; transfer only the enumerated nonsecret source/test/helper files with hashes; perform sandbox preflight; execute bounded synthetic tests in that sandbox and write only workspace outputs. This is not deployment approval, not production Research promotion authorization, and not permission to modify services. Cleanup requires a subsequent path-specific approval.
