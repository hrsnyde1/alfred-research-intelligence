# Phase 7L staging gate decision

2026-10-16 — **BLOCKED for Research/Memory staging test execution.**

## Proven during this phase

- Two synthetic forced-timeout trials terminated the exact parent and all five tracked descendants/reaper processes, including a child that created a separate session.
- Exact pidfds and PID/starttime checks showed no matching processes left; subreaper collection prevented persistent orphans.
- Per-file 4096-byte limit and per-process 32-descriptor limit produced EFBIG/EMFILE in both trials.
- All synthetic temporary files removed; no production process signaled, data accessed, package transferred or services modified.

## Aggregate gate remains open

CPU/memory/process aggregate enforcement was not tested. Per-process rlimits and bounded wall time do not prove dedicated whole-tree quotas.

Important new evidence: user-manager root is writable and already enables cpu/memory/pids for children. Earlier SSH-session-only inspection missed this. Nonprivileged aggregate control may be feasible in a newly created child, with no change to existing quotas or services. app.slice enables only memory/pids; do not toggle its shared settings.

Current explicit restriction prohibits cgroup configuration changes. No new cgroup control files were written, no subtree modified, no existing process moved and no systemd unit created. This is an authorization/evidence blocker, not demonstrated technical need for sudo. Details: PHASE7L_RESOURCE_CONTROL_RESULTS.md.

## Smallest proposed next boundary

Separately authorize a unique synthetic child cgroup beneath the existing delegated user-manager root, only if its controller inheritance/permissions are confirmed. Permit limits solely on that new empty child, move only exact probe-owned processes, run tiny bounded aggregate tests, and remove only that child when empty. Preserve all existing unit/controller/quota configuration. No sudo, security policy changes or production workload migration. If this narrow authorization is unavailable, select an independently isolated fixed-resource Linux test environment.

Even after aggregate validation, full staging still requires reviewed application-runtime mounts/import origins, synthetic passwd/group and public-key harness, source/output confinement, optional Node/PDF coverage decisions and separate exact-inventory transfer/execution approval. No Research or Memory tests have run in this phase.

Stop after these reports; no deployment or package execution is approved.

