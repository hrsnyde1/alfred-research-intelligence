# Phase 7A operator guide: verify now, integrate only after authorization

This is a portable **source archive**, not an installer, service definition, production credential bundle, wheel or live Research release. Package version remains 0.1.0; release identity is `alfred-research-v1-0.1.0-phase7a-mac-20261015`. Existing Alfred/Hermes/Photon/Memory/Obsidian/Development components are not packaged or modified. Do not enable synthetic adapters in production.

## Integrity layout and commands

The versioned directory under `artifacts/releases/` contains the `.tar.gz`, external `RELEASE_INVENTORY.json`, `FILES.sha256`, `SHA256SUMS` and `INTEGRITY_VERIFICATION.json`. The archive has one release-named root and includes source/tests/manifests, the supplied master plan/handoffs, all operator/integration documents, and two standard-library release utilities.

`RELEASE_INVENTORY.json` lists every payload file's relative path, bytes and SHA-256. `FILES.sha256` covers that payload plus the inventory itself. These two generated metadata members are counted separately from payload. External `SHA256SUMS` covers the **complete archive**, inventory and file manifest. The verification report is an external observation, not a self-hashed payload. No circular/self-hash claim is made. Digests are unsigned integrity checks, not provenance signatures; compare the archive digest with the separately received owner-reviewed value.

On the Mac, from this repository:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/prepare_mac_release.py verify artifacts/releases/alfred-research-v1-0.1.0-phase7a-mac-20261015/alfred-research-v1-0.1.0-phase7a-mac-20261015.tar.gz
```

The verifier reads without extracting or executing archive content. It rejects path traversal, symlinks, duplicate/nonregular members, unexpected members, size/hash/count differences, altered inventory/manifest and archive checksum mismatch.

To validate the external checksums, first change to that versioned release directory, then run `shasum -a 256 -c SHA256SUMS` on Mac, or `sha256sum -c SHA256SUMS` on an independently authorized Linux staging host. Do not transfer anything as part of Phase 7A.

## Reproducible validation and packaging

From the source root (or a separately authorized isolated extraction root):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 scripts/linux_compatibility_check.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 -c 'from pathlib import Path; files=[*Path("src").rglob("*.py"),*Path("tests").rglob("*.py"),*Path("scripts").rglob("*.py")]; [compile(p.read_bytes(),str(p),"exec") for p in files]; print(len(files),"compiled in memory")'
PYTHONDONTWRITEBYTECODE=1 python3 -c 'import tomllib; from pathlib import Path; p=tomllib.loads(Path("pyproject.toml").read_text()); assert p["project"]["dependencies"]==[]; assert p["project"]["requires-python"]==">=3.10"; assert p["tool"]["setuptools"]["packages"]["find"]["where"]==["src"]; print("metadata PASS")'
```

For packaging, save the actual full unittest stdout/stderr to a local temporary transcript; confirm exit 0. The packager records its SHA-256, count and elapsed time but excludes logs from the release. Example used on this Mac:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -p 'test_*.py' -v > /tmp/alfred-phase7a-tests.txt 2>&1
PYTHONDONTWRITEBYTECODE=1 python3 scripts/prepare_mac_release.py build --release-id alfred-research-v1-0.1.0-phase7a-mac-20261015 --test-results /tmp/alfred-phase7a-tests.txt
```

The versioned output cannot be overwritten. To reproduce the same archive use an empty different local output directory with `--output`, the identical source bytes, successful test transcript and Python/zlib toolchain. Header order, owners, modes and timestamps are normalized; gzip timestamp is zero. A newly executed test transcript has a new duration/digest, so its release inventory and archive hash will legitimately differ. Do not reuse a test transcript after source changes as if it validates the new source. A new approved baseline/release ID is needed for a changed accepted component.

## Linux compatibility and dependencies

Only Mac Python 3.14.3 / SQLite 3.50.4 has passed locally. Metadata remains >=3.10, but Python **>=3.11 is a release staging gate** because hot-journal recovery uses SQLite exception `sqlite_errorname`; 3.10 is not qualified. `tomllib` in these preparation utilities also requires 3.11. Use an explicitly selected interpreter; do not rely on `python` aliases. No claim is made that every >=3.11 interpreter/SQLite build works until its complete regression and large-transaction diagnostics pass.

Runtime dependencies are empty. Python must provide sqlite3, hashlib, dataclasses, pathlib, json, contextlib, threading/concurrent.futures, subprocess/tempfile for synthetic tests, fcntl/flock and POSIX directory descriptors, O_NOFOLLOW/O_DIRECTORY, fwalk, stat/open dir_fd and hard-link/fsync semantics. Windows runtime is unqualified. Linux storage must separately prove same-filesystem publication, directory fsync, lock exclusion, permission/tenant boundaries and hot-journal behavior. The compatibility utility inspects APIs and uses SQLite `:memory:` only; it does not test host filesystems or access databases.

On a **separately authorized** Linux read-only inspection, use `PYTHONDONTWRITEBYTECODE=1 python3 scripts/linux_compatibility_check.py --require-linux`. No such execution occurred here. The probe reports installed setuptools metadata without installing/importing its build backend. `pyproject.toml` declares setuptools>=61 only for a future approved package build; it is not needed to run source tests. Do not run pip/uv install, a wheel build or network build isolation without new authorization. If a wheel is later required, inspect the existing approved backend first and approve an offline build procedure separately.

## Proposed staging, rollback and acceptance sequence

1. **Owner review now:** review current archive digest, exact inventory, test results and exclusions. Preserve this Mac baseline; hashes are authoritative for this snapshot because Git has no commits/tracked baseline. Nothing has been transferred.
2. **Authorize read-only discovery separately:** approve host and redacted scope; complete the contract checklist. Inventory existing service metadata and Python/SQLite/permissions without reading company content or secrets. No automatic adapter enablement.
3. **Resolve contracts and authorize staging separately:** approve exact smallest adapters, tenant/principal mappings, protected registration/credential authority, model assignments/budgets and receipt/currentness semantics. Review all expected changes before transfer/install. Use a separate immutable release directory and synthetic staging state; never copy test authority/state into production. No automatic schema migration.
4. **Stage and verify under that authorization:** verify transfer digest/members before extraction. Use an isolated destination, approved user and safe extraction policy. Run the complete suite, Mac/Linux canonical digest vectors, real target filesystem tests, large-transaction recovery, forged-registration denials, all 12 cross-company pairs and stale/ambiguous receipt tests. Do not point tests at production roots or vaults.
5. **Concrete rollout approval:** document exact Research-only files/configuration, service attachment to existing Hermes/Photon, scoped credential references, backups, health gates and stop/rollback conditions. Review actual installed baseline and schema compatibility first. Do not add a second orchestrator, messaging gateway or Memory system, replace existing workers or modify Development approvals.
6. **Authorized canaries:** one low-risk public Personal Alfred task, then an article and legitimately accessible document/media; actual model research and independent verdict, separate real commit/promotion/fresh specialist retrieval, proposal-only CTO handoff and truthful Photon completion. Add each company independently and explicitly eligible HQ owner retrieval; verify denied cross-company access, retractions, policy changes, stale events and source limits. No global enabling on partial success.
7. **Rollback proposal:** stop only the newly authorized Research attachment/dispatch, reconcile outstanding external receipts without blind resend, retain immutable evidence and revocation state, and revert approved Research-only routing/configuration to the inspected baseline. Pin the prior compatible code release; quarantine incompatible Research state for reviewed recovery. Never delete/reset databases, restore stale registration authority or reverse published Memory/HQ/Obsidian state blindly. Use Memory-owned compensating correction/revocation and distinct notification updates. Preserve repaired export staging and quarantines. Service operations/restoration still require owner authorization.
8. **Operational acceptance:** retain real task/source pins/packet digests/verifier identities and independent Memory/Photon/HQ/export receipts, current authorized retrieval and outage/restart evidence. Owner acceptance requires the actual Linux end-to-end pipeline, isolation and recovery. Mac simulations and this archive do not complete Research V1 operational acceptance.
