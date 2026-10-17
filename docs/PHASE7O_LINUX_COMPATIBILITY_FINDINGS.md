# Phase 7O — Linux compatibility findings

2026-10-16 — **PASS for the approved eight-test subset on Python 3.12.3.** Eight tests ran in separate Bubblewrap namespaces; all passed with no failures, errors or skips. [Results and exact commands](PHASE7O_LINUX_TEST_RESULTS.md).

## Validator correction

The original validator incorrectly equated checksum coverage with the 90-file payload inventory. The corrected procedure requires exactly 90 payload entries, 91 checksum entries (payload plus `RELEASE_INVENTORY.json`) and 92 archive/extracted regular files (adding `FILES.sha256`). The inventory is accepted as a checksum entry only at its exact path with its independently pinned digest and validated bytes. No general extra-file allowance was introduced.

All payload hashes/lengths, every checksum entry, exact file membership and archive-member bytes passed. Duplicate/unsafe paths, duplicate JSON keys, missing/extra/modified entries and mismatches are rejected. The archive matched the Mac-pinned SHA-256 `ec6dedd835e8c926d5e862a15d392c090e6831fbc84b41f1d5e6848d2c3fe63e`. Before/after comparisons confirmed all 92 extracted files and the archive unchanged.

A synthetic preflight initially rejected Bubblewrap-generated PWD because the new environment check omitted it. A names-only diagnostic identified that benign variable. Validation was corrected to allow it only when exactly `/workspace`; environment clearing and isolation controls were retained. No Research test or import occurred in those unsuccessful synthetic preflights. These were validator issues, not Research compatibility failures or observed production exposure.

## Compatibility demonstrated

- All 31 statically listed package modules imported successfully inside each test sandbox.
- Packet/source-result serialization, determinism and malformed-contract rejection passed.
- SQLite-backed cross-company read/write denial passed with temporary synthetic databases.
- All offline source categories and company identities passed their approved checks; PDF remains explicitly unsupported.
- Cross-company/principal source denial, local fixture-root isolation, and local script/symlink nonexecution checks passed.
- No Linux-specific application defect was observed within this scope. Sandbox application wall time totaled 3.250 s; maximum interpreter self peak RSS was 27,088 KiB.

## Isolation and cleanup

The approved filesystem/network restrictions and ceilings were applied unchanged. Synthetic preflight verified private namespaces, no host service/credential paths or SSH agent environment, no host-loopback/outbound connectivity, read-only code/runtime mounts, sized private scratch mounts and exact rlimit readback. The supervisor's exact-pidfd forced cleanup succeeded before application execution; every observed launcher/reaper/interpreter identity was gone after each case. Private scratch mounts and unlinked logs were released. No production service or vault was mounted or contacted.

No application timeout or resource ceiling was hit. Aggregate resource enforcement was not added or measured; the result is limited to the reviewed finite single-interpreter subset. The forced cleanup probe exercised the teardown path after synthetic readiness, while retaining the 20-second watchdog; it was not a full 20-second exhaustion probe or a fresh separate-session descendant test.

## Scope and owner review

This is a limited Linux compatibility result, not full Research acceptance or deployment readiness. The other 297 tests, restart/hot-journal/concurrency coverage, live providers and service integrations were not executed. No cgroup/AppArmor, packages, services or configuration changed. No activation, production Memory/Obsidian write, commit, push or deployment occurred.

Stop after these reports. Await owner review before any expanded execution or activation.
