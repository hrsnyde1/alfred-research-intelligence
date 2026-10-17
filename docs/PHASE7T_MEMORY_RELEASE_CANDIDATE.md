# Phase 7T — Memory integration release candidate

2026-10-16 — **Candidate prepared and integrity-verified; installation/activation BLOCKED pending component-owner gates.** No Linux source/service/database/configuration change or test execution occurred in Phase 7T. Memory was observed active/running before and after read-only inspection. Research remains inactive.

## Exact package

Version: `0.1.0-rc1`.
Release ID: `alfred-memory-research-extension-0.1.0-rc1-phase7t-linux-20261016`.

[Candidate archive](../artifacts/releases/alfred-memory-research-extension-0.1.0-rc1-phase7t-linux-20261016/alfred-memory-research-extension-0.1.0-rc1-phase7t-linux-20261016.tar.gz)

Repository-relative path:
`artifacts/releases/alfred-memory-research-extension-0.1.0-rc1-phase7t-linux-20261016/alfred-memory-research-extension-0.1.0-rc1-phase7t-linux-20261016.tar.gz`

SHA-256: `77c8fa1487ccc4d42919ef38a334da4e98d5a29e5798bcb69429660bfd8eca00`.
Size: **39,576 bytes**.

[External checksums](../artifacts/releases/alfred-memory-research-extension-0.1.0-rc1-phase7t-linux-20261016/SHA256SUMS), [candidate manifest](../artifacts/releases/alfred-memory-research-extension-0.1.0-rc1-phase7t-linux-20261016/contents/CANDIDATE_MANIFEST.json), [integrity verification](../artifacts/releases/alfred-memory-research-extension-0.1.0-rc1-phase7t-linux-20261016/INTEGRITY_VERIFICATION.json), [complete unified diff](../artifacts/releases/alfred-memory-research-extension-0.1.0-rc1-phase7t-linux-20261016/contents/FULL_DIFF.patch).

This is a minimal **source-overlay review candidate**, not a standalone Memory service, executable installer, wheel or approved deployable production integration. It preserves the exact tested bytes; no new production feature was implemented to satisfy deployment requirements. It contains two source files and one validation test file plus seven review/integrity files, ten regular archive members total. No databases, ledger/key material, vaults, credentials, configuration, service units, installers, production migrations, caches or runtime state are bundled. Historical test outcome metadata is evidence, not saved application state.

## Installed baseline comparison

`/opt/alfred-obsidian-v1/current` resolves to the expected release:
`/opt/alfred-obsidian-v1/releases/4d5ba29bd3027e74c808a8feaf1b5dadfded22f0`.

All **34 exact tested BASELINE_MANIFEST paths** match installed source byte lengths and SHA-256, with **zero mismatches**. All 17 Linux staging payload files and its checksum manifest match Phase 7S/7R pins. Both added paths are absent from installed source. Local untouched baseline/work comparison finds exactly 33 unchanged originals, one modified original and two additions. Packaging proceeded only after those comparisons succeeded; a mismatch would have blocked creation.

Coverage is explicit: the copied 34-path baseline is a reviewed source subset, **not every file in the installed release**. Directory-name inspection also finds installed backup/history/ops/stage and Hermes adapter modules outside that tested snapshot; they were not bundled, modified, or represented as tested. Owner review of additional consumers remains an installation gate. Current source match does not prove effective process imports/service runtime configuration; no protected configuration or production data was opened.

The service reports `ActiveState=active`, `SubState=running` in both snapshots. This is bounded service-state evidence, not a live API/health/data test or a guarantee against unrelated changes between observations. Our Linux actions were reads only; existing Memory operation was not altered.

## Exact approved code changes

| Candidate member | Intended future source mapping | Status / tested SHA-256 |
| --- | --- | --- |
| `source/focused_v1/store.py` | New reviewed Memory release's `source/focused_v1/store.py` | Modify duplicate reply only; `0d84c9c12c0715f14be7729a5007073ebc99f55fa7820e6bed81a55834d969c1` |
| `source/focused_v1/research_stage.py` | Same release's `source/focused_v1/research_stage.py` | Add test-only structured extension; `15e24eb7aa3f84f8796d12dd9d4684d2748943cfda58dc3fa8827428b12dcd3a` |
| `tests/test_research_memory_stage.py` | Isolated validation fixture only | Add unchanged 23-method test file; `53e1f0b095443401ec79daa8a0a7c534a48c47b649972395123af1d457e6cd1e` |

The test file contains all original 23 definitions so its bytes remain identical to the tested source; only seven methods have Linux execution acceptance. Packaging the file does not authorize discovery/running its other methods. No tests are installed into or executed by the Memory service.

No existing server, API action allowlist, Obsidian bridge/export/Sync code or service configuration is included for replacement. The legacy API's one deliberate difference would be truthful stored `review_state` in a duplicate-create reply; request/response keys and stored state remain unchanged. Pending-edit and legacy kind-mismatch policy are not silently redesigned.

## Test support and current disable status

Phase 7S: **7 selected Linux extension methods passed, 0 failures/errors/skips**, exact IDs and evidence in TEST_EVIDENCE.json and [Phase 7S results](PHASE7S_MEMORY_LINUX_TEST_RESULTS.md). Baseline duplicate probe raw exit 1 reproduces its expected false-approved pending reply; work comparison passes. Seven-test wall 6.112 s, self peak RSS 39,560 KiB, Python 3.12.3, cryptography 41.0.7/OpenSSL 3.0.13 in Bubblewrap. No tests rerun during packaging.

These tests support candidate/provenance checks, denial of synthetic-to-production trust, separate commit/simulated-promotion receipts, full scoped retrieval and invalidation. They do not establish full Memory/Obsidian regression clearance. The original copied Mac suites retain their historical 17 failures/3 errors/3 skips; remaining sixteen extension methods and broad Linux regressions remain unexecuted.

Production remains disabled in candidate bytes: explicit test_only/TestAuthority constructor guards; real `promote()` and `dispatch_research()` always deny; no Research HTTP route; retention/delete and export/Sync raise Unavailable. Test `simulate_promotion` is explicitly NON_PRODUCTION and cannot authenticate a real trusted attestation. **No default Research principal has real promotion authority.**

## Integrity checks actually completed

- Current installed 34-path and staged 17-path read-only SHA comparisons before/after; exact added-path absence; source diff verified against local original bytes.
- Every archived source/test file equals Phase 7S input bytes.
- Ten unique safe regular members, no links/devices/special entries or traversal paths; fixed tar metadata and gzip mtime for reproducible archive encoding.
- Read-back archive-member bytes matched all expected bytes without extraction/execution; all nine FILES.sha256 entries verified. CANDIDATE_MANIFEST covers eight non-self/non-checksum content files; FILES.sha256 additionally covers that manifest; its own digest and archive digest are pinned by external SHA256SUMS.
- Disk re-read of archive and all member source files matched; candidate source syntax parsed only, no imports.

Candidate manifest SHA-256: `2e01004743beef79fefc874780d5679024f4cf0ec91a7988932c82339eb599b9`.
FULL_DIFF.patch SHA-256: `8add6781899c220bb4489636599db2401ffbe8263ed30bdf813f9cab5df50e1f`.
FILES.sha256 SHA-256: `c3948fe0d55785de7be6b498a8476c74c3b76256beacc97fbb863d2087b0ceed`.

## Remaining blockers and proposed next step

Review [complete diff/API/schema analysis](PHASE7T_MEMORY_DIFF_REPORT.md) and [installation gates](PHASE7T_MEMORY_INSTALLATION_GATES.md). Required closure includes Memory-owner source/consumer sign-off, genuine verifier/principal/grant/receipt contracts, production schema/retention/backup/migration/rollback design, approved dependency layout, broader isolated regressions and exact new-release/service action/canary authorization.

**Next step:** Memory component owner reviews this exact archive/hash and its dormant production boundary, then separately authorizes a package-to-isolated-staging regression/migration rehearsal with agreed scope. Do not install this overlay into current source, run test initialization against production, enable simulate_promotion as real promotion, restart services or move the live symlink. Any production-capable implementation must be reviewed/tested and versioned as a new candidate; flipping test flags is not an integration plan.

No Linux transfer of this candidate, deployment, commit/push, service restart, credential change, database migration, Obsidian change or Research activation occurred. Stop after candidate preparation; await owner approval.
