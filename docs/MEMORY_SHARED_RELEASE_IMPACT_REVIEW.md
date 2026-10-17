# Memory shared-release impact review

2026-10-16. **BLOCKED for a shared-current switch under the existing runtime pins.** This is a read-only Linux inspection. No service, timer, symlink, production source, database, vault or credential was changed/accessed as data. Application code was read statically, not imported or executed. No production API or Sync operation was invoked.

## Observed release and consumers

`/opt/alfred-obsidian-v1/current` resolves to `/opt/alfred-obsidian-v1/releases/4d5ba29bd3027e74c808a8feaf1b5dadfded22f0` (OLD). Five services directly reference `current/source` in effective systemd metadata. All five report `CanReload=no`, `KillMode=control-group`, SIGTERM and 90-second stop timeout. Active states below are observations, not guarantees for a later window.

| Exact unit | Observed state | Source/interpreter binding | Load and restart decision |
|---|---|---|---|
| `alfred-memory-v1.service` | active/running | WorkingDirectory `current/source`; `/opt/alfred-memory-v1/venv/bin/python -m obsidian_candidate.service_api` | Modules imported at startup. Its VersionedMemoryStore inherits corrected create. Stop/start required; it does not use the cloned shared venv as its primary interpreter. |
| `alfred-hq-capture.service` | active/running | Shared venv interpreter; external R42 `hq-capture-runtime.py`; absolute OLD/source inserted into sys.path after pin checks | Capture code loaded at startup; R40 checker imported when needed. Restart against NEW currently refuses. Quiesce and later start only after compatible pins are approved. |
| `alfred-obsidian-editor-hq.service` | active/running | Shared venv and cwd; `-m obsidian_candidate.alfred_editor_v1`, serve | Startup imports retain OLD code; late Python imports/resources may resolve paths again. Stop/start for one coherent release. SIGTERM raises SystemExit, so owner must first establish no in-flight ingress request. |
| `alfred-obsidian-editor-hq-worker.service` | inactive/dead, prior status 0 | Shared venv/cwd; effective commands include R55 `hq-capture-runtime.py` and editor `process-once` | One-shot imports at each activation. Disable its timer and let any invocation finish naturally; do not interrupt a publication. Next invocation currently refuses the NEW pin. |
| `alfred-hq-v1-sync-cycle.service` | inactive/dead, prior status 0 | Shared venv/cwd; external R40 `sync-cycle.py` | One-shot export checks and child headless Node Sync. Exact OLD symlink guard is checked at runtime before Sync. Disable timer and let active service plus child complete. Next activation currently refuses NEW. |

Indirect scheduling consumers: `alfred-obsidian-editor-hq-worker.timer` and `alfred-hq-v1-sync-cycle.timer`, both active/waiting, `Persistent=no`. Restarting either may schedule work promptly; do not restore them until recovery/health acceptance. The Sync service Requires both the worker and editor plus Memory. Worker/capture/editor also Require Memory. Explicitly stopping Memory can therefore stop dependent units; restarting Memory does not establish that all dependents return to their original state.

Additional discovered paths:

- `bin/editor-ssh-forced` changes cwd to shared `current/source` and invokes shared `current/venv/bin/python -E`. Each future invocation resolves current again. Its presence is established; active SSH authorization/configuration was not read, so active external ingress binding is not proven. Owner must account for any installed use when pausing editor clients.
- `alfred-memory-v1-backup.service` uses separate `/opt/alfred-memory-v1/current` and its venv, `focused_v1.ops`; it is inactive at observation. Its active backup timer is `Persistent=yes`. It does not resolve to the inspected shared release. No backup command, database or keys were opened. No restart is proposed for it; owner must account for any backup overlapping the maintenance window under existing backup policy.
- Inspected Hermes, Photon and Development service metadata has no shared current binding; no changes/stops/restarts are proposed for those services. Their clients may still call Memory or capture, so owner must establish a quiet write/ingress window without inventing service/configuration changes here.

Discovery examined 298 concrete installed service/timer/socket/path unit names for working-directory/path bindings and 31 Alfred/shared units for effective executable/module/dependency metadata. Uninstantiated systemd templates were excluded after the initial bulk query refused them. No other direct service consumer was discovered in this scope. This is not an audit of every cron, manual shell command, plugin/config environment or external client. Environment/configuration/credential files, process arguments and actual company data were not read. `/proc` cwd/exe links for service accounts were inaccessible; no privilege escalation was used to bypass that restriction.

## Hard blockers demonstrated by actual source

Three installed external runtime files enforce the original release identity:

| File | SHA-256 | Exact guard |
|---|---|---|
| R42 `/opt/alfred-hq-r42-review/alfred-hq-v1-hq-capture-integration-4d5ba29-r42/hq-capture-runtime.py` | `dc7da685c8c2ccfd6a5a26a4579d072d202578a38029a4bfeace7746ac5f3d4f` | SOURCE at line 20 is OLD/source; pinned(), lines 49–58, requires current.resolve() == SOURCE.parent, validates six unchanged source hashes and R40_SHA, then inserts OLD/source. |
| R55 `/opt/alfred-hq-r55-review/alfred-hq-v1-stage-repair-r55/hq-capture-runtime.py` | `840ae2973d016ee1a8e927076de1610ce4e271d0d12ac9df60568ef6815e7287` | Same OLD/source and current-target guard, lines 19, 48–57; also pins the R40 digest. |
| R40 `/opt/alfred-hq-r40-review/alfred-hq-v1-multi-export-sync-4d5ba29-r40/sync-cycle.py` | `c7066a924a958c80fb3a18f8f49ca45fb6348fce5ddb49910c27b54241eb628c` | RELEASE at line 23 is OLD; pinned_runtime(), lines 280–289, requires readlink(current) == str(RELEASE). |

Static `pin_preflight.py` against the proposed NEW returned exactly these three mismatches (exit 75), without importing or executing those runtimes. The six R42/R55 source hashes do not include store.py, but their exact-target guard alone blocks the new release. Rebinding R40 also changes its digest, requiring reviewed updates of both R40_SHA consumers. Do not remove/weaken these guards or retain running OLD processes to conceal the mismatch.

There is no successful shared-current installation sequence that both leaves these installed guards unchanged and resumes all normal services against NEW. A separately approved compatible pin/release binding, with an exact forward AND rollback manifest, is required. Such a binding is outside the two-line Memory patch, has not been built/authorized, and is not implemented by this review. Do not introduce an alternate Memory production path or unit override as a shortcut.

## Dynamic loading and mixed-version risks

Python modules remain in each process's sys.modules after a symlink switch; a changed current does not hot-patch them. Modules may be imported lazily, absolute current paths reopened, and new processes started under NEW while OLD ones still run. R42/R55 additionally force OLD/source. R40 dynamically loads the pinned headless runtime and is also loaded by capture export code. Atomic symlink rename is atomic only for directory entry lookup, not for this distributed process/job transition.

Consequences of the original Memory-only restart plan: dependents may stop through Requires relationships; active OLD processes can survive with old imports; the next capture/worker restart or Sync activation can fail its pin; shared forced-command invocations can observe NEW immediately. Restarting just Memory is therefore insufficient for coherent and operational rollout.

## Quiescence and publication safety

R42 capture's SIGTERM handler sets a stopping flag, allowing the current synchronous receive to finish before loop exit and socket removal. Editor ingress instead raises SystemExit on SIGTERM; no general drain API is present. Client quiet/acknowledgment and absence of in-flight work are prerequisites to stopping editor or Memory. Do not label systemctl inactive alone as proof that a request committed successfully.

Worker-route holds existing WriterCoordinator locks, recovers capture intents by original IDs and can stage/publish one export. Sync uses the existing vault-writers lock, checks export/Sync state and starts a separate-session Node child with a 900-second timeout. Unit stop timeout is only 90 seconds: stopping a running Sync unit could interrupt a publication even though its command has a longer natural bound. Stop the two timers, then wait for both one-shots and their cgroups/jobs to finish naturally before stopping their required editor/Memory services. Do not run runtime `inspect`, worker-route, process-once, recover, export or Sync as a preflight here; these can read credentials/state or publish.

Durable pending receipts are not a reason to purge queues or replay requests with new IDs. Owner must preserve operation IDs, expected versions, capture bindings, stages, receipts and tombstones, reconcile ambiguous outcomes through existing reviewed mechanisms, and never rewind completed Memory/Obsidian records on code rollback. No production state was inspected, so drain/reconciliation is an owner acceptance gate, not established evidence.

## Complete release integrity evidence

All 1,378 regular files (56,396,059 bytes), 185 directories including root and one symlink were inventoried and reverified. The sole link is internal `venv/lib64 -> lib`; no special files or state-path symlinks were found. All entries are root-owned. SHA-256 includes regular-file bytes; inventory includes exact membership, types, sizes, modes, UID/GID, link targets and xattr digests (none present). No symlink content was followed. Immutable package code/runtime, sample configuration and public certifi CA certificates are included; no production DB/vault/credential/state file was selected. No store.py bytecode cache was present in the source tree.

- Original canonical entry-list SHA-256: `66d72779e1fa34f56245061344d0f935a0d962343b8d8677ac313e54151161ac`.
- Saved full inventory SHA-256: `a837c601db2e1dc807fe3e5592baa61ade0e5dc9a13809d3ca3e455ecaa3d239`.
- Expected patched canonical entry-list SHA-256: `87227645b324a724f90d812dd4ceeb3665c4e7d179728e47b087f77094fe7bd2` — computed expectation, NOT a staged/installed full release observation. Only store.py bytes/size change; expected regular-byte total is 56,396,083.

Evidence: `artifacts/reviews/memory-installation-procedure-20261016/INSTALLED_RELEASE_INVENTORY.json`, `SHARED_UNIT_METADATA.jsonl`, `RUNTIME_SOURCE_REVIEW.jsonl`, `TIMER_METADATA.jsonl`, `FINAL_READ_ONLY_VERIFICATION.jsonl`. The final read-only verifier matched every original entry again. No candidate full-release clone was created on Linux.

**Decision:** correction procedure preparation can finish, but installation stays BLOCKED pending compatible owner-approved shared-runtime pins, window/quiescence and rollback/health acceptance. See [corrected owner procedure](MEMORY_DUPLICATE_CREATE_OWNER_INSTALLATION.md).
