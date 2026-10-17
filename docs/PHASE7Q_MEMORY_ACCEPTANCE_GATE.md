# Phase 7Q — Memory acceptance gate

2026-10-16 — **Preparation complete; execution BLOCKED pending owner approval and Memory-specific runtime preflight.** No files transferred, Linux writes made or Memory tests executed. Research remains disabled. See [scope](PHASE7Q_MEMORY_TEST_SCOPE.md) and [exact transfer/commands](PHASE7Q_MEMORY_TRANSFER_PLAN.md).

## Compatibility design review

| Requirement | Evidence / conclusion |
| --- | --- |
| Reuse existing Memory architecture | ResearchStage holds the existing copied MemoryStore object and uses its SQLite transaction context; additive research_stage tables are explicitly initialized in a fresh synthetic database. No second authoritative Memory service or server process is introduced |
| Existing Obsidian behavior | All 33 unchanged original baseline/work files, including server, service_api and Obsidian modules/exporter/tests, remain byte-identical; only ordinary create duplicate response in store.py changes. Candidate capture's separate fixed-actor behavior is untouched. No Research projection enters legacy approved memory/export. Paired unmanaged-note regression is proposed, not executed; full behavioral preservation remains unproven |
| Production Research promotion disabled | TestAuthority and ResearchStage require explicit test_only=True/production=False. ResearchStage.promote and dispatch_research always deny. Existing HTTP dispatcher action set excludes Research. simulate_promotion is visibly simulated, not genuine verification |
| No live credentials/company data | Fixtures generate deletion keys/tokens/principals locally in ephemeral scratch; synthetic personal/gabos/fintra/sc labels do not grant real company access. No credential/vault/config mounts or live endpoints |
| No additional service | Test code constructs local store/authority objects only. No HTTP server, Unix listener, systemd unit, scheduler or daemon is launched by selected methods |
| Linux compatibility | Selected paths use stdlib SQLite/WAL/fcntl/owned-temp filesystem operations and installed x86_64 cryptography/CFFI native runtime. No macOS framework, Homebrew executable, Node, PDF, live /opt key, /etc/skel or account fixture is needed. Static/source/linkage evidence supports feasibility; no Memory runtime pass is claimed |

The copied extension is staging-only, not a deployable API/migration. Real attestation issuer/signature policy, schema/migration/rollback approval, production grants/tenant mapping, retention/legal hold/delete and Research export/Sync decisions remain unresolved. Deletion/export paths intentionally fail closed. Those remain deployment blockers even after any bounded synthetic test pass.

## Gate A — owner approval of exact plan

Approve or revise the seven existing work extension IDs, the paired derived duplicate-state probe and one existing unmanaged-note test in each copy (eleven planned invocations total), the 17 source/evidence files, twenty reused Research inputs, and 77 additional public-runtime file binds. The exact bytes/hashes and unexecuted supervisor are in the transfer plan. This gate does not authorize 23-case discovery, 102/125 Memory suites, the 305 Research suite, services or activation.

Acknowledge missing requested PHASE7H_MEMORY_CHANGE_PLAN.md / PHASE7H_MEMORY_ACCEPTANCE_TESTS.md and the explicitly identified Phase 7G/reconstructed 7H evidence mapping, or provide the originals. rsync availability is not verified; an absent transfer utility must not trigger installation or an unreviewed archive-copy fallback.

## Gate B — isolated source transfer (future authorization only)

1. Rehash all selected Mac files against the pinned 17-entry manifest; reject path/hash/length/duplicate/symlink changes. Preserve baseline originals and the existing release.
2. Recheck non-symlink UID-1000 parent and absent leaf; create only fresh mode-0700 phase7q-memory-20261016 after explicit approval. No reused service/staging directory.
3. Transfer exactly listed files, preserve layout and verify exact remote membership/hashes. Verify selected baseline files against BASELINE_MANIFEST's unchanged entries. No archive/config/log/key/DB/vault transfer.
4. Reverify the frozen Research archive/release and the twenty reused files. A mismatching accepted input stops the plan; do not fix or reinitialize it on Linux.

## Gate C — mandatory Memory runtime/isolation preflight

This is new Memory authorization, not inherited from Research tests. Before importing any Memory test, require:

- Python 3.12.3, exact installed cryptography 41.0.7/native origins, all 85 runtime hashes/resolved targets, no site/.pth/config fallback. AESGCM round-trip with newly generated synthetic bytes and temporary SQLite commit/reopen must actually succeed inside the namespace.
- Private user/mount/net/PID/IPC/UTS, zero capabilities/NoNewPrivs, disabled additional userns, private proc/dev, no service/credential/vault/agent sockets or host paths, exact reviewed read-only source/runtime binds, private 16 MiB temp mounts and verified safe environment including PWD=/workspace.
- No nonloopback route/interface; probe-owned host-loopback listener denied; no actual production endpoint probe.
- Exact readback of per-process ceilings: CPU 10 s, AS 256 MiB, FSIZE 8 MiB, NOFILE 64, CORE 0, NPROC 128 shared-UID guard; wall 20 s/case, bounded output and 300-second serial campaign. No aggregate-cgroup claim.
- Successful exact-pidfd forced namespace cleanup using the same launcher/reaper logic; no observed matching process identities/listeners remain. The new Memory-specific source/runtime mount arrangement must be dynamically confirmed, not inferred solely from Phase 7P.

Any unrelated failure stops before Memory methods. Do not install, add broad mounts, read production configuration/credentials, patch signature/ownership checks, adjust AppArmor/cgroups or fall back to host execution. Missing cryptography ABI/provider files are preparation blockers, not permission to change crypto semantics or expose host /etc.

## Gate D — bounded comparison acceptance

The seven original work extension methods each execute exactly once, one loaded ID per namespace; no errors/skips. Paired derived duplicate probe uses the unchanged existing method AST with a minimal store fixture: baseline must show only its known pending→approved response assertion failure, work must pass all states; preserve raw baseline exit 1. Unexpected baseline pass/different failure or any error invalidates this narrow negative-witness comparison. Do not manufacture a baseline Research extension or overlay the work module onto it.

The original unmanaged-note refusal test must pass unchanged in both copies. Tests must report actual IDs, source origins, case durations, self CPU/peak RSS, raw exits and cleanup evidence. Every other invocation requires exit 0; no new work-only failure is acceptable. Compare evidence per test, not aggregate counts. Rehash all staged/reused/runtime inputs after testing; no mutated/extra source or ambiguous remaining process identity may be accepted.

A future PASS may say only: seven selected extension cases and narrowly scoped comparisons succeeded under synthetic isolated Linux execution. It cannot claim all 23 extension tests passed, all inherited Mac failures resolved, all Obsidian/Memory compatibility cleared, cryptographic factual verification established or production integration enabled.

## Relationship to earlier blockers

Phase 7O/P supersedes the earlier uncertainty about whether unprivileged Bubblewrap can launch this class of finite workload; actual namespace/forced-cleanup evidence now exists. Phase 7J's full-suite runtime/account/public-key/Node/PDF/concurrency and aggregate-resource gates are **not globally cleared**. This proposal excludes those cases and uses no child/worker fan-out, so a dedicated cgroup is not essential for this reviewed serial tranche. Supervisor/kernel/tmpfs overhead remains outside a strict aggregate guarantee.

Missing production trust/schema/export/retention decisions are untouched. Full Memory operational acceptance still needs broader separately approved comparisons, including inherited atomic-rename/peer-credential and deployment-fixture reproductions. Research's 16 passing tests concern Research simulation; they are not proof of this different Memory-owned extension.

## Current stop boundary

Only the three Phase 7Q Mac-local documents and Mac /tmp planning/evidence text were written. Actual Memory source/tests, 92-file inventory, baseline/work artifacts, release/archive and production systems remain unchanged. Remote activity was stdlib read/hash/linkage metadata inspection only; no cryptography/Memory imports, test, Linux file creation, transfer, service/config change, package install, cgroup/AppArmor modification, credentials/vault/data access, commit, push or deployment occurred.

**Recommendation: approve/review this narrow proposal separately; do not execute yet. Await owner approval.**
