# Phase 7K isolation decision

2026-10-16 — **BLOCKED for full isolated Memory staging execution.**

The narrow Bubblewrap synthetic isolation probe **passed**. Nonprivileged namespace creation works with explicit --unshare-user; no AppArmor change or sudo was needed. Filesystem/network separation, capability dropping, no-new-privileges and disabled nested user namespaces were directly demonstrated. All synthetic files were cleaned up. See PHASE7K_BUBBLEWRAP_PROBE_RESULTS.md for exact commands, exit statuses and evidence.

## What this closes

- Uncertainty that Bubblewrap can start under current host policy.
- Synthetic proof that approved inputs/workspace/private temp are accessible while host home and production directory parents are absent.
- Synthetic proof host loopback and outbound network are inaccessible.
- Synthetic proof read-only/root write restrictions and tested privilege barriers work.
- Per-process resource limits can be lowered without privileged/system-wide changes.
- Normal bounded exit and exact-file cleanup work.

This is a shared-kernel smoke test, not a complete adversarial escape proof or approval for a different mount layout. Preserve the minimal runtime allowlist, root remount, capability/namespace controls and clean environment in any future design.

## Remaining full-test blockers

1. No effective aggregate sandbox memory/process/CPU/output quota is demonstrated. Per-process rlimits cannot substitute for dedicated cgroup/VM limits. RLIMIT_NPROC is tied to the shared real UID, not an isolated workload allocation. Do not lower host/account-wide or service-level configuration.
2. The timeout path and descendant cleanup were not exercised; only normal completion was demonstrated.
3. Full Memory test runtime needs a reviewed expansion for cryptography, synthetic passwd/group/NSS, SQLite and synthetic local HTTP/Unix fixtures; this probe deliberately used Python -I -S without application/site packages. Import origins and revised mount set need validation.
4. The fixture-adjusted wrapper remains a proposal; a complete executable harness needs review/hash verification and a narrow one-method scope. No original tests should be modified.
5. Node/PDF remain optional missing coverage. Do not claim skipped original failures resolved; reduced coverage requires explicit acceptance.
6. No 92-file package transfer/execution authorization is inferred from this probe. Source/output mount confinement and current input hashes must still be checked before any such transfer.

## Minimum next decision

Approve a bounded synthetic follow-up only if an existing nonprivileged aggregate resource mechanism can be shown effective, including forced-timeout tree cleanup. Otherwise select a separately approved isolated Linux VM/container test environment with fixed resources; do not change Alfred host security policies or obtain privileged Docker access as a workaround.

After resource/runtime/harness gates are satisfied, seek separate explicit transfer and synthetic test execution approval. No deployment, production Memory promotion, credentials, live messages/providers or service modifications are authorized. Stop after this report.

