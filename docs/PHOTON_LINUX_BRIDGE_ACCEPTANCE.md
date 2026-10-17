# Photon Linux isolated bridge acceptance

2026-10-16. **PASS for the authorized isolated synthetic Linux validation.** All **23 tests passed**, none failed or skipped. This does not authorize production installation, live Spectrum connection, messaging or Research activation.

## Acceptance evidence

| Requirement | Result |
|---|---|
| libffi correction is narrow and legitimate | PASS; libffi8:amd64, root-owned system target, exact digest, one read-only file mount |
| Python isolation and no-credential checks | PASS; namespaces isolated, host paths absent, no privileged capability, clear environment |
| Node v26.7.0 resource/runtime availability | PASS; exact pinned binary initializes inside Bubblewrap |
| Network and host-loopback exclusion | PASS; probe-owned host-loopback and TEST-NET endpoint unreachable |
| Actual timeout process-tree cleanup | PASS for Python and Node; expected -9, no tracked identities remaining |
| Personal-only compatibility | PASS within preserved-source/fake-transport tests |
| Research disabled by default | PASS; disabled configuration invokes no Research factory or subscription |
| Project/line/sender/conversation identity separation | PASS with issued synthetic connection data |
| Explicit outbound identity and wrong-project denial | PASS |
| Research cannot fall back to Personal | PASS in staged terminal guard and unavailable/error tests |
| Duplicate/conflict/retry/restart separation | PASS; accepted logical sends reused, unknown sends not repeated |
| Baseline/SDK/runtime and stage integrity | PASS; 15 host hashes unchanged and exact 25-file stage verified |
| No actual Photon connection/message | PASS by reviewed fake-only execution scope plus network/credential confinement |

The original attempt was BLOCKED by the missing libffi mount before tests. Its evidence is preserved. The owner-authorized correction changed only that pinned mount; both corrected preflights passed before any transfer. No restriction was removed, no broad library-directory access added and no dependency installed.

## Executed scope and retained staging

Executed exactly 11 JavaScript bridge tests plus two installed-SDK source compatibility checks and ten Python guard/Personal compatibility tests. Node used --jitless, --max-old-space-size=64, --test-isolation=none and concurrency 1. Node runner duration 72.153153 ms; Python unittest duration 0.236 s. End-to-end sandbox walls were 0.193774 s and 0.419565 s respectively. Complete exact commands, names, limits, digests and cleanup records are in PHOTON_LINUX_BRIDGE_TEST_RESULTS.md and artifacts/audits/photon-linux-bridge-20261016/.

Retained isolated stage: `/home/alfred/research-staging/photon-two-project-20261016-kk95dzvp`, UID 1000, directories 0700/files 0600. Only reviewed nonsecret baseline/SDK entry files, patch, fake tests, manifest and bounded supervisor were transferred. Modified source was generated only inside this stage. No production source or configuration was modified. Both production services remained active/running; no restarts or service calls were made. No credentials, private messages, databases or vault contents were accessed.

## Compatibility limits

These results qualify the bounded synthetic subset on Linux Node v26.7.0 and Python 3.12.3 against pinned Spectrum 12.7.0 source definitions. They do not qualify a real two-project SDK session, full SDK import/initialization, active Hermes plugin installation/profile discovery, provider identity/delivery guarantees or production service-user filesystem behavior. Tests deliberately use fake transports and scoped hook/interface models rather than booting the installed orchestrator. No unrelated suite or optional SDK import-only case was run.

The existing current intake remains offline-only. Filling live IDs or changing enabled flags does not create a genuine host issuer, durable registration or acquisition authority. Research acquisition, model execution, Memory operations and FINAL notifications remain separately disabled/gated. Per-process limits and finite-tree cleanup do not establish aggregate cgroup limits or authorize broader multiprocess tests.

## Remaining production activation blockers

1. Independently review the five-file candidate delta and hashes against the then-current production baseline. Potential files remain: modify plugins/platforms/photon/sidecar/index.mjs, plugins/platforms/photon/adapter.py and gateway/run_inbound.py; add plugins/platforms/photon/sidecar/research-project.mjs and gateway/photon_research.py. No installation has occurred.
2. Approve protected Research project credential references and exact connection/receiving-line/sender/conversation/served-profile mapping. Preserve Personal credentials, line and route. Confirm Personal stable-line compatibility; no shared-mode assumption.
3. Review genuine host authentication/registration and exactly one durable research_project_intake handler with terminal failure behavior. Test actual Hermes loading/served-profile context through a separately approved scope before live use.
4. Review full SDK two-app lifecycle, logging/telemetry and failure/reconnect semantics separately; copied-source tests cannot prove them. Any SDK import-only or additional runtime case needs explicit bounded scope.
5. Approve protected Research ledger path, service-user ownership/permissions, single-process access, retention/capacity and authoritative UNKNOWN reconciliation. Do not delete dedupe records to force retry.
6. Approve concrete coordinated installation, service replacement/health checks and rollback. Preserve Development observer dependencies, existing Personal outbox and in-flight work. Never overlap consumers or remove Research reservation before disconnecting its ingress.
7. Separately approve a controlled live Research message/acceptance ACK and Personal control evidence proving actual destination and From identity. No live provider authentication or message is authorized by these test results.

**Next owner action:** review this PASS evidence and authorize a separate concrete integration/installation-readiness review. Research stays disabled; stop here for owner review.
