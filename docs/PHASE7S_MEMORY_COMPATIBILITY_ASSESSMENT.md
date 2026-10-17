# Phase 7S — Memory compatibility assessment

2026-10-16 — **PASS within the seven approved synthetic extension tests on Linux Python 3.12.3.** Seven ran and seven passed, with zero failures/errors/skips. [Exact names, commands, comparisons and cleanup](PHASE7S_MEMORY_LINUX_TEST_RESULTS.md).

The exact Phase 7R staging root was used; no new root or source substitution. All 17 source hashes and checksum-manifest bytes, separate baseline/work trees, runtime mounts and dependencies, network/host-loopback isolation, resource ceilings and actual 20-second timeout cleanup passed pre-execution checks. Cryptography 41.0.7/OpenSSL 3.0.13 loaded inside the sandbox. No production path/config/credential/vault was exposed.

## Findings

- Duplicate-create accurately returns stored pending/rejected/approved state without changing rows. The paired Phase 7Q derived control reproduces the untouched baseline's known false-approved pending reply (raw exit 1, one expected assertion failure) and passes on work (raw exit 0). These two control invocations are separate from the seven extension passes.
- Candidate checks bind packet version/digest, source revision/full evidence, per-claim review and independent contributors; changed metadata cannot reuse an attestation.
- Production constructors/promotion remain denied. Synthetic REJECTED/NMR verdicts cannot obtain test attestation issuance, and simulated attestation/promotion does not establish genuine production trust.
- Submit, commit, simulated promotion and fresh retrieval produce distinct operations/receipts; commit alone does not create readable promoted knowledge.
- Authorized specialist retrieval preserves the complete candidate/citations, including >1536-character evidence; mismatched audience is denied. Historical receipt replay remains labeled historical.
- Invalid, expired, disputed, superseded and revoked records are excluded along the selected authorization/currentness paths. This is not exhaustive principal/issuer revocation coverage of unselected methods.

No Linux-specific defect was observed in these modified paths. The baseline duplicate issue is an existing implementation defect, not a new platform failure. Compatibility of all legacy Memory/Obsidian behavior remains unproven: the current vault restriction excluded Phase 7Q's unmanaged-note controls, and no full original suite ran. Source/server/export files retain their approved bytes.

## Resources and confinement

Seven extension cases used **6.112 s** total sandbox wall, **1.604 s** test-run time and **5.185 s** interpreter self CPU. Highest self peak RSS was **39,560 KiB** (38.63 MiB). Each case retained 10-second process CPU, 256 MiB address-space, 8 MiB/file, 64 descriptors, no cores, 20-second wall and private 16 MiB /tmp plus /workspace ceilings. No application resource denial or timeout occurred. No aggregate cgroup claim is made.

The forced synthetic timeout exited -9 as expected and left no matching identities. All two comparison and seven extension namespace trees also cleaned up, with no observed descendants remaining. No arbitrary process/account signals. Before/after hashing confirmed all **196 unique pinned paths** unchanged, including 18 staged files, runtime files and the frozen Research release/archive. No staging source or production Memory data/config changed.

## Acceptance limits and next boundary

This result establishes only the selected staging-only extension behavior and narrow duplicate comparison. It does not establish all 23 extension tests, full Memory/Obsidian compatibility, resolution of inherited Mac failures, factual verification, genuine attestation credentials, production grants/schema migration or deployment readiness.

The module still reuses the existing MemoryStore transaction boundary and has no enabled Research HTTP action or additional service. Real promotion/dispatch remain denied; deletion/retention and export/Sync policy remain unconfigured/fail-closed. Broader regressions and production trust/schema/tenant/retention/export decisions remain blockers to activation.

No production API call, Memory write, vault read/modification, credential access, installation, service change, cgroup/AppArmor change, commit, push, deployment or Research activation occurred. Staging is retained. Stop after these reports; any broader tests or operational change require a new owner instruction.
