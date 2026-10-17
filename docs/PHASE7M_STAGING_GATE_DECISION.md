# Phase 7M staging gate decision

2026-10-16 — **BLOCKED.**

The delegated user-manager directory has CPU/memory/pids controllers and adequate observed headroom. However, SSH-born synthetic processes are outside that delegation. The common ancestor's cgroup.procs is root-owned and not writable by alfred, preventing direct nonprivileged placement into a newly created probe child under documented kernel containment rules.

No cgroup or temporary file was created, no aggregate test ran, no quota/membership changed and no cleanup is outstanding. Inspection commands exited 0; these are not aggregate-test pass results. See PHASE7M_CGROUP_PROBE_RESULTS.md for exact commands/access evidence and [kernel containment requirements](https://docs.kernel.org/admin-guide/cgroup-v2.html#delegation-containment).

## Minimum next boundary

Obtain component-owner evidence and separate authorization for launching a tiny synthetic process **already inside** the existing delegated user-manager subtree, for example through a specifically reviewed transient user-service launch. This is a different operation from directly moving an SSH child. Do not assume permission to create a unit or call the user-manager bus from the present one-cgroup authorization.

Review that launch route's exact ownership, child-cgroup creation, quota placement, inherited limits and cleanup before attempting it. It must not modify/restart existing services or expand global delegation. No sudo, ancestor permission changes or production process migration is proposed.

If a bounded nonprivileged launch path cannot be authorized, select a separately approved isolated fixed-resource Linux test host. Existing Bubblewrap isolation and Phase 7L timeout/file/descriptor evidence remain valid within their scope, but do not close aggregate enforcement.

The full staging gate still also requires reviewed application runtime/account fixtures, one-case public-key harness, source/output confinement, optional Node/PDF coverage decisions, and separate package transfer/execution approval. No deployment or production Memory operation is authorized.

Stop and await owner review.

