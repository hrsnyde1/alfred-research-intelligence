# Photon two-project bridge corrected diff

2026-10-16. **Compatibility corrections implemented and validated Mac-locally; Linux production unchanged.** This revision supersedes the prior staged patch. Prior Linux 23-test PASS belongs to the archived revision and does not qualify the new worker/caller-authority code.

Workspace: staging/photon-two-project-v1. Original candidate retained in staging/photon-two-project-v1-before-corrections. Exact installed baseline remains byte-for-byte unchanged. Corrected bridge.patch SHA-256: be1b8c0b900210f691b67e2e77cebea954b17909a9295d5f4edcbcacb29d632e. SOURCE_INVENTORY.json and TEST_INVENTORY.json freeze the source and synthetic evidence. Patch applied cleanly to an isolated baseline copy, all nine result file digests match.

## Source inventory

Paths relative to /home/alfred/.hermes/hermes-agent/. Eight proposed production files differ (three existing modifications, five additive modules). send-format.mjs is unchanged. No Development source correction is now needed: its authenticated legacy request is accepted unchanged. No Linux files were edited or transferred in this task.

| File | Original SHA-256 | Corrected SHA-256 |
|---|---|---|
| gateway/photon_research.py | NEW | 4aba0fdf6ed2b45ae5c401255e8d9d759e78e1bd2e4e38c7fbc4c63ccab5ee14 |
| gateway/run_inbound.py | 6a1a40708075e3550a824eae5519e98db97f52ea7995154e8c7e941de4e02144 | 89c3cf4daa0a04473d6302bf53f20b6d3839bd4960f0bc70674c27b9c429b018 |
| plugins/platforms/photon/adapter.py | 841ed6cb6e2d392fcec33f8983dd34fffe677c6a8d40e442bc449e66beeb16e5 | 540288fed36df43cb2e3049a1e46b94b1ddb0e94a4e8efad3f947e4f389e64c1 |
| plugins/platforms/photon/sidecar/caller-bindings.mjs | NEW | 1bafa6bb31376fcdf5cf237003555fc7ba7d289711bcc192335ed565232075bf |
| plugins/platforms/photon/sidecar/index.mjs | ef019d1d50e4ca680aede49276181f8eff8d396d9b7c22a73bb5da2b2d7bb8e4 | 2ac209c3864cf4165d55fbfff7ffa9e29d9a43b010d35937bc08ea51c73082ba |
| plugins/platforms/photon/sidecar/research-lifecycle.mjs | NEW | 6ae5e27a677cc6df9c2065e73ce727ccf11174c8a915d29134792fbe3df089dc |
| plugins/platforms/photon/sidecar/research-project.mjs | NEW | ea65df22546e19233bb79e976aaf366470fb3fb5d197c1c40c006a9aa9cb6e96 |
| plugins/platforms/photon/sidecar/research-worker.mjs | NEW | 98ac1071ae1c06d0cba0e31bde819cec5288fe16cb577479c9862a6c8bf501a7 |
| plugins/platforms/photon/sidecar/send-format.mjs | 827c6c0b3a7fd3b731365ecd17bb52d65b05c9a53e67795922ec2ebb79de58fe | 827c6c0b3a7fd3b731365ecd17bb52d65b05c9a53e67795922ec2ebb79de58fe |

## Caller binding correction

New caller-bindings.mjs binds the existing x-hermes-sidecar-token credential to immutable legacy-personal authority. Its unchanged authenticated /send body may omit project; only that credential resolves omission to Personal. Explicit personal remains valid. A research project field cannot elevate this caller. Unknown/invalid credentials deny before dispatch; a present invalid Research credential never falls back on a valid Personal credential.

Research requires a distinct PHOTON_RESEARCH_SIDECAR_TOKEN, conveyed through x-hermes-research-token, plus explicit project=research and scoped Research target. Colliding/missing tokens do not configure Research authority. Research authority cannot use Personal default, Personal action or inbound/control endpoints. Token values are never printed or placed in policy records. Immutable capability identity rejects copied caller objects.

adapter.py resolves the Research caller credential only in its protected Research send lane; it cannot substitute the existing Personal token. Legacy Personal/Development callers and their existing project initialization/handlers stay unchanged. index.mjs emits only fixed caller-role/project/action audit labels, never tokens, phone IDs or message contents. Shared legacy credentials identify an authorized host caller class, not individual humans or distinct Development/Hermes principals; that trust boundary must be approved.

## Independent startup correction

index.mjs no longer awaits Research startup. Personal creates its app and starts its existing listener; only the listen-ready callback requests Research start. New research-lifecycle.mjs creates a disposable Node worker (same bridge process, not a new service or Hermes instance). New research-worker.mjs initializes only the Research SDK project and state. Worker environment is empty, config is explicit, and stdout/stderr are drained without forwarding SDK output. No Personal credential is inherited by the worker. Both project secrets still reside within one OS process memory; worker isolation is not adversarial secret protection.

Research authentication deadline is 10 seconds, request deadline 10 seconds, one initialization attempt per lifecycle and no automatic worker restart. A five-minute hard session lease also bounds SDK internal/background retry activity, then makes Research unavailable. Timeout/error/exit/lease expiry terminates only that worker, rejects its pending obligations and does not close the Personal app/listener. This intentionally bounded canary lifetime is not an indefinitely available production connection; renewal policy needs owner review. Main-thread timers depend on a responsive host event loop; tests do not prove real-time scheduling guarantees.

Parent delivery receives an abort signal; Research cancellation removes only its waiter and does not clear a healthy Personal consumer. Research forwarding allows at most three write attempts and the session deadline; Personal retains its existing default delivery behavior. Research send ledger UNKNOWN-before-effect and no-resend semantics remain unchanged. Parent permits at most 16 pending Research RPCs. Graceful whole-bridge shutdown still stops Personal as before and terminates Research independently; no second inbound subscriber or competing Personal retry owner.

Research disabled means no caller-token lookup for Research in index initialization, no worker, no SDK factory and no state-directory creation. Missing caller authority or configuration leaves Research unavailable. Neither project field nor source text selects credentials/profile/environment. The existing terminal Research guard and offline-only intake boundary remain intact.

## Validation and remaining gates

Corrected Mac suites: 30 Node + 11 Python staged tests PASS; all 347 Research regressions PASS. Original 23 staged bridge/SDK checks remain included. Before/after reproductions show old Development body rejection and old awaited startup stall; corrected tests pass unchanged payload and independent Personal readiness. See PHOTON_TWO_PROJECT_BRIDGE_TEST_RESULTS.md.

New worker/resource/termination behavior and caller-token integration require a fresh separately authorized Linux isolated run; no old Linux evidence is relabeled. Genuine host intake, protected credential mapping, actual Hermes profile/hook integration, provider reconciliation, owner-approved canary lifetime and coordinated installation/rollback remain gates. No live credentials, Spectrum connection, messages, service restart or activation occurred.
