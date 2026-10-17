# Memory installation procedure correction

2026-10-16. **Procedure correction completed; installation remains BLOCKED.** No production patch, transfer, release-directory creation, symlink switch, service/timer change, database/vault modification, credential read, Research activation, commit/push or deployment occurred. Mac-local documents/review evidence and isolated synthetic checksum fixtures only were written.

## Reviewed inputs and preserved patch

Read MEMORY_DUPLICATE_CREATE_PATCH_VALIDATION.md, MEMORY_DUPLICATE_CREATE_OWNER_INSTALLATION.md, PHASE7U_MEMORY_RELEASE_DECISION.md and PHASE7U_MINIMAL_CHANGE_INVENTORY.md; inspected the exact patch and existing owner install/rollback helpers. The patch remains byte-identical SHA-256 `0b25c3b80d2c5878ed6a1b9f76a9f638b58e17ade7717bdb08e4e8e2566a3a4a`. Original store remains `5ca002bd93e486875191292c21ba782fb2df5eb3fa4d525654e80ad29069cf8c`; approved patched store remains `0d84c9c12c0715f14be7729a5007073ebc99f55fa7820e6bed81a55834d969c1`.

The change still only selects/returns the existing duplicate row's review_state. It adds no write or approval/promotion policy, schema/migration, Obsidian/Development behavior or Research integration. The prior six patched synthetic tests passed; no Memory or Research tests/imports were rerun in this read-only procedure correction.

## Checksum mistake and corrected command

The previous document used TWO literal backslashes before n inside the single-quoted printf format, producing a filename ending in literal backslash-n instead of newline-separated checksum input. The corrected format has ONE:

```sh
printf '%s  %s\n' '051bc9867010dd22882e4ac7982c071535208b2c566402958877468ecd20095c' OWNER_FILES.sha256 | sha256sum --strict --check -
```

That historical manifest still matches; verification does not make its superseded install scripts safe. Revision-2 helper payload verification is:

```sh
printf '%s  %s\n' 'e95ba6391c3fbd91880b0f9dd1b37e39a4bbb928d15f472efe788d1ce94b2dbc' PROCEDURE_FILES.sha256 | sha256sum --strict --check -
sha256sum --strict --check PROCEDURE_FILES.sha256
```

Mac-local synthetic tests created two synthetic files in a private temporary directory: correct newline input passed (exit 0); old malformed input failed (1); modified file failed (1); missing file failed (1); restored exact bytes passed (0). printf output was also asserted to contain two actual newline bytes and no literal backslash-n. GNU sha256sum is unavailable on this Mac, so its local check consumer was `/opt/local/bin/shasum -a 256 --check -`; actual printf bytes were unchanged. Local Perl locale warnings did not affect results. An initial harness-format assertion exposed an escaping error in the new test construction; it was corrected before accepting the final five-case evidence.

A read-only Linux check then ran GNU `/usr/bin/sha256sum --strict --check -` using printf-generated expected empty-file digest and `/dev/null`: corrected format exit 0 (`/dev/null: OK`), old format exit 1 (literal filename cannot be opened). No Linux temporary file was created. This validates the exact Linux consumer/format as well as isolated synthetic-file digest behavior. Evidence: `artifacts/reviews/memory-installation-procedure-20261016/CHECKSUM_SYNTHETIC_RESULTS.json`, `checksum_synthetic_test.py`, `FINAL_READ_ONLY_VERIFICATION.jsonl`.

## Shared-release correction and new blocker

Read-only systemd/source inspection found five direct shared consumers: `alfred-memory-v1.service`, `alfred-hq-capture.service`, `alfred-obsidian-editor-hq.service`, `alfred-obsidian-editor-hq-worker.service`, `alfred-hq-v1-sync-cycle.service`; two active publication timers; and a current-relative forced-command launcher. Capture/Editor/worker/Sync Require Memory, so a Memory-only stop/restart is not an isolated transition. Python code is startup-loaded and may also perform lazy/path-based loads later; atomic symlink replacement is not a process/job transaction.

R42 and R55 capture runtimes require current.resolve() == OLD; R40 Sync requires readlink(current) == OLD. All three constants were statically verified against actual installed source. Proposed NEW mismatches all three, with static checker exit 75. Capture files also pin R40's digest. Restarting all services would not fix this: they would refuse the new target. Retaining old processes or suppressing the checks is not an acceptable workaround.

Therefore the corrected document explicitly supersedes the old scripts, stops at the pin gate before mutation and requires owner-approved compatible forward/rollback guard binding through the existing release architecture. No replacement guards, production path, service unit or pin override were created. This remaining cross-component approval cannot be inferred from authorization for the two-line Memory correction.

## Complete original release evidence

The 34-file reviewed baseline is now supplemented by a complete installed code/runtime inventory:

- 1,378 regular files, 56,396,059 bytes; 185 directories including root; one internal `venv/lib64 -> lib` symlink; 1,564 total entries; all root-owned; no special files; no xattrs found.
- Exact paths, file sizes/SHA-256, type/mode/UID/GID, link targets and xattr digests were captured without following links, and independently rechecked after inspection. Membership/type checks precede content reads. Per-file stat identity/timestamps were checked around hashing. Known code/runtime/sample configs and public certifi CA bundle were hashed; no production credential, database, vault or runtime-state file was opened.
- Canonical original entry-list SHA-256 `66d72779e1fa34f56245061344d0f935a0d962343b8d8677ac313e54151161ac`.
- Saved full inventory SHA-256 `a837c601db2e1dc807fe3e5592baa61ade0e5dc9a13809d3ca3e455ecaa3d239`.
- Expected patched canonical entry-list SHA-256 `87227645b324a724f90d812dd4ceeb3665c4e7d179728e47b087f77094fe7bd2`, computed by changing only store size/digest. It is not a report of a newly created release; no clone or patch was applied in this phase.

`release_integrity_check.py` checks this exact inventory in original or patched mode, including missing/extra/unsafe paths and metadata, before preparation, after copy, after patch, immediately before/after switch, after service recovery and on rollback. A read-only run against OLD returned PASS for all 1,564 entries. Original full inventory remained unchanged; current still resolves to OLD.

## Required ordering and health/rollback criteria

The corrected owner document specifies: approve compatible pins and paired rollback first; exclusive window and existing-client ingress quiet; stop only two timers; let one-shot worker/export/Sync and child finish naturally; no stopping a 900-second Sync job under a 90-second unit-stop timeout; confirm authoritative idle/receipt state; stop Capture and idle Editor before Memory; verify full old/new code and external bindings; atomic rename with parent-directory fsync; start/accept Memory then Capture/Editor; restore only originally active timers/ingress and observe normal scheduled work, never a duplicate manual publication.

Editor SIGTERM raises SystemExit and has no general drain API; capture SIGTERM can finish its synchronous receive. Owner-provided quiet/drain/receipt evidence is required, not fabricated from unit inactive status. No private database, ledger, socket, actual Sync lock or receipt data was inspected in this task. Health, startup/cold-load and publication-currentness acceptance remain future owner checks; normal service startup/recovery may perform baseline database I/O and idempotent capture recovery. The patch adds no such I/O/migration.

Rollback uses the same quiescence and dependency ordering, revalidates both exact code inventories and the approved OLD-compatible external pins, atomically restores the preserved original source and recovers service/timer states. It preserves all latest database/ledger/receipt/tombstone/Sync state. Never rewind completed records/publications, restore an older DB/Sync snapshot, delete stages/queues/locks, create new IDs for ambiguous retries, force-kill publications or reverse-patch running production source. Reverting intentionally restores the known false-approved response defect.

## Remaining approvals and decision

Required: Memory semantic/consumer acceptance; shared Capture/Editor/Sync owners' compatible pin binding with exact forward/rollback files and hashes; complete runtime/import map; secure root-owned administrative payload and exclusive window; defined ingress/drain/reconciliation evidence; multi-service/timer ordering and health/currentness acceptance; normal publication resumption and rollback criteria. Owner must supply exact guard-bundle actions and authoritative drain mechanism before this specification becomes executable.

**PASS for corrected checksum validation and complete original integrity. BLOCKED for installation.** Next action: owner review of the discovered hard pins and a compatible guarded shared-release transition, then approval/revalidation of the coordinated procedure. Stop here; nothing has been installed or restarted.
