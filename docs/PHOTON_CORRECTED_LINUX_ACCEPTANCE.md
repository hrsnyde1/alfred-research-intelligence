# Corrected Photon bridge Linux acceptance

2026-10-16. **PASS — all 41 approved corrected bridge tests passed on Linux**, 0 failed/skipped. Installation, service replacement, credential provisioning and live Research activation remain unauthorized.

## Acceptance disposition

| Requirement | Evidence/result |
|---|---|
| Installed source/SDK/runtime baseline | PASS; 15 pinned host inputs match before/after, Node26.7.0 and SDK12.7.0 |
| Existing Personal-only initialization | PASS; preserved source/function equivalence and disabled-worker tests |
| Unchanged Development /send body | PASS; archived handler rejection reproduced, corrected exact handler accepts through authenticated legacy Personal binding |
| Unknown callers cannot obtain default authority | PASS; invalid/missing credentials and copied capability objects deny |
| Independent Research authority and explicit project | PASS; distinct host token required; payload field cannot elevate legacy Personal |
| Research cannot use Personal/default | PASS; Research credential with absent/personal project denied, no fallback |
| Authentication stalls/failures cannot gate Personal | PASS; fake-factory and actual disposable-worker tests with Personal availability |
| Research disabled by default/missing credentials | PASS; no worker/factory/config access when disabled, missing authority/config unavailable |
| Project identity/ID/cache/retry separation | PASS; concurrent fake traffic, cross-project denial, scoped ledgers and UNKNOWN no-resend |
| Research cannot fall through to Personal agent | PASS; terminal guard/profile/error/unknown-event tests |
| Worker resource and timeout confinement | PASS; actual worker readiness under unchanged limits, forced namespace teardown and all tracked identities gone |
| No real provider authentication/messages | PASS; fake-only execution with network/host paths/credentials excluded |
| Transfer/candidate integrity | PASS; exact 30-file stage, all payload/candidate hashes and permissions independently verified |

Missing project is permitted **only** for an already authenticated legacy Personal caller under the approved fixed binding; unknown callers and Research callers cannot use that default. This compatibility rule is intentional, not a missing-identity bypass. Legacy shared token denotes a trusted host caller class, not individual human identity.

## Executed scope

30 Node tests plus 11 Python tests, including all 23 original checks and 18 correction regressions. Node runner duration 408.726753 ms, Python 0.268 s; complete sandbox walls 0.537292 s and 0.441401 s. Three narrowly scoped 2-second forced timeout preflights passed for Python, Node and Node worker; actual test deadlines were 45 seconds. All cleanup remaining lists were empty. No unrelated suite or real SDK initialization was run.

Exact commands, original/result hashes, every test name, runtime/resource records and source/transfer manifests: PHOTON_CORRECTED_LINUX_TEST_RESULTS.md and artifacts/audits/photon-corrected-linux-20261016/.

Corrected patch SHA-256: be1b8c0b900210f691b67e2e77cebea954b17909a9295d5f4edcbcacb29d632e. Linux stage retained at `/home/alfred/research-staging/photon-corrected-20261016-i4rcwpsy`, owned by UID1000 with 0700 directories/0600 files. It is an isolated test tree, not an installed service path. The former test stage and production remain untouched.

## What this closes

The corrected candidate's previously pending Linux synthetic validation is complete, including the new worker under the existing 64 GiB virtual/15 s CPU limits and pinned libffi mount. No package, mount-directory expansion, cgroup/AppArmor or permission change was required. Both compatibility blockers are closed within the tested synthetic scope. There was no Linux-specific test failure or corrective product edit during this run.

Personal's active service connection was never restarted or used for a test. Read-only postcheck shows Photon PID140714 and Hermes PID454732 active/running, and all 15 host input hashes unchanged. No actual phone/account identifier, secret, private message, database or vault content was accessed. Synthetic credentials in fixtures do not become production trust.

## Limits and remaining installation approvals

1. Owner must review the current eight-file source delta and freshly reverify baseline/dependency hashes immediately before any installation. The old five-file manifest and proposed Development source edit are superseded; Development caller stays unchanged.
2. Approve protected Research project ID/secret and **separate Research sidecar caller-token** references, scope/permissions and exclusion from company agents. No real references were populated or read. The shared Node process is not an adversarial memory boundary.
3. Approve exact line/requester/conversation/connection/Research profile and actual served-profile/plugin configuration. A genuine host issuer, durable registration and intake hook remain required; current offline capability fixtures cannot be enabled for real messages.
4. Review actual SDK two-project import/authentication/stream lifecycle, log redaction and provider delivery/reconciliation guarantees separately. This run used real Node workers with substituted fake SDK where needed, not actual provider sessions.
5. Approve the bounded five-minute Research session lease, single auth attempt/no automatic worker restart and UNKNOWN outcome policy, or separately review a bounded renewal design. Successful fake tests do not establish indefinite production availability.
6. Approve service-user ledger directory, single-process access, retention/capacity and backup/currentness policy. Tests used private tmpfs as UID1000, not the production service user's state directory.
7. Prepare/review updated Research-disabled installation, shared-client inventory, source ownership, quiescence, coordinated Photon/Hermes restart/health/Personal regression and rollback. Earlier procedure documents must be reconciled with the eight-file patch and distinct caller token before execution. No live switch or source write is authorized by this acceptance.
8. Separately approve controlled real Research destination/From identity and Personal control evidence. No live login, message, model/provider work, Memory promotion or Research activation follows from this PASS.

The prior 347 Mac Research regressions remain valid historical evidence; they were not rerun outside this task's 41-test scope. Full installed Hermes boot/plugin integration and actual messaging remain outside acceptance. Per-process limits and finite worker cleanup do not establish aggregate cgroup controls for broader workloads.

**Recommendation: PASS for corrected isolated Linux acceptance. Minimum next step: owner review of a revised Research-disabled installation candidate and maintenance/rollback plan. Keep Research disabled and stop here.**
