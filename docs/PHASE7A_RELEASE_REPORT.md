# Phase 7A Mac release preparation report

Release ID: `alfred-research-v1-0.1.0-phase7a-mac-20261015`. Scope: Mac-only packaging of the owner-accepted Phase 0–6 offline baseline. No Linux access/transfer, installation, service changes, external calls, company/vault/credential access, Git commit/push or live adapter implementation is authorized or performed.

## Baseline and inventory

The repository is on unborn `main`, with no tracked files/commits. Source, tests and reports are local untracked files; do not invent a Git commit reference. The accepted `docs/PHASE6_RELEASE_INVENTORY.json` has **70 entries**, every byte count/SHA-256 and aggregate matches current files, and records 256 tests. No Phase 6 inventory update is necessary. Preserve it as historical accepted evidence; the new release inventory adds that inventory itself and Phase 7A documentation/utilities.

No approved `src/` or `tests/` file, dependency manifest, handoff or earlier report was rewritten. Available authoritative handoffs retain their ` (1)` filenames. Earlier reports contain milestone-era status/counts; latest Phase 6 correction and test reports describe the accepted corrected baseline.

The release payload has **77 files**: 28 source files, 10 test files, 32 documentation files (including the accepted Phase 6 inventory), 2 release/compatibility utilities, and 5 root manifests/handoffs. The archive has **79 regular-file members**, including generated `RELEASE_INVENTORY.json` and `FILES.sha256`; no directory/link/device members are needed. Exact relative paths, byte counts and hashes are in the generated inventory. External `SHA256SUMS` records the archive and both metadata hashes; the complete archive digest is not embedded in its own payload.

## Files added and output scope

- `scripts/prepare_mac_release.py`: allowlisted standard-library source packager, deterministic archive and strict no-extraction integrity verifier.
- `scripts/linux_compatibility_check.py`: read-only interpreter/API probe, no actual filesystem/service/credential/network access; SQLite is in-memory.
- `docs/PHASE7_LINUX_READ_ONLY_CHECKLIST.md`: contract-by-contract evidence, permissions and future acceptance gates.
- `docs/PHASE7A_INTEGRATION_GAP_REPORT.md`: actual offline capabilities versus blocked live integration, Python compatibility and stale-notification limits.
- `docs/PHASE7A_OPERATOR_GUIDE.md`: integrity/validation/build commands, dependency checks and proposed staged acceptance/rollback.
- `docs/PHASE7A_RELEASE_REPORT.md`: this report.
- Generated versioned files only under `artifacts/releases/alfred-research-v1-0.1.0-phase7a-mac-20261015/`: archive, exact inventory, per-file manifest, archive checksums and verification result. Artifacts remain ignored by the existing `.gitignore`.

## Exclusions and trust

Packaging uses explicit root/extension inclusion, not Git status or a whole-directory tar. Git internals, `error.log`/other logs, `.env`/credentials/secrets, runtime databases, hot journals, registration receipts/authority snapshots, company state/vault data, caches/bytecode, temporary fixtures and prior release outputs are absent. No runtime state or actual company research is included. Source/tests contain explicitly synthetic fixture descriptions and the provided architecture/handoffs; these are not real credentials or company records. Symlinks, unsafe paths, nonregular archive members and bounded secret signatures are rejected. The heuristic signature scan is not a proof against arbitrary disguised secrets; the file allowlist and inspected provenance are the primary controls.

All models, verification, Memory/HQ, export/Sync and conversations remain explicitly SIMULATED / NON_PRODUCTION and disabled for production. SHA-256 manifests are unsigned integrity metadata, not authenticated approval or a substitute for a separate owner-approved transfer/deployment.

## Validation and future gates

Required full suite rerun: **256 passed, 0 failures, 0 errors**, 37.113 seconds, exit 0, Python 3.14.3 / SQLite 3.50.4 / macOS 14.3.1 ARM64. It retained all accepted tests, including large-transaction hot-journal recovery (intentional child exit 29 in each environment), forged-registration denial (child exit 30), stale cached/Sync receipts, immutable historical results, missing commit-outbox recovery, all environments, owner HQ permissions and notification deduplication.

The source compatibility metadata is unchanged (>=3.10), but hot recovery and its tests depend on `sqlite_errorname` from Python 3.11; Linux staging must use >=3.11 and pass the entire suite. Only the current Mac interpreter is positively validated. Empty runtime dependencies do not prove Linux filesystem/permission/registry compatibility. Optional setuptools>=61 build configuration is not an installation instruction.

See the external `INTEGRITY_VERIFICATION.json` for actual final archive SHA-256 and byte count, verified payload/member counts and exclusions. `SHA256SUMS` is the canonical archive digest record; this avoids a circular checksum in this included report. Packaging verification, reproducibility and negative-diagnostic results are recorded below after execution.

### Executed packaging and compatibility evidence

- Existing Phase 6 inventory: all 70 entries and its aggregate verified against current bytes; no mismatch and no update. The new 77-file release payload includes the historical inventory itself and six Phase 7A files. All 28 accepted source and 10 accepted test files retain their accepted SHA-256 digests.
- In-memory compilation: **40 Python files passed** (38 accepted src/test files plus two preparation utilities). `tomllib` assertions confirmed unchanged Python >=3.10 metadata, empty runtime dependencies and src package discovery. No bytecode, build or install.
- Compatibility probe on Mac: **PASS** for Python >=3.11/error-name API, sqlite3 foreign keys/triggers, POSIX flock/no-follow/dir-fd/fwalk availability. Python 3.14.3, SQLite 3.50.4, Darwin. Setuptools is **not installed**; source execution/tests require no backend. This is not Linux/filesystem acceptance. Compression toolchain: zlib build/runtime 1.2.12.
- Preflight packaging: exact 77 payload files plus two generated metadata members, every payload digest/size, inventory aggregate and external checksum verified. Two builds from identical bytes/transcript/toolchain produced identical archive bytes.
- Six temporary negative diagnostics were **rejected** as required: changed payload, traversal member, duplicate member, symlink member, missing member and changed external archive checksum. No hostile member was extracted or executed.
- An isolated extraction of the verified preflight package executed the complete suite: **256 passed, 0 failures, 0 errors**, 37.049 seconds, exit 0. Temporary package/test files were cleaned. The final report/guide then received this evidence; final packaging revalidates all approved code/test hashes and every final payload byte. The two full runs validate the same unchanged code/tests; they are not Linux acceptance.
- Final publication is local and versioned; no output is transferred or installed. Verify the final archive using the included utility and external SHA256SUMS. The external integrity report records the actual complete-archive digest and exact counts without a circular self-reference in this included report.

### Proposed owner gates

Review the current archive, manifests and docs; separately authorize redacted Linux read-only discovery. Resolve protected registration/identity, model/provider, source access, independent factual verification, Memory/HQ/Obsidian and Photon/correction contracts before proposing any live adapter. Staging, transfer, installation, service changes and canary writes require their own concrete approval. Preserve existing Memory/export/Sync repairs, runtime revocations and Development approval boundaries. Phase 7A stops at packaging; full V1 operational acceptance remains pending actual Linux integration.
